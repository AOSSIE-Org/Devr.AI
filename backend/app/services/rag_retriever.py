import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings

# Assuming SemanticTextSplitter is in langchain_experimental
from langchain_experimental.text_splitter import SemanticChunker
from vector_db import VectorDBClient
from github_downloader import GitHubDownloader
from faq_assistant import FaqAssistant

load_dotenv()


# Custom wrapper to make HuggingFaceEmbeddings compatible with SemanticChunker
class CustomHuggingFaceEmbeddings(HuggingFaceEmbeddings):
    def embed(self, text: str):
        """Wraps embed_query to match the expected method signature in Semantic Chunker."""
        return self.embed_query(text)

class RAGRetriever:
    def __init__(self, github_token: str, supabase_url: str, supabase_key: str):
        self.github_downloader = GitHubDownloader(github_token)
        self.vector_db = VectorDBClient(supabase_url, supabase_key)
        self.embedding_model = CustomHuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
        self.text_splitter = SemanticChunker(
            embeddings=self.embedding_model,
            breakpoint_threshold_amount=0.8,
            breakpoint_threshold_type='gradient'
        )

    def process_github_file(self, url: str):
        file_path = self.github_downloader.download_file(url)
        file_content = url + "\n" +self.get_file_content(file_path)
        print(file_content)
        # Remove the file after reading its content to avoid clutter
        if os.path.exists(file_path):
            os.remove(file_path)
        return self.chunk_and_store(file_content)

    def get_file_content(self, file_path: str):
        with open(file_path, 'r') as file:
            return file.read()

    def chunk_and_store(self, content: str):
        chunks = self.text_splitter.split_text(content)
        embeddings = [self.embedding_model.embed(chunk) for chunk in chunks]
        self.vector_db.store_embeddings(chunks, embeddings)

    def retrieve_documents(self, query: str):
        query_embedding = self.embedding_model.embed(query)
        return self.vector_db.retrieve_documents(query_embedding)



# Example usage
if __name__ == "__main__":
    github_token = os.getenv('GITHUB_TOKEN')
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    openai_base_url = os.getenv('OPENAI_BASE_URL')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    sample_file_path = '/media/mun/Shared/GSOC/Devr.AI/README.md'

    question = 'Give detailed features of Devr.AI?'
    question2 = 'what are the dependencies of Devr.AI?'
    github_file_url= 'https://api.github.com/repos/muntaxir4/Devr.AI/contents/pyproject.toml?ref=main'

    rag_retriever = RAGRetriever(github_token, supabase_url, supabase_key)
    file_content = rag_retriever.get_file_content(sample_file_path)
    rag_retriever.chunk_and_store(file_content)
    rag_retriever.process_github_file(github_file_url)
    retrieved_documents = rag_retriever.retrieve_documents(question2)
    faq_assistant = FaqAssistant(base_url=openai_base_url, api_key=openai_api_key)
    response = faq_assistant.generate_faq_response(question2, retrieved_documents)
    print(response)