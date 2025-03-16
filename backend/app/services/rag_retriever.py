import os
from dotenv import load_dotenv
from typing import List

from text_embedder import TextEmbedder
from vector_db import VectorDBClient
from github_downloader import GitHubDownloader
from faq_assistant import FaqAssistant

load_dotenv()


class RAGRetriever:
    def __init__(self, github_token: str, supabase_url: str, supabase_key: str):
        """Initialize the RAG retriever with necessary components.
        
        Args:
            github_token: Token for GitHub API authentication
            supabase_url: URL for Supabase database
            supabase_key: API key for Supabase authentication
        """
        try:
            self.github_downloader = GitHubDownloader(github_token)
            self.vector_db = VectorDBClient(supabase_url, supabase_key)
            self.text_embedder = TextEmbedder()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize RAG retriever: {str(e)}")

    def _get_file_content(self, file_path: str) -> str:
        """Read content from a file.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            Content of the file as string
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            IOError: If the file can't be read
        """
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except IOError as e:
            raise IOError(f"Error reading file {file_path}: {str(e)}")
    
    def process_github_files(self, urls: List[str]) -> None:
        """Process multiple GitHub files: download, chunk, and store in vector DB.
        
        Args:
            urls: List of GitHub API URLs for files
            
        Raises:
            ValueError: If downloading or processing any file fails
        """
        file_paths = []
        try:
            file_paths = self.github_downloader._download_files(urls)
            for file_path in file_paths:
                try:
                    file_content = self._get_file_content(file_path)
                    self.chunk_and_store(file_content)
                except Exception as e:
                    print(f"Warning: Failed to process file {file_path}: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to process GitHub files: {str(e)}")
        finally:
            for file_path in file_paths:
                try:
                    self.github_downloader._delete_downloaded_file(file_path)
                except:
                    pass

    def chunk_and_store(self, content: str) -> None:
        """Split content into semantic chunks and store in vector database.
        
        Args:
            content: Text content to process
            
        Raises:
            ValueError: If chunking or storing fails
        """
        try:
            chunks, embeddings = self.text_embedder.process_text(content)
            self.vector_db.store_embeddings(chunks, embeddings)
        except Exception as e:
            raise ValueError(f"Failed to chunk and store content: {str(e)}")

    def retrieve_documents(self, query: str) -> List[str]:
        """Retrieve relevant documents for a query.
        
        Args:
            query: The search query
            
        Returns:
            List of relevant document chunks
            
        Raises:
            ValueError: If retrieval fails
        """
        try:
            query_embedding = self.text_embedder.embed_query(query)
            return self.vector_db.retrieve_documents(query_embedding)
        except Exception as e:
            raise ValueError(f"Failed to retrieve documents for query '{query}': {str(e)}")



# Example usage
if __name__ == "__main__":
    github_token = os.getenv('GITHUB_TOKEN')
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    groq_api_key = os.getenv('GROQ_API_KEY')
    groq_model = os.getenv('GROQ_MODEL')

    question = 'Give detailed features of Devr.AI?'
    question2 = 'what are the dependencies of Devr.AI?'
    github_file_url= 'https://api.github.com/repos/muntaxir4/Devr.AI/contents/README.md?ref=feat/RAG'

    rag_retriever = RAGRetriever(github_token, supabase_url, supabase_key)
    # file_content = rag_retriever.get_file_content(sample_file_path)
    # rag_retriever.chunk_and_store(file_content)
    rag_retriever.process_github_files([github_file_url])
    retrieved_documents = rag_retriever.retrieve_documents(question)
    faq_assistant = FaqAssistant(groq_api_key=groq_api_key, groq_model=groq_model)
    response = faq_assistant.generate_faq_response(question, retrieved_documents)
    print(response)