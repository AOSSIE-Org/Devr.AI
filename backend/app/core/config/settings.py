from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pydantic import field_validator,ConfigDict
from typing import Optional

load_dotenv()

class Settings(BaseSettings):
    # Gemini LLM API Key
    gemini_api_key: str = ""

    # Tavily API Key
    tavily_api_key: str = ""

    # Platforms
    github_token: str = ""
    discord_bot_token: str = ""

    # DB configuration
    supabase_url: str
    supabase_key: str

    # LangSmith Tracing
    langsmith_tracing: bool = False
    langsmith_endpoint: str = "https://api.smith.langchain.com"
    langsmith_api_key: str = ""
    langsmith_project: str = "DevR_AI"

    # Agent Configuration
    devrel_agent_model: str = "gemini-2.5-flash"
    github_agent_model: str = "gemini-2.5-flash"
    classification_agent_model: str = "gemini-2.0-flash"
    agent_timeout: int = 30
    max_retries: int = 3

    # RabbitMQ configuration
    rabbitmq_url: Optional[str] = None

    # Backend URL
    backend_url: str = ""

    # Onboarding UX toggles
    onboarding_show_oauth_button: bool = True

    # MCP configuration
    mcp_server_url: Optional[str] = None
    mcp_api_key: Optional[str] = None

    @field_validator("supabase_url", "supabase_key", mode="before")
    @classmethod
    def _not_empty(cls, v, field):
        if not v:
            raise ValueError(f"{field.name} must be set")
        return v

    model_config =  ConfigDict(
        env_file = ".env",
        extra = "ignore" 
    ) # to prevent errors from extra env variables


settings = Settings()
