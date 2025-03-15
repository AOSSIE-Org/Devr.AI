import json
from supabase import create_client, Client
from typing import List, Dict, Any


class VectorDBClient:
    def __init__(self, supabase_url: str, supabase_key: str, create_schema: bool = False):
        self.supabase: Client = create_client(supabase_url, supabase_key)
        if create_schema:
            try:
                self.create_embeddings_table_and_function()
            except Exception as e:
                print(f"Warning: Could not create database schema: {e}")
                print("Assuming schema already exists. If not, please create it manually.")

    def create_embeddings_table_and_function(self):
        """Creates the embeddings table and the match_documents function in the database which will be used to query embeddings. """
        create_table_query = """
        CREATE EXTENSION IF NOT EXISTS vector;
        CREATE TABLE IF NOT EXISTS embeddings (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            embedding VECTOR(384) -- Assuming a 384-dimensional embedding from Hugging Face
        );
        """
        create_function_query = """
        CREATE OR REPLACE FUNCTION match_documents(query_embedding VECTOR(384), result_limit INT DEFAULT 5)
        RETURNS TABLE(id INT, content TEXT, distance FLOAT) AS $$
        BEGIN
            RETURN QUERY
            SELECT e.id, e.content, l2_distance(e.embedding, query_embedding) AS distance
            FROM embeddings e
            ORDER BY distance
            LIMIT result_limit;
        END;
        $$ LANGUAGE plpgsql;
        """
        self.supabase.postgrest.rpc('execute_sql', {'sql': create_table_query}).execute()
        self.supabase.postgrest.rpc('execute_sql', {'sql': create_function_query}).execute()

    def store_embeddings(self, chunks: List[str], embeddings: List[List[float]]):
        data = [{'content': chunks[i], 'embedding': json.dumps(embedding)} for i, embedding in enumerate(embeddings)]
        response = self.supabase.table('embeddings').insert(data).execute()
        if hasattr(response, 'error') and response.error:
            raise Exception(f"Failed to store embeddings: {response.error}")

    def retrieve_documents(self, query_embedding: List[float], limit: int = 3) -> List[Dict[str, Any]]:
        response = self.supabase.rpc('match_documents', {'query_embedding': json.dumps(query_embedding), 'result_limit': limit}).execute()
        if hasattr(response, 'error') and response.error:
            raise Exception(f"Failed to retrieve documents: {response.error}")
        return response.data
