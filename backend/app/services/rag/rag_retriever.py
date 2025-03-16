import os
from dotenv import load_dotenv
from typing import List

from app.services.rag.text_embedder import TextEmbedder
from app.services.rag.vector_db import VectorDBClient
from app.services.github.github_downloader import GitHubDownloader
from app.services.faq.faq_assistant import FaqAssistant

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
    
    def process_github_content(self, urls: List[str]) -> List[str]:
        """Process GitHub content (file or directory) from multiple URLs and store in vector database.
        
        Args:
            urls: List of GitHub URLs to process
            
        Returns:
            List of processed file paths
            
        Raises:
            ValueError: If no valid content could be processed
        """
        processed_files = []
        
        for url in urls:
            try:
                downloaded_files = self.github_downloader.download_from_github(url)
                
                for file_path in downloaded_files:
                    try:
                        file_content = self._get_file_content(file_path)
                        # Store file information with content
                        content_with_metadata = f"Source: {url}\nPath: {file_path.replace(self.github_downloader.output_dir, '')}\n\n{file_content}"
                        self.chunk_and_store(content_with_metadata)
                        processed_files.append(file_path)
                        
                        # Clean up after processing
                        self.github_downloader._delete_downloaded_file(file_path)
                    except Exception as e:
                        print(f"Warning: Failed to process file {file_path}: {str(e)}")
            except Exception as e:
                print(f"Warning: Failed to process URL {url}: {str(e)}")
        
        if not processed_files:
            raise ValueError("No files were successfully processed from the provided URLs")
  
        return processed_files

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
    
    def cleanup(self):
        """Perform any necessary cleanup operations like github downloaded folder."""
        self.github_downloader._delete_output_dir()
        
