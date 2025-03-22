import logging
import os
from typing import List, Dict, Any, Optional
import torch
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

MODEL_NAME = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
MAX_BATCH_SIZE = int(os.getenv("EMBEDDING_MAX_BATCH_SIZE", "32"))
EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "cpu")

logger = logging.getLogger(__name__)


class EmbeddingItem(BaseModel):
    id: str
    collection: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    embedding: Optional[List[float]] = None

class EmbeddingService:
    """Service for generating embeddings for text using Hugging Face models"""

    def __init__(self, model_name: str = MODEL_NAME, device: str = EMBEDDING_DEVICE):
        """Initialize the embedding service with specified model"""
        self.model_name = model_name
        self.device = device
        self._model = None
        logger.info(f"Initializing EmbeddingService with model: {model_name} on device: {device}")

    @property
    def model(self) -> SentenceTransformer:
        """Lazy-load model to avoid loading during import"""
        if self._model is None:
            try:
                logger.info(f"Loading model: {self.model_name}")
                self._model = SentenceTransformer(self.model_name, device=self.device)
            except Exception as e:
                logger.error(f"Error loading model {self.model_name}: {str(e)}")
                raise
        return self._model

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
            return embedding_list
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            raise

    # Process_item and process_items are used to add embeddings to items
    # Can be migrated to a separate class if needed aligning both VectorDB service and Embedding service
    async def process_item(self, item: EmbeddingItem) -> EmbeddingItem:
        """Process a single item to add embedding"""
        if not item.embedding:
            item.embedding = await self.get_embedding(item.content)
        return item

    async def process_items(self, items: List[EmbeddingItem]) -> List[EmbeddingItem]:
        """Process multiple items to add embeddings efficiently"""
        # Extract content from items that need embeddings
        texts_to_embed = []
        items_to_embed = []
        
        for item in items:
            if not item.embedding:
                texts_to_embed.append(item.content)
                items_to_embed.append(item)
        
        if texts_to_embed:
            # Generate embeddings in batch
            embeddings = await self.get_embeddings(texts_to_embed)
            
            # Update items with their embeddings
            for i, item in enumerate(items_to_embed):
                item.embedding = embeddings[i]
        
        return items

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
            # Force garbage collection
            import gc
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
