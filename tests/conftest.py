"""Pytest configuration and fixtures."""

import pytest
from el_pipeline.config import PipelineConfig, DatabaseConfig


@pytest.fixture
def test_config():
    """Provide test configuration."""
    return PipelineConfig(
        refills_db=DatabaseConfig(
            host="localhost",
            port=5432,
            database="refills",
            user="refills_user",
            password="refills_pass",
        ),
        bodies_db=DatabaseConfig(
            host="localhost",
            port=5433,
            database="bodies",
            user="bodies_user",
            password="bodies_pass",
        ),
        springs_db=DatabaseConfig(
            host="localhost",
            port=5434,
            database="springs",
            user="springs_user",
            password="springs_pass",
        ),
        warehouse_db=DatabaseConfig(
            host="localhost",
            port=5435,
            database="warehouse",
            user="warehouse_user",
            password="warehouse_pass",
        ),
        batch_size=100,
        log_level="DEBUG",
    )


@pytest.fixture
def db_config():
    """Provide database configuration for testing."""
    return DatabaseConfig(
        host="localhost",
        port=5432,
        database="refills",
        user="refills_user",
        password="refills_pass",
    )
