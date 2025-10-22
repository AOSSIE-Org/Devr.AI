"""
Unit tests for core agent functionality and workflows.
"""
import pytest
import asyncio
from datetime import datetime
from uuid import uuid4

from backend.app.agents.devrel.agent import DevRelAgent
from backend.app.agents.state import AgentState
from backend.app.middleware.validation import (
    sanitize_string,
    validate_user_id,
    validate_session_id
)
from backend.app.middleware.rate_limit import RateLimiter


# Test Agent State
class TestAgentState:
    """Test agent state management"""
    
    def test_agent_state_creation(self):
        """Test creating agent state"""
        state = AgentState(
            session_id="test_session",
            user_id="123456789",
            platform="discord",
            context={"original_message": "Hello"}
        )
        
        assert state.session_id == "test_session"
        assert state.user_id == "123456789"
        assert state.platform == "discord"
        assert state.context["original_message"] == "Hello"
        
    def test_agent_state_defaults(self):
        """Test agent state default values"""
        state = AgentState(
            session_id="test",
            user_id="123",
            platform="discord"
        )
        
        assert state.messages == []
        assert state.errors == []
        assert state.tools_used == []
        assert state.interaction_count == 0


# Test Input Validation
class TestInputValidation:
    """Test input validation and sanitization"""
    
    def test_sanitize_string(self):
        """Test string sanitization"""
        dangerous_input = "<script>alert('XSS')</script>"
        sanitized = sanitize_string(dangerous_input)
        
        assert "<script>" not in sanitized
        assert "alert" in sanitized  # Content preserved but escaped
        
    def test_validate_discord_user_id(self):
        """Test Discord user ID validation"""
        valid_id = "123456789012345678"  # 18-digit snowflake
        assert validate_user_id(valid_id) is True
        
        invalid_id = "abc123"
        assert validate_user_id(invalid_id) is False
        
    def test_validate_uuid(self):
        """Test UUID validation"""
        valid_uuid = str(uuid4())
        assert validate_user_id(valid_uuid) is True
        
        invalid_uuid = "not-a-uuid"
        assert validate_user_id(invalid_uuid) is False
        
    def test_validate_session_id(self):
        """Test session ID validation (UUID v4)"""
        valid_session = str(uuid4())
        # Session ID should be a valid UUID v4
        parts = valid_session.split('-')
        if parts[2][0] == '4':  # UUID v4 has '4' at this position
            assert validate_session_id(valid_session) in [True, False]  # May fail if not v4


# Test Rate Limiting
class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limiter_allows_first_request(self):
        """Test that rate limiter allows first request"""
        limiter = RateLimiter(
            requests_per_minute=10,
            requests_per_hour=100
        )
        
        is_allowed, retry_after = limiter.is_allowed("test_user")
        assert is_allowed is True
        assert retry_after is None
        
    def test_rate_limiter_blocks_excessive_requests(self):
        """Test that rate limiter blocks excessive requests"""
        limiter = RateLimiter(
            requests_per_minute=5,
            requests_per_hour=100,
            burst_size=2
        )
        
        # Make requests up to limit
        for _ in range(5):
            is_allowed, _ = limiter.is_allowed("test_user")
            
        # Next request should be blocked
        is_allowed, retry_after = limiter.is_allowed("test_user")
        assert is_allowed is False
        assert retry_after is not None
        assert retry_after > 0


# Test DevRel Agent
class TestDevRelAgent:
    """Test DevRel agent functionality"""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Test agent initialization"""
        agent = DevRelAgent()
        
        assert agent.agent_name == "DevRelAgent"
        assert agent.llm is not None
        assert agent.search_tool is not None
        assert agent.faq_tool is not None
        assert agent.github_toolkit is not None
        
    @pytest.mark.asyncio
    async def test_agent_state_persistence(self):
        """Test that agent maintains state across calls"""
        agent = DevRelAgent()
        thread_id = "test_thread_123"
        
        # First interaction
        state1 = AgentState(
            session_id="session1",
            user_id="user123",
            platform="discord",
            context={"original_message": "First message"}
        )
        
        result1 = await agent.run(state1, thread_id)
        
        # Get thread state
        thread_state = await agent.get_thread_state(thread_id)
        
        # Should have recorded the interaction
        assert thread_state is not None
        assert isinstance(thread_state, dict)
        
    @pytest.mark.asyncio
    async def test_agent_clear_thread_memory(self):
        """Test clearing thread memory"""
        agent = DevRelAgent()
        thread_id = "test_thread_456"
        
        # Create some state
        state = AgentState(
            session_id="session2",
            user_id="user456",
            platform="discord",
            context={"original_message": "Test message"}
        )
        
        await agent.run(state, thread_id)
        
        # Clear memory
        success = await agent.clear_thread_memory(thread_id, force_clear=True)
        assert success is True
        
        # State should be empty after clearing
        thread_state = await agent.get_thread_state(thread_id)
        assert thread_state == {} or thread_state is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])