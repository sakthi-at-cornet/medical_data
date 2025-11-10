"""FastAPI application for Manufacturing Analytics Agents."""
import logging
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from models import (
    ChatRequest,
    ChatResponse,
    ChatMessage,
    HealthResponse,
    SessionInfo
)
from cubejs_client import cubejs_client
from data_analyst_agent import data_analyst_agent
from chat_agent import chat_agent
from session_manager import session_manager

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


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Main chat endpoint.

    Processes user message, determines if data query is needed,
    executes query via Cube.js, generates insights, and returns response.
    """
    try:
        # Get or create session
        session_id = request.session_id or session_manager.create_session()

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
        context_string = chat_agent.build_context_string(context_messages[:-1])  # Exclude current message

        logger.info(f"Processing message: '{request.message}' (session: {session_id})")

        # Determine if data query is needed
        needs_query = await chat_agent.should_query_data(request.message, context_string)

        if not needs_query:
            # Generate conversational response without data query
            response_text = await chat_agent.generate_conversational_response(
                request.message,
                context_string
            )

            assistant_message = ChatMessage(
                role="assistant",
                content=response_text,
                timestamp=datetime.now().isoformat()
            )
            session_manager.add_message(session_id, assistant_message)

            return ChatResponse(
                message=response_text,
                session_id=session_id,
                chart=None,
                insights=None,
                suggested_questions=["What's the overall pass rate?", "Which component has the best quality?"]
            )

        # Translate to Cube.js query
        cube_query, chart_type = await data_analyst_agent.translate_to_query(
            request.message,
            context_string
        )

        logger.info(f"Generated query: {cube_query.model_dump(exclude_none=True)}")

        # Execute query
        cube_response = await cubejs_client.execute_query(cube_query)

        # Format chart data
        chart_data = data_analyst_agent.format_chart_data(
            cube_response,
            chart_type,
            cube_query
        )

        # Generate insights
        insights = await data_analyst_agent.generate_insights(
            request.message,
            cube_response
        )

        # Generate follow-up suggestions
        suggestions = await chat_agent.suggest_followup_questions(
            request.message,
            cube_response
        )

        # Create response message
        response_text = "\n".join([f"• {insight}" for insight in insights])

        assistant_message = ChatMessage(
            role="assistant",
            content=response_text,
            timestamp=datetime.now().isoformat()
        )
        session_manager.add_message(session_id, assistant_message)

        return ChatResponse(
            message=response_text,
            session_id=session_id,
            chart=chart_data,
            insights=insights,
            suggested_questions=suggestions
        )

    except ValueError as e:
        logger.error(f"Query execution error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except ConnectionError as e:
        logger.error(f"Connection error: {str(e)}")
        raise HTTPException(status_code=503, detail="Cannot connect to data service")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
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
