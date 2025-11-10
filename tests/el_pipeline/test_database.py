"""Tests for database module."""

import pytest
from el_pipeline.database import DatabaseConnection
from el_pipeline.config import DatabaseConfig


@pytest.mark.integration
def test_database_connection(db_config):
    """Test database connection establishment."""
    db = DatabaseConnection(db_config)

    try:
        conn = db.connect()
        assert conn is not None
        assert not conn.closed
    finally:
        db.close()


@pytest.mark.integration
def test_database_close(db_config):
    """Test database connection closing."""
    db = DatabaseConnection(db_config)
    db.connect()
    db.close()

    assert db._conn.closed


@pytest.mark.integration
def test_execute_query(db_config):
    """Test query execution."""
    db = DatabaseConnection(db_config)

    try:
        result = db.execute_query("SELECT COUNT(*) as count FROM refills_production")
        assert len(result) == 1
        assert 'count' in result[0]
        assert result[0]['count'] >= 0
    finally:
        db.close()


@pytest.mark.integration
def test_get_table_count(db_config):
    """Test table row count retrieval."""
    db = DatabaseConnection(db_config)

    try:
        count = db.get_table_count("refills_production")
        assert isinstance(count, int)
        assert count >= 0
    finally:
        db.close()


@pytest.mark.integration
def test_cursor_context_manager(db_config):
    """Test cursor context manager."""
    db = DatabaseConnection(db_config)

    try:
        with db.cursor() as cur:
            cur.execute("SELECT 1 as test")
            result = cur.fetchone()
            assert result['test'] == 1
    finally:
        db.close()


@pytest.mark.integration
def test_connection_reuse(db_config):
    """Test that connection is reused."""
    db = DatabaseConnection(db_config)

    try:
        conn1 = db.connect()
        conn2 = db.connect()
        assert conn1 is conn2
    finally:
        db.close()
