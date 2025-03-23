import unittest
from unittest.mock import patch, MagicMock
import json

from .app.services.rag.vector_db import VectorDBClient

class TestVectorDBClient(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.supabase_url = "https://test.supabase.co"
        self.supabase_key = "test_supabase_key"
        
        # Create a patcher for the create_client
        self.client_patcher = patch('app.services.rag.vector_db.create_client')
        self.mock_create_client = self.client_patcher.start()
        
        # Create mock Supabase client
        self.mock_supabase = MagicMock()
        self.mock_create_client.return_value = self.mock_supabase
        
    def tearDown(self):
        """Clean up after each test method."""
        self.client_patcher.stop()
        
    def test_initialization(self):
        """Test that the client initializes correctly."""
        # Create client
        client = VectorDBClient(self.supabase_url, self.supabase_key)
        
        # Assertions
        self.mock_create_client.assert_called_once_with(self.supabase_url, self.supabase_key)
        self.assertEqual(client.supabase, self.mock_supabase)
                  
    def test_store_embeddings(self):
        """Test storing embeddings."""
        # Setup test data
        chunks = ["First chunk", "Second chunk"]
        embeddings = [[0.1, 0.2], [0.3, 0.4]]
        
        # Setup mock response
        mock_table = MagicMock()
        mock_insert = MagicMock()
        mock_execute = MagicMock()
        
        self.mock_supabase.table.return_value = mock_table
        mock_table.insert.return_value = mock_insert
        mock_insert.execute.return_value = MagicMock(error=None)
        
        # Create client and call method
        client = VectorDBClient(self.supabase_url, self.supabase_key)
        client.store_embeddings(chunks, embeddings)
        
        # Assertions
        self.mock_supabase.table.assert_called_once_with('embeddings')
        
        # Verify correct data was prepared
        expected_data = [
            {'content': 'First chunk', 'embedding': json.dumps([0.1, 0.2])},
            {'content': 'Second chunk', 'embedding': json.dumps([0.3, 0.4])}
        ]
        mock_table.insert.assert_called_once_with(expected_data)
        mock_insert.execute.assert_called_once()
        
    def test_store_embeddings_error(self):
        """Test error handling when storing embeddings."""
        # Setup test data
        chunks = ["First chunk", "Second chunk"]
        embeddings = [[0.1, 0.2], [0.3, 0.4]]
        
        # Setup mock response with error
        mock_table = MagicMock()
        mock_insert = MagicMock()
        mock_execute = MagicMock()
        
        self.mock_supabase.table.return_value = mock_table
        mock_table.insert.return_value = mock_insert
        mock_insert.execute.return_value = MagicMock(error="DB Error")
        
        # Create client and call method
        client = VectorDBClient(self.supabase_url, self.supabase_key)
        
        # Should raise exception
        with self.assertRaises(Exception) as context:
            client.store_embeddings(chunks, embeddings)
            
        self.assertIn("Failed to store embeddings", str(context.exception))
        
    def test_retrieve_documents(self):
        """Test retrieving documents."""
        # Setup test data
        query_embedding = [0.1, 0.2, 0.3]
        limit = 5
        
        # Mock documents to return
        mock_documents = [
            {"content": "Doc 1", "similarity": 0.95},
            {"content": "Doc 2", "similarity": 0.85}
        ]
        
        # Setup mock response
        mock_rpc = MagicMock()
        mock_execute = MagicMock()
        
        self.mock_supabase.rpc.return_value = mock_rpc
        mock_rpc.execute.return_value = MagicMock(data=mock_documents, error=None)
        
        # Create client and call method
        client = VectorDBClient(self.supabase_url, self.supabase_key)
        result = client.retrieve_documents(query_embedding, limit)
        
        # Assertions
        self.mock_supabase.rpc.assert_called_once_with(
            'match_documents', 
            {'query_embedding': json.dumps(query_embedding), 'result_limit': limit}
        )
        mock_rpc.execute.assert_called_once()
        self.assertEqual(result, mock_documents)
        
    def test_retrieve_documents_default_limit(self):
        """Test retrieving documents with default limit."""
        # Setup test data
        query_embedding = [0.1, 0.2, 0.3]
        
        # Mock documents to return
        mock_documents = [
            {"content": "Doc 1", "similarity": 0.95},
            {"content": "Doc 2", "similarity": 0.85}
        ]
        
        # Setup mock response
        mock_rpc = MagicMock()
        mock_execute = MagicMock()
        
        self.mock_supabase.rpc.return_value = mock_rpc
        mock_rpc.execute.return_value = MagicMock(data=mock_documents, error=None)
        
        # Create client and call method
        client = VectorDBClient(self.supabase_url, self.supabase_key)
        result = client.retrieve_documents(query_embedding)  # No limit specified
        
        # Assertions
        self.mock_supabase.rpc.assert_called_once_with(
            'match_documents', 
            {'query_embedding': json.dumps(query_embedding), 'result_limit': 3}  # Default limit is 3
        )
        self.assertEqual(result, mock_documents)
        
    def test_retrieve_documents_error(self):
        """Test error handling when retrieving documents."""
        # Setup test data
        query_embedding = [0.1, 0.2, 0.3]
        
        # Setup mock response with error
        mock_rpc = MagicMock()
        mock_execute = MagicMock()
        
        self.mock_supabase.rpc.return_value = mock_rpc
        mock_rpc.execute.return_value = MagicMock(error="DB Error")
        
        # Create client and call method
        client = VectorDBClient(self.supabase_url, self.supabase_key)
        
        # Should raise exception
        with self.assertRaises(Exception) as context:
            client.retrieve_documents(query_embedding)
            
        self.assertIn("Failed to retrieve documents", str(context.exception))

if __name__ == '__main__':
    unittest.main()