from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Keys
    gemini_api_key: str = ""
    tavily_api_key: str = ""
    github_token: str = ""
    discord_bot_token: str = ""

    # TODO: Add DB configuration
    # Database
    # Supabase
    # Weaviate

    # Agent Configuration
    devrel_agent_model: str = "gemini-2.0-flash"
    github_agent_model: str = "gemini-2.0-flash"
    classification_agent_model: str = "gemini-1.5-flash"
    agent_timeout: int = 30
    max_retries: int = 3

    class Config:
        env_file = ".env"


settings = Settings()
