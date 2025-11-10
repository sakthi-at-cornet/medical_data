"""Configuration management for EL pipeline."""

from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os


class DatabaseConfig(BaseModel):
    """Database connection configuration."""

    host: str
    port: int
    database: str
    user: str
    password: str

    @property
    def connection_string(self) -> str:
        """Generate PostgreSQL connection string."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class PipelineConfig(BaseModel):
    """EL Pipeline configuration."""

    # Source databases
    refills_db: DatabaseConfig
    bodies_db: DatabaseConfig
    springs_db: DatabaseConfig

    # Warehouse
    warehouse_db: DatabaseConfig

    # Pipeline settings
    batch_size: int = Field(default=1000, description="Batch size for data extraction")
    log_level: str = Field(default="INFO", description="Logging level")

    @classmethod
    def from_env(cls, env_file: Optional[str] = ".env.el") -> "PipelineConfig":
        """Load configuration from environment variables."""
        load_dotenv(env_file)

        return cls(
            refills_db=DatabaseConfig(
                host=os.getenv("REFILLS_HOST", "localhost"),
                port=int(os.getenv("REFILLS_PORT", "5432")),
                database=os.getenv("REFILLS_DB", "refills"),
                user=os.getenv("REFILLS_USER", "refills_user"),
                password=os.getenv("REFILLS_PASSWORD", "refills_pass"),
            ),
            bodies_db=DatabaseConfig(
                host=os.getenv("BODIES_HOST", "localhost"),
                port=int(os.getenv("BODIES_PORT", "5433")),
                database=os.getenv("BODIES_DB", "bodies"),
                user=os.getenv("BODIES_USER", "bodies_user"),
                password=os.getenv("BODIES_PASSWORD", "bodies_pass"),
            ),
            springs_db=DatabaseConfig(
                host=os.getenv("SPRINGS_HOST", "localhost"),
                port=int(os.getenv("SPRINGS_PORT", "5434")),
                database=os.getenv("SPRINGS_DB", "springs"),
                user=os.getenv("SPRINGS_USER", "springs_user"),
                password=os.getenv("SPRINGS_PASSWORD", "springs_pass"),
            ),
            warehouse_db=DatabaseConfig(
                host=os.getenv("WAREHOUSE_HOST", "localhost"),
                port=int(os.getenv("WAREHOUSE_PORT", "5435")),
                database=os.getenv("WAREHOUSE_DB", "warehouse"),
                user=os.getenv("WAREHOUSE_USER", "warehouse_user"),
                password=os.getenv("WAREHOUSE_PASSWORD", "warehouse_pass"),
            ),
            batch_size=int(os.getenv("BATCH_SIZE", "1000")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )
