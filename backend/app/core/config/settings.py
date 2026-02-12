import os
import sys
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pydantic import field_validator, ConfigDict, Field
from typing import Optional, List
import logging

load_dotenv()

class Settings(BaseSettings):
    # Environment configuration
    environment: str = Field(default="development", description="Application environment")
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Gemini LLM API Key
    gemini_api_key: str = Field(default="", description="Google Gemini API key")

    # Tavily API Key
    tavily_api_key: str = Field(default="", description="Tavily search API key")

    # Platforms
    github_token: str = Field(default="", description="GitHub access token")
    discord_bot_token: str = Field(default="", description="Discord bot token")

    # DB configuration
    supabase_url: str = Field(description="Supabase project URL")
    supabase_key: str = Field(description="Supabase anon key")

    # LangSmith Tracing
    langsmith_tracing: bool = Field(default=False, description="Enable LangSmith tracing")
    langsmith_endpoint: str = Field(default="https://api.smith.langchain.com", description="LangSmith API endpoint")
    langsmith_api_key: str = Field(default="", description="LangSmith API key")
    langsmith_project: str = Field(default="DevR_AI", description="LangSmith project name")

    # Agent Configuration
    devrel_agent_model: str = Field(default="gemini-2.5-flash", description="DevRel agent model")
    github_agent_model: str = Field(default="gemini-2.5-flash", description="GitHub agent model")
    classification_agent_model: str = Field(default="gemini-2.0-flash", description="Classification agent model")
    agent_timeout: int = Field(default=30, description="Agent timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")

    # RabbitMQ configuration
    rabbitmq_url: Optional[str] = Field(default=None, description="RabbitMQ connection URL")

    # Backend URL
    backend_url: str = Field(default="http://localhost:8000", description="Backend API URL")

    # Onboarding UX toggles
    onboarding_show_oauth_button: bool = Field(default=True, description="Show OAuth button in onboarding")
    
    # CORS configuration
    cors_origins: List[str] = Field(
        default=[
            "http://localhost:5173",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000",
        ],
        description="Allowed CORS origins"
    )
    
    # Security settings
    secret_key: str = Field(default="dev-secret-key-change-in-production", description="Secret key for encryption")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiration time in minutes")
    
    # Database connection settings
    db_pool_size: int = Field(default=10, description="Database connection pool size")
    db_max_overflow: int = Field(default=20, description="Database connection pool max overflow")
    
    # External service timeouts
    external_api_timeout: int = Field(default=30, description="External API timeout in seconds")
    github_api_timeout: int = Field(default=30, description="GitHub API timeout in seconds")
    discord_api_timeout: int = Field(default=30, description="Discord API timeout in seconds")
    
    # Rate limiting
    rate_limit_per_minute: int = Field(default=60, description="Rate limit per minute per user")
    
    # Health check settings
    health_check_timeout: int = Field(default=5, description="Health check timeout in seconds")

    @field_validator("supabase_url", "supabase_key", mode="before")
    @classmethod
    def validate_required_fields(cls, v, info):
        field_name = info.field_name
        if not v or v.strip() == "":
            raise ValueError(f"{field_name} is required and cannot be empty")
        return v.strip()
    
    @field_validator("environment", mode="before")
    @classmethod
    def validate_environment(cls, v):
        valid_environments = ["development", "staging", "production", "testing"]
        if v not in valid_environments:
            raise ValueError(f"Environment must be one of: {', '.join(valid_environments)}")
        return v
    
    @field_validator("log_level", mode="before")
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Log level must be one of: {', '.join(valid_levels)}")
        return v_upper
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def validate_cors_origins(cls, v):
        if isinstance(v, str):
            # Handle comma-separated string
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        elif isinstance(v, list):
            return [origin.strip() for origin in v if origin.strip()]
        return v
    
    @field_validator("agent_timeout", "max_retries", "external_api_timeout", mode="before")
    @classmethod
    def validate_positive_integers(cls, v, info):
        field_name = info.field_name
        if not isinstance(v, int) or v <= 0:
            raise ValueError(f"{field_name} must be a positive integer")
        return v

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"
    
    def get_database_url(self) -> str:
        """Get database URL for connections."""
        return f"{self.supabase_url}/rest/v1"
    
    def validate_required_services(self) -> List[str]:
        """Validate that required services are configured."""
        missing_services = []
        
        # Check critical services
        if not self.supabase_url:
            missing_services.append("Supabase URL")
        if not self.supabase_key:
            missing_services.append("Supabase Key")
        
        # Check AI services (at least one should be configured)
        if not self.gemini_api_key:
            missing_services.append("Gemini API Key")
        
        # Check platform integrations (warn if missing but don't fail)
        optional_missing = []
        if not self.github_token:
            optional_missing.append("GitHub Token")
        if not self.discord_bot_token:
            optional_missing.append("Discord Bot Token")
        
        if optional_missing:
            logging.warning(f"Optional services not configured: {', '.join(optional_missing)}")
        
        return missing_services


def get_settings() -> Settings:
    """Get application settings with validation."""
    try:
        settings = Settings()
        
        # Validate required services
        missing_services = settings.validate_required_services()
        if missing_services:
            error_msg = f"Missing required configuration: {', '.join(missing_services)}"
            logging.error(error_msg)
            if settings.is_production():
                sys.exit(1)
            else:
                logging.warning("Running in development mode with missing configuration")
        
        return settings
        
    except Exception as e:
        logging.error(f"Failed to load configuration: {e}")
        sys.exit(1)


# Global settings instance
settings = get_settings()
