"""Tests for session management."""
import pytest
from datetime import datetime, timedelta
from models import ChatMessage
from session_manager import SessionManager


def test_create_session():
    """Test session creation."""
    manager = SessionManager()
    session_id = manager.create_session()

    assert session_id is not None
    assert len(session_id) > 0
    assert session_id in manager.sessions
    assert manager.sessions[session_id] == []


def test_add_message():
    """Test adding messages to session."""
    manager = SessionManager()
    session_id = manager.create_session()

    message = ChatMessage(role="user", content="Hello")
    manager.add_message(session_id, message)

    assert len(manager.sessions[session_id]) == 1
    assert manager.sessions[session_id][0].content == "Hello"


def test_get_context():
    """Test retrieving conversation context."""
    manager = SessionManager()
    session_id = manager.create_session()

    # Add multiple messages
    for i in range(10):
        msg = ChatMessage(role="user" if i % 2 == 0 else "assistant", content=f"Message {i}")
        manager.add_message(session_id, msg)

    context = manager.get_context(session_id, max_messages=5)

    assert len(context) == 5
    assert context[-1].content == "Message 9"


def test_max_messages_limit():
    """Test that sessions don't exceed max message limit."""
    manager = SessionManager()
    manager.sessions = {}  # Reset
    session_id = manager.create_session()

    # Add more messages than the limit
    for i in range(15):
        msg = ChatMessage(role="user", content=f"Message {i}")
        manager.add_message(session_id, msg)

    # Should only keep last 10 (default max)
    assert len(manager.sessions[session_id]) == 10
    assert manager.sessions[session_id][0].content == "Message 5"


def test_session_exists():
    """Test checking if session exists."""
    manager = SessionManager()
    session_id = manager.create_session()

    assert manager.session_exists(session_id) is True
    assert manager.session_exists("non-existent") is False


def test_cleanup_expired_sessions():
    """Test cleanup of expired sessions."""
    manager = SessionManager()
    session_id = manager.create_session()

    # Manually set timestamp to past
    manager.session_timestamps[session_id] = datetime.now() - timedelta(hours=1)

    # Trigger cleanup
    manager._cleanup_expired_sessions()

    assert session_id not in manager.sessions
