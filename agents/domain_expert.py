"""
Domain Expert Agent.

Medical radiology domain expert that translates user queries into structured requests.
Enriches queries with domain knowledge and routes them to Analytics Specialist.
"""
import json
import logging
import os
from typing import Dict, List, Any
from praval import agent, broadcast, Spore, Agent  # Import Agent to explicitly set provider
from async_utils import run_async
from schemas.radiology import RADIOLOGY_DATA_SCHEMA

logger = logging.getLogger(__name__)

# Load Groq credentials from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL")

if not GROQ_API_KEY or not GROQ_MODEL or not GROQ_BASE_URL:
    raise ValueError("Groq credentials not set. Please set GROQ_API_KEY, GROQ_MODEL, GROQ_BASE_URL.")

class DomainExpertAgent:
    """
    Domain Expert Agent.
    
    Translates natural language queries into domain-enriched requests
    with cube recommendations, metrics, dimensions, and filters.
    """
    
    def __init__(self):
        """Initialize the Domain Expert Agent with Groq."""
        self.agent = Agent(
            name="domain_expert",
            provider="groq",            # Explicitly tell Praval to use Groq
            model=GROQ_MODEL,
            api_key=GROQ_API_KEY,
            base_url=GROQ_BASE_URL,
            knowledge_base=None          # If you have a knowledge base, set it here
        )
        logger.info("Domain Expert Agent initialized with Groq/Kimi K2")
    
    async def analyze_query(self, message: str, context: List[Dict[str, str]], session_id: str) -> Dict[str, Any]:
        """
        Analyze user query and create domain-enriched request.
        """
        prompt = f"""You are an intelligent analytics assistant for a medical radiology audit system. Your job is to understand user questions and map them to the correct data query.

USER QUESTION: "{message}"

AVAILABLE DATA SCHEMA:
{RADIOLOGY_DATA_SCHEMA}

OUTPUT FORMAT (JSON only):
{{
    "is_rejected": false,
    "rejection_reason": null,
    "cube_recommendation": "RadiologyAudits",
    "metrics": ["count", "avgSafetyScore"],
    "dimensions": [],
    "filters": {{}},
    "time_range": null,
    "analysis_type": "summary",
    "user_message": "{message}"
}}

Output ONLY the JSON response.
"""
        try:
            # Use Praval Agent's `ask` method for Groq
            response = await self.agent.ask(prompt)
            
            result = json.loads(response) if isinstance(response, str) else response

            # Ensure metrics/dimensions are normalized (same as your original logic)
            validated_dimensions = result.get("dimensions", [])
            validated_metrics = result.get("metrics", ["count"])

            enriched_request = {
                "type": "domain_enriched_request",
                "is_rejected": result.get("is_rejected", False),
                "rejection_reason": result.get("rejection_reason"),
                "cube_recommendation": result.get("cube_recommendation", "RadiologyAudits"),
                "metrics": validated_metrics,
                "dimensions": validated_dimensions,
                "filters": result.get("filters", {}),
                "time_range": result.get("time_range"),
                "part_families": [],
                "analysis_type": result.get("analysis_type", "summary"),
                "user_message": message,
                "session_id": session_id,
            }
            return enriched_request

        except Exception as e:
            logger.error(f"Error analyzing query: {e}")
            return {
                "type": "domain_enriched_request",
                "is_rejected": False,
                "rejection_reason": None,
                "cube_recommendation": "RadiologyAudits",
                "metrics": ["count"],
                "dimensions": [],
                "filters": {},
                "time_range": None,
                "part_families": [],
                "analysis_type": "summary",
                "user_message": message,
                "session_id": session_id,
            }

# Praval agent decorator with explicit provider
@agent(
    "domain_expert",
    provider="groq",  # Force Groq provider
    responds_to=["user_query"],
    system_message="You are a medical radiology domain expert who translates natural language queries into structured analytical requests.",
    auto_broadcast=False
)
def domain_expert_handler(spore: Spore):
    logger.info(f"Domain Expert received spore: {spore.id}")

    knowledge = spore.knowledge
    message = knowledge.get("message", "")
    context = knowledge.get("context", [])
    session_id = knowledge.get("session_id", "")

    expert = DomainExpertAgent()
    enriched_request = run_async(expert.analyze_query(message, context, session_id))

    logger.info(f"Broadcasting domain_enriched_request: cube={enriched_request.get('cube_recommendation')}, metrics={enriched_request.get('metrics')}")
    broadcast(enriched_request)
