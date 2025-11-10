"""In-memory session management for conversation state."""
import uuid
from datetime import datetime, timedelta
from typing import Optional
from models import ChatMessage
from config import settings


class SessionManager:
    """Manages conversation sessions in memory."""

    def __init__(self):
        """Initialize session storage."""
        self.sessions: dict[str, list[ChatMessage]] = {}
        self.session_timestamps: dict[str, datetime] = {}

    def create_session(self) -> str:
        """Create a new session and return session ID."""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = []
        self.session_timestamps[session_id] = datetime.now()
        return session_id

    def get_session(self, session_id: str) -> Optional[list[ChatMessage]]:
        """Get messages for a session."""
        self._cleanup_expired_sessions()
        return self.sessions.get(session_id)

    def add_message(self, session_id: str, message: ChatMessage) -> None:
        """Add a message to session history."""
        if session_id not in self.sessions:
            self.sessions[session_id] = []

        self.sessions[session_id].append(message)
        self.session_timestamps[session_id] = datetime.now()

        # Keep only last N messages
        max_messages = settings.max_session_messages
        if len(self.sessions[session_id]) > max_messages:
            self.sessions[session_id] = self.sessions[session_id][-max_messages:]

    def get_context(self, session_id: str, max_messages: int = 5) -> list[ChatMessage]:
        """Get recent conversation context for a session."""
        messages = self.get_session(session_id)
        if not messages:
            return []
        return messages[-max_messages:]

    def _cleanup_expired_sessions(self) -> None:
        """Remove sessions older than timeout."""
        timeout = timedelta(minutes=settings.session_timeout_minutes)
        now = datetime.now()
        expired = [
            sid for sid, ts in self.session_timestamps.items()
            if now - ts > timeout
        ]
        for sid in expired:
            self.sessions.pop(sid, None)
            self.session_timestamps.pop(sid, None)

    def session_exists(self, session_id: str) -> bool:
        """Check if session exists and is valid."""
        self._cleanup_expired_sessions()
        return session_id in self.sessions


# Global session manager instance
session_manager = SessionManager()
