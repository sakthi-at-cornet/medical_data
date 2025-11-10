"""Tests for data extractor."""

import pytest
from el_pipeline.extractor import RefillsExtractor, BodiesExtractor, SpringsExtractor
from el_pipeline.config import DatabaseConfig


@pytest.mark.integration
def test_refills_extractor(test_config):
    """Test refills data extraction."""
    extractor = RefillsExtractor(test_config.refills_db)

    try:
        data = extractor.extract(incremental=False)

        assert len(data) > 0
        assert 'id' in data[0]
        assert 'line_id' in data[0]
        assert 'ink_viscosity_pas' in data[0]
        assert 'quality_status' in data[0]
    finally:
        extractor.close()


@pytest.mark.integration
def test_bodies_extractor(test_config):
    """Test bodies data extraction."""
    extractor = BodiesExtractor(test_config.bodies_db)

    try:
        data = extractor.extract(incremental=False)

        assert len(data) > 0
        assert 'id' in data[0]
        assert 'line_id' in data[0]
        assert 'durability_score' in data[0]
        assert 'material' in data[0]
    finally:
        extractor.close()


@pytest.mark.integration
def test_springs_extractor(test_config):
    """Test springs data extraction."""
    extractor = SpringsExtractor(test_config.springs_db)

    try:
        data = extractor.extract(incremental=False)

        assert len(data) > 0
        assert 'id' in data[0]
        assert 'line_id' in data[0]
        assert 'diameter_mm' in data[0]
        assert 'tensile_strength_mpa' in data[0]
    finally:
        extractor.close()


@pytest.mark.integration
def test_extractor_get_max_timestamp(test_config):
    """Test getting maximum timestamp from table."""
    extractor = RefillsExtractor(test_config.refills_db)

    try:
        max_ts = extractor.get_max_timestamp("refills_production")
        assert max_ts is not None
    finally:
        extractor.close()


@pytest.mark.integration
def test_incremental_extraction(test_config):
    """Test incremental data extraction."""
    extractor = RefillsExtractor(test_config.refills_db)

    try:
        # Get max timestamp
        max_ts = extractor.get_max_timestamp("refills_production")

        # Extract incremental data (should be empty since we're using max timestamp)
        data = extractor.extract(incremental=True, last_sync_time=max_ts)

        # Should return empty or very few records
        assert isinstance(data, list)
    finally:
        extractor.close()
