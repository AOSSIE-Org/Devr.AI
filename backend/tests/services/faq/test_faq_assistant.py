import unittest
from unittest.mock import patch, MagicMock
import os
from dotenv import load_dotenv

# Import the module to test
from app.services.faq.faq_assistant import FaqAssistant

# Load environment variables for API keys if running actual API calls
load_dotenv()

class TestFaqAssistant(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Use fake/mock API keys for testing
        self.api_key = os.getenv("GROQ_API_KEY", "test_api_key")
        self.model = os.getenv("GROQ_MODEL", "llama3-8b-8192")
        
    @patch('app.services.faq.faq_assistant.ChatGroq')
    def test_initialization(self, mock_chatgroq):
        """Test that the assistant initializes correctly."""
        # Create a new instance with mocked LLM
        assistant = FaqAssistant(groq_api_key="test_key", groq_model="test_model")
        
        # Assert that ChatGroq was called with correct parameters
        mock_chatgroq.assert_called_once_with(
            api_key="test_key",
            model="test_model",
            streaming=False
        )
        
        # Assert that the prompt and chain were created
        self.assertIsNotNone(assistant.faq_prompt)
        self.assertIsNotNone(assistant.faq_chain)
    
    @patch('app.services.faq.faq_assistant.ChatGroq')
    def test_generate_faq_response_with_context(self, mock_chatgroq):
        """Test generating a response when relevant context is provided."""
        # Set up the mock for the LLM and chain
        mock_llm = MagicMock()
        mock_chatgroq.return_value = mock_llm
        
        # Create a mock chain that returns our expected response
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "This is a test response based on the context."
        
        # Create our assistant
        assistant = FaqAssistant(groq_api_key="test_key", groq_model="test_model")
        assistant.faq_chain = mock_chain  # Replace the chain with our mock
        
        # Test data
        question = "What is the purpose of this project?"
        retrieved_docs = [
            {"id": 1, "content": "This project is a FAQ system using RAG.", "distance": 0.92},
            {"id": 2, "content": "It retrieves relevant documents and generates answers.", "distance": 0.85}
        ]
        
        # Call the method
        response = assistant.generate_faq_response(question, retrieved_docs)
        
        # Assertions
        self.assertEqual(response, "This is a test response based on the context.")
        mock_chain.invoke.assert_called_once()
        
        # Check that the invoke method was called with the right arguments
        args, kwargs = mock_chain.invoke.call_args
        input_dict = args[0] if args else kwargs  # could be positional or keyword arg
        
        self.assertEqual(input_dict['question'], question)
        self.assertIn("This project is a FAQ system using RAG.", input_dict['context'])
        self.assertIn("It retrieves relevant documents and generates answers.", input_dict['context'])
    
    @patch('app.services.faq.faq_assistant.ChatGroq')
    def test_generate_faq_response_with_empty_context(self, mock_chatgroq):
        """Test generating a response when no context is provided."""
        # Set up the mock for the LLM
        mock_llm = MagicMock()
        mock_chatgroq.return_value = mock_llm
        
        # Create a mock chain
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "I do not know."
        
        # Create the assistant
        assistant = FaqAssistant(groq_api_key="test_key", groq_model="test_model")
        assistant.faq_chain = mock_chain  # Replace the chain with our mock
        
        # Test data
        question = "What is the purpose of this project?"
        retrieved_docs = []  # Empty context
        
        # Call the method
        response = assistant.generate_faq_response(question, retrieved_docs)
        
        # Assertions
        self.assertEqual(response, "I do not know.")
        mock_chain.invoke.assert_called_once()
        
        # Check that invoke was called with empty context
        args, kwargs = mock_chain.invoke.call_args
        input_dict = args[0] if args else kwargs  # could be positional or keyword arg
        self.assertEqual(input_dict['context'], "")
    
    @patch('app.services.faq.faq_assistant.ChatGroq')
    def test_generate_faq_response_error_handling(self, mock_chatgroq):
        """Test error handling during response generation."""
        # Set up the mock for the LLM
        mock_llm = MagicMock()
        mock_chatgroq.return_value = mock_llm
        
        # Create a mock chain that raises an exception
        mock_chain = MagicMock()
        mock_chain.invoke.side_effect = Exception("API error")
        
        # Create the assistant
        assistant = FaqAssistant(groq_api_key="test_key", groq_model="test_model")
        assistant.faq_chain = mock_chain  # Replace the chain with our mock
        
        # Test data
        question = "What is the purpose of this project?"
        retrieved_docs = [
            {"id": 1, "content": "Some context", "distance": 0.75}
        ]
        
        # Call the method and check exception handling
        with self.assertRaises(Exception) as context:
            assistant.generate_faq_response(question, retrieved_docs)
        
        self.assertIn("API error", str(context.exception))

if __name__ == '__main__':
    unittest.main()