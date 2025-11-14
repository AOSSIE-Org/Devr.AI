from typing import Dict, Any, List, Optional, Annotated
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from operator import add

def replace_summary(existing: Optional[str], new: Optional[str]) -> Optional[str]:
    """Replace summary"""
    if new is not None:
        return new
    return existing

def replace_topics(existing: List[str], new: List[str]) -> List[str]:
    """Replace topics"""
    if new:
        return new
    return existing

class AgentState(BaseModel):
    """Base state for all LangGraph agents"""
    # Core identification
    session_id: str
    user_id: str
    platform: str  # discord, slack, github

    # Conversation context
    messages: Annotated[List[Dict[str, Any]], add] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)

    # Channel-specific conversation state (e.g., onboarding workflow progress)
    onboarding_state: Dict[str, Any] = Field(default_factory=dict)

    # TODO: PERSISTENT MEMORY DATA (survives across sessions via summarization)
    user_profile: Dict[str, Any] = Field(default_factory=dict)

    # LLM-generated summary of PAST conversations
    conversation_summary: Annotated[Optional[str], replace_summary] = None

    # Key topics discussed with the user
    key_topics: Annotated[List[str], replace_topics] = Field(default_factory=list)

    # SESSION MANAGEMENT
    session_start_time: datetime = Field(default_factory=datetime.now)
    last_interaction_time: datetime = Field(default_factory=datetime.now)
    interaction_count: Annotated[int, add] = Field(default=0)
    summarization_needed: bool = False

    # Memory management flag (for thread timeout)
    memory_timeout_reached: bool = False

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
    
    # HIL implementation
    waiting_for_human_input: bool = Field(
        default=False,
        description="True if the agent is paused and waiting for user input."
    )
    
    hil_message: Optional[str] = Field(
        default=None,
        description="The message to send to the user when waiting for input."
    )
    
    # Platform-specific
    thread_id: Optional[str] = None
    channel_id: Optional[str] = None

    # Error handling
    errors: List[str] = Field(default_factory=list)
    retry_count: int = 0
    max_retries: int = Field(default=3)

    # Response
    final_response: Optional[str] = None

    model_config = ConfigDict(
        arbitrary_types_allowed = True
    )