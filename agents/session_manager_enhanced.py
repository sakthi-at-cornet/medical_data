"""Enhanced session management with PostgreSQL persistence and entity tracking."""
import uuid
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from models import ChatMessage
from config import settings
from database import db
import logging

logger = logging.getLogger(__name__)


class EntityTracker:
    """Tracks entities mentioned in conversation for context resolution."""

    def __init__(self):
        """Initialize entity tracker."""
        self.entities: Dict[str, Any] = {}

    def extract_entities(self, message: str) -> Dict[str, Any]:
        """
        Extract medical entities from message.

        Entities tracked:
        - modalities: CT, MRI, X-ray
        - metrics: quality_score, safety_score, tat, cat_rating
        - body_parts: Brain, Spine, Chest, Abdomen
        - radiologists: names mentioned
        - time_periods: last_week, yesterday, etc.
        """
        entities = {}
        msg_lower = message.lower()

        # Modalities
        modalities = []
        if "ct" in msg_lower or "computed tomography" in msg_lower:
            modalities.append("CT")
        if "mri" in msg_lower or "magnetic resonance" in msg_lower:
            modalities.append("MRI")
        if "x-ray" in msg_lower or "xray" in msg_lower:
            modalities.append("X-ray")
        
        if modalities:
            entities["modality"] = modalities

        # Metrics
        metric_keywords = {
            "quality": "quality_score",
            "safety": "safety_score",
            "score": "quality_score",
            "rating": "star_rating",
            "star": "star_rating",
            "cat": "cat_rating",
            "tat": "turnaround_time",
            "time": "turnaround_time",
            "count": "count",
            "volume": "count"
        }
        for keyword, metric in metric_keywords.items():
            if keyword in msg_lower:
                entities["current_metric"] = metric

        # Body Parts
        body_parts = ["brain", "spine", "chest", "abdomen", "pelvis", "neck", "knee", "shoulder"]
        mentioned_parts = [bp.title() for bp in body_parts if bp in msg_lower]
        if mentioned_parts:
            entities["body_part"] = mentioned_parts

        # CAT Ratings
        for i in range(1, 6):
            if f"cat{i}" in msg_lower or f"cat {i}" in msg_lower:
                entities["cat_rating"] = f"CAT{i}"

        # Time periods
        time_keywords = {
            "today": "today",
            "yesterday": "yesterday",
            "last week": "last_7_days",
            "last month": "last_30_days",
            "this week": "current_week",
            "this month": "current_month"
        }
        for keyword, period in time_keywords.items():
            if keyword in msg_lower:
                entities["time_period"] = period

        return entities

    def update(self, message: str):
        """Update tracked entities from new message."""
        new_entities = self.extract_entities(message)
        # Update with new entities (newer values override)
        self.entities.update(new_entities)

    def resolve_reference(self, reference: str) -> Optional[str]:
        """
        Resolve references like 'it', 'that', 'these'.

        Returns the likely entity being referenced.
        """
        reference_lower = reference.lower()

        # Handle plural references
        if reference_lower in ["these", "those", "them"]:
            if "modality" in self.entities:
                return ", ".join(self.entities["modality"])
            if "body_part" in self.entities:
                return ", ".join(self.entities["body_part"])

        # Handle singular references
        if reference_lower in ["it", "that", "this"]:
            # Most recent single entity
            if "current_metric" in self.entities:
                return self.entities["current_metric"]
            if "modality" in self.entities and len(self.entities["modality"]) == 1:
                return self.entities["modality"][0]
            if "body_part" in self.entities and len(self.entities["body_part"]) == 1:
                return self.entities["body_part"][0]

        return None

    def get_context_string(self) -> str:
        """Get human-readable context summary."""
        if not self.entities:
            return "No context established yet."

        parts = []
        if "modality" in self.entities:
            parts.append(f"Modality: {', '.join(self.entities['modality'])}")
        if "current_metric" in self.entities:
            parts.append(f"Metric: {self.entities['current_metric']}")
        if "body_part" in self.entities:
            parts.append(f"Body Part: {', '.join(self.entities['body_part'])}")
        if "cat_rating" in self.entities:
            parts.append(f"Rating: {self.entities['cat_rating']}")
        if "time_period" in self.entities:
            parts.append(f"Period: {self.entities['time_period']}")

        return " | ".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return self.entities

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EntityTracker":
        """Load from dictionary."""
        tracker = cls()
        tracker.entities = data
        return tracker


class EnhancedSessionManager:
    """Session manager with PostgreSQL persistence and entity tracking."""

    def __init__(self):
        """Initialize session manager."""
        # In-memory cache for hot sessions
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.entity_trackers: Dict[str, EntityTracker] = {}

    async def initialize(self):
        """Initialize database connection."""
        await db.connect()
        logger.info("Session manager initialized with database connection")

    async def create_session(self, user_id: Optional[str] = None) -> str:
        """Create a new session and persist to database."""
        session_id = str(uuid.uuid4())

        await db.execute(
            """
            INSERT INTO conversation_history
            (session_id, user_id, messages, entities, created_at, last_activity)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            session_id,
            user_id,
            json.dumps([]),
            json.dumps({}),
            datetime.now(),
            datetime.now()
        )

        # Cache it
        self.cache[session_id] = {
            "messages": [],
            "user_id": user_id,
            "created_at": datetime.now(),
            "last_activity": datetime.now()
        }
        self.entity_trackers[session_id] = EntityTracker()

        logger.info(f"Created new session: {session_id}")
        return session_id

    async def get_session(self, session_id: str) -> Optional[List[ChatMessage]]:
        """Get messages for a session (from cache or database)."""
        # Check cache first
        if session_id in self.cache:
            return self.cache[session_id]["messages"]

        # Load from database
        row = await db.fetchrow(
            "SELECT messages FROM conversation_history WHERE session_id = $1",
            session_id
        )

        if row:
            messages_data = json.loads(row["messages"]) if isinstance(row["messages"], str) else row["messages"]
            messages = [ChatMessage(**msg) for msg in messages_data]
            # Cache it
            self.cache[session_id] = {"messages": messages}
            return messages

        return None

    async def add_message(self, session_id: str, message: ChatMessage) -> None:
        """Add a message to session history and update entities."""
        # Load session if not cached
        if session_id not in self.cache:
            await self.get_session(session_id)

        if session_id not in self.cache:
            self.cache[session_id] = {"messages": []}

        # Add message to cache
        self.cache[session_id]["messages"].append(message)
        self.cache[session_id]["last_activity"] = datetime.now()

        # Keep only last N messages in memory
        max_messages = settings.max_session_messages
        if len(self.cache[session_id]["messages"]) > max_messages:
            self.cache[session_id]["messages"] = self.cache[session_id]["messages"][-max_messages:]

        # Update entity tracking
        if session_id not in self.entity_trackers:
            self.entity_trackers[session_id] = EntityTracker()

        if message.role == "user":
            self.entity_trackers[session_id].update(message.content)

        # Persist to database
        messages_json = json.dumps([msg.model_dump() for msg in self.cache[session_id]["messages"]])
        entities_json = json.dumps(self.entity_trackers[session_id].to_dict())

        await db.execute(
            """
            UPDATE conversation_history
            SET messages = $1, entities = $2, last_activity = $3
            WHERE session_id = $4
            """,
            messages_json,
            entities_json,
            datetime.now(),
            session_id
        )

    async def get_context(self, session_id: str, max_messages: int = 30) -> List[ChatMessage]:
        """Get recent conversation context for a session."""
        messages = await self.get_session(session_id)
        if not messages:
            return []
        return messages[-max_messages:]

    async def get_entities(self, session_id: str) -> EntityTracker:
        """Get entity tracker for session."""
        if session_id not in self.entity_trackers:
            # Load from database
            row = await db.fetchrow(
                "SELECT entities FROM conversation_history WHERE session_id = $1",
                session_id
            )
            if row:
                entities_data = json.loads(row["entities"]) if isinstance(row["entities"], str) else row["entities"]
                self.entity_trackers[session_id] = EntityTracker.from_dict(entities_data)
            else:
                self.entity_trackers[session_id] = EntityTracker()

        return self.entity_trackers[session_id]

    async def session_exists(self, session_id: str) -> bool:
        """Check if session exists in database."""
        result = await db.fetchval(
            "SELECT EXISTS(SELECT 1 FROM conversation_history WHERE session_id = $1)",
            session_id
        )
        return result

    async def cleanup_old_sessions(self, days: int = 30):
        """Archive sessions older than N days."""
        cutoff = datetime.now() - timedelta(days=days)
        await db.execute(
            "DELETE FROM conversation_history WHERE last_activity < $1",
            cutoff
        )
        logger.info(f"Cleaned up sessions older than {days} days")


# Global enhanced session manager instance
enhanced_session_manager = EnhancedSessionManager()
