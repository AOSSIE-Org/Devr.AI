import logging
import threading
import asyncio
import os
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor

import torch
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

import config
from app.core.config import settings
from app.models.database.weaviate import WeaviateUserProfile
from app.services.embedding_service.profile_summarization.prompts.summarization_prompt import (
    PROFILE_SUMMARIZATION_PROMPT,
)

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

logger = logging.getLogger(__name__)

MODEL_NAME = config.MODEL_NAME
EMBEDDING_DEVICE = config.EMBEDDING_DEVICE
MAX_BATCH_SIZE = config.MAX_BATCH_SIZE
SAFE_BATCH_SIZE = getattr(config, "SAFE_BATCH_SIZE", 32)
EXECUTOR_MAX_WORKERS = getattr(
    config, "EXECUTOR_MAX_WORKERS", min(2, os.cpu_count() or 1)
)
DEFAULT_MAX_CONCURRENT_GPU_TASKS = getattr(
    config, "MAX_CONCURRENT_GPU_TASKS", 2
)


class ProfileSummaryResult(BaseModel):
    summary_text: str
    token_count_estimate: int
    embedding: List[float]


class EmbeddingService:
    # Class-level resources shared across all instances
    _global_model: Optional[SentenceTransformer] = None
    _global_model_lock = threading.Lock()
    _shutting_down_global = False  # Global shutdown flag for shared model

    def __init__(self) -> None:
        self._llm: Optional[ChatGoogleGenerativeAI] = None
        self._tokenizer: Optional[Any] = None

        self._embedding_executor: Optional[ThreadPoolExecutor] = None
        self._llm_executor: Optional[ThreadPoolExecutor] = None

        self._executor_lock = threading.Lock()
        self._llm_lock = threading.Lock()
        self._tokenizer_lock = threading.Lock()

        self._gpu_semaphores: Dict[int, asyncio.Semaphore] = {}
        self._gpu_semaphore_lock = threading.Lock()

        self._shutting_down = False

        logger.info(
            "EmbeddingService initialized | device=%s | workers=%s | gpu_limit=%s",
            EMBEDDING_DEVICE,
            EXECUTOR_MAX_WORKERS,
            DEFAULT_MAX_CONCURRENT_GPU_TASKS,
        )

    def _get_gpu_semaphore(self, limit: Optional[int]) -> asyncio.Semaphore:
        concurrency = limit or DEFAULT_MAX_CONCURRENT_GPU_TASKS

        with self._gpu_semaphore_lock:
            if concurrency not in self._gpu_semaphores:
                self._gpu_semaphores[concurrency] = asyncio.Semaphore(concurrency)
            return self._gpu_semaphores[concurrency]

    @property
    def embedding_executor(self) -> ThreadPoolExecutor:
        if self._embedding_executor is None:
            with self._executor_lock:
                if self._embedding_executor is None:
                    self._embedding_executor = ThreadPoolExecutor(
                        max_workers=EXECUTOR_MAX_WORKERS,
                        thread_name_prefix="embedding-worker",
                    )
        return self._embedding_executor

    @property
    def llm_executor(self) -> ThreadPoolExecutor:
        if self._llm_executor is None:
            with self._executor_lock:
                if self._llm_executor is None:
                    self._llm_executor = ThreadPoolExecutor(
                        max_workers=1,
                        thread_name_prefix="llm-worker",
                    )
        return self._llm_executor

    @property
    def model(self) -> SentenceTransformer:
        # First check instance shutdown flag
        if self._shutting_down:
            raise RuntimeError("This EmbeddingService instance is shutting down")

        # Then check and load model with proper locking
        if EmbeddingService._global_model is None:
            with EmbeddingService._global_model_lock:
                # Check global shutdown flag inside the lock
                if EmbeddingService._shutting_down_global:
                    raise RuntimeError("EmbeddingService globally is shutting down")
                
                if EmbeddingService._global_model is None:
                    logger.info("Loading embedding model: %s", MODEL_NAME)
                    EmbeddingService._global_model = SentenceTransformer(
                        MODEL_NAME,
                        device=EMBEDDING_DEVICE,
                    )
        return EmbeddingService._global_model

    @property
    def llm(self) -> ChatGoogleGenerativeAI:
        if self._llm is None:
            with self._llm_lock:
                if self._llm is None:
                    self._llm = ChatGoogleGenerativeAI(
                        model=settings.github_agent_model,
                        temperature=0.3,
                        google_api_key=settings.gemini_api_key,
                    )
        return self._llm

    @property
    def tokenizer(self) -> Optional[Any]:
        if not TIKTOKEN_AVAILABLE:
            return None

        if self._tokenizer is None:
            with self._tokenizer_lock:
                if self._tokenizer is None:
                    self._tokenizer = tiktoken.get_encoding("cl100k_base")
        return self._tokenizer

    def _count_tokens(self, text: str) -> int:
        if self.tokenizer:
            try:
                return len(self.tokenizer.encode(text))
            except Exception as e:
                logger.warning(f"Tokenizer failed: {e}, falling back to heuristic")
        # Fallback estimation based on words
        return max(1, int(len(text.split()) * 1.3))

    async def _encode(
        self,
        texts: List[str],
        max_concurrent_tasks: Optional[int],
    ) -> torch.Tensor:
        if not texts:
            embedding_dim = self.model.get_sentence_embedding_dimension()
            return torch.empty((0, embedding_dim))

        semaphore = self._get_gpu_semaphore(max_concurrent_tasks)

        async with semaphore:
            loop = asyncio.get_running_loop()
            outputs: List[torch.Tensor] = []

            for i in range(0, len(texts), MAX_BATCH_SIZE):
                batch = texts[i : i + MAX_BATCH_SIZE]

                tensor = await loop.run_in_executor(
                    self.embedding_executor,
                    lambda b=batch: self.model.encode(
                        b,
                        convert_to_tensor=True,
                        normalize_embeddings=True,
                        batch_size=min(len(b), SAFE_BATCH_SIZE),
                    ),
                )

                outputs.append(tensor)
                await asyncio.sleep(0)

            return torch.cat(outputs, dim=0)

    async def get_embedding(
        self,
        text: str,
        max_concurrent_tasks: Optional[int] = None,
    ) -> List[float]:
        tensor = await self._encode([text], max_concurrent_tasks)
        return tensor[0].cpu().tolist()

    async def get_embeddings(
        self,
        texts: List[str],
        max_concurrent_tasks: Optional[int] = None,
    ) -> List[List[float]]:
        tensor = await self._encode(texts, max_concurrent_tasks)
        return tensor.cpu().tolist()

    async def _invoke_llm(self, messages: List[HumanMessage]) -> str:
        try:
            response = await self.llm.ainvoke(messages)
            return response.content.strip()
        except Exception as e:
            logger.exception(
                "LLM invocation failed for profile=%s",
                getattr(messages[0], "content", "")[:50],
            )

            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                self.llm_executor,
                lambda: self.llm.invoke(messages),
            )
            return response.content.strip()

    async def summarize_user_profile(
        self,
        profile: WeaviateUserProfile,
        max_concurrent_tasks: Optional[int] = None,
    ) -> ProfileSummaryResult:
        prompt = PROFILE_SUMMARIZATION_PROMPT.format(
            github_username=profile.github_username,
            bio=profile.bio or "No bio",
            languages=", ".join(profile.languages or []),
            topics=", ".join(profile.topics or []),
            pull_requests=" | ".join(
                f"{pr.title}: {pr.body or ''}" for pr in profile.pull_requests
            ) or "No PRs",
            stats=f"Followers={profile.followers_count}, Stars={profile.total_stars_received}",
        )

        summary = await self._invoke_llm([HumanMessage(content=prompt)])
        token_count = self._count_tokens(summary)
        embedding = await self.get_embedding(summary, max_concurrent_tasks)

        return ProfileSummaryResult(
            summary_text=summary,
            token_count_estimate=token_count,
            embedding=embedding,
        )

    async def process_user_profile(
        self,
        profile: WeaviateUserProfile,
        max_concurrent_tasks: Optional[int] = None,
    ) -> tuple[WeaviateUserProfile, List[float]]:
        summary_result = await self.summarize_user_profile(profile, max_concurrent_tasks)
        profile.profile_text_for_embedding = summary_result.summary_text
        return profile, summary_result.embedding

    async def search_similar_profiles(
        self,
        query_text: str,
        limit: int = 10,
        max_concurrent_tasks: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        query_embedding = await self.get_embedding(query_text, max_concurrent_tasks)
        from app.database.weaviate.operations import search_similar_contributors

        return await search_similar_contributors(
            query_embedding=query_embedding,
            limit=limit,
            min_distance=0.5,
        )

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "model_name": MODEL_NAME,
            "device": EMBEDDING_DEVICE,
            "embedding_size": self.model.get_sentence_embedding_dimension(),
            "tiktoken_available": TIKTOKEN_AVAILABLE,
            "safe_batch_size": SAFE_BATCH_SIZE,
            "max_batch_size": MAX_BATCH_SIZE,
            "default_max_concurrent_gpu_tasks": DEFAULT_MAX_CONCURRENT_GPU_TASKS,
            "executor_workers": EXECUTOR_MAX_WORKERS,
            "model_loaded": EmbeddingService._global_model is not None,
            "global_shutdown": EmbeddingService._shutting_down_global,
            "instance_shutdown": self._shutting_down,
        }

    def shutdown(self) -> None:
        """Shutdown this instance and optionally the global model if no other instances exist."""
        self._shutting_down = True
        logger.info("Shutting down EmbeddingService instance")

        with self._executor_lock:
            if self._embedding_executor:
                self._embedding_executor.shutdown(wait=True)
                self._embedding_executor = None
            if self._llm_executor:
                self._llm_executor.shutdown(wait=True)
                self._llm_executor = None

        # Clear instance-specific resources
        with self._llm_lock:
            self._llm = None
        
        with self._tokenizer_lock:
            self._tokenizer = None

        logger.info("EmbeddingService instance shutdown complete")

    @classmethod
    def shutdown_global(cls) -> None:
        """Shutdown all global resources (model) shared across all instances."""
        with cls._global_model_lock:
            cls._shutting_down_global = True
            cls._global_model = None
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            logger.info("Cleared GPU cache")
        
        logger.info("EmbeddingService global shutdown complete")

    async def __aenter__(self) -> "EmbeddingService":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        self.shutdown()