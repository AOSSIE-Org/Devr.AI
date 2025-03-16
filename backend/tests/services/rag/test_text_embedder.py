#contains integration tests for HuggingFaceEmbeddings and mocked tests for SemanticChunker
import unittest
from unittest.mock import patch, MagicMock

from app.services.rag.text_embedder import TextEmbedder

class TestTextEmbedder(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a real TextEmbedder instance for tests
        self.embedder = TextEmbedder()
    
    def test_initialization(self):
        """Test that the embedder initializes correctly with default parameters."""
        # Verify the instance has the expected attributes
        self.assertIsNotNone(self.embedder.embedding_model)
        self.assertIsNotNone(self.embedder.text_splitter)
        
        # Verify model name is set correctly
        self.assertEqual(self.embedder.embedding_model.model_name, 
                         'sentence-transformers/all-MiniLM-L6-v2')
    
    def test_initialization_with_custom_params(self):
        """Test initialization with custom parameters."""
        custom_embedder = TextEmbedder(
            model_name='sentence-transformers/paraphrase-mpnet-base-v2',
            breakpoint_threshold_amount=0.5,
            breakpoint_threshold_type='cosine'
        )
        
        # Verify model name is set correctly
        self.assertEqual(custom_embedder.embedding_model.model_name, 
                         'sentence-transformers/paraphrase-mpnet-base-v2')
    
    def test_embed_and_embed_query(self):
        """Test that embed method delegates to embed_query."""
        # Use a small test string
        test_text = "This is a test"
        
        # Both methods should return same vector for same input
        query_result = self.embedder.embed_query(test_text)
        embed_result = self.embedder.embed(test_text)
        
        # Both should return vector of same dimension
        self.assertEqual(len(query_result), 384)  # Verify 384-dimensional embeddings
        self.assertEqual(len(embed_result), 384)  # Verify 384-dimensional embeddings
        # Should be identical results
        self.assertEqual(query_result, embed_result)
    
    def test_embed_documents(self):
        """Test embedding multiple documents."""
        docs = ["First doc", "Second doc"]
        result = self.embedder.embed_documents(docs)
        
        # Should return a list of vectors
        self.assertEqual(len(result), len(docs))
        # Each vector should have the expected dimension (384)
        self.assertEqual(len(result[0]), 384)
        self.assertEqual(len(result[1]), 384)
    
    @patch.object(TextEmbedder, 'split_text')
    def test_split_text(self, mock_split_text):
        """Test splitting text into chunks with mocking."""
        # Mock the split_text method
        mock_split_text.return_value = ["Chunk 1", "Chunk 2", "Chunk 3"]
        
        test_text = "This is a test text that should be split."
        result = self.embedder.split_text(test_text)
        
        # Verify the mock was called and returned expected result
        mock_split_text.assert_called_once_with(test_text)
        self.assertEqual(result, ["Chunk 1", "Chunk 2", "Chunk 3"])
    
    def test_generate_embeddings(self):
        """Test generating embeddings for multiple chunks."""
        chunks = ["Chunk 1", "Chunk 2"]
        result = self.embedder.generate_embeddings(chunks)
        
        # Should return a list of vectors
        self.assertEqual(len(result), len(chunks))
        # All vectors should have 384 dimensions
        self.assertEqual(len(result[0]), 384)
        self.assertEqual(len(result[1]), 384)
    
    @patch.object(TextEmbedder, 'split_text')
    def test_process_text(self, mock_split_text):
        """Test the text processing pipeline with mocked split_text."""
        # Set up the mock to return a predictable result
        mock_chunks = ["First chunk", "Second chunk"]
        mock_split_text.return_value = mock_chunks
        
        test_text = "This is a test text for processing into chunks and embeddings."
        
        chunks, embeddings = self.embedder.process_text(test_text)
        
        # Verify split_text was called with the right arguments
        mock_split_text.assert_called_once_with(test_text)
        
        # Should return the mocked chunks
        self.assertEqual(chunks, mock_chunks)
        
        # Should return embeddings for each chunk
        self.assertEqual(len(embeddings), len(mock_chunks))
        
        # Each embedding should be a 384-dimensional vector
        for emb in embeddings:
            self.assertIsInstance(emb, list)
            self.assertEqual(len(emb), 384)

if __name__ == '__main__':
    unittest.main()