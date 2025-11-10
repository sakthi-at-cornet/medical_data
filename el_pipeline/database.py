"""Database connection management."""

import psycopg2
from psycopg2.extras import RealDictCursor, execute_batch
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
import logging

from .config import DatabaseConfig

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Manages PostgreSQL database connections."""

    def __init__(self, config: DatabaseConfig):
        """Initialize database connection.

        Args:
            config: Database configuration
        """
        self.config = config
        self._conn: Optional[psycopg2.extensions.connection] = None

    def connect(self) -> psycopg2.extensions.connection:
        """Establish database connection.

        Returns:
            PostgreSQL connection object
        """
        if self._conn is None or self._conn.closed:
            self._conn = psycopg2.connect(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.user,
                password=self.config.password,
            )
            logger.info(f"Connected to {self.config.database} at {self.config.host}:{self.config.port}")
        return self._conn

    def close(self):
        """Close database connection."""
        if self._conn and not self._conn.closed:
            self._conn.close()
            logger.info(f"Closed connection to {self.config.database}")

    @contextmanager
    def cursor(self, cursor_factory=RealDictCursor):
        """Get a cursor with automatic connection management.

        Args:
            cursor_factory: Cursor factory class

        Yields:
            Database cursor
        """
        conn = self.connect()
        cur = conn.cursor(cursor_factory=cursor_factory)
        try:
            yield cur
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            cur.close()

    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of rows as dictionaries
        """
        with self.cursor() as cur:
            cur.execute(query, params)
            results = cur.fetchall()
            logger.debug(f"Query returned {len(results)} rows")
            return [dict(row) for row in results]

    def execute_insert_batch(self, query: str, data: List[tuple], batch_size: int = 1000):
        """Execute batch insert operation.

        Args:
            query: INSERT query with placeholders
            data: List of tuples containing row data
            batch_size: Number of rows per batch
        """
        with self.cursor() as cur:
            execute_batch(cur, query, data, page_size=batch_size)
            logger.info(f"Inserted {len(data)} rows in batches of {batch_size}")

    def get_table_count(self, table_name: str, schema: Optional[str] = None) -> int:
        """Get row count for a table.

        Args:
            table_name: Name of the table
            schema: Optional schema name

        Returns:
            Number of rows in the table
        """
        full_table_name = f"{schema}.{table_name}" if schema else table_name
        query = f"SELECT COUNT(*) as count FROM {full_table_name}"

        with self.cursor() as cur:
            cur.execute(query)
            result = cur.fetchone()
            return result['count']

    def truncate_table(self, table_name: str, schema: Optional[str] = None):
        """Truncate a table.

        Args:
            table_name: Name of the table
            schema: Optional schema name
        """
        full_table_name = f"{schema}.{table_name}" if schema else table_name
        query = f"TRUNCATE TABLE {full_table_name} RESTART IDENTITY CASCADE"

        with self.cursor() as cur:
            cur.execute(query)
            logger.info(f"Truncated table {full_table_name}")
