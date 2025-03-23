import json
from supabase import create_client, Client
from typing import List, Dict, Any


class VectorDBClient:
    """
    Client for interacting with Supabase vector database to store and retrieve embeddings.
    Provides methods for storing text chunks with their vector embeddings and finding similar documents.
    """
    def __init__(self, supabase_url: str, supabase_key: str, create_schema: bool = False):
        """
        Initialize the vector database client with Supabase credentials.
        
        Args:
            supabase_url: URL of the Supabase project
            supabase_key: API key for the Supabase project
            create_schema: Whether to create the database schema if it doesn't exist
        """
        self.supabase: Client = create_client(supabase_url, supabase_key)
        if create_schema:
            try:
                self.create_embeddings_table_and_function()
            except Exception as e:
                print(f"Warning: Could not create database schema: {e}")
                print("Assuming schema already exists. If not, please create it manually.")

    def store_embeddings(self, chunks: List[str], embeddings: List[List[float]]):
        """
        Store text chunks and their corresponding embeddings in the database. Length of chunks and embeddings should match.
        
        Args:
            chunks: List of text chunks to store
            embeddings: List of embedding vectors corresponding to each chunk
        
        Raises:
            Exception: If the storage operation fails
        """
        data = [{'content': chunks[i], 'embedding': json.dumps(embedding)} for i, embedding in enumerate(embeddings)]
        response = self.supabase.table('embeddings').insert(data).execute()
        if hasattr(response, 'error') and response.error:
            raise Exception(f"Failed to store embeddings: {response.error}")

    def retrieve_documents(self, query_embedding: List[float], limit: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve documents similar to the query embedding using vector similarity search.
        
        Args:
            query_embedding: The embedding vector of the query
            limit: Maximum number of results to return
            
        Returns:
            List of documents with similarity scores
            
        Raises:
            Exception: If the retrieval operation fails
        """
        response = self.supabase.rpc('match_documents', {'query_embedding': json.dumps(query_embedding), 'result_limit': limit}).execute()
        if hasattr(response, 'error') and response.error:
            raise Exception(f"Failed to retrieve documents: {response.error}")
        return response.data
