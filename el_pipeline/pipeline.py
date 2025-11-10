"""EL Pipeline orchestration."""

import logging
from typing import Optional
from datetime import datetime

from .config import PipelineConfig
from .extractor import RefillsExtractor, BodiesExtractor, SpringsExtractor
from .loader import DataLoader

logger = logging.getLogger(__name__)


class ELPipeline:
    """Orchestrates the EL pipeline."""

    def __init__(self, config: PipelineConfig):
        """Initialize EL pipeline.

        Args:
            config: Pipeline configuration
        """
        self.config = config

        # Initialize extractors
        self.refills_extractor = RefillsExtractor(config.refills_db)
        self.bodies_extractor = BodiesExtractor(config.bodies_db)
        self.springs_extractor = SpringsExtractor(config.springs_db)

        # Initialize loader
        self.loader = DataLoader(config.warehouse_db)

    def run_full_sync(self):
        """Run full sync of all sources to warehouse."""
        logger.info("Starting full sync")

        # Extract and load refills
        logger.info("=" * 60)
        logger.info("Processing REFILLS")
        logger.info("=" * 60)
        refills_data = self.refills_extractor.extract(incremental=False)
        self.loader.load_refills(refills_data, truncate=True)

        # Extract and load bodies
        logger.info("=" * 60)
        logger.info("Processing BODIES")
        logger.info("=" * 60)
        bodies_data = self.bodies_extractor.extract(incremental=False)
        self.loader.load_bodies(bodies_data, truncate=True)

        # Extract and load springs
        logger.info("=" * 60)
        logger.info("Processing SPRINGS")
        logger.info("=" * 60)
        springs_data = self.springs_extractor.extract(incremental=False)
        self.loader.load_springs(springs_data, truncate=True)

        logger.info("=" * 60)
        logger.info("Full sync completed successfully")
        logger.info("=" * 60)

        return {
            "refills_count": len(refills_data),
            "bodies_count": len(bodies_data),
            "springs_count": len(springs_data),
        }

    def run_incremental_sync(self, last_sync_time: Optional[datetime] = None):
        """Run incremental sync of all sources.

        Args:
            last_sync_time: Timestamp of last sync

        Returns:
            Dictionary with sync statistics
        """
        logger.info(f"Starting incremental sync since {last_sync_time}")

        # Extract and load refills
        refills_data = self.refills_extractor.extract(incremental=True, last_sync_time=last_sync_time)
        self.loader.load_refills(refills_data, truncate=False)

        # Extract and load bodies
        bodies_data = self.bodies_extractor.extract(incremental=True, last_sync_time=last_sync_time)
        self.loader.load_bodies(bodies_data, truncate=False)

        # Extract and load springs
        springs_data = self.springs_extractor.extract(incremental=True, last_sync_time=last_sync_time)
        self.loader.load_springs(springs_data, truncate=False)

        logger.info("Incremental sync completed successfully")

        return {
            "refills_count": len(refills_data),
            "bodies_count": len(bodies_data),
            "springs_count": len(springs_data),
        }

    def get_warehouse_stats(self) -> dict:
        """Get statistics from warehouse.

        Returns:
            Dictionary with table counts
        """
        return {
            "refills_count": self.loader.get_load_count("refills_production"),
            "bodies_count": self.loader.get_load_count("bodies_production"),
            "springs_count": self.loader.get_load_count("springs_production"),
        }

    def close(self):
        """Close all connections."""
        self.refills_extractor.close()
        self.bodies_extractor.close()
        self.springs_extractor.close()
        self.loader.close()
