from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pydantic import field_validator
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

    @field_validator("supabase_url", "supabase_key", mode="before")
    @classmethod
    def _not_empty(cls, v, field):
        if not v:
            raise ValueError(f"{field.name} must be set")
        return v

# Add the new org info fields:
    org_name: str = "AOSSIE"
    org_website: str = "https://aossie.org"
    org_github: str = "https://github.com/AOSSIE-Org"
    org_twitter: str = "https://twitter.com/aossie_org"

    class Config:
        env_file = ".env"
        extra = "ignore"  # to prevent errors from extra env variables


settings = Settings()
