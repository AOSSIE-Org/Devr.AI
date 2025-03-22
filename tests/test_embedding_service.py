import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.app.services.embedding_service.service import EmbeddingService
import unittest
from sklearn.metrics.pairwise import cosine_similarity


class TestEmbeddingService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.embedding_service = EmbeddingService(device="cuda")

    async def test_get_embedding(self):
        text = "Hi, this seems to be great!"
        embedding = await self.embedding_service.get_embedding(text)
        self.assertTrue(len(embedding) == 384)
    
    async def test_similarity(self):
        texts = ["Hi, this seems to be great!", "This is good!"]
        embeddings = await self.embedding_service.get_embeddings(texts)
        similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        self.assertTrue(similarity > 0.5)
        
    def test_get_model_info(self):
        # Access model once to initialize it
        _ = self.embedding_service.model
        
        info = self.embedding_service.get_model_info()
        
        # Check that all expected keys are present
        self.assertIn("model_name", info)
        self.assertIn("device", info)
        self.assertIn("embedding_size", info)
        
        # Verify values
        self.assertEqual(info["model_name"], self.embedding_service.model_name)
        self.assertEqual(info["device"], self.embedding_service.device)
        self.assertEqual(info["embedding_size"], 384)  # For BGE-small model
    
    def test_clear_cache(self):
        # Access model first to ensure it's loaded
        _ = self.embedding_service.model
        self.assertIsNotNone(self.embedding_service._model)
        
        # Clear the cache
        self.embedding_service.clear_cache()
        
        # Verify model is cleared
        self.assertIsNone(self.embedding_service._model)
        
        # Verify model loads again after clearing
        _ = self.embedding_service.model
        self.assertIsNotNone(self.embedding_service._model)

# run the tests
if __name__ == "__main__":
    unittest.main()