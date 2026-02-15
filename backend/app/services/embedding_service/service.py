import logging
import config
from typing import List, Dict, Any, Optional
import torch
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from app.core.config import settings
from app.models.database.weaviate import WeaviateUserProfile
from app.services.embedding_service.profile_summarization.prompts.summarization_prompt import PROFILE_SUMMARIZATION_PROMPT


MODEL_NAME = config.MODEL_NAME
MAX_BATCH_SIZE = config.MAX_BATCH_SIZE
EMBEDDING_DEVICE = config.EMBEDDING_DEVICE


logger = logging.getLogger(__name__)


class ProfileSummaryResult(BaseModel):
    """Result of profile summarization"""
    summary_text: str
    token_count_estimate: int
    embedding: Optional[List[float]] = None

class EmbeddingService:
    """Service for generating embeddings and profile summarization for Weaviate integration"""

    def __init__(self, model_name: str = MODEL_NAME, device: str = EMBEDDING_DEVICE):
        """
        Initialize EmbeddingService with the embedding model name and target device.
        
        Parameters:
            model_name (str): Identifier of the embedding model to use (defaults to configured MODEL_NAME).
            device (str): Device for model execution (e.g., "cpu" or "cuda"; defaults to configured EMBEDDING_DEVICE).
        """
        self.model_name = model_name
        self.device = device
        self._model = None
        self._llm = None
        self._model_loading = False
        self._model_access_count = 0
        logger.info(f"Initializing EmbeddingService with model: {model_name} on device: {device}")

    @property
    def model(self) -> SentenceTransformer:
        ## track how often model is accessed
        """
        Provide the SentenceTransformer instance, loading it on first access if necessary.
        
        Returns:
            model (SentenceTransformer): The embedding model instance used for generating embeddings.
        """
        self._model_access_count+=1
        logger.debug(
            f"EmbeddingService.model accessed "    
            f"(access count={self._model_access_count}, "
            f"model_loaded={self._model is not None})"
        )
        
        """Lazy-load embedding model to avoid loading during import"""
        if self._model is None:
            # Detect concurrent initialization attempts (observability only)
            if self._model_loading:
                logger.warning(
                    "Concurrent access detected while embedding model is initializing. "
                    "This may indicate a race condition."
                )

            self._model_loading = True
            try:
                logger.info(
                    f"No cached embedding model found. "
                    f"Initializing model '{self.model_name}' on device '{self.device}'."
                )
                self._model = SentenceTransformer(self.model_name, device=self.device)
                
                logger.info(
                    f"Embedding model initialized successfully. "
                    f"Embedding dimension: {self._model.get_sentence_embedding_dimension()}"
                )
            except Exception as e:
                logger.error(f"Error loading model {self.model_name}: {str(e)}",
                exc_info=True
                )
                raise
            finally:
                self._model_loading = False
        else:
            # Explicit reuse log (this was missing earlier)
            logger.debug(
                "Reusing existing embedding model instance from cache."
            )
                
        return self._model

    @property
    def llm(self) -> ChatGoogleGenerativeAI:
        """Lazy-load LLM for profile summarization"""
        if self._llm is None:
            try:
                self._llm = ChatGoogleGenerativeAI(
                    model=settings.github_agent_model,
                    temperature=0.3,
                    google_api_key=settings.gemini_api_key
                )
                logger.info("LLM initialized for profile summarization")
            except Exception as e:
                logger.error(f"Error initializing LLM: {str(e)}")
                raise
        return self._llm

    async def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text input"""
        try:
            # Convert to list for consistency
            if isinstance(text, str):
                text = [text]

            # Generate embeddings
            embeddings = self.model.encode(
                text,
                convert_to_tensor=True,
                show_progress_bar=False
            )

            # Convert to standard Python list and return
            embedding_list = embeddings[0].cpu().tolist()
            logger.debug(f"Generated embedding with dimension: {len(embedding_list)}")
            return embedding_list
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple text inputs in batches"""
        try:
            # Generate embeddings
            embeddings = self.model.encode(
                texts,
                convert_to_tensor=True,
                batch_size=MAX_BATCH_SIZE,
                show_progress_bar=len(texts) > 10
            )

            # Convert to standard Python list
            embedding_list = embeddings.cpu().tolist()
            logger.info(f"Generated {len(embedding_list)} embeddings")
            return embedding_list
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            raise

    async def summarize_user_profile(self, profile: WeaviateUserProfile) -> ProfileSummaryResult:
        """Generate a comprehensive summary of a user profile optimized for embedding and semantic search."""
        try:
            logger.info(f"Summarizing profile for user: {profile.github_username}")

            bio = profile.bio or "No bio provided"
            languages = ", ".join(profile.languages) if profile.languages else "No languages specified"
            topics = ", ".join(profile.topics) if profile.topics else "No topics specified"

            prs_info = []
            for pr in profile.pull_requests:
                pr_desc = pr.body if pr.body else "No description"
                prs_info.append(f"{pr.title} in {pr.repository}: {pr_desc}")
            pull_requests_text = " | ".join(prs_info) if prs_info else "No recent pull requests"

            stats_text = f"Followers: {profile.followers_count}, Following: {profile.following_count}, Total Stars: {profile.total_stars_received}, Total Forks: {profile.total_forks}"

            prompt = PROFILE_SUMMARIZATION_PROMPT.format(
                github_username=profile.github_username,
                bio=bio,
                languages=languages,
                pull_requests=pull_requests_text,
                topics=topics,
                stats=stats_text
            )

            logger.info(f"Sending profile summarization request to LLM for {profile.github_username}")
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            summary_text = response.content.strip()

            # Estimate token count (rough approximation: 1 token ≈ 4 characters)
            token_estimate = len(summary_text) // 4
            logger.info(
                f"Generated profile summary for {profile.github_username}: {len(summary_text)} chars (~{token_estimate} tokens)"
            )

            embedding = await self.get_embedding(summary_text)

            return ProfileSummaryResult(
                summary_text=summary_text,
                token_count_estimate=token_estimate,
                embedding=embedding
            )

        except Exception as e:
            logger.error(f"Error summarizing profile for {profile.github_username}: {str(e)}")
            raise

    async def process_user_profile(self, profile: WeaviateUserProfile) -> tuple[WeaviateUserProfile, List[float]]:
        """Process a user profile by generating summary and embedding, then updating the profile object."""
        try:
            logger.info(f"Processing user profile for Weaviate storage: {profile.github_username}")

            summary_result = await self.summarize_user_profile(profile)

            profile.profile_text_for_embedding = summary_result.summary_text

            logger.info(
                f"Successfully processed profile for {profile.github_username}: summary generated with {summary_result.token_count_estimate} estimated tokens"
            )

            return profile, summary_result.embedding

        except Exception as e:
            logger.error(f"Error processing user profile for Weaviate: {str(e)}")
            raise

    async def search_similar_profiles(self, query_text: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for similar profiles using embedding similarity.
        This method generates an embedding for the query and searches for similar contributors.
        """
        try:
            logger.info(f"Searching for similar profiles with query: {query_text[:100]}")

            query_embedding = await self.get_embedding(query_text)

            logger.info(f"Generated query embedding with dimension: {len(query_embedding)}")

            from app.database.weaviate.operations import search_similar_contributors

            results = await search_similar_contributors(
                query_embedding=query_embedding,
                limit=limit,
                min_distance=0.5
            )

            logger.info(f"Found {len(results)} similar contributors for query")
            return results

        except Exception as e:
            logger.error(f"Error searching similar profiles: {str(e)}")
            raise

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model being used"""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "embedding_size": self.model.get_sentence_embedding_dimension(),
        }

    def clear_cache(self):
        """Clear the model cache to free memory"""
        if self._model:
            del self._model
            self._model = None
        if self._llm:
            del self._llm
            self._llm = None
        # Force garbage collection
        import gc
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("Cleared embedding service cache")