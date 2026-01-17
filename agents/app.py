"""FastAPI application for Manufacturing Analytics Agents."""
import logging
import uuid
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from schemas.models import (
    ChatRequest,
    ChatResponse,
    ChatMessage,
    HealthResponse,
    SessionInfo,
    AgentInfo,
    AgentListResponse,
    ChartData
)
from cubejs_client import cubejs_client
from session_manager import session_manager

# Import Praval infrastructure
from reef_config import initialize_reef, cleanup_reef
from praval import broadcast, get_reef, get_registry

# Import all Praval agents (registers them via @agent decorator)

import domain_expert
import analytics_specialist
import visualization_specialist
import quality_inspector
import report_writer

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the application."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    # Initialize Praval Reef
    try:
        reef = initialize_reef()
        logger.info("✓ Praval Reef initialized")
        logger.info(f"✓ Registered agents: Analytics Specialist, "
                   f"Visualization Specialist, Quality Inspector, Report Writer")
    except Exception as e:
        logger.error(f"✗ Reef initialization error: {str(e)}")

    # Check Cube.js connection on startup
    try:
        is_connected = await cubejs_client.health_check()
        if is_connected:
            logger.info("✓ Cube.js connection verified")
        else:
            logger.warning("⚠ Cube.js connection failed")
    except Exception as e:
        logger.error(f"✗ Cube.js connection error: {str(e)}")

    yield

    logger.info("Shutting down application")
    cleanup_reef()


# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    cubejs_connected = await cubejs_client.health_check()

    return HealthResponse(
        status="healthy" if cubejs_connected else "degraded",
        version=settings.app_version,
        cubejs_connected=cubejs_connected
    )


@app.get("/agents", response_model=AgentListResponse, tags=["Agents"])
async def list_agents():
    """
    Get list of all registered Praval agents.

    Uses Praval's reef channels to discover registered agents.
    Returns agent metadata including name, description, and status.
    """
    try:
        # Get reef instance and channel stats
        reef = get_reef()
        stats = reef.get_network_stats()

        agent_info_list = []
        agent_names_set = set()

        # Agent descriptions based on architecture documentation
        agent_descriptions = {
            "domain_expert": "Query analysis and domain enrichment",
            "analytics_specialist": "Query translation and Cube.js execution",
            "visualization_specialist": "Chart type selection and data visualization",
            "quality_inspector": "Anomaly detection and root cause analysis",
            "report_writer": "Narrative composition and insights generation",
            "response_storage": "Response storage for HTTP endpoint"
        }

        # Extract agent names from all channels
        for channel_name, channel_stats in stats.get('channel_stats', {}).items():
            channel = reef.get_channel(channel_name)
            if channel and hasattr(channel, 'subscribers'):
                # Get unique agent names from subscribers
                for agent_name in channel.subscribers.keys():
                    agent_names_set.add(agent_name)

        # Also try to get agents from global registry as fallback
        try:
            registry = get_registry()
            all_agents = registry.get_all_agents()
            for agent_name in all_agents.keys():
                agent_names_set.add(agent_name)
        except Exception as registry_error:
            logger.warning(f"Could not access registry: {registry_error}")

        # Build agent info list
        for agent_name in sorted(agent_names_set):
            # Skip non-agent subscribers (like chat_endpoint)
            if agent_name in ['chat_endpoint', 'system']:
                continue

            agent_info = AgentInfo(
                name=agent_name,
                status="active",
                description=agent_descriptions.get(agent_name, "Manufacturing analytics agent"),
                provider="openai",  # Default provider
                tools=[],
                memory_enabled=False
            )
            agent_info_list.append(agent_info)

        logger.info(f"Listed {len(agent_info_list)} registered agents from reef channels")

        return AgentListResponse(
            agents=agent_info_list,
            total_count=len(agent_info_list)
        )

    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve agent list")


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Main chat endpoint using Praval multi-agent system.

    Broadcasts user_query Spore and waits for final_response_ready from agents.
    """
    try:
        # Get or create session
        session_id = request.session_id or str(uuid.uuid4())

        if not session_manager.session_exists(session_id):
            session_id = session_manager.create_session()

        # Add user message to session
        user_message = ChatMessage(
            role="user",
            content=request.message,
            timestamp=datetime.now().isoformat()
        )
        session_manager.add_message(session_id, user_message)

        # Get conversation context
        context_messages = session_manager.get_context(session_id, max_messages=5)
        context = [
            {"role": msg.role, "content": msg.content}
            for msg in context_messages[:-1]  # Exclude current message
        ]

        logger.info(f"Processing message via Praval agents: '{request.message}' (session: {session_id})")

        # Create user_query Spore knowledge
        user_query_knowledge = {
            "type": "user_query",
            "message": request.message,
            "session_id": session_id,
            "context": context,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Broadcast user_query Spore using Reef's API
        logger.info(f"Broadcasting user_query Spore for session {session_id}")
        reef = get_reef()
        reef.broadcast(from_agent="chat_endpoint", knowledge=user_query_knowledge)

        # Wait for final_response_ready with timeout
        # Since Praval agents process Spores asynchronously, we need to wait for the response
        # Multiple LLM calls in sequence: Manufacturing Advisor -> Quality Inspector -> Report Writer
        # Each can take 3-5 seconds, so allow sufficient time for the full pipeline
        timeout_seconds = 30.0
        poll_interval = 0.2
        start_time = asyncio.get_event_loop().time()

        final_response = None

        # Create temporary response storage if not exists
        if not hasattr(report_writer, '_pending_responses'):
            report_writer._pending_responses = {}

        while asyncio.get_event_loop().time() - start_time < timeout_seconds:
            await asyncio.sleep(poll_interval)

            # Check if Report Writer has stored the response
            if hasattr(report_writer, '_pending_responses'):
                final_response = report_writer._pending_responses.get(session_id)
                if final_response:
                    # Clean up
                    del report_writer._pending_responses[session_id]
                    logger.info(f"Received final_response_ready for session {session_id}")
                    break

        # Timeout handling
        if final_response is None:
            logger.error(f"Timeout waiting for final_response_ready (session {session_id})")

            # Create fallback response
            assistant_message = ChatMessage(
                role="assistant",
                content="I'm analyzing your query. This is taking longer than expected. Please try again.",
                timestamp=datetime.now().isoformat()
            )
            session_manager.add_message(session_id, assistant_message)

            return ChatResponse(
                message="Processing timeout. Please try again.",
                session_id=session_id,
                chart=None,
                insights=None,
                suggested_questions=["Can you rephrase your question?"]
            )

        # Extract final response
        narrative = final_response.get("narrative", "No response generated")
        chart_spec = final_response.get("chart_spec")
        follow_ups = final_response.get("follow_ups", [])

        # Convert chart_spec to ChartData model if present
        chart_data = None
        if chart_spec:
            chart_type = chart_spec.get("type", "table")
            valid_chart_types = ["bar", "line", "table", "donut", "gauge", "grouped_bar", "kpi"]
            if chart_type in valid_chart_types:
                chart_data = {
                    "chart_type": chart_type,
                    "data": chart_spec.get("data", {}),  # Chart.js format dict with labels/datasets
                    "options": chart_spec.get("options"),
                    "x_axis": None,
                    "y_axis": None,
                    "title": chart_spec.get("options", {}).get("plugins", {}).get("title", {}).get("text"),
                    "centerValue": chart_spec.get("centerValue"),  # For gauge charts
                }

        # Add assistant message to session
        assistant_message = ChatMessage(
            role="assistant",
            content=narrative,
            timestamp=datetime.now().isoformat()
        )
        session_manager.add_message(session_id, assistant_message)

        # Extract insights from narrative (split by bullet points)
        insights = [line.strip("• ").strip() for line in narrative.split("\n") if line.strip().startswith("•")]

        return ChatResponse(
            message=narrative,
            session_id=session_id,
            chart=chart_data,
            insights=insights if insights else None,
            suggested_questions=follow_ups[:3] if follow_ups else []
        )

    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/session/{session_id}", response_model=SessionInfo, tags=["Session"])
async def get_session(session_id: str):
    """Get session information."""
    if not session_manager.session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")

    messages = session_manager.get_session(session_id)
    timestamp = session_manager.session_timestamps.get(session_id)

    return SessionInfo(
        session_id=session_id,
        message_count=len(messages),
        created_at=timestamp.isoformat() if timestamp else "",
        last_activity=timestamp.isoformat() if timestamp else ""
    )


@app.delete("/session/{session_id}", tags=["Session"])
async def delete_session(session_id: str):
    """Delete a session."""
    if session_id in session_manager.sessions:
        session_manager.sessions.pop(session_id)
        session_manager.session_timestamps.pop(session_id, None)
        return {"message": "Session deleted"}

    raise HTTPException(status_code=404, detail="Session not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower()
    )
