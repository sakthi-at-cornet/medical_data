"""Configuration settings for the analytics agents service."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Settings
    app_name: str = "Manufacturing Analytics Agents"
    app_version: str = "0.1.0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Cube.js Settings
    cubejs_api_url: str = "http://cubejs:4000/cubejs-api/v1"
    cubejs_api_secret: str = "mysecretkey1234567890abcdefghijkl"

    # OpenAI Settings
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 0.1
    openai_max_tokens: int = 1000

    # Multi-Model Strategy
    model_quality_inspector: str = "gpt-4o"  # Complex reasoning
    model_report_writer: str = "gpt-4o"      # Narrative composition
    model_manufacturing_advisor: str = "gpt-4o-mini"  # Simple tasks
    model_analytics_specialist: str = "gpt-4o-mini"
    model_visualization_specialist: str = "gpt-4o-mini"

    # Session Settings
    max_session_messages: int = 30  # Increased from 10 for better context
    session_timeout_minutes: int = 30

    # Database Settings (for persistent storage)
    db_host: str = "postgres-warehouse"
    db_port: int = 5432
    db_name: str = "warehouse"
    db_user: str = "warehouse_user"
    db_password: str = "warehouse_pass"

    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


settings = Settings()
