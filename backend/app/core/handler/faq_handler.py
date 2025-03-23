import logging
from typing import Dict, Any
from ..events.base import BaseEvent
from ..events.enums import EventType
from .base import BaseHandler
import os
from backend.app.services.rag.rag_retriever import RAGRetriever
from backend.app.services.faq.faq_assistant import FaqAssistant
from backend.app.core.events.faq_event import AnswerEvent, GithubKnowledgeUpdateEvent, KnowledgeUpdateEvent
from backend.app.core.events.event_bus import EventBus

logger = logging.getLogger(__name__)

class FAQHandler(BaseHandler):
    """Handler for FAQ and knowledge base queries"""
    
    async def handle(self, event: BaseEvent) -> Dict[str, Any]:
        logger.info(f"Handling FAQ request event: {event.event_type}")
        
        if event.event_type == EventType.FAQ_REQUESTED:
            return await self._handle_faq_request(event)
        elif event.event_type == EventType.KNOWLEDGE_UPDATED:
            return await self._handle_knowledge_update(event)
        elif event.event_type == EventType.GITHUB_KNOWLEDGE_UPDATED:
            return await self._handle_github_knowledge_update(event)
        else:
            logger.warning(f"Unsupported FAQ event type: {event.event_type}")
            return {"success": False, "reason": "Unsupported event type"}
    
    def _get_rag_retriever(self):
        # This function will be modified in the future to retrieve the required keys from database for the organization
        GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        rag_retriever = RAGRetriever(GITHUB_TOKEN, SUPABASE_URL, SUPABASE_KEY)
        return rag_retriever

    def _get_faq_assistant(self):
        # This function will be modified in the future to retrieve the required keys from database for the organization
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        GROQ_MODEL = os.getenv("GROQ_MODEL")
        faq_assistant = FaqAssistant(groq_api_key=GROQ_API_KEY, groq_model=GROQ_MODEL)
        return faq_assistant

    async def _handle_faq_request(self, event: AnswerEvent) -> Dict[str, Any]:
        # Implementation for FAQ request
        retriever : RAGRetriever = self._get_rag_retriever()
        assistant : FaqAssistant = self._get_faq_assistant()
        # Retrieve relevant documents
        relevant_docs = retriever.retrieve_documents(event.question)
        
        if not relevant_docs:
            return {"success": True, "answer": "I couldn't find any relevant information to answer your question."}
        
        # Generate response using LLM
        response = assistant.generate_faq_response(event.question, relevant_docs)
        return {"success": True, "answer" : response , "action": "faq_processed"}
    
    async def _handle_knowledge_update(self, event: GithubKnowledgeUpdateEvent) -> Dict[str, Any]:
        # Implementation for updating knowledge base
        retriever : RAGRetriever =self._get_rag_retriever()
        retriever.chunk_and_store(event.content)
        return {"success": True, "action": "knowledge_updated"}
    
    async def _handle_github_knowledge_update(self, event: KnowledgeUpdateEvent) -> Dict[str, Any]:
        # Implementation for updating knowledge base from GitHub
        print("Updating knowledge base from GitHub")
        retriever : RAGRetriever =self._get_rag_retriever()
        total_files = 0
        for url in event.urls:
            processed_files = retriever.process_github_content([url])
            total_files += len(processed_files)
        retriever.cleanup()
        return {"success": True, "action": "knowledge_updated", "files_processed": total_files}
    

def register_faq_handlers(event_bus : EventBus):
    faq_handler = FAQHandler()
    event_bus.register_handler(EventType.FAQ_REQUESTED, faq_handler.handle)
    event_bus.register_handler(EventType.KNOWLEDGE_UPDATED, faq_handler.handle)
    event_bus.register_handler(EventType.GITHUB_KNOWLEDGE_UPDATED, faq_handler.handle)
