"""
Analytics Specialist Agent.

Data analyst specializing in press shop metrics and production analytics.
Translates manufacturing questions into analytical queries and executes them.
"""
import json
import logging
import time
from typing import Dict, List, Any
from praval import agent, broadcast, Spore
from models import CubeQuery
from cubejs_client import cubejs_client
from openai import AsyncOpenAI
from config import settings
from async_utils import run_async

logger = logging.getLogger(__name__)

# Metric to Cube.js measure mapping by cube
METRIC_MAPPING = {
    # Medical Radiology Audits Cube
    "RadiologyAudits": {
        "count": "RadiologyAudits.count",
        "avgQualityScore": "RadiologyAudits.avgQualityScore",
        "quality_score": "RadiologyAudits.avgQualityScore",
        "quality": "RadiologyAudits.avgQualityScore",
        "avgSafetyScore": "RadiologyAudits.avgSafetyScore",
        "safety_score": "RadiologyAudits.avgSafetyScore",
        "safety": "RadiologyAudits.avgSafetyScore",
        "avgProductivityScore": "RadiologyAudits.avgProductivityScore",
        "productivity_score": "RadiologyAudits.avgProductivityScore",
        "productivity": "RadiologyAudits.avgProductivityScore",
        "avgEfficiencyScore": "RadiologyAudits.avgEfficiencyScore",
        "efficiency_score": "RadiologyAudits.avgEfficiencyScore",
        "efficiency": "RadiologyAudits.avgEfficiencyScore",
        "avgStarScore": "RadiologyAudits.avgStarScore",
        "star_score": "RadiologyAudits.avgStarScore",
        "avgStarRating": "RadiologyAudits.avgStarRating",
        "star_rating": "RadiologyAudits.avgStarRating",
        "stars": "RadiologyAudits.avgStarRating",
        "cat5Count": "RadiologyAudits.cat5Count",
        "cat5": "RadiologyAudits.cat5Count",
        "cat4Count": "RadiologyAudits.cat4Count",
        "cat4": "RadiologyAudits.cat4Count",
        "cat3Count": "RadiologyAudits.cat3Count",
        "cat3": "RadiologyAudits.cat3Count",
        "cat2Count": "RadiologyAudits.cat2Count",
        "cat2": "RadiologyAudits.cat2Count",
        "cat1Count": "RadiologyAudits.cat1Count",
        "cat1": "RadiologyAudits.cat1Count",
        "highQualityRate": "RadiologyAudits.highQualityRate",
        "high_quality_rate": "RadiologyAudits.highQualityRate",
        "reauditCount": "RadiologyAudits.reauditCount",
        "reaudit_count": "RadiologyAudits.reauditCount",
        "avgAge": "RadiologyAudits.avgAge",
        "avg_age": "RadiologyAudits.avgAge",
        "avg_age": "RadiologyAudits.avgAge",
    },
}

# Dimension mapping by cube
DIMENSION_MAPPING = {
    # Medical Radiology Audits Cube
    "RadiologyAudits": {
        "modality": "RadiologyAudits.modality",
        "sub_specialty": "RadiologyAudits.subSpecialty",
        "subSpecialty": "RadiologyAudits.subSpecialty",
        "subspecialty": "RadiologyAudits.subSpecialty",
        "body_part_category": "RadiologyAudits.bodyPartCategory",
        "bodyPartCategory": "RadiologyAudits.bodyPartCategory",
        "body_part": "RadiologyAudits.bodyPartCategory",
        "bodyPart": "RadiologyAudits.bodyPart",
        "original_radiologist": "RadiologyAudits.originalRadiologist",
        "originalRadiologist": "RadiologyAudits.originalRadiologist",
        "radiologist": "RadiologyAudits.originalRadiologist",
        "reviewer": "RadiologyAudits.reviewer",
        "review_radiologist": "RadiologyAudits.reviewer",
        "final_output": "RadiologyAudits.finalOutput",
        "finalOutput": "RadiologyAudits.finalOutput",
        "cat_rating": "RadiologyAudits.finalOutput",
        "cat": "RadiologyAudits.finalOutput",
        "star_rating": "RadiologyAudits.starRating",
        "starRating": "RadiologyAudits.starRating",
        "star": "RadiologyAudits.starRating",
        "gender": "RadiologyAudits.gender",
        "age": "RadiologyAudits.age",
        "age_cohort": "RadiologyAudits.ageCohort",
        "ageCohort": "RadiologyAudits.ageCohort",
        "scan_type": "RadiologyAudits.scanType",
        "scanType": "RadiologyAudits.scanType",
        "institute_name": "RadiologyAudits.instituteName",
        "instituteName": "RadiologyAudits.instituteName",
        "unit_identifier": "RadiologyAudits.unitIdentifier",
        "unitIdentifier": "RadiologyAudits.unitIdentifier",
        "second_review": "RadiologyAudits.secondReview",
        "secondReview": "RadiologyAudits.secondReview",
        "required_reaudit": "RadiologyAudits.requiredReaudit",
        "requiredReaudit": "RadiologyAudits.requiredReaudit",
        "requiredReaudit": "RadiologyAudits.requiredReaudit",
    },
}


class AnalyticsSpecialistAgent:
    """
    Analytics Specialist Agent.

    Translates domain-enriched requests into Cube.js queries and executes them.
    """

    def __init__(self):
        """Initialize the Analytics Specialist Agent."""
        self.client = cubejs_client
        logger.info("Analytics Specialist Agent initialized")

    def build_cube_query(self, enriched_request: Dict[str, Any]) -> CubeQuery:
        """
        Build Cube.js query from domain-enriched request.

        Args:
            enriched_request: Domain-enriched request knowledge

        Returns:
            CubeQuery ready for execution
        """
        cube_recommendation = enriched_request.get("cube_recommendation", "PressOperations")

        # Handle pipe-separated cube recommendations - pick the first valid one
        if "|" in cube_recommendation:
            cube_options = [c.strip() for c in cube_recommendation.split("|")]
            cube_name = cube_options[0]  # Use first cube as default
            logger.info(f"Multiple cubes recommended: {cube_options}, selecting: {cube_name}")
        else:
            cube_name = cube_recommendation

        metrics = enriched_request.get("metrics", [])
        dimensions = enriched_request.get("dimensions", [])
        part_families = enriched_request.get("part_families", [])
        filters_dict = enriched_request.get("filters", {})
        time_range = enriched_request.get("time_range")

        logger.info(f"Building query for cube: {cube_name}")
        logger.info(f"Metrics: {metrics}, Dimensions: {dimensions}, Part Families: {part_families}")

        # Map metrics to Cube.js measures
        measures = []
        metric_map = METRIC_MAPPING.get(cube_name, {})
        for metric in metrics:
            mapped = metric_map.get(metric)
            if mapped:
                measures.append(mapped)
            else:
                logger.warning(f"Metric '{metric}' not found in {cube_name}, skipping")

        # If no measures mapped, use default count from mapping
        if not measures:
            default_count = metric_map.get("count", f"{cube_name}.count")
            measures = [default_count]

        # Map dimensions to Cube.js dimensions
        cube_dimensions = []
        dimension_map = DIMENSION_MAPPING.get(cube_name, {})
        for dim in dimensions:
            mapped = dimension_map.get(dim)
            if mapped:
                cube_dimensions.append(mapped)
            else:
                logger.warning(f"Dimension '{dim}' not found in {cube_name}, skipping")

        # Build filters
        filters = []

        # Add part_family filter if specified
        if part_families:
            part_family_dim = dimension_map.get("part_family")
            if part_family_dim:
                filters.append({
                    "member": part_family_dim,
                    "operator": "equals" if len(part_families) == 1 else "contains",
                    "values": part_families
                })

        # Add custom filters from enriched request
        for key, value in filters_dict.items():
            mapped_dim = dimension_map.get(key)
            if mapped_dim:
                # Handle advanced operator format: {"operator": "lt", "value": 25}
                if isinstance(value, dict) and "operator" in value:
                    op = value.get("operator", "equals")
                    val = value.get("value")
                    filters.append({
                        "member": mapped_dim,
                        "operator": op,
                        "values": [str(val)] if val is not None else []
                    })
                elif isinstance(value, list):
                    filters.append({
                        "member": mapped_dim,
                        "operator": "contains",
                        "values": value
                    })
                else:
                    filters.append({
                        "member": mapped_dim,
                        "operator": "equals",
                        "values": [str(value)]
                    })

        # Build time dimensions if time_range provided
        time_dimensions = []
        if time_range:
            # Assume PressOperations uses productionDate
            time_dim = f"{cube_name}.productionDate"
            time_dimensions.append({
                "dimension": time_dim,
                "dateRange": [time_range.get("start"), time_range.get("end")]
            })

        # Build query
        query = CubeQuery(
            measures=measures,
            dimensions=cube_dimensions if cube_dimensions else None,
            filters=filters if filters else None,
            timeDimensions=time_dimensions if time_dimensions else None,
            limit=1000  # Default limit
        )

        return query

    async def execute_query(self, query: CubeQuery, session_id: str) -> Dict[str, Any]:
        """
        Execute Cube.js query and prepare data_ready Spore.

        Args:
            query: CubeQuery to execute
            session_id: Session identifier

        Returns:
            data_ready knowledge payload
        """
        start_time = time.time()

        try:
            # Execute query
            result = await self.client.execute_query(query)

            # Extract data
            query_results = result.get("data", [])
            row_count = len(query_results)

            # Calculate query time
            query_time_ms = int((time.time() - start_time) * 1000)

            logger.info(f"Query executed successfully: {row_count} rows in {query_time_ms}ms")

            # Analyze data shape for metadata
            metadata = self._analyze_data_shape(query_results, query)

            # Build data_ready Spore knowledge
            data_ready = {
                "type": "data_ready",
                "query_results": query_results,
                "cube_used": self._extract_cube_name(query.measures[0] if query.measures else ""),
                "measures": query.measures or [],
                "dimensions": query.dimensions or [],
                "row_count": row_count,
                "query_time_ms": query_time_ms,
                "session_id": session_id,
                "metadata": metadata,
            }

            return data_ready

        except Exception as e:
            logger.error(f"Query execution error: {str(e)}")
            raise

    def _extract_cube_name(self, measure: str) -> str:
        """Extract cube name from measure (e.g., 'PressOperations.count' → 'PressOperations')."""
        if "." in measure:
            return measure.split(".")[0]
        return "PressOperations"

    def _analyze_data_shape(self, data: List[Dict[str, Any]], query: CubeQuery) -> Dict[str, Any]:
        """
        Analyze data shape to help downstream agents.

        Args:
            data: Query result rows
            query: Original query

        Returns:
            Metadata dictionary
        """
        if not data:
            return {"data_shape": "empty", "row_count": 0}

        metadata = {
            "data_shape": "table",
            "row_count": len(data),
            "column_count": len(data[0].keys()) if data else 0,
            "has_time_series": False,
            "has_multiple_dimensions": False,
            "category_counts": {},
        }

        # Check if time series
        if query.timeDimensions and len(query.timeDimensions) > 0:
            metadata["has_time_series"] = True
            metadata["data_shape"] = "time_series"

        # Check dimension count
        if query.dimensions and len(query.dimensions) > 1:
            metadata["has_multiple_dimensions"] = True

        # Count unique values for each dimension
        if query.dimensions:
            for dim in query.dimensions:
                dim_name = dim.split(".")[-1]  # Get dimension name without cube prefix
                unique_values = set()
                for row in data:
                    # Try both formats: "PressOperations.partFamily" and "partFamily"
                    value = row.get(dim) or row.get(dim_name)
                    if value:
                        unique_values.add(value)
                metadata["category_counts"][dim_name] = len(unique_values)

        return metadata


# Praval agent decorator
@agent(
    "analytics_specialist",
    responds_to=["domain_enriched_request", "query_refinement_needed"],
    system_message="You are a medical data specialist focusing on radiology audit analytics.",
    auto_broadcast=False
)
def analytics_specialist_handler(spore: Spore):
    """
    Handle domain-enriched requests and translate to Cube.js queries.

    Args:
        spore: Spore with domain_enriched_request knowledge
    """
    import asyncio

    logger.info(f"Analytics Specialist received spore: {spore.id}")

    # Extract knowledge from spore
    knowledge = spore.knowledge
    spore_type = knowledge.get("type")
    session_id = knowledge.get("session_id", "")

    logger.info(f"Processing {spore_type} (session {session_id})")

    # Initialize specialist
    specialist = AnalyticsSpecialistAgent()

    if spore_type == "domain_enriched_request":
        is_rejected = knowledge.get("is_rejected", False)

        # Handle rejected queries
        if is_rejected:
            logger.info(f"Query rejected: {knowledge.get('rejection_reason')}")
            broadcast({
                "type": "data_ready",
                "query_results": [],
                "cube_used": "None",
                "measures": [],
                "dimensions": [],
                "row_count": 0,
                "query_time_ms": 0,
                "session_id": session_id,
                "metadata": {"is_rejected": True, "rejection_reason": knowledge.get("rejection_reason")},
            })
            return

        # Execute query - let downstream agents interpret results intelligently
        # Pass through user_message for context
        try:
            # Build Cube.js query from enriched request
            cube_query = specialist.build_cube_query(knowledge)
            logger.info(f"Built Cube.js query: {cube_query.model_dump(exclude_none=True)}")

            # Execute query and prepare data_ready Spore
            data_ready = run_async(specialist.execute_query(cube_query, session_id))

            # Broadcast data_ready for Visualization Specialist and Quality Inspector
            logger.info(f"Broadcasting data_ready: {data_ready['row_count']} rows")
            broadcast(data_ready)

        except ValueError as e:
            logger.error(f"Query execution error: {str(e)}")
            broadcast({
                "type": "data_ready",
                "query_results": [],
                "cube_used": "Error",
                "measures": [],
                "dimensions": [],
                "row_count": 0,
                "query_time_ms": 0,
                "session_id": session_id,
                "metadata": {"error": str(e), "error_type": "query_error"},
            })

        except ConnectionError as e:
            logger.error(f"Connection error: {str(e)}")
            broadcast({
                "type": "data_ready",
                "query_results": [],
                "cube_used": "Error",
                "measures": [],
                "dimensions": [],
                "row_count": 0,
                "query_time_ms": 0,
                "session_id": session_id,
                "metadata": {"error": "Cannot connect to data service", "error_type": "connection_error"},
            })

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            broadcast({
                "type": "data_ready",
                "query_results": [],
                "cube_used": "Error",
                "measures": [],
                "dimensions": [],
                "row_count": 0,
                "query_time_ms": 0,
                "session_id": session_id,
                "metadata": {"error": "Internal error processing query", "error_type": "internal_error"},
            })

    elif spore_type == "query_refinement_needed":
        # Handle query refinement from Visualization Specialist
        # For now, log and skip - future: implement refinement logic
        logger.info(f"Received query_refinement_needed: {knowledge.get('reason')}")
        logger.info("Query refinement not yet implemented, skipping")

    return
