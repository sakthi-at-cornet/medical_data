"""Pydantic models for API requests and responses."""
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """A single chat message."""
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., min_length=1, max_length=500)
    session_id: Optional[str] = None


class ChartData(BaseModel):
    """Chart data and configuration."""
    chart_type: Literal["bar", "line", "table"]
    data: list[dict[str, Any]]
    x_axis: Optional[str] = None
    y_axis: Optional[str] = None
    title: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    message: str
    session_id: str
    chart: Optional[ChartData] = None
    insights: Optional[list[str]] = None
    suggested_questions: Optional[list[str]] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    cubejs_connected: bool


class SessionInfo(BaseModel):
    """Session information."""
    session_id: str
    message_count: int
    created_at: str
    last_activity: str


class CubeQuery(BaseModel):
    """Cube.js query structure."""
    measures: Optional[list[str]] = None
    dimensions: Optional[list[str]] = None
    filters: Optional[list[dict[str, Any]]] = None
    timeDimensions: Optional[list[dict[str, Any]]] = None
    order: Optional[dict[str, str]] = None
    limit: Optional[int] = None
