import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import tempfile
import shutil

from .app.services.rag.rag_retriever import RAGRetriever

class TestRAGRetriever(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create mock parameters
        self.github_token = "test_github_token"
        self.supabase_url = "https://test.supabase.co"
        self.supabase_key = "test_supabase_key"
        
        # Create test directory for temp files
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up after each test method."""
        # Remove test directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
    @patch('app.services.rag.rag_retriever.GitHubDownloader')
    @patch('app.services.rag.rag_retriever.VectorDBClient')
    @patch('app.services.rag.rag_retriever.TextEmbedder')
    def test_initialization(self, mock_text_embedder, mock_vector_db, mock_gh_downloader):
        """Test that the retriever initializes correctly."""
        # Setup mocks
        mock_gh_downloader_instance = MagicMock()
        mock_vector_db_instance = MagicMock()
        mock_text_embedder_instance = MagicMock()
        
        mock_gh_downloader.return_value = mock_gh_downloader_instance
        mock_vector_db.return_value = mock_vector_db_instance
        mock_text_embedder.return_value = mock_text_embedder_instance
        
        # Create retriever
        retriever = RAGRetriever(self.github_token, self.supabase_url, self.supabase_key)
        
        # Assertions
        mock_gh_downloader.assert_called_once_with(self.github_token)
        mock_vector_db.assert_called_once_with(self.supabase_url, self.supabase_key)
        mock_text_embedder.assert_called_once()
        
        self.assertEqual(retriever.github_downloader, mock_gh_downloader_instance)
        self.assertEqual(retriever.vector_db, mock_vector_db_instance)
        self.assertEqual(retriever.text_embedder, mock_text_embedder_instance)
        
    @patch('app.services.rag.rag_retriever.GitHubDownloader')
    @patch('app.services.rag.rag_retriever.VectorDBClient')
    @patch('app.services.rag.rag_retriever.TextEmbedder')
    def test_initialization_error(self, mock_text_embedder, mock_vector_db, mock_gh_downloader):
        """Test error handling during initialization."""
        # Setup mock to raise exception
        mock_gh_downloader.side_effect = Exception("Connection error")
        
        # Create retriever should raise RuntimeError
        with self.assertRaises(RuntimeError) as context:
            RAGRetriever(self.github_token, self.supabase_url, self.supabase_key)
        
        self.assertIn("Failed to initialize RAG retriever", str(context.exception))
        
    def test_get_file_content(self):
        """Test reading content from a file."""
        # Create a test retriever
        with patch('app.services.rag.rag_retriever.GitHubDownloader'), \
             patch('app.services.rag.rag_retriever.VectorDBClient'), \
             patch('app.services.rag.rag_retriever.TextEmbedder'):
                
            retriever = RAGRetriever(self.github_token, self.supabase_url, self.supabase_key)
        
        # Create a test file
        test_file = os.path.join(self.test_dir, "test_file.txt")
        with open(test_file, 'w') as f:
            f.write("Test file content")
        
        # Test reading the file
        content = retriever._get_file_content(test_file)
        self.assertEqual(content, "Test file content")
        
    def test_get_file_content_not_found(self):
        """Test handling of non-existent file."""
        # Create a test retriever
        with patch('app.services.rag.rag_retriever.GitHubDownloader'), \
             patch('app.services.rag.rag_retriever.VectorDBClient'), \
             patch('app.services.rag.rag_retriever.TextEmbedder'):
                
            retriever = RAGRetriever(self.github_token, self.supabase_url, self.supabase_key)
        
        # Test reading a non-existent file
        with self.assertRaises(FileNotFoundError) as context:
            retriever._get_file_content(os.path.join(self.test_dir, "nonexistent.txt"))
        
        self.assertIn("File not found", str(context.exception))
        
    @patch('app.services.rag.rag_retriever.GitHubDownloader')
    @patch('app.services.rag.rag_retriever.VectorDBClient')
    @patch('app.services.rag.rag_retriever.TextEmbedder')
    def test_process_github_content(self, mock_text_embedder, mock_vector_db, mock_gh_downloader):
        """Test processing GitHub content."""
        # Setup mocks
        mock_gh_downloader_instance = MagicMock()
        mock_vector_db_instance = MagicMock()
        mock_text_embedder_instance = MagicMock()
        
        mock_gh_downloader.return_value = mock_gh_downloader_instance
        mock_vector_db.return_value = mock_vector_db_instance
        mock_text_embedder.return_value = mock_text_embedder_instance
        
        # Setup mock response for download_from_github
        mock_gh_downloader_instance.download_from_github.return_value = [
            "/tmp/file1.py",
            "/tmp/file2.py"
        ]
        
        # Setup mock output_dir
        mock_gh_downloader_instance.output_dir = "/tmp"
        
        # Create retriever
        retriever = RAGRetriever(self.github_token, self.supabase_url, self.supabase_key)
        
        # Mock file reading
        with patch.object(retriever, '_get_file_content', return_value="File content"):
            # Mock chunk_and_store
            with patch.object(retriever, 'chunk_and_store') as mock_chunk_store:
                # Call the method
                result = retriever.process_github_content(["https://github.com/user/repo/test.py"])
                
                # Assertions
                self.assertEqual(len(result), 2)
                self.assertEqual(result, ["/tmp/file1.py", "/tmp/file2.py"])
                
                # Verify chunk_and_store was called with the right data
                self.assertEqual(mock_chunk_store.call_count, 2)
                
                # Verify delete_downloaded_file was called
                self.assertEqual(mock_gh_downloader_instance._delete_downloaded_file.call_count, 2)
                
    @patch('app.services.rag.rag_retriever.GitHubDownloader')
    @patch('app.services.rag.rag_retriever.VectorDBClient')
    @patch('app.services.rag.rag_retriever.TextEmbedder')
    def test_process_github_content_empty_result(self, mock_text_embedder, mock_vector_db, mock_gh_downloader):
        """Test handling of empty result when processing GitHub content."""
        # Setup mocks
        mock_gh_downloader_instance = MagicMock()
        mock_vector_db_instance = MagicMock()
        mock_text_embedder_instance = MagicMock()
        
        mock_gh_downloader.return_value = mock_gh_downloader_instance
        mock_vector_db.return_value = mock_vector_db_instance
        mock_text_embedder.return_value = mock_text_embedder_instance
        
        # Setup mock response for download_from_github (empty list)
        mock_gh_downloader_instance.download_from_github.return_value = []
        
        # Create retriever
        retriever = RAGRetriever(self.github_token, self.supabase_url, self.supabase_key)
        
        # Call the method and expect ValueError
        with self.assertRaises(ValueError) as context:
            retriever.process_github_content(["https://github.com/user/repo/test.py"])
        
        self.assertIn("No files were successfully processed", str(context.exception))
        
    @patch('app.services.rag.rag_retriever.GitHubDownloader')
    @patch('app.services.rag.rag_retriever.VectorDBClient')
    @patch('app.services.rag.rag_retriever.TextEmbedder')
    def test_chunk_and_store(self, mock_text_embedder, mock_vector_db, mock_gh_downloader):
        """Test chunking and storing content."""
        # Setup mocks
        mock_gh_downloader_instance = MagicMock()
        mock_vector_db_instance = MagicMock()
        mock_text_embedder_instance = MagicMock()
        
        mock_gh_downloader.return_value = mock_gh_downloader_instance
        mock_vector_db.return_value = mock_vector_db_instance
        mock_text_embedder.return_value = mock_text_embedder_instance
        
        # Setup mock return for process_text
        mock_chunks = ["Chunk 1", "Chunk 2"]
        mock_embeddings = [[0.1, 0.2], [0.3, 0.4]]
        mock_text_embedder_instance.process_text.return_value = (mock_chunks, mock_embeddings)
        
        # Create retriever
        retriever = RAGRetriever(self.github_token, self.supabase_url, self.supabase_key)
        
        # Call the method
        retriever.chunk_and_store("Test content")
        
        # Assertions
        mock_text_embedder_instance.process_text.assert_called_once_with("Test content")
        mock_vector_db_instance.store_embeddings.assert_called_once_with(mock_chunks, mock_embeddings)
        
    @patch('app.services.rag.rag_retriever.GitHubDownloader')
    @patch('app.services.rag.rag_retriever.VectorDBClient')
    @patch('app.services.rag.rag_retriever.TextEmbedder')
    def test_chunk_and_store_error(self, mock_text_embedder, mock_vector_db, mock_gh_downloader):
        """Test error handling in chunk_and_store."""
        # Setup mocks
        mock_gh_downloader_instance = MagicMock()
        mock_vector_db_instance = MagicMock()
        mock_text_embedder_instance = MagicMock()
        
        mock_gh_downloader.return_value = mock_gh_downloader_instance
        mock_vector_db.return_value = mock_vector_db_instance
        mock_text_embedder.return_value = mock_text_embedder_instance
        
        # Setup mock to raise exception
        mock_text_embedder_instance.process_text.side_effect = Exception("Process error")
        
        # Create retriever
        retriever = RAGRetriever(self.github_token, self.supabase_url, self.supabase_key)
        
        # Call the method and expect ValueError
        with self.assertRaises(ValueError) as context:
            retriever.chunk_and_store("Test content")
        
        self.assertIn("Failed to chunk and store content", str(context.exception))
        
    @patch('app.services.rag.rag_retriever.GitHubDownloader')
    @patch('app.services.rag.rag_retriever.VectorDBClient')
    @patch('app.services.rag.rag_retriever.TextEmbedder')
    def test_retrieve_documents(self, mock_text_embedder, mock_vector_db, mock_gh_downloader):
        """Test retrieving documents for a query."""
        # Setup mocks
        mock_gh_downloader_instance = MagicMock()
        mock_vector_db_instance = MagicMock()
        mock_text_embedder_instance = MagicMock()
        
        mock_gh_downloader.return_value = mock_gh_downloader_instance
        mock_vector_db.return_value = mock_vector_db_instance
        mock_text_embedder.return_value = mock_text_embedder_instance
        
        # Setup mock returns
        mock_query_embedding = [0.1, 0.2, 0.3]
        mock_documents = ["Doc 1", "Doc 2"]
        
        mock_text_embedder_instance.embed_query.return_value = mock_query_embedding
        mock_vector_db_instance.retrieve_documents.return_value = mock_documents
        
        # Create retriever
        retriever = RAGRetriever(self.github_token, self.supabase_url, self.supabase_key)
        
        # Call the method
        result = retriever.retrieve_documents("test query")
        
        # Assertions
        mock_text_embedder_instance.embed_query.assert_called_once_with("test query")
        mock_vector_db_instance.retrieve_documents.assert_called_once_with(mock_query_embedding)
        self.assertEqual(result, mock_documents)
        
    @patch('app.services.rag.rag_retriever.GitHubDownloader')
    @patch('app.services.rag.rag_retriever.VectorDBClient')
    @patch('app.services.rag.rag_retriever.TextEmbedder')
    def test_retrieve_documents_error(self, mock_text_embedder, mock_vector_db, mock_gh_downloader):
        """Test error handling in retrieve_documents."""
        # Setup mocks
        mock_gh_downloader_instance = MagicMock()
        mock_vector_db_instance = MagicMock()
        mock_text_embedder_instance = MagicMock()
        
        mock_gh_downloader.return_value = mock_gh_downloader_instance
        mock_vector_db.return_value = mock_vector_db_instance
        mock_text_embedder.return_value = mock_text_embedder_instance
        
        # Setup mock to raise exception
        mock_text_embedder_instance.embed_query.side_effect = Exception("Embedding error")
        
        # Create retriever
        retriever = RAGRetriever(self.github_token, self.supabase_url, self.supabase_key)
        
        # Call the method and expect ValueError
        with self.assertRaises(ValueError) as context:
            retriever.retrieve_documents("test query")
        
        self.assertIn("Failed to retrieve documents", str(context.exception))
        
    @patch('app.services.rag.rag_retriever.GitHubDownloader')
    @patch('app.services.rag.rag_retriever.VectorDBClient')
    @patch('app.services.rag.rag_retriever.TextEmbedder')
    def test_cleanup(self, mock_text_embedder, mock_vector_db, mock_gh_downloader):
        """Test the cleanup method."""
        # Setup mocks
        mock_gh_downloader_instance = MagicMock()
        mock_vector_db_instance = MagicMock()
        mock_text_embedder_instance = MagicMock()
        
        mock_gh_downloader.return_value = mock_gh_downloader_instance
        mock_vector_db.return_value = mock_vector_db_instance
        mock_text_embedder.return_value = mock_text_embedder_instance
        
        # Create retriever
        retriever = RAGRetriever(self.github_token, self.supabase_url, self.supabase_key)
        
        # Call the method
        retriever.cleanup()
        
        # Assertions
        mock_gh_downloader_instance._delete_output_dir.assert_called_once()

if __name__ == '__main__':
    unittest.main()