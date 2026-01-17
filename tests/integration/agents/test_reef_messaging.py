"""Integration tests for Reef messaging and Spore schemas."""
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from praval import Spore, broadcast, get_reef

# Add agents directory to path
agents_dir = Path(__file__).parent.parent.parent.parent / "agents"
sys.path.insert(0, str(agents_dir))

from schemas.spore import (
    UserQueryKnowledge,
    DomainEnrichedRequestKnowledge,
    DataReadyKnowledge,
    ChartReadyKnowledge,
    InsightsReadyKnowledge,
    FinalResponseReadyKnowledge,
    ObservationInsight,
    AnomalyInsight,
    RootCauseHypothesis
)
from reef_config import initialize_reef, cleanup_reef, get_reef_instance


@pytest.mark.integration
def test_reef_initialization():
    """Test Reef initialization."""
    reef = initialize_reef()

    assert reef is not None
    assert get_reef_instance() == reef


@pytest.mark.integration
def test_reef_singleton_pattern():
    """Test that Reef follows singleton pattern."""
    reef1 = initialize_reef()
    reef2 = initialize_reef()

    assert reef1 is reef2


@pytest.mark.integration
def test_user_query_spore_schema():
    """Test UserQueryKnowledge Spore schema validation."""
    knowledge = UserQueryKnowledge(
        message="Show me defects by part family",
        session_id="test-session-123",
        context=[
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi! How can I help?"}
        ]
    )

    assert knowledge.type == "user_query"
    assert knowledge.message == "Show me defects by part family"
    assert knowledge.session_id == "test-session-123"
    assert len(knowledge.context) == 2
    assert knowledge.timestamp is not None


@pytest.mark.integration
def test_domain_enriched_request_spore_schema():
    """Test DomainEnrichedRequestKnowledge Spore schema validation."""
    knowledge = DomainEnrichedRequestKnowledge(
        user_intent="compare_defects_by_part_family",
        part_families=["Door_Outer_Left", "Door_Outer_Right"],
        metrics=["defect_count"],
        dimensions=["part_family"],
        cube_recommendation="PartFamilyPerformance",
        filters={"quality_status": "failed"},
        time_range={"start": "2024-01-01", "end": "2024-01-31"},
        session_id="test-session-123"
    )

    assert knowledge.type == "domain_enriched_request"
    assert knowledge.user_intent == "compare_defects_by_part_family"
    assert "Door_Outer_Left" in knowledge.part_families
    assert "defect_count" in knowledge.metrics
    assert knowledge.cube_recommendation == "PartFamilyPerformance"
    assert knowledge.filters["quality_status"] == "failed"


@pytest.mark.integration
def test_data_ready_spore_schema():
    """Test DataReadyKnowledge Spore schema validation."""
    knowledge = DataReadyKnowledge(
        query_results=[
            {"PartFamilyPerformance.partFamily": "Door_Outer_Left", "PartFamilyPerformance.defectCount": "45"},
            {"PartFamilyPerformance.partFamily": "Door_Outer_Right", "PartFamilyPerformance.defectCount": "28"}
        ],
        cube_used="PartFamilyPerformance",
        measures=["PartFamilyPerformance.defectCount"],
        dimensions=["PartFamilyPerformance.partFamily"],
        row_count=2,
        query_time_ms=125,
        session_id="test-session-123",
        metadata={
            "data_shape": "table",
            "has_time_series": False,
            "category_counts": {"partFamily": 2}
        }
    )

    assert knowledge.type == "data_ready"
    assert knowledge.row_count == 2
    assert knowledge.query_time_ms == 125
    assert knowledge.cube_used == "PartFamilyPerformance"
    assert len(knowledge.query_results) == 2


@pytest.mark.integration
def test_chart_ready_spore_schema():
    """Test ChartReadyKnowledge Spore schema validation."""
    knowledge = ChartReadyKnowledge(
        chart_spec={
            "type": "bar",
            "data": {
                "labels": ["Door_Outer_Left", "Door_Outer_Right"],
                "datasets": [{"data": [45, 28]}]
            }
        },
        chart_type="bar",
        session_id="test-session-123"
    )

    assert knowledge.type == "chart_ready"
    assert knowledge.chart_type == "bar"
    assert knowledge.chart_spec["type"] == "bar"
    assert len(knowledge.chart_spec["data"]["labels"]) == 2


@pytest.mark.integration
def test_insights_ready_spore_schema():
    """Test InsightsReadyKnowledge Spore schema validation."""
    knowledge = InsightsReadyKnowledge(
        observations=[
            ObservationInsight(
                type="comparative",
                text="Door_Outer_Left has 60% more defects than Door_Outer_Right",
                confidence=0.9,
                data_points={"left": 45, "right": 28}
            )
        ],
        anomalies=[
            AnomalyInsight(
                entity="Door_Outer_Left",
                metric="defect_count",
                severity="high",
                description="Defect count significantly higher"
            )
        ],
        root_causes=[
            RootCauseHypothesis(
                hypothesis="Die wear on LINE_A tooling",
                confidence=0.75,
                evidence=["High defect concentration", "Left panel specific"],
                recommended_action="Schedule die inspection and potential replacement"
            )
        ],
        session_id="test-session-123"
    )

    assert knowledge.type == "insights_ready"
    assert len(knowledge.observations) == 1
    assert len(knowledge.anomalies) == 1
    assert len(knowledge.root_causes) == 1
    assert knowledge.observations[0].confidence == 0.9


@pytest.mark.integration
def test_final_response_ready_spore_schema():
    """Test FinalResponseReadyKnowledge Spore schema validation."""
    knowledge = FinalResponseReadyKnowledge(
        narrative="Door_Outer_Left shows 45 defects compared to 28 for Door_Outer_Right. This indicates potential die wear on LINE_A.",
        chart_spec={
            "type": "bar",
            "data": {"labels": ["Door_Outer_Left", "Door_Outer_Right"], "datasets": [{"data": [45, 28]}]}
        },
        follow_ups=[
            "Show me die changeover history for LINE_A",
            "What's the defect breakdown by type for Door_Outer_Left?",
            "Compare cycle times between left and right doors"
        ],
        session_id="test-session-123"
    )

    assert knowledge.type == "final_response_ready"
    assert "Door_Outer_Left" in knowledge.narrative
    assert len(knowledge.follow_ups) == 3
    assert knowledge.chart_spec is not None
    assert knowledge.session_id == "test-session-123"


@pytest.mark.integration
def test_spore_schema_validation_errors():
    """Test that Spore schemas properly validate required fields."""
    # Missing required field should raise validation error
    with pytest.raises(Exception):  # Pydantic ValidationError
        UserQueryKnowledge(
            # Missing 'message' field
            session_id="test-session-123"
        )

    with pytest.raises(Exception):
        DataReadyKnowledge(
            query_results=[],
            # Missing required fields
        )


@pytest.mark.integration
def test_spore_schema_default_values():
    """Test that Spore schemas apply default values correctly."""
    knowledge = DomainEnrichedRequestKnowledge(
        user_intent="test_intent",
        cube_recommendation="PressOperations",
        session_id="test-session-123"
        # Not providing optional fields
    )

    # Check defaults are applied
    assert knowledge.part_families == []
    assert knowledge.metrics == []
    assert knowledge.dimensions == []
    assert knowledge.filters == {}
    assert knowledge.time_range is None
    assert knowledge.context_notes == ""


@pytest.mark.integration
def test_spore_message_serialization():
    """Test that Spore knowledge can be serialized/deserialized."""
    original = UserQueryKnowledge(
        message="Test query",
        session_id="test-123",
        context=[]
    )

    # Serialize to dict
    serialized = original.model_dump()

    # Deserialize back
    deserialized = UserQueryKnowledge(**serialized)

    assert deserialized.message == original.message
    assert deserialized.session_id == original.session_id
    assert deserialized.type == original.type


@pytest.mark.integration
def test_reef_cleanup():
    """Test Reef cleanup."""
    initialize_reef()
    cleanup_reef()

    # After cleanup, should need to reinitialize
    with pytest.raises(RuntimeError, match="Reef not initialized"):
        get_reef_instance()
