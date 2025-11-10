"""Data extraction from source databases."""

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from .database import DatabaseConnection
from .config import DatabaseConfig

logger = logging.getLogger(__name__)


class DataExtractor:
    """Extracts data from source databases."""

    def __init__(self, db_config: DatabaseConfig, source_name: str):
        """Initialize extractor.

        Args:
            db_config: Database configuration
            source_name: Name of the source (refills, bodies, springs)
        """
        self.db = DatabaseConnection(db_config)
        self.source_name = source_name

    def extract_all(self, table_name: str) -> List[Dict[str, Any]]:
        """Extract all rows from a table.

        Args:
            table_name: Name of the table to extract from

        Returns:
            List of rows as dictionaries
        """
        query = f"SELECT * FROM {table_name} ORDER BY id"
        logger.info(f"Extracting all data from {self.source_name}.{table_name}")

        try:
            data = self.db.execute_query(query)
            logger.info(f"Extracted {len(data)} rows from {self.source_name}.{table_name}")
            return data
        except Exception as e:
            logger.error(f"Failed to extract from {self.source_name}.{table_name}: {e}")
            raise

    def extract_incremental(
        self,
        table_name: str,
        last_sync_time: Optional[datetime] = None,
        timestamp_column: str = "timestamp"
    ) -> List[Dict[str, Any]]:
        """Extract rows modified since last sync.

        Args:
            table_name: Name of the table
            last_sync_time: Last sync timestamp
            timestamp_column: Column to use for incremental sync

        Returns:
            List of new/modified rows
        """
        if last_sync_time:
            query = f"""
                SELECT * FROM {table_name}
                WHERE {timestamp_column} > %s
                ORDER BY id
            """
            logger.info(
                f"Extracting incremental data from {self.source_name}.{table_name} "
                f"since {last_sync_time}"
            )
            data = self.db.execute_query(query, (last_sync_time,))
        else:
            logger.info(f"No last sync time, extracting all data from {table_name}")
            data = self.extract_all(table_name)

        logger.info(f"Extracted {len(data)} rows from {self.source_name}.{table_name}")
        return data

    def get_max_timestamp(self, table_name: str, timestamp_column: str = "timestamp") -> Optional[datetime]:
        """Get the maximum timestamp from a table.

        Args:
            table_name: Name of the table
            timestamp_column: Timestamp column name

        Returns:
            Maximum timestamp or None if table is empty
        """
        query = f"SELECT MAX({timestamp_column}) as max_ts FROM {table_name}"
        result = self.db.execute_query(query)

        if result and result[0]['max_ts']:
            return result[0]['max_ts']
        return None

    def close(self):
        """Close database connection."""
        self.db.close()


class RefillsExtractor(DataExtractor):
    """Extractor for refills production data."""

    def __init__(self, db_config: DatabaseConfig):
        super().__init__(db_config, "refills")
        self.table_name = "refills_production"

    def extract(self, incremental: bool = False, last_sync_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Extract refills production data.

        Args:
            incremental: Whether to do incremental extraction
            last_sync_time: Last sync timestamp for incremental

        Returns:
            List of production records
        """
        if incremental:
            return self.extract_incremental(self.table_name, last_sync_time)
        return self.extract_all(self.table_name)


class BodiesExtractor(DataExtractor):
    """Extractor for bodies production data."""

    def __init__(self, db_config: DatabaseConfig):
        super().__init__(db_config, "bodies")
        self.table_name = "bodies_production"

    def extract(self, incremental: bool = False, last_sync_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Extract bodies production data.

        Args:
            incremental: Whether to do incremental extraction
            last_sync_time: Last sync timestamp for incremental

        Returns:
            List of production records
        """
        if incremental:
            return self.extract_incremental(self.table_name, last_sync_time)
        return self.extract_all(self.table_name)


class SpringsExtractor(DataExtractor):
    """Extractor for springs production data."""

    def __init__(self, db_config: DatabaseConfig):
        super().__init__(db_config, "springs")
        self.table_name = "springs_production"

    def extract(self, incremental: bool = False, last_sync_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Extract springs production data.

        Args:
            incremental: Whether to do incremental extraction
            last_sync_time: Last sync timestamp for incremental

        Returns:
            List of production records
        """
        if incremental:
            return self.extract_incremental(self.table_name, last_sync_time)
        return self.extract_all(self.table_name)
