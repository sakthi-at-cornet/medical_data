"""Data loading to warehouse."""

from typing import List, Dict, Any
import logging
from datetime import datetime, timezone

from .database import DatabaseConnection
from .config import DatabaseConfig

logger = logging.getLogger(__name__)


class DataLoader:
    """Loads data into warehouse."""

    def __init__(self, warehouse_config: DatabaseConfig):
        """Initialize loader.

        Args:
            warehouse_config: Warehouse database configuration
        """
        self.db = DatabaseConnection(warehouse_config)

    def load_refills(self, data: List[Dict[str, Any]], truncate: bool = False):
        """Load refills data into warehouse raw schema.

        Args:
            data: List of refills production records
            truncate: Whether to truncate table before loading
        """
        if not data:
            logger.warning("No refills data to load")
            return

        table_name = "raw.refills_production"

        if truncate:
            self.db.truncate_table("refills_production", schema="raw")

        # Prepare insert query
        insert_query = """
            INSERT INTO raw.refills_production (
                id, timestamp, line_id, batch_id,
                ink_viscosity_pas, write_distance_km, tip_diameter_mm,
                ink_color, flow_consistency, quality_status,
                created_at, _airbyte_emitted_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """

        # Prepare data tuples
        now = datetime.now(timezone.utc)
        rows = [
            (
                row['id'],
                row['timestamp'],
                row['line_id'],
                row['batch_id'],
                row['ink_viscosity_pas'],
                row['write_distance_km'],
                row['tip_diameter_mm'],
                row['ink_color'],
                row['flow_consistency'],
                row['quality_status'],
                row.get('created_at', now),
                now,  # _airbyte_emitted_at
            )
            for row in data
        ]

        self.db.execute_insert_batch(insert_query, rows)
        logger.info(f"Loaded {len(rows)} refills records into {table_name}")

    def load_bodies(self, data: List[Dict[str, Any]], truncate: bool = False):
        """Load bodies data into warehouse raw schema.

        Args:
            data: List of bodies production records
            truncate: Whether to truncate table before loading
        """
        if not data:
            logger.warning("No bodies data to load")
            return

        table_name = "raw.bodies_production"

        if truncate:
            self.db.truncate_table("bodies_production", schema="raw")

        insert_query = """
            INSERT INTO raw.bodies_production (
                id, timestamp, line_id, batch_id,
                durability_score, color_match_rating, length_mm,
                wall_thickness_mm, material, quality_status,
                created_at, _airbyte_emitted_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """

        now = datetime.now(timezone.utc)
        rows = [
            (
                row['id'],
                row['timestamp'],
                row['line_id'],
                row['batch_id'],
                row['durability_score'],
                row['color_match_rating'],
                row['length_mm'],
                row['wall_thickness_mm'],
                row['material'],
                row['quality_status'],
                row.get('created_at', now),
                now,
            )
            for row in data
        ]

        self.db.execute_insert_batch(insert_query, rows)
        logger.info(f"Loaded {len(rows)} bodies records into {table_name}")

    def load_springs(self, data: List[Dict[str, Any]], truncate: bool = False):
        """Load springs data into warehouse raw schema.

        Args:
            data: List of springs production records
            truncate: Whether to truncate table before loading
        """
        if not data:
            logger.warning("No springs data to load")
            return

        table_name = "raw.springs_production"

        if truncate:
            self.db.truncate_table("springs_production", schema="raw")

        insert_query = """
            INSERT INTO raw.springs_production (
                id, timestamp, line_id, batch_id,
                diameter_mm, tensile_strength_mpa, material,
                compression_ratio, quality_status,
                created_at, _airbyte_emitted_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """

        now = datetime.now(timezone.utc)
        rows = [
            (
                row['id'],
                row['timestamp'],
                row['line_id'],
                row['batch_id'],
                row['diameter_mm'],
                row['tensile_strength_mpa'],
                row['material'],
                row['compression_ratio'],
                row['quality_status'],
                row.get('created_at', now),
                now,
            )
            for row in data
        ]

        self.db.execute_insert_batch(insert_query, rows)
        logger.info(f"Loaded {len(rows)} springs records into {table_name}")

    def get_load_count(self, table_name: str) -> int:
        """Get count of loaded records.

        Args:
            table_name: Name of the table (without schema)

        Returns:
            Number of records in raw table
        """
        return self.db.get_table_count(table_name, schema="raw")

    def close(self):
        """Close database connection."""
        self.db.close()
