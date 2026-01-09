"""Configuration settings for the analytics agents service."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Settings
    app_name: str = "Medical Analytics Agents"
    app_version: str = "0.1.0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Cube.js Settings
    cubejs_api_url: str = "http://cubejs:4000/cubejs-api/v1"
    cubejs_api_secret: str = "mysecretkey1234567890abcdefghijkl"

    # Groq API Settings (OpenAI-compatible)
    groq_api_key: str = ""
    groq_model: str = "moonshotai/Kimi-K2-Instruct-0905"
    groq_base_url: str = "https://api.groq.com/openai/v1"
    groq_temperature: float = 0.1
    groq_max_tokens: int = 1000

    # All agents use the same Groq model (Kimi K2)
    model_quality_inspector: str = "moonshotai/Kimi-K2-Instruct-0905"
    model_report_writer: str = "moonshotai/Kimi-K2-Instruct-0905"
    # model_manufacturing_advisor removed
    model_analytics_specialist: str = "moonshotai/Kimi-K2-Instruct-0905"
    model_visualization_specialist: str = "moonshotai/Kimi-K2-Instruct-0905"

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
