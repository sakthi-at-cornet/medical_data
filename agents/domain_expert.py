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
from schemas.radiology import RADIOLOGY_DATA_SCHEMA

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
        prompt = f"""You are an intelligent analytics assistant for a medical radiology audit system. Your job is to understand user questions and map them to the correct data query.

USER QUESTION: "{message}"

AVAILABLE DATA SCHEMA:
{RADIOLOGY_DATA_SCHEMA}

COMMON TERM MAPPINGS:
- "doctor", "radiologist", "physician", "RAD" → dimension "originalRadiologist"
- "hospital", "location", "unit", "center" → dimension "unitIdentifier" 
- "body part", "anatomy" → dimension "bodyPartCategory"
- "modality", "scan type" → dimension "modality"
- "CAT", "rating", "category" → dimension "finalOutput"
- "gender", "male", "female" → dimension "gender"

SPECIAL METRICS FOR CONDITIONS:
- "safety score above 80", "high safety" → use metric "highSafetyCount" (counts cases with safety > 80)
- "quality score above 70" → use metric "highQualityCount" (counts cases with quality > 70)
- "quality score below 60", "low quality" → use metric "lowQualityCount"
- "percentage with high safety" → use metric "highSafetyRate"

QUERY PATTERNS:
1. "top/best [entity]" → dimensions: [entity], metrics: ["count", "avgQualityScore"]
2. "[entity] with high safety / safety above 80" → dimensions: [entity], metrics: ["count", "highSafetyCount", "avgSafetyScore"]
3. "highest volume with safety above 80" → dimensions: [entity], metrics: ["count", "highSafetyCount"]
4. "distribution of [entity]" → dimensions: [entity], metrics: ["count"]
5. "compare [entity]" → dimensions: [entity], metrics: ["count", "avgQualityScore"]

IMPORTANT RULES:
- ALWAYS include "count" as a metric
- For "safety score above 80", use the "highSafetyCount" metric, NOT a filter
- For performance questions, include both "count" and relevant avg score
- "radiologists with highest volume AND safety above 80" = dimensions: ["originalRadiologist"], metrics: ["count", "highSafetyCount", "avgSafetyScore"]

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

Output ONLY the JSON response."""


        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Validate and normalize dimensions - these are the valid dimension names
            valid_dimensions = {
                "caseId", "srNo", "modality", "subSpecialty", "bodyPartCategory", 
                "bodyPart", "studyDescription", "scanType", "instituteName", 
                "unitIdentifier", "originalRadiologist", "reviewer", "secondReview",
                "finalOutput", "starRating", "gender", "ageCohort", "age",
                "unableToAudit", "requiredReaudit", "comments", "reportDate",
                "scanDate", "uploadDate", "assignDate", "reviewDate"
            }
            
            # Normalize common dimension variations
            dimension_aliases = {
                "cat_rating": "finalOutput", "cat": "finalOutput", "catRating": "finalOutput",
                "quality_category": "finalOutput", "peerReviewCategory": "finalOutput",
                "body_part": "bodyPart", "body_part_category": "bodyPartCategory",
                "sub_specialty": "subSpecialty", "subspecialty": "subSpecialty",
                "radiologist": "originalRadiologist", "original_radiologist": "originalRadiologist",
                "institute": "instituteName", "hospital": "instituteName",
                "age_cohort": "ageCohort", "ageGroup": "ageCohort", "age_group": "ageCohort",
                "star": "starRating", "stars": "starRating",
                "scan_type": "scanType", "imaging_type": "modality",
                "sex": "gender", "patient_gender": "gender",
            }
            
            # Validate and fix dimensions
            raw_dimensions = result.get("dimensions", [])
            validated_dimensions = []
            for dim in raw_dimensions:
                if dim in valid_dimensions:
                    validated_dimensions.append(dim)
                elif dim in dimension_aliases:
                    validated_dimensions.append(dimension_aliases[dim])
                    logger.info(f"Normalized dimension '{dim}' → '{dimension_aliases[dim]}'")
                else:
                    logger.warning(f"Unknown dimension '{dim}' from LLM, skipping")
            
            # Validate and normalize metrics
            valid_metrics = {
                "count", "avgQualityScore", "avgSafetyScore", "avgProductivityScore",
                "avgEfficiencyScore", "avgStarScore", "avgStarRating", "avgAge",
                "avgAssignTat", "avgReviewTat", "cat1Count", "cat2Count", "cat3Count",
                "cat4Count", "cat5Count", "highQualityRate", "reauditCount",
                "avgQ1", "avgQ2", "avgQ3", "avgQ4", "avgQ5", "avgQ6", "avgQ7",
                "avgQ8", "avgQ9", "avgQ10", "avgQ11", "avgQ12Q", "avgQ12S",
                "avgQ13", "avgQ14", "avgQ15", "avgQ16", "avgQ17"
            }
            
            metric_aliases = {
                "total": "count", "cases": "count", "number": "count",
                "quality_score": "avgQualityScore", "quality": "avgQualityScore",
                "safety_score": "avgSafetyScore", "safety": "avgSafetyScore",
                "productivity_score": "avgProductivityScore", "productivity": "avgProductivityScore",
                "efficiency_score": "avgEfficiencyScore", "efficiency": "avgEfficiencyScore",
                "star_rating": "avgStarRating", "stars": "avgStarRating",
                "avg_age": "avgAge", "average_age": "avgAge",
            }
            
            raw_metrics = result.get("metrics", ["count"])
            validated_metrics = []
            for metric in raw_metrics:
                if metric in valid_metrics:
                    validated_metrics.append(metric)
                elif metric in metric_aliases:
                    validated_metrics.append(metric_aliases[metric])
                    logger.info(f"Normalized metric '{metric}' → '{metric_aliases[metric]}'")
                else:
                    logger.warning(f"Unknown metric '{metric}' from LLM, defaulting to 'count'")
                    if "count" not in validated_metrics:
                        validated_metrics.append("count")
            
            # Ensure at least one metric
            if not validated_metrics:
                validated_metrics = ["count"]
            
            logger.info(f"Domain analysis: query='{message[:50]}...', "
                       f"metrics={validated_metrics}, dimensions={validated_dimensions}, "
                       f"filters={result.get('filters', {})}")
            
            # Build domain_enriched_request
            enriched_request = {
                "type": "domain_enriched_request",
                "is_rejected": result.get("is_rejected", False),
                "rejection_reason": result.get("rejection_reason"),
                "cube_recommendation": result.get("cube_recommendation", "RadiologyAudits"),
                "metrics": validated_metrics,
                "dimensions": validated_dimensions,
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
    
    # Extract knowledge from spores
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
