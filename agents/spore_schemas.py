"""
Spore Knowledge Schemas for Praval Multi-Agent Communication.

Pydantic models defining the structure of knowledge payloads in Spores.
"""
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


# ============================================================================
# Spore Knowledge Schemas
# ============================================================================


class UserQueryKnowledge(BaseModel):
    """Knowledge payload for user_query Spore (Frontend → Manufacturing Advisor)."""

    type: Literal["user_query"] = "user_query"
    message: str = Field(..., description="User's natural language query")
    session_id: str = Field(..., description="Unique session identifier")
    context: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Previous conversation messages (role, content)",
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Query timestamp",
    )


class DomainEnrichedRequestKnowledge(BaseModel):
    """Knowledge payload for domain_enriched_request Spore (Domain Expert → Analytics Specialist)."""

    type: Literal["domain_enriched_request"] = "domain_enriched_request"
    user_intent: str = Field(..., description="Classified intent (e.g., 'compare_quality_by_modality')")
    entities: List[str] = Field(default_factory=list, description="Entities involved (modalities, body parts, etc.)")
    metrics: List[str] = Field(default_factory=list, description="Metrics requested")
    dimensions: List[str] = Field(default_factory=list, description="Dimensions for breakdown")
    cube_recommendation: str = Field(..., description="Recommended Cube.js cube")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Query filters")
    time_range: Optional[Dict[str, str]] = Field(None, description="Time range filter")
    session_id: str = Field(..., description="Session identifier")
    context_notes: str = Field(default="", description="Additional context from conversation")


class DataReadyKnowledge(BaseModel):
    """Knowledge payload for data_ready Spore (Analytics Specialist → Viz Specialist, Quality Inspector)."""

    type: Literal["data_ready"] = "data_ready"
    query_results: List[Dict[str, Any]] = Field(..., description="Query result rows")
    cube_used: str = Field(..., description="Cube.js cube queried")
    measures: List[str] = Field(default_factory=list, description="Measures queried")
    dimensions: List[str] = Field(default_factory=list, description="Dimensions queried")
    row_count: int = Field(..., description="Number of result rows")
    query_time_ms: int = Field(..., description="Query execution time in ms")
    session_id: str = Field(..., description="Session identifier")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Query metadata (data_shape, has_time_series, category_counts, etc.)",
    )


class ChartReadyKnowledge(BaseModel):
    """Knowledge payload for chart_ready Spore (Visualization Specialist → Report Writer)."""

    type: Literal["chart_ready"] = "chart_ready"
    chart_spec: Dict[str, Any] = Field(..., description="Chart.js specification")
    chart_type: str = Field(..., description="Chart type (bar, line, table, etc.)")
    session_id: str = Field(..., description="Session identifier")


class ObservationInsight(BaseModel):
    """Individual observation insight."""

    type: str = Field(..., description="Insight type (comparative, pattern, etc.)")
    text: str = Field(..., description="Human-readable insight text")
    confidence: float = Field(..., description="Confidence score (0-1)")
    data_points: Dict[str, Any] = Field(default_factory=dict, description="Supporting data points")


class AnomalyInsight(BaseModel):
    """Individual anomaly detected."""

    entity: str = Field(..., description="Entity with anomaly (e.g., CT, Brain)")
    metric: str = Field(..., description="Metric with anomaly")
    severity: str = Field(..., description="Severity (low, moderate, high, critical)")
    description: str = Field(..., description="Human-readable anomaly description")


class RootCauseHypothesis(BaseModel):
    """Root cause hypothesis."""

    hypothesis: str = Field(..., description="Root cause hypothesis text")
    confidence: float = Field(..., description="Confidence score (0-1)")
    evidence: List[str] = Field(default_factory=list, description="Supporting evidence")
    recommended_action: str = Field(..., description="Recommended corrective action")


class InsightsReadyKnowledge(BaseModel):
    """Knowledge payload for insights_ready Spore (Quality Inspector → Report Writer)."""

    type: Literal["insights_ready"] = "insights_ready"
    observations: List[ObservationInsight] = Field(default_factory=list, description="Observation insights")
    anomalies: List[AnomalyInsight] = Field(default_factory=list, description="Detected anomalies")
    root_causes: List[RootCauseHypothesis] = Field(default_factory=list, description="Root cause hypotheses")
    session_id: str = Field(..., description="Session identifier")


class FinalResponseReadyKnowledge(BaseModel):
    """Knowledge payload for final_response_ready Spore (Report Writer → Frontend)."""

    type: Literal["final_response_ready"] = "final_response_ready"
    narrative: str = Field(..., description="Composed narrative with insights")
    chart_spec: Optional[Dict[str, Any]] = Field(None, description="Chart.js specification (if available)")
    follow_ups: List[str] = Field(default_factory=list, description="Suggested follow-up questions")
    session_id: str = Field(..., description="Session identifier")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Response timestamp",
    )


class ClarificationQuestionKnowledge(BaseModel):
    """Knowledge payload for clarification_question Spore (Manufacturing Advisor → Frontend)."""

    type: Literal["clarification_question"] = "clarification_question"
    question: str = Field(..., description="Clarification question text")
    options: List[Dict[str, str]] = Field(
        ..., description="Options for user to choose (label, text)"
    )
    session_id: str = Field(..., description="Session identifier")


class QueryRefinementNeededKnowledge(BaseModel):
    """Knowledge payload for query_refinement_needed Spore (Visualization Specialist → Analytics Specialist)."""

    type: Literal["query_refinement_needed"] = "query_refinement_needed"
    reason: str = Field(..., description="Reason for refinement (e.g., 'too_many_data_points')")
    current_row_count: int = Field(..., description="Current result row count")
    suggested_refinement: str = Field(..., description="Suggested refinement action")
    session_id: str = Field(..., description="Session identifier")


class QueryExecutionErrorKnowledge(BaseModel):
    """Knowledge payload for query_execution_error Spore (Analytics Specialist → Frontend)."""

    type: Literal["query_execution_error"] = "query_execution_error"
    error: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Error type (schema_error, connection_error, etc.)")
    session_id: str = Field(..., description="Session identifier")


# ============================================================================
# Helper Functions
# ============================================================================


def create_user_query_knowledge(message: str, session_id: str, context: List[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Create user_query knowledge payload.

    Args:
        message: User's query message
        session_id: Session identifier
        context: Previous conversation messages

    Returns:
        Dict suitable for Spore knowledge field
    """
    return UserQueryKnowledge(
        message=message,
        session_id=session_id,
        context=context or [],
    ).dict()


def create_domain_enriched_request_knowledge(
    user_intent: str,
    entities: List[str],
    metrics: List[str],
    dimensions: List[str],
    cube_recommendation: str,
    session_id: str,
    filters: Dict[str, Any] = None,
    time_range: Optional[Dict[str, str]] = None,
    context_notes: str = "",
) -> Dict[str, Any]:
    """
    Create domain_enriched_request knowledge payload.

    Args:
        user_intent: Classified intent
        entities: Entities involved (modalities, etc.)
        metrics: Metrics requested
        dimensions: Dimensions for breakdown
        cube_recommendation: Recommended cube
        session_id: Session identifier
        filters: Query filters
        time_range: Time range filter
        context_notes: Additional context

    Returns:
        Dict suitable for Spore knowledge field
    """
    return DomainEnrichedRequestKnowledge(
        user_intent=user_intent,
        entities=entities,
        metrics=metrics,
        dimensions=dimensions,
        cube_recommendation=cube_recommendation,
        session_id=session_id,
        filters=filters or {},
        time_range=time_range,
        context_notes=context_notes,
    ).dict()


def create_data_ready_knowledge(
    query_results: List[Dict[str, Any]],
    cube_used: str,
    measures: List[str],
    dimensions: List[str],
    session_id: str,
    query_time_ms: int,
    metadata: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Create data_ready knowledge payload.

    Args:
        query_results: Query result rows
        cube_used: Cube queried
        measures: Measures queried
        dimensions: Dimensions queried
        session_id: Session identifier
        query_time_ms: Query execution time
        metadata: Query metadata

    Returns:
        Dict suitable for Spore knowledge field
    """
    return DataReadyKnowledge(
        query_results=query_results,
        cube_used=cube_used,
        measures=measures,
        dimensions=dimensions,
        row_count=len(query_results),
        query_time_ms=query_time_ms,
        session_id=session_id,
        metadata=metadata or {},
    ).dict()


def create_chart_ready_knowledge(
    chart_spec: Dict[str, Any],
    chart_type: str,
    session_id: str,
) -> Dict[str, Any]:
    """
    Create chart_ready knowledge payload.

    Args:
        chart_spec: Chart.js specification
        chart_type: Chart type
        session_id: Session identifier

    Returns:
        Dict suitable for Spore knowledge field
    """
    return ChartReadyKnowledge(
        chart_spec=chart_spec,
        chart_type=chart_type,
        session_id=session_id,
    ).dict()


def create_insights_ready_knowledge(
    observations: List[Dict[str, Any]],
    anomalies: List[Dict[str, Any]],
    root_causes: List[Dict[str, Any]],
    session_id: str,
) -> Dict[str, Any]:
    """
    Create insights_ready knowledge payload.

    Args:
        observations: Observation insights
        anomalies: Detected anomalies
        root_causes: Root cause hypotheses
        session_id: Session identifier

    Returns:
        Dict suitable for Spore knowledge field
    """
    return InsightsReadyKnowledge(
        observations=[ObservationInsight(**obs) for obs in observations],
        anomalies=[AnomalyInsight(**anom) for anom in anomalies],
        root_causes=[RootCauseHypothesis(**rc) for rc in root_causes],
        session_id=session_id,
    ).dict()


def create_final_response_ready_knowledge(
    narrative: str,
    session_id: str,
    chart_spec: Optional[Dict[str, Any]] = None,
    follow_ups: List[str] = None,
) -> Dict[str, Any]:
    """
    Create final_response_ready knowledge payload.

    Args:
        narrative: Composed narrative
        session_id: Session identifier
        chart_spec: Chart specification
        follow_ups: Follow-up question suggestions

    Returns:
        Dict suitable for Spore knowledge field
    """
    return FinalResponseReadyKnowledge(
        narrative=narrative,
        chart_spec=chart_spec,
        follow_ups=follow_ups or [],
        session_id=session_id,
    ).dict()
