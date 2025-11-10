"""Chat Agent: Manages conversation context and coordinates responses."""
import logging
from typing import Optional
from openai import AsyncOpenAI
from models import ChatMessage
from config import settings

logger = logging.getLogger(__name__)


class ChatAgent:
    """Agent that manages conversation flow and context."""

    def __init__(self):
        """Initialize the Chat Agent."""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

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
        prompt = f"""Determine if this user message requires querying automotive manufacturing analytics data.

User message: "{user_message}"
{f"Context: {context}" if context else ""}

Respond with JSON: {{"requires_data_query": true/false, "reason": "brief explanation"}}

Messages requiring data queries:
- Specific questions about OEE, pass rates, quality metrics, production volumes
- Requests for trends, comparisons, statistics on actual data
- "What is the OEE?", "Show me defect trends", "Compare press lines", "Which shift is most productive?"
- Cost analysis, shift performance, part family comparisons
- "What's the cost per part?", "Show weekend vs weekday production"

Messages NOT requiring data queries (respond conversationally):
- Meta-questions about the system: "What datasets?", "What data is available?", "What can I ask?"
- Schema/capability questions: "What metrics do you track?", "What press lines?", "What part families?"
- Manufacturing domain education: "What is OEE?", "Explain SMED", "What's tonnage?"
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
        system_prompt = """You are a helpful assistant for an automotive press manufacturing analytics system.

Manufacturing Context:
- 2 Press Lines: Line A (800T) produces door outer panels (left/right), Line B (1200T) produces bonnet outer panels
- 3 Part Families: Door_Outer_Left, Door_Outer_Right, Bonnet_Outer
- Material Grades: CRS_SPCC (cold rolled steel), HSLA_350, DP600 (high-strength steels)
- Process: High-speed stamping with cycle times of 1.2-2.0 seconds per part
- Quality Focus: OEE (Overall Equipment Effectiveness), defect analysis, first pass yield

Available Data Sources:
• PressOperations: Production-level data with full traceability
  - Metrics: pass rate, OEE (availability, performance, quality rate), tonnage, cycle time, costs (material/labor/energy)
  - Dimensions: part family, press line, die, material grade, coil, shift, operator, defect type
  - Use for: Root cause analysis, shift performance, die/coil traceability, defect patterns

• PartFamilyPerformance: Aggregated performance by part type
  - Metrics: first pass yield, rework rate, OEE components, cost per part, material correlation (coil defect rate, yield/tensile strength)
  - Dimensions: part family (Door Left/Right vs Bonnet), part type, material grade
  - Use for: Part family comparison, material grade optimization, cost analysis

• PressLineUtilization: Press line capacity and shift analysis
  - Metrics: overall OEE, shift productivity (morning/afternoon/night), weekend vs weekday production, utilization rate (parts/day)
  - Dimensions: press line (Line A vs Line B), part type
  - Use for: Capacity planning, shift optimization, line comparison

When users ask meta-questions like "What datasets?" or "What can I ask?", explain these data sources and automotive context clearly.

Example questions to suggest:
- "What's the OEE for each press line?"
- "Which part family has the best quality?"
- "Show me defect trends over time"
- "Compare shift performance"
- "Which material grade performs better?"
- "What's the cost per part by line?"
- "Show me weekend vs weekday production"
- "Which defect types are most common?"

Be friendly and concise. If asked about capabilities, explain what manufacturing data we track without overwhelming the user.
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
            return "Hello! I can help you analyze manufacturing data. Try asking about pass rates, quality, or production trends."

    async def suggest_followup_questions(
        self,
        user_question: str,
        response_data: dict
    ) -> list[str]:
        """Generate relevant follow-up questions based on the current query."""
        suggestions = []

        # Pattern-based suggestions for automotive manufacturing domain
        if "oee" in user_question.lower() or "efficiency" in user_question.lower():
            suggestions.extend([
                "What's the OEE breakdown (availability, performance, quality)?",
                "Compare OEE by shift",
                "Show me OEE trends over time"
            ])

        if "pass rate" in user_question.lower() or "quality" in user_question.lower():
            suggestions.extend([
                "Which defect types are most common?",
                "What's the first pass yield by part family?",
                "Show me quality trends over time"
            ])

        if "part" in user_question.lower() or "door" in user_question.lower() or "bonnet" in user_question.lower():
            suggestions.extend([
                "Compare cost per part across part families",
                "Which part family has the best OEE?",
                "Show me production volumes by part"
            ])

        if "line" in user_question.lower() or "press" in user_question.lower():
            suggestions.extend([
                "Compare Line A vs Line B utilization",
                "What's the shift performance on each line?",
                "Show me weekend vs weekday production"
            ])

        if "shift" in user_question.lower():
            suggestions.extend([
                "Which shift has the highest productivity?",
                "Compare morning, afternoon, and night shift output",
                "What's the quality by shift?"
            ])

        if "cost" in user_question.lower():
            suggestions.extend([
                "Break down costs by material, labor, and energy",
                "Which line has lower cost per part?",
                "Compare costs across part families"
            ])

        if "defect" in user_question.lower():
            suggestions.extend([
                "Which defects require the most rework?",
                "Show me defect trends by part family",
                "What's the defect rate by material grade?"
            ])

        if "material" in user_question.lower() or "coil" in user_question.lower():
            suggestions.extend([
                "Compare material grades by quality",
                "Which coils have the highest defect rate?",
                "What's the yield strength correlation with quality?"
            ])

        if "trend" in user_question.lower() or "time" in user_question.lower():
            suggestions.extend([
                "What's the overall OEE?",
                "Compare part families by quality",
                "Show me shift productivity"
            ])

        # Default suggestions if none matched
        if not suggestions:
            suggestions = [
                "What's the OEE for each press line?",
                "Which part family has the best quality?",
                "Compare shift performance",
                "Show me defect trends over time"
            ]

        return suggestions[:3]  # Return max 3 suggestions


# Global agent instance
chat_agent = ChatAgent()
