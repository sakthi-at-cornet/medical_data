"""Tests for configuration module."""

import pytest
from el_pipeline.config import DatabaseConfig, PipelineConfig


def test_database_config_creation():
    """Test DatabaseConfig creation."""
    config = DatabaseConfig(
        host="localhost",
        port=5432,
        database="testdb",
        user="testuser",
        password="testpass",
    )

    assert config.host == "localhost"
    assert config.port == 5432
    assert config.database == "testdb"
    assert config.user == "testuser"
    assert config.password == "testpass"


def test_database_config_connection_string():
    """Test connection string generation."""
    config = DatabaseConfig(
        host="localhost",
        port=5432,
        database="testdb",
        user="testuser",
        password="testpass",
    )

    expected = "postgresql://testuser:testpass@localhost:5432/testdb"
    assert config.connection_string == expected


def test_pipeline_config_creation(test_config):
    """Test PipelineConfig creation."""
    assert test_config.refills_db.database == "refills"
    assert test_config.bodies_db.database == "bodies"
    assert test_config.springs_db.database == "springs"
    assert test_config.warehouse_db.database == "warehouse"
    assert test_config.batch_size == 100
    assert test_config.log_level == "DEBUG"


def test_pipeline_config_defaults():
    """Test PipelineConfig default values."""
    config = PipelineConfig(
        refills_db=DatabaseConfig(
            host="localhost", port=5432, database="refills",
            user="user", password="pass"
        ),
        bodies_db=DatabaseConfig(
            host="localhost", port=5432, database="bodies",
            user="user", password="pass"
        ),
        springs_db=DatabaseConfig(
            host="localhost", port=5432, database="springs",
            user="user", password="pass"
        ),
        warehouse_db=DatabaseConfig(
            host="localhost", port=5432, database="warehouse",
            user="user", password="pass"
        ),
    )

    assert config.batch_size == 1000  # Default value
    assert config.log_level == "INFO"  # Default value
