from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pydantic import field_validator, ConfigDict
from typing import Optional
import os

load_dotenv()

class Settings(BaseSettings):
    ## CORE (minimal code)
    backend_url: str
    
    ## OPTIONAL
    
    # Gemini LLM API Key
    gemini_api_key: Optional[str] = None

    # Tavily API Key
    tavily_api_key: Optional[str] = None

    # Platforms
    github_token: Optional[str] = None
    discord_bot_token: Optional[str] = None

    # DB configuration
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None

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
    
    # FalkorDB / CodeGraph
    falkordb_host: Optional[str] = None
    falkordb_port: Optional[str] = None
    codegraph_backend_url: Optional[str] = None
    secret_token: Optional[str] = None

    # RabbitMQ configuration
    rabbitmq_url: Optional[str] = None

    # Onboarding UX toggles
    onboarding_show_oauth_button: bool = True
    # ------------------
    # Derived feature gates
    # ------------------

    @property
    def discord_enabled(self) -> bool:
        return bool(self.discord_bot_token) and bool(self.gemini_api_key)

    @property
    def github_enabled(self) -> bool:
        """
        GitHub verification + OAuth.
        """
        return self.discord_enabled and bool(self.backend_url) and all([
            self.github_token,
            self.supabase_url,
            self.supabase_key,
        ])

    @property
    def code_intelligence_enabled(self) -> bool:
        """
        Runs DevrAI in full mode.
        """
        return self.github_enabled and all([
            self.rabbitmq_url,
            self.falkordb_host,
            self.falkordb_port,
            self.codegraph_backend_url,
            self.secret_token,
        ])


settings = Settings()
