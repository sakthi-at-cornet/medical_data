"""
Domain Expert Agent.

Medical radiology domain expert that translates user queries into structured requests.
Enriches queries with domain knowledge and routes them to Analytics Specialist.
"""
import json
import logging
from typing import Dict, List, Any
from praval import agent, broadcast, Spore
from openai import AsyncOpenAI
from config import settings
from async_utils import run_async

logger = logging.getLogger(__name__)


class DomainExpertAgent:
    """
    Domain Expert Agent.
    
    Translates natural language queries into domain-enriched requests
    with cube recommendations, metrics, dimensions, and filters.
    """
    
    def __init__(self):
        """Initialize the Domain Expert Agent."""
        self.client = AsyncOpenAI(
            api_key=settings.groq_api_key,
            base_url=settings.groq_base_url
        )
        self.model = settings.groq_model
        logger.info("Domain Expert Agent initialized with Groq/Kimi K2")
    
    async def analyze_query(self, message: str, context: List[Dict[str, str]], session_id: str) -> Dict[str, Any]:
        """
        Analyze user query and create domain-enriched request.
        
        Args:
            message: User's natural language query
            context: Conversation context
            session_id: Session identifier
            
        Returns:
            domain_enriched_request knowledge payload
        """
        prompt = f"""You are a medical radiology domain expert. Analyze this query and generate a structured analytical request.

User Query: "{message}"

Available Data Schema:

Cube: RadiologyAudits (448 total audit records with patient demographics and quality scores)

Dimensions (group by / filter):
- modality: "CT" or "MRI" (imaging type)
- subSpecialty: Neuroradiology, Musculoskeletal, GI, etc.
- bodyPartCategory: "NEURO", "ABDOMEN/PELVIS", "SPINE", "MSK", "HEAD AND NECK", "CHEST", etc.
- bodyPart: Specific body parts like "Brain", "Pelvis", "Spine", etc.
- originalRadiologist: Name of reporting radiologist
- reviewer: Name of reviewing radiologist
- finalOutput: CAT rating ("CAT1", "CAT2", "CAT3", "CAT4", "CAT5")
- starRating: Star rating (1-5)
- gender: "Male" or "Female" (patient gender)
- ageCohort: Age group like "Adult", "Pediatric", "Geriatric"
- age: Patient age (numeric, use for filtering like age < 25, age > 60)
- scanType: Type of scan
- instituteName: Hospital/clinic name

Measures (metrics to calculate):
- count: Total number of audits/patients
- avgQualityScore: Average quality score (typically 0-100)
- avgSafetyScore: Average safety score (typically 0-100)
- avgProductivityScore: Average productivity score
- avgEfficiencyScore: Average efficiency score
- avgStarRating: Average star rating (1-5)
- cat5Count, cat4Count, cat3Count, cat2Count, cat1Count: Count by CAT rating
- avgAge: Average patient age

IMPORTANT RULES:
1. For radiology/medical audit/patient data questions, set is_rejected=false
2. For completely unrelated questions (weather, sports, etc.), set is_rejected=true
3. Always use "RadiologyAudits" as the cube
4. For age-related filters like "under 25", "less than 25", "below 25":
   - Use filters with "age" dimension and "lt" (less than) operator
5. For gender questions: use dimension "gender"
6. For "how many" or counting questions: use metric "count"

FILTER OPERATORS:
- "lt": less than (e.g., age < 25)
- "gt": greater than (e.g., age > 60)
- "lte": less than or equal
- "gte": greater than or equal
- "equals": exact match

Respond with JSON:
{{
    "is_rejected": false,
    "rejection_reason": null,
    "cube_recommendation": "RadiologyAudits",
    "metrics": ["count"],
    "dimensions": [],
    "filters": {{"age": {{"operator": "lt", "value": 25}}}},
    "time_range": null,
    "analysis_type": "summary",
    "user_message": "{message}"
}}

Example mappings:
- "How many patients under 25?" → metrics: ["count"], dimensions: [], filters: {{"age": {{"operator": "lt", "value": 25}}}}
- "How many patients age less than 25?" → metrics: ["count"], dimensions: [], filters: {{"age": {{"operator": "lt", "value": 25}}}}
- "Patients over 60" → metrics: ["count"], dimensions: ["ageCohort"], filters: {{"age": {{"operator": "gt", "value": 60}}}}
- "Compare quality scores between CT and MRI" → metrics: ["avgQualityScore"], dimensions: ["modality"], filters: {{}}
- "Show CAT rating distribution" → metrics: ["count"], dimensions: ["finalOutput"], filters: {{}}
- "Male vs female patients" → metrics: ["count"], dimensions: ["gender"], filters: {{}}
- "Total audit count" → metrics: ["count"], dimensions: [], filters: {{}}
- "Average age of patients" → metrics: ["avgAge"], dimensions: [], filters: {{}}
- "Quality by body part" → metrics: ["avgQualityScore"], dimensions: ["bodyPartCategory"], filters: {{}}
"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"Domain analysis result: cube={result.get('cube_recommendation')}, "
                       f"metrics={result.get('metrics')}, dimensions={result.get('dimensions')}")
            
            # Build domain_enriched_request
            enriched_request = {
                "type": "domain_enriched_request",
                "is_rejected": result.get("is_rejected", False),
                "rejection_reason": result.get("rejection_reason"),
                "cube_recommendation": result.get("cube_recommendation", "RadiologyAudits"),
                "metrics": result.get("metrics", ["count"]),
                "dimensions": result.get("dimensions", []),
                "filters": result.get("filters", {}),
                "time_range": result.get("time_range"),
                "part_families": [],  # Legacy field, kept for compatibility
                "analysis_type": result.get("analysis_type", "summary"),
                "user_message": message,
                "session_id": session_id,
            }
            
            return enriched_request
            
        except Exception as e:
            logger.error(f"Error analyzing query: {e}")
            # Return fallback enriched request
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


# Praval agent decorator
@agent(
    "domain_expert",
    responds_to=["user_query"],
    system_message="You are a medical radiology domain expert who translates natural language queries into structured analytical requests.",
    auto_broadcast=False
)
def domain_expert_handler(spore: Spore):
    """
    Handle user_query Spores and translate to domain-enriched requests.
    
    Args:
        spore: Spore with user_query knowledge
    """
    logger.info(f"Domain Expert received spore: {spore.id}")
    
    # Extract knowledge from spore
    knowledge = spore.knowledge
    message = knowledge.get("message", "")
    context = knowledge.get("context", [])
    session_id = knowledge.get("session_id", "")
    
    logger.info(f"Processing user_query (session {session_id}): {message}")
    
    # Initialize expert
    expert = DomainExpertAgent()
    
    # Analyze query and create domain-enriched request
    enriched_request = run_async(expert.analyze_query(message, context, session_id))
    
    # Broadcast domain_enriched_request for Analytics Specialist
    logger.info(f"Broadcasting domain_enriched_request: "
               f"cube={enriched_request.get('cube_recommendation')}, "
               f"metrics={enriched_request.get('metrics')}")
    broadcast(enriched_request)
    
    return
