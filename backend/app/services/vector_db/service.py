import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class EmbeddingItem(BaseModel):
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


class EmbeddingService:
    """Service for generating embeddings for text"""


class VectorDBService:
    """Service for interacting with Supabase Vector DB"""
    