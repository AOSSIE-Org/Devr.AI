from typing import List
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_experimental.text_splitter import SemanticChunker

class TextEmbedder:
    """
    A unified class for text embedding and semantic chunking operations.
    Combines the functionality of HuggingFaceEmbeddings and SemanticChunker
    into a single interface.
    """
    
    def __init__(
        self, 
        model_name: str = 'sentence-transformers/all-MiniLM-L6-v2',
        breakpoint_threshold_amount: float = 0.8,
        breakpoint_threshold_type: str = 'gradient'
    ):
        """
        Initialize the text embedder with embedding model and chunking parameters.
        
        Args:
            model_name: Name of the Hugging Face model to use for embeddings
            breakpoint_threshold_amount: Threshold for determining chunk boundaries
            breakpoint_threshold_type: Method for determining boundaries ('gradient' or 'cosine')
        """
        # Initialize the embedding model
        self.embedding_model = HuggingFaceEmbeddings(model_name=model_name)
        
        # Initialize the text splitter with our embedding model
        self.text_splitter = SemanticChunker(
            embeddings=self,  # The SemanticChunker will use this class for embeddings
            breakpoint_threshold_amount=breakpoint_threshold_amount,
            breakpoint_threshold_type=breakpoint_threshold_type
        )
    
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embeddings for a query text.
        
        Args:
            text: The input text to embed
            
        Returns:
            A list of floats representing the embedding vector
        """
        return self.embedding_model.embed_query(text)
    
    def embed(self, text: str) -> List[float]:
        """
        Generate embeddings for a text chunk.
        This method allows the class to be used directly with SemanticChunker.
        
        Args:
            text: The input text to embed
            
        Returns:
            A list of floats representing the embedding vector
        """
        return self.embed_query(text)
    
    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple documents.
        
        Args:
            documents: List of text documents to embed
            
        Returns:
            List of embedding vectors
        """
        return self.embedding_model.embed_documents(documents)
    
    def split_text(self, text: str) -> List[str]:
        """
        Split text into semantic chunks.
        
        Args:
            text: The input text to split
            
        Returns:
            List of text chunks
        """
        return self.text_splitter.split_text(text)
    
    def generate_embeddings(self, chunks: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of text chunks.
        
        Args:
            chunks: List of text chunks to embed
            
        Returns:
            List of embedding vectors
        """
        return [self.embed(chunk) for chunk in chunks]
    
    def process_text(self, text: str) -> tuple[List[str], List[List[float]]]:
        """
        Process a text by splitting it into chunks and generating embeddings.
        
        Args:
            text: Input text to process
            
        Returns:
            Tuple of (chunks, embeddings)
        """
        chunks = self.split_text(text)
        embeddings = self.generate_embeddings(chunks)
        return chunks, embeddings