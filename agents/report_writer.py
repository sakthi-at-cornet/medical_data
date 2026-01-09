"""
Report Writer Agent.

Technical writer who creates executive summaries and data narratives.
Combines chart and insights into final response (session correlation).
"""
import json
import logging
from typing import Dict, List, Any, Optional
from praval import agent, broadcast, Spore
from openai import AsyncOpenAI
from config import settings
from async_utils import run_async

logger = logging.getLogger(__name__)

# Session correlation storage
# {session_id: {"chart": chart_spec, "insights": insights_knowledge}}
_session_data: Dict[str, Dict[str, Any]] = {}

# Pending responses for app.py endpoint to retrieve
# {session_id: final_response_knowledge}
_pending_responses: Dict[str, Dict[str, Any]] = {}


# Response storage agent - listens for final_response_ready and stores for HTTP endpoint
@agent(
    "response_storage",
    responds_to=["final_response_ready"],
    system_message="Storage agent for HTTP endpoint responses",
    auto_broadcast=False
)
def response_storage_handler(spore: Spore):
    """
    Store final responses for HTTP endpoint retrieval.
    This agent listens to final_response_ready broadcasts from any source.
    """
    global _pending_responses

    knowledge = spore.knowledge
    session_id = knowledge.get("session_id", "")

    logger.info(f"Response Storage received final_response_ready for session {session_id}")

    # Store the response
    _pending_responses[session_id] = knowledge
    logger.info(f"Stored response for session {session_id}")


class ReportWriterAgent:
    """
    Report Writer Agent.

    Composes final narrative response by combining chart and insights.
    """

    def __init__(self):
        """Initialize the Report Writer Agent."""
        self.client = AsyncOpenAI(
            api_key=settings.groq_api_key,
            base_url=settings.groq_base_url
        )
        self.model = settings.groq_model
        logger.info("Report Writer Agent initialized with Groq/Kimi K2")

    async def compose_narrative(
        self,
        chart_spec: Dict[str, Any],
        insights: Dict[str, Any],
        session_id: str
    ) -> Dict[str, Any]:
        """
        Compose final narrative from chart and insights.

        Args:
            chart_spec: Chart specification from Visualization Specialist
            insights: Insights from Quality Inspector
            session_id: Session identifier

        Returns:
            final_response_ready knowledge payload
        """
        observations = insights.get("observations", [])
        anomalies = insights.get("anomalies", [])
        root_causes = insights.get("root_causes", [])

        # Build narrative prompt
        # Build narrative prompt
        prompt = f"""You are a medical data analyst creating a data narrative for radiology audits.

Chart Type: {chart_spec.get('type', 'unknown')}
Number of Data Points: {len(chart_spec.get('data', {}).get('labels', []))}

Insights:
Observations ({len(observations)}):
{self._format_observations(observations)}

Anomalies ({len(anomalies)}):
{self._format_anomalies(anomalies)}

Root Causes ({len(root_causes)}):
{self._format_root_causes(root_causes)}

Compose a clear, actionable narrative following this structure:

🔍 Key Findings:
• [3-5 bullet points highlighting the most important observations from the data]
• Use specific numbers and percentages
• Focus on comparisons, trends, and quality differences

🔧 Root Causes:
• [2-3 bullet points explaining WHY these patterns exist, based strictly on the data]
• Connect to radiology factors (modality complexity, radiologist expertise, scan types, etc.)
• Only include if root causes were identified in the data

💡 Recommended Actions:
• [2-3 bullet points with specific next steps for the radiology department]
• Be concrete and actionable (e.g., "Review training for X scan type", "Audit high-volume radiologists")

Guidelines:
- Use clear, professional medical/technical language
- ABSOLUTELY NO manufacturing terminology (no "die wear", "press line", "material grade", "OEE", etc.)
- Focus on: Quality Scores, Safety Scores, Turnaround Times (TAT), CAT Ratings, Radiologist Performance, Modalities
- Start with the most important findings
- Include context (e.g., "12% higher error rate" not just "5 errors")
- Be concise (3-5 sentences per section)
- Skip sections if no relevant insights

Respond with ONLY the narrative text (no JSON, no extra formatting).
"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=800,
            )

            narrative = response.choices[0].message.content.strip()
            logger.info(f"Composed narrative ({len(narrative)} chars)")

            # Use LLM to generate contextual follow-up questions
            chart_type = chart_spec.get("type", "unknown")
            follow_ups = await self._generate_follow_ups(
                observations, root_causes, chart_type, narrative
            )

            return {
                "type": "final_response_ready",
                "narrative": narrative,
                "chart_spec": chart_spec,
                "follow_ups": follow_ups,
                "session_id": session_id,
            }

        except Exception as e:
            logger.error(f"Error composing narrative: {e}")
            # Fallback: create simple narrative from insights
            narrative = self._create_fallback_narrative(observations, anomalies, root_causes)

            return {
                "type": "final_response_ready",
                "narrative": narrative,
                "chart_spec": chart_spec,
                "follow_ups": [],
                "session_id": session_id,
            }

    def _format_observations(self, observations: List[Dict[str, Any]]) -> str:
        """Format observations for prompt."""
        if not observations:
            return "  None"

        lines = []
        for i, obs in enumerate(observations, 1):
            text = obs.get("text", "")
            confidence = obs.get("confidence", 0.0)
            lines.append(f"  {i}. {text} (confidence: {confidence:.2f})")

        return "\n".join(lines)

    def _format_anomalies(self, anomalies: List[Dict[str, Any]]) -> str:
        """Format anomalies for prompt."""
        if not anomalies:
            return "  None"

        lines = []
        for i, anom in enumerate(anomalies, 1):
            entity = anom.get("entity", "")
            metric = anom.get("metric", "")
            severity = anom.get("severity", "")
            description = anom.get("description", "")
            lines.append(f"  {i}. [{severity.upper()}] {entity} - {metric}: {description}")

        return "\n".join(lines)

    def _format_root_causes(self, root_causes: List[Dict[str, Any]]) -> str:
        """Format root causes for prompt."""
        if not root_causes:
            return "  None"

        lines = []
        for i, rc in enumerate(root_causes, 1):
            hypothesis = rc.get("hypothesis", "")
            confidence = rc.get("confidence", 0.0)
            action = rc.get("recommended_action", "")
            lines.append(f"  {i}. {hypothesis} (confidence: {confidence:.2f})")
            if action:
                lines.append(f"     → Action: {action}")

        return "\n".join(lines)

    async def _generate_follow_ups(
        self,
        observations: List[Dict[str, Any]],
        root_causes: List[Dict[str, Any]],
        chart_type: str,
        narrative: str
    ) -> List[str]:
        """
        Use LLM to generate contextual follow-up question suggestions.

        Args:
            observations: Observation insights
            root_causes: Root cause hypotheses
            chart_type: Type of chart displayed
            narrative: The narrative that was generated

        Returns:
            List of follow-up question strings
        """
        # Build context for LLM
        context_parts = []

        if observations:
            context_parts.append(f"Key observations: {', '.join([obs.get('text', '') for obs in observations[:2]])}")

        if root_causes:
            context_parts.append(f"Root causes identified: {', '.join([rc.get('hypothesis', '') for rc in root_causes[:2]])}")

        context_parts.append(f"Chart type shown: {chart_type}")

        context = "\n".join(context_parts)

        prompt = f"""You are helping users explore medical radiology audit data. Based on the current analysis, suggest 3 logical follow-up questions.

Current Analysis:
{context}

Narrative shown to user:
{narrative}

Available data includes (448 audit records):
- Quality Scores, Safety Scores, Star Ratings (numeric metrics)
- CAT Ratings (CAT1-CAT5 final output) - AVAILABLE
- Modalities: CT (233), MRI (214) - AVAILABLE
- Gender: Male (197), Female (251) - AVAILABLE
- Body Part Category: NEURO, SPINE, ABDOMEN/PELVIS, etc. - AVAILABLE
- Sub-specialty: Neuro, Body, MSK, etc. - AVAILABLE
- Age: Patient ages (126 under 25, 322 over 25) - AVAILABLE
- NOTE: Radiologist names are NOT available in this dataset

Generate 3 specific, actionable follow-up questions that:
1. Drill deeper into findings (e.g., if showing modality, suggest body part breakdown)
2. Explore related metrics (e.g., if showing quality, suggest safety score or CAT rating)
3. Investigate demographics (e.g., compare by gender or age group)

IMPORTANT: Do NOT suggest radiologist-related questions as that data is not available.

Respond with JSON:
{{
    "follow_ups": ["question 1", "question 2", "question 3"]
}}

Make questions natural and specific to the current analysis."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.4,
                max_tokens=200,
            )

            result = json.loads(response.choices[0].message.content)
            return result.get("follow_ups", [])[:3]

        except Exception as e:
            logger.error(f"Error generating follow-ups: {e}")
            # Fallback to generic suggestions that work with available data
            return [
                "Compare quality scores between CT and MRI",
                "Show the CAT rating distribution",
                "How many male vs female patients?"
            ]

    def _create_fallback_narrative(
        self,
        observations: List[Dict[str, Any]],
        anomalies: List[Dict[str, Any]],
        root_causes: List[Dict[str, Any]]
    ) -> str:
        """Create simple fallback narrative if LLM fails."""
        lines = []

        lines.append("🔍 Key Findings:")
        if observations:
            for obs in observations[:3]:
                lines.append(f"• {obs.get('text', '')}")
        else:
            lines.append("• Data retrieved successfully")

        if root_causes:
            lines.append("\n🔧 Root Causes:")
            for rc in root_causes[:2]:
                lines.append(f"• {rc.get('hypothesis', '')}")

        if anomalies:
            lines.append("\n⚠️ Anomalies Detected:")
            for anom in anomalies[:2]:
                lines.append(f"• {anom.get('description', '')}")

        return "\n".join(lines)


# Praval agent decorator
@agent(
    "report_writer",
    responds_to=["chart_ready", "insights_ready"],
    system_message="You are a medical technical writer creating clear, actionable data narratives for radiology analytics.",
    auto_broadcast=False
)
def report_writer_handler(spore: Spore):
    """
    Handle chart_ready and insights_ready Spores.
    Implements session correlation - waits for BOTH before composing.

    Args:
        spore: Spore with chart_ready or insights_ready knowledge
    """
    import asyncio

    global _session_data

    logger.info(f"Report Writer received spore: {spore.id}")

    # Extract knowledge from spore
    knowledge = spore.knowledge
    spore_type = knowledge.get("type")
    session_id = knowledge.get("session_id", "")

    logger.info(f"Processing {spore_type} (session {session_id})")

    # Initialize session data if needed
    if session_id not in _session_data:
        _session_data[session_id] = {
            "chart": None,
            "insights": None,
        }

    # Accumulate data based on spore type
    if spore_type == "chart_ready":
        # Store full chart specification from Visualization Specialist
        _session_data[session_id]["chart"] = knowledge.get("chart_spec", {"type": "unknown"})
        logger.info(f"Received chart_ready for session {session_id}")

    elif spore_type == "insights_ready":
        _session_data[session_id]["insights"] = knowledge
        _session_data[session_id]["is_rejected"] = knowledge.get("is_rejected", False)
        logger.info(f"Received insights_ready for session {session_id}")

    # Check if we have BOTH chart and insights
    session = _session_data.get(session_id, {})
    has_chart = session.get("chart") is not None
    has_insights = session.get("insights") is not None

    if has_chart and has_insights:
        logger.info(f"Session {session_id}: Have BOTH chart and insights, composing final response")

        # Initialize writer
        writer = ReportWriterAgent()

        # Check if rejected query
        is_rejected = session.get("is_rejected", False)

        if is_rejected:
            logger.info(f"Rejected query - generating rejection response")
            rejection_reason = session["insights"].get("rejection_reason", "Query out of scope")
            final_response = {
                "type": "final_response_ready",
                "narrative": f"I can only answer questions about medical radiology audit data. {rejection_reason}\n\nPlease ask about:\n• Quality Metrics (Quality Scores, Safety Scores, Star Ratings)\n• CAT Ratings (CAT1-CAT5)\n• Radiologist Performance\n• Modality Analysis (CT, MRI)\n• Turnaround Times",
                "chart_spec": None,
                "follow_ups": [
                    "What's the average quality score by modality?",
                    "Show me the CAT rating distribution"
                ],
                "session_id": session_id,
            }
        else:
            # All in-scope queries - compose narrative with LLM
            final_response = run_async(writer.compose_narrative(
                chart_spec=session["chart"],
                insights=session["insights"],
                session_id=session_id
            ))

        # Store response for app.py endpoint to retrieve
        global _pending_responses
        _pending_responses[session_id] = final_response
        logger.info(f"Stored final_response in _pending_responses for session {session_id}")

        # Broadcast final_response_ready
        logger.info(f"Broadcasting final_response_ready for session {session_id}")
        broadcast(final_response)

        # Cleanup session data
        del _session_data[session_id]
        logger.info(f"Cleaned up session data for {session_id}")

    else:
        logger.info(f"Session {session_id}: Waiting for {'insights' if has_chart else 'chart'}")

    return
