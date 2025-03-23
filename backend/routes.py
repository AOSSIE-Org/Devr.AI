from fastapi import APIRouter
from .app.api.routes.faq import router as faq_router

api_router = APIRouter()
api_router.include_router(faq_router)