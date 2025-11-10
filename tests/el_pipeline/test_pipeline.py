"""Integration tests for EL pipeline."""

import pytest
from el_pipeline.pipeline import ELPipeline


@pytest.mark.integration
def test_pipeline_full_sync(test_config):
    """Test full pipeline sync."""
    pipeline = ELPipeline(test_config)

    try:
        # Run full sync
        stats = pipeline.run_full_sync()

        # Verify stats
        assert stats['refills_count'] > 0
        assert stats['bodies_count'] > 0
        assert stats['springs_count'] > 0

        # Verify data landed in warehouse
        warehouse_stats = pipeline.get_warehouse_stats()
        assert warehouse_stats['refills_count'] == stats['refills_count']
        assert warehouse_stats['bodies_count'] == stats['bodies_count']
        assert warehouse_stats['springs_count'] == stats['springs_count']

    finally:
        pipeline.close()


@pytest.mark.integration
def test_pipeline_warehouse_stats(test_config):
    """Test warehouse statistics retrieval."""
    pipeline = ELPipeline(test_config)

    try:
        stats = pipeline.get_warehouse_stats()

        assert 'refills_count' in stats
        assert 'bodies_count' in stats
        assert 'springs_count' in stats
        assert all(isinstance(count, int) for count in stats.values())

    finally:
        pipeline.close()


@pytest.mark.integration
def test_pipeline_closes_connections(test_config):
    """Test that pipeline properly closes all connections."""
    pipeline = ELPipeline(test_config)

    # Establish connections by running a small operation
    pipeline.get_warehouse_stats()

    # Close connections
    pipeline.close()

    # Verify all connections are closed
    assert pipeline.refills_extractor.db._conn is None or pipeline.refills_extractor.db._conn.closed
    assert pipeline.bodies_extractor.db._conn is None or pipeline.bodies_extractor.db._conn.closed
    assert pipeline.springs_extractor.db._conn is None or pipeline.springs_extractor.db._conn.closed
    assert pipeline.loader.db._conn.closed
