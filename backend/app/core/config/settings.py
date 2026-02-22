from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pydantic import field_validator, ConfigDict
from typing import Optional
import os

load_dotenv()


class Settings(BaseSettings):
    # ----------------------------
    # API Keys
    # ----------------------------

    gemini_api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None

    # ----------------------------
    # Platforms
    # ----------------------------

    github_token: Optional[str] = None
    discord_bot_token: Optional[str] = None

    # ----------------------------
    # DB configuration
    # ----------------------------

    supabase_url: str
    supabase_key: str

    # ----------------------------
    # LangSmith Tracing
    # ----------------------------

    langsmith_tracing: bool = False
    langsmith_endpoint: str = "https://api.smith.langchain.com"
    langsmith_api_key: Optional[str] = None
    langsmith_project: str = "DevR_AI"

    # ----------------------------
    # Agent Configuration
    # ----------------------------

    devrel_agent_model: str = "gemini-2.5-flash"
    github_agent_model: str = "gemini-2.5-flash"
    classification_agent_model: str = "gemini-2.0-flash"
    agent_timeout: int = 30
    max_retries: int = 3

    # ----------------------------
    # RabbitMQ configuration
    # ----------------------------

    rabbitmq_url: Optional[str] = None

    # ----------------------------
    # Backend URL
    # ----------------------------

    backend_url: Optional[str] = None

    # ----------------------------
    # Onboarding UX toggles
    # ----------------------------

    onboarding_show_oauth_button: bool = True

    # ----------------------------
    # Validators
    # ----------------------------

    @field_validator("supabase_url", "supabase_key", mode="before")
    @classmethod
    def _not_empty(cls, v, field):
        if not v:
            raise ValueError(f"{field.name} must be set")
        return v

    # ----------------------------
    # GitHub Token Resolver
    # ----------------------------

    @property
    def github_token_resolved(self) -> str:
        """
        Ensures consistent GitHub token usage across the app.
        Fallback order:
        1. Value from .env (github_token)
        2. GITHUB_TOKEN
        3. GH_TOKEN
        """
        return (
            self.github_token
            or os.getenv("GITHUB_TOKEN")
            or os.getenv("GH_TOKEN")
            or ""
        )

    model_config = ConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()