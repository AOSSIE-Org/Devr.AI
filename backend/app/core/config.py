from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Gemini LLM API Key
    gemini_api_key: str = ""

    # Tavily API Key
    tavily_api_key: str = ""

    # Platforms
    github_token: str = ""
    discord_bot_token: str = ""

    # TODO: Add DB configuration
    # Database
    # Supabase
    # Weaviate

    # LangSmith Tracing
    langsmith_tracing: bool = False
    langsmith_endpoint: str = "https://api.smith.langchain.com"
    langsmith_api_key: str = ""
    langsmith_project: str = "DevR_AI"

    # Agent Configuration
    devrel_agent_model: str = "gemini-2.0-flash"
    github_agent_model: str = "gemini-2.0-flash"
    classification_agent_model: str = "gemini-1.5-flash"
    agent_timeout: int = 30
    max_retries: int = 3

    class Config:
        env_file = ".env"
        extra = "ignore"  # to prevent errors from extra env variables


settings = Settings()
