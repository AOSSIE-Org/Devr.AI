import os
import logging
from typing import List, Dict, Any, Optional
from uuid import UUID
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()

# Get Supabase credentials from environment variables
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

logger = logging.getLogger(__name__)

class EmbeddingItem(BaseModel):
    """
    Pydantic model representing an embedding item to be stored in the vector database.
    
    Attributes:
        id: Unique identifier for the embedding
        collection: Collection name this embedding belongs to
        content: The original text content that was embedded
        metadata: Additional information about the embedding as key-value pairs
        embedding: Vector representation of the content as a list of floats
    """
    id: str
    collection: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    embedding: Optional[List[float]] = None


class VectorDBService:
    """
    Service for interacting with Supabase Vector Database via RPC calls.
    
    This service provides methods to perform CRUD operations on embedding items
    stored in a Supabase PostgreSQL database with pgvector extension.
    """

    def __init__(self, table_name: str = "embeddings"):
        """
        Initialize the VectorDBService with Supabase connection.
        
        Args:
            table_name: Name of the table to store embeddings (default: "embeddings")
        """
        if not supabase_url or not supabase_key:
            logger.warning("Supabase credentials not provided. Operations will fail.")

        self.client: Client = create_client(supabase_url, supabase_key)
        self.table_name = table_name

    def _convert_embedding_to_pg_vector(self, embedding: List[float]) -> str:
        """
        Convert a list of floats to PostgreSQL vector string format.
        
        Args:
            embedding: List of floating point values representing an embedding vector
            
        Returns:
            String representation of the vector compatible with PostgreSQL
        """
        if not embedding:
            return "[]"
        return '[' + ','.join(map(str, embedding)) + ']'

    def _parse_pg_vector(self, vector_str: str) -> Optional[List[float]]:
        """
        Parse PostgreSQL vector string to list of floats.
        
        Args:
            vector_str: String representation of a vector from PostgreSQL
            
        Returns:
            List of floating point values or None if input is empty
        """
        if not vector_str:
            return None

        vector_str = vector_str.strip('[]()')
        return [float(x) for x in vector_str.split(',') if x]

    async def create_table(self) -> bool:
        """
        Create the embeddings table using an RPC function.
        
        Returns:
            Boolean indicating success or failure
        """
        try:
            response = self.client.rpc("create_embeddings_table").execute()
            return response.data is not None
        except Exception as e:
            logger.error(f"Error creating table: {str(e)}")
            return False

    async def add_item(self, item: EmbeddingItem) -> bool:
        """
        Insert a single embedding item into the vector database using RPC.
        
        Args:
            item: EmbeddingItem instance to be stored
            
        Returns:
            Boolean indicating success or failure
        """
        try:
            embedding_str = self._convert_embedding_to_pg_vector(item.embedding)
            response = self.client.rpc(
                "add_embedding",
                {
                    "p_id": item.id,
                    "p_collection": item.collection,
                    "p_content": item.content,
                    "p_metadata": item.metadata,
                    "p_embedding": embedding_str,
                },
            ).execute()
            return response.data is not None
        except Exception as e:
            logger.error(f"Error adding item: {str(e)}")
            return False

    async def add_items(self, items: List[EmbeddingItem]) -> bool:
        """
        Insert multiple embedding items using a single RPC call.
        
        Args:
            items: List of EmbeddingItem instances to be stored
            
        Returns:
            Boolean indicating success or failure
        """
        try:
            data = [
                {
                    "p_id": str(item.id),
                    "p_collection": item.collection,
                    "p_content": item.content,
                    "p_metadata": item.metadata,
                    "p_embedding": self._convert_embedding_to_pg_vector(item.embedding),
                }
                for item in items
            ]

            response = self.client.rpc("add_multiple_embeddings", {"data": data}).execute()
            return response.data is not None
        except Exception as e:
            logger.error(f"Error adding multiple items: {str(e)}")
            return False

    async def search(
        self, query_embedding: List[float], collection: str, limit: int = 5, threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar embeddings using Supabase RPC.
        
        Args:
            query_embedding: Vector representation to search for
            collection: Collection name to search in
            limit: Maximum number of results to return (default: 5)
            threshold: Similarity threshold, higher values mean more similar results (default: 0.5)
            
        Returns:
            List of matching embedding items with similarity scores
        """
        try:
            query_embedding_str = self._convert_embedding_to_pg_vector(query_embedding)
            response = self.client.rpc(
                "search_embeddings",
                {
                    "p_query_embedding": query_embedding_str,
                    "p_collection": collection,
                    "p_limit": limit,
                    "p_threshold": threshold,
                },
            ).execute()
            # Parse embeddings from strings to lists
            results = response.data or []
            for result in results:
                result['embedding'] = self._parse_pg_vector(result['embedding'])
            return results
        except Exception as e:
            logger.error(f"Error searching embeddings: {str(e)}")
            return []

    async def get_item(self, item_id: str, collection: str) -> Optional[EmbeddingItem]:
        """
        Retrieve an embedding item by ID and collection via RPC.
        
        Args:
            item_id: Unique identifier of the item
            collection: Collection name the item belongs to
            
        Returns:
            EmbeddingItem if found, None otherwise
        """
        try:
            response = self.client.rpc(
                "get_embedding",
                {
                    "p_id": item_id,
                    "p_collection": collection
                },
            ).execute()

            if response.data:
                data = response.data[0]
                # Parse the embedding string to a list
                embedding = self._parse_pg_vector(data.get('embedding'))
                return EmbeddingItem(
                    id=data["id"],
                    collection=data["collection"],
                    content=data["content"],
                    metadata=data["metadata"],
                    embedding=embedding,  # Using the already parsed embedding
                )
            return None
        except Exception as e:
            logger.error(f"Error getting item: {str(e)}")
            return None

    async def update_item(self, item: EmbeddingItem) -> bool:
        """
        Update an embedding item via RPC.
        
        Args:
            item: EmbeddingItem instance with updated values
            
        Returns:
            Boolean indicating success or failure
        """
        try:
            embedding_str = self._convert_embedding_to_pg_vector(item.embedding)
            response = self.client.rpc(
                "update_embedding",
                {
                    "p_id": str(item.id),
                    "p_collection": item.collection,
                    "p_content": item.content,
                    "p_metadata": item.metadata,
                    "p_embedding": embedding_str,
                },
            ).execute()
            return response.data is not None
        except Exception as e:
            logger.error(f"Error updating item: {str(e)}")
            return False

    async def delete_item(self, item_id: str, collection: str) -> bool:
        """
        Delete an embedding item via RPC.
        
        Args:
            item_id: Unique identifier of the item to delete
            collection: Collection name the item belongs to
            
        Returns:
            Boolean indicating success or failure
        """
        try:
            response = self.client.rpc(
                "delete_embedding",
                {
                    "p_id": item_id,
                    "p_collection": collection
                }
            ).execute()
            return response.data is not None
        except Exception as e:
            logger.error(f"Error deleting item: {str(e)}")
            return False

    async def list_collections(self) -> List[str]:
        """
        List all unique collections via RPC.
        
        Returns:
            List of collection names available in the database
        """
        try:
            response = self.client.rpc("list_collections").execute()
            return [row["collection"] for row in response.data] if response.data else []
        except Exception as e:
            logger.error(f"Error listing collections: {str(e)}")
            return []

    async def check_connection(self) -> bool:
        """
        Check Supabase connection via an RPC function.
        
        Returns:
            Boolean indicating if the connection is working
        """
        try:
            response = self.client.rpc("check_embeddings_connection").execute()
            return response.data is not None
        except Exception as e:
            logger.error(f"Connection check failed: {str(e)}")
            return False
