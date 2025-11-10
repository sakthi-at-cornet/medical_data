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

    # Session Settings
    max_session_messages: int = 10
    session_timeout_minutes: int = 30

    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


settings = Settings()
