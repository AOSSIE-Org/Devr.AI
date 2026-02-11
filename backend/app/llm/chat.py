from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from app.core.config import settings

async def chat_completion(prompt: str, context: dict | None = None) -> str:
    """
    Stateless LLM chat used in discord-only mode.
    No agents, no memory, no queue.
    """
    # if not settings.llm_enabled:
    #     return "LLM responses are currently disabled."

    llm = ChatGoogleGenerativeAI(
        model=settings.classification_agent_model,
        temperature=0.7,
        google_api_key=settings.gemini_api_key,
    )

    response = await llm.ainvoke(
        [HumanMessage(content=prompt)]
    )
    return response.content
