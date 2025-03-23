from fastapi import APIRouter, HTTPException
from uuid import uuid4

#Load the request and response models
from ...schemas.faq import ContentRequest, GithubFileRequest, FaqRequest, FaqResponse

from backend.event_bus_init import event_bus
from ...core.events.faq_event import AnswerEvent, GithubKnowledgeUpdateEvent, KnowledgeUpdateEvent


# Initialize the router
router = APIRouter(prefix="/faq", tags=["FAQ"])

@router.post("/content", status_code=201)
async def store_content(
    request: ContentRequest
):
    """Store content in the vector database"""
    knowledge_update_event = KnowledgeUpdateEvent(id=str(uuid4()),actor_id="faq-test",content=request.content)
    result =( await event_bus.dispatch(knowledge_update_event))[0]
    if not result.get("success")==True:
        raise HTTPException(status_code=500, detail="Error storing content")
    return {"status": "success", "message": "Content stored successfully"}

@router.post("/github", status_code=201)
async def store_github_content(
    request: GithubFileRequest
):
    """Download GitHub files/directories and store in the vector database"""
    github_knowledge_update_event = GithubKnowledgeUpdateEvent(id=str(uuid4()),actor_id="faq-test",urls=request.urls)
    result = (await event_bus.dispatch(github_knowledge_update_event))[0]
    if not result.get("success")==True:
        raise HTTPException(status_code=500, detail="Error storing GitHub content")
    return {"status": "success", "message": "GitHub content stored successfully"}

@router.post("/ask", response_model=FaqResponse)
async def generate_faq_response(
    request: FaqRequest
):
    """Generate an answer to a question using RAG"""
    faq_request_event = AnswerEvent(id=str(uuid4()),actor_id="faq-test",question=request.question)
    result = (await event_bus.dispatch(faq_request_event))[0]
    if not result.get("success")==True:
        raise HTTPException(status_code=500, detail="Error generating FAQ response")
    return FaqResponse(answer=result.get("answer"))