from fastapi import APIRouter, Depends, HTTPException
import os

from app.services.rag.rag_retriever import RAGRetriever
from app.services.faq.faq_assistant import FaqAssistant

#Load the request and response models
from app.models.faq import ContentRequest, GithubFileRequest, FaqRequest, FaqResponse


# Initialize the router
router = APIRouter(prefix="/faq", tags=["FAQ"])

def get_rag_retriever():
    # This function will be modified in the future to retrieve the required keys from database for the organization
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    rag_retriever = RAGRetriever(GITHUB_TOKEN, SUPABASE_URL, SUPABASE_KEY)
    return rag_retriever

def get_faq_assistant():
    # This function will be modified in the future to retrieve the required keys from database for the organization
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = os.getenv("GROQ_MODEL")
    faq_assistant = FaqAssistant(groq_api_key=GROQ_API_KEY, groq_model=GROQ_MODEL)
    return faq_assistant


@router.post("/content", status_code=201)
async def store_content(
    request: ContentRequest,
    retriever: RAGRetriever = Depends(get_rag_retriever)
):
    """Store content in the vector database"""
    try:
        retriever.chunk_and_store(request.content)
        return {"status": "success", "message": "Content stored successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        retriever.cleanup()

@router.post("/github", status_code=201)
async def store_github_content(
    request: GithubFileRequest,
    retriever: RAGRetriever = Depends(get_rag_retriever)
):
    """Download GitHub files/directories and store in the vector database"""
    try:
        total_files = 0
        for url in request.urls:
            processed_files = retriever.process_github_content([url])
            total_files += len(processed_files)
        
        return {
            "status": "success", 
            "message": f"Successfully processed {total_files} files from {len(request.urls)} GitHub URLs"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        retriever.cleanup()

@router.post("/ask", response_model=FaqResponse)
async def generate_faq_response(
    request: FaqRequest,
    retriever: RAGRetriever = Depends(get_rag_retriever),
    assistant: FaqAssistant = Depends(get_faq_assistant)
):
    """Generate an answer to a question using RAG"""
    try:
        # Retrieve relevant documents
        relevant_docs = retriever.retrieve_documents(request.question)
        
        if not relevant_docs:
            return FaqResponse(answer="I couldn't find any relevant information to answer your question.")
        
        # Generate response using LLM
        response = assistant.generate_faq_response(request.question, relevant_docs)
        return FaqResponse(answer=response)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        retriever.cleanup()