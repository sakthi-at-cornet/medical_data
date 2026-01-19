"""Chat Agent: Manages conversation context and coordinates responses."""
import logging
from typing import Optional
from openai import AsyncOpenAI
from schemas.models import ChatMessage, ChatResponse, ChatRequesttings
from config import settings

logger = logging.getLogger(__name__)


class ChatAgent:
    """Agent that manages conversation flow and context."""

    def __init__(self):
        """Initialize the Chat Agent."""
        self.client = AsyncOpenAI(
            api_key=settings.groq_api_key,
            base_url=settings.groq_base_url
        )
        self.model = settings.groq_model

    def build_context_string(self, messages: list[ChatMessage]) -> str:
        """Build a context string from recent messages."""
        if not messages:
            return ""

        context_parts = []
        for msg in messages[-5:]:  # Last 5 messages
            role = msg.role.capitalize()
            context_parts.append(f"{role}: {msg.content}")

        return "\n".join(context_parts)

    async def should_query_data(self, user_message: str, context: str = "") -> bool:
        """
        Determine if the user's message requires a data query.

        Returns:
            True if a data query is needed, False for general chat
        """
        prompt = f"""Determine if this user message requires querying medical radiology audit data.

User message: "{user_message}"
{f"Context: {context}" if context else ""}

Respond with JSON: {{"requires_data_query": true/false, "reason": "brief explanation"}}


Messages NOT requiring data queries (respond conversationally):
- Meta-questions about the system: "What data is this?", "What can I ask?"
- Domain education: "What is a CAT5 rating?", "Explain safety score"
- Greetings: "hello", "hi", "hey"
- Thank you messages
- Clarification questions about previous responses
- General conversation
"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=150,
                response_format={"type": "json_object"}
            )

            import json
            result = json.loads(response.choices[0].message.content)
            should_query = result.get("requires_data_query", True)

            logger.info(f"Should query data: {should_query} - {result.get('reason', 'N/A')}")
            return should_query

        except Exception as e:
            logger.error(f"Error determining query need: {str(e)}")
            # Default to querying if uncertain
            return True

    async def generate_conversational_response(
        self,
        user_message: str,
        context: str = ""
    ) -> str:
        """Generate a conversational response without data query."""
        # Import schema dynamically to avoid hardcoding
        from schemas.radiology import RADIOLOGY_SCHEMA_DICT
        
        # Build dynamic dimension and metric lists
        dimensions_list = ", ".join(list(RADIOLOGY_SCHEMA_DICT.get("dimensions", {}).keys())[:10])
        metrics_list = ", ".join(list(RADIOLOGY_SCHEMA_DICT.get("measures", {}).keys())[:10])
        
        system_prompt = f"""You are a helpful assistant for a medical radiology audit analytics system.

Medical Radiology Context:
- Modalities: CT, MRI
- Key Metrics: Quality Score (Q1-Q17), Safety Score, Star Rating (1-5), Turnaround Time (TAT)
- CAT Ratings: 
  - CAT1: Good (concurrence)
  - CAT2: Minor discrepancy (no clinical impact)
  - CAT3: Moderate discrepancy (possible impact)
  - CAT4: Major discrepancy (clinical impact)
  - CAT5: Severe discrepancy (critical impact)
- Goals: Monitor diagnostic quality, improve patient safety, optimize radiologist performance

Available Data Schema:
- Dimensions (for grouping/filtering): {dimensions_list}, and more...
- Metrics (for calculations): {metrics_list}, and more...

When users ask meta-questions like "What data?", explain these metrics and the medical context clearly.
Query the database to get actual counts - do not assume specific numbers.

Example questions to suggest:
- "What is the average quality score by modality?"
- "Which radiologist has the most CAT5 cases?"
- "Show me the distribution of star ratings"
- "How does quality compare between CT and MRI?"
- "What are the common issues in CAT4 cases?"
- "Show audits by time of day"

Be friendly and concise. Explain capabilities clearly without overwhelming the user.
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        if context:
            messages.insert(1, {"role": "assistant", "content": f"Previous context: {context}"})

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=200
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "Hello! I can help you analyze radiology audit data. Try asking about quality scores, CAT ratings, or radiologist performance."

    async def suggest_followup_questions(
        self,
        user_question: str,
        response_data: dict
    ) -> list[str]:
        """Generate relevant follow-up questions based on the current query."""
        suggestions = []

        # Pattern-based suggestions for medical radiology domain
        if "quality" in user_question.lower() or "score" in user_question.lower():
            suggestions.extend([
                "How does safety score correlate with quality?",
                "What's the average quality score by radiologist?",
                "Show me the trend of quality scores"
            ])

        if "cat" in user_question.lower() or "rating" in user_question.lower():
            suggestions.extend([
                "Which modality has the most CAT5 cases?",
                "Show me the distribution of CAT ratings",
                "What are the common causes for CAT4?"
            ])

        if "radiologist" in user_question.lower():
            suggestions.extend([
                "Compare radiologist performance metrics",
                "Who has the highest safety score?",
                "Show audit counts per radiologist"
            ])

        if "modality" in user_question.lower() or "ct" in user_question.lower() or "mri" in user_question.lower():
            suggestions.extend([
                "Compare quality scores between CT and MRI",
                "What's the CAT rating breakdown for CT?",
                "Show me the audit volume by modality"
            ])

        if "tat" in user_question.lower() or "time" in user_question.lower():
            suggestions.extend([
                "What's the average turnaround time?",
                "How does TAT vary by time of day?",
                "Show me the relationship between TAT and quality"
            ])

        if "body part" in user_question.lower():
            suggestions.extend([
                "Which body part category has the lowest quality score?",
                "Compare safety scores by body part",
                "Show audit volume by body part"
            ])

        # Default suggestions if none matched
        if not suggestions:
            suggestions = [
                "What is the average quality score?",
                "Show me the distribution of CAT ratings",
                "How many audits were conducted?",
                "Compare performance by modality"
            ]

        return suggestions[:3]  # Return max 3 suggestions


# Global agent instance
chat_agent = ChatAgent()
