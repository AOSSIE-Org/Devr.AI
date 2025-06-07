from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class AgentState(BaseModel):
    """Base state for all LangGraph agents"""
    # Core identification
    session_id: str
    user_id: str
    platform: str  # discord, slack, github

    # Conversation context
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)

    # Processing state
    current_task: Optional[str] = None
    task_result: Optional[Dict[str, Any]] = None
    next_action: Optional[str] = None

    # Tools and capabilities
    tools_used: List[str] = Field(default_factory=list)
    available_tools: List[str] = Field(default_factory=list)

    # Human-in-the-loop
    requires_human_review: bool = False
    human_feedback: Optional[str] = None

    # Platform-specific
    thread_id: Optional[str] = None
    channel_id: Optional[str] = None

    # Error handling
    errors: List[str] = Field(default_factory=list)
    retry_count: int = 0
    max_retries: int = Field(default=3)

    # Response
    final_response: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
