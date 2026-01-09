"""
Quality Inspector Agent.

Quality engineer with expertise in root cause analysis and statistical process control.
Analyzes data for anomalies, patterns, and generates manufacturing insights.
"""
import json
import logging
from typing import Dict, List, Any
from praval import agent, broadcast, Spore
from openai import AsyncOpenAI
from config import settings
from async_utils import run_async

logger = logging.getLogger(__name__)


class QualityInspectorAgent:
    """
    Quality Inspector Agent.

    Analyzes query results and generates insights with root cause hypotheses.
    """

    def __init__(self):
        """Initialize the Quality Inspector Agent."""
        self.client = AsyncOpenAI(
            api_key=settings.groq_api_key,
            base_url=settings.groq_base_url
        )
        self.model = settings.groq_model
        logger.info("Quality Inspector Agent initialized with Groq/Kimi K2")

    async def analyze_data(
        self,
        data: List[Dict[str, Any]],
        measures: List[str],
        dimensions: List[str],
        cube_used: str,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Analyze data for patterns, anomalies, and root causes.

        Args:
            data: Query result rows
            measures: Measures in the query
            dimensions: Dimensions in the query
            cube_used: Cube that was queried
            session_id: Session identifier

        Returns:
            insights_ready knowledge payload
        """
        if not data:
            return {
                "type": "insights_ready",
                "observations": [],
                "anomalies": [],
                "root_causes": [],
                "session_id": session_id,
            }

        # Prepare data summary for LLM
        data_summary = self._summarize_data(data, measures, dimensions)

        # Build analysis prompt with strict anti-hallucination instructions
        prompt = f"""You are a medical quality auditor analyzing radiology performance data.

Medical Radiology Context:
- Modalities: CT, MRI
- Metrics: Quality Score (Q1-Q17), Safety Score, Star Rating (1-5), Turnaround Time (TAT)
- CAT Ratings: CAT1 (Good) to CAT5 (Severe deficiencies)
- Key Factors: Radiologist experience, case complexity, body part scanned, time of day
- Goals: Improve patient safety, reduce diagnostic errors, optimize efficiency

Data Summary:
{data_summary}

Cube Queried: {cube_used}
Measures: {', '.join(measures)}
Dimensions: {', '.join(dimensions)}

CRITICAL ANTI-HALLUCINATION RULES:
1. ONLY analyze the data shown above - do NOT make up numbers
2. ONLY mention entities that appear in the data
3. ONLY report patterns you can see in the actual data
4. If you cite a number, it MUST match exactly what's in the data
5. DO NOT infer data from previous conversations or general knowledge
6. If the data is empty or has only aggregate counts, say so directly

Analyze this data and provide:
1. Observation Insights: Key patterns, comparisons, trends FROM THE DATA ABOVE ONLY
2. Anomalies: Unusual values or outliers (ONLY if visible in the data, e.g., low safety scores)
3. Root Cause Hypotheses: Clinical/Operational reasons for patterns YOU CAN SEE in the data

Respond in JSON format:
{{
    "observations": [
        {{
            "type": "comparative" | "pattern" | "trend" | "summary",
            "text": "Human-readable insight text with EXACT numbers from the data",
            "confidence": 0.0-1.0,
            "data_points": {{"key metrics with values from the actual data"}}
        }}
    ],
    "anomalies": [
        {{
            "entity": "entity with anomaly (MUST be in the data above)",
            "metric": "metric with anomaly (MUST be in the data above)",
            "severity": "low" | "moderate" | "high" | "critical",
            "description": "Human-readable anomaly description with EXACT values"
        }}
    ],
    "root_causes": [
        {{
            "hypothesis": "Root cause hypothesis text",
            "confidence": 0.0-1.0,
            "evidence": ["supporting evidence DIRECTLY from the data above"],
            "recommended_action": "Specific corrective action for radiology dept"
        }}
    ]
}}

Guidelines:
- VERIFY every number you cite matches the data above
- Compare ONLY entities that exist in the data
- If data is limited or aggregated, acknowledge that in your insights
- Only flag anomalies if there are genuine outliers in THIS data
- If you can't see a clear pattern in the data, say "insufficient data for pattern detection"
"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.2,
            )

            insights = json.loads(response.choices[0].message.content)
            logger.info(f"Generated {len(insights.get('observations', []))} observations, "
                       f"{len(insights.get('anomalies', []))} anomalies, "
                       f"{len(insights.get('root_causes', []))} root causes")

            return {
                "type": "insights_ready",
                "observations": insights.get("observations", []),
                "anomalies": insights.get("anomalies", []),
                "root_causes": insights.get("root_causes", []),
                "session_id": session_id,
            }

        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            # Return empty insights on error
            return {
                "type": "insights_ready",
                "observations": [],
                "anomalies": [],
                "root_causes": [],
                "session_id": session_id,
            }

    def _summarize_data(self, data: List[Dict[str, Any]], measures: List[str], dimensions: List[str]) -> str:
        """
        Create a concise summary of the data for LLM analysis.
        CRITICAL: Include ALL data to prevent hallucination.

        Args:
            data: Query result rows
            measures: Measures in the query
            dimensions: Dimensions in the query

        Returns:
            Text summary with COMPLETE data
        """
        summary_lines = []

        # Overall stats
        summary_lines.append(f"Total rows: {len(data)}")
        summary_lines.append(f"\n*** IMPORTANT: ONLY analyze the data shown below. DO NOT make up numbers or infer patterns not visible in this data. ***\n")

        # ALWAYS include all data rows to prevent hallucination
        summary_lines.append("\nCOMPLETE DATA (all rows):")
        for i, row in enumerate(data, 1):
            row_str = ", ".join([f"{k}: {v}" for k, v in row.items()])
            summary_lines.append(f"  {i}. {row_str}")

        # Calculate basic statistics for numeric measures
        if len(data) > 1:
            summary_lines.append("\nStatistics (calculated from above data):")
            for measure in measures:
                # Try to find measure in data
                measure_key = self._find_measure_key(data[0], measure)
                if measure_key:
                    values = []
                    for row in data:
                        val = row.get(measure_key)
                        if isinstance(val, (int, float)):
                            values.append(val)

                    if values:
                        summary_lines.append(f"  {measure_key}:")
                        summary_lines.append(f"    Min: {min(values):.2f}")
                        summary_lines.append(f"    Max: {max(values):.2f}")
                        summary_lines.append(f"    Mean: {sum(values)/len(values):.2f}")
                        summary_lines.append(f"    Total: {sum(values):.2f}")

        return "\n".join(summary_lines)

    def _find_measure_key(self, row: Dict[str, Any], measure: str) -> str:
        """Find actual measure key in row data."""
        # Try full name
        if measure in row:
            return measure

        # Try short name
        if "." in measure:
            short_name = measure.split(".")[-1]
            if short_name in row:
                return short_name

        return ""

    def detect_critical_anomalies(self, insights: Dict[str, Any]) -> bool:
        """
        Check if any critical anomalies were detected.

        Args:
            insights: insights_ready knowledge

        Returns:
            True if critical anomalies exist
        """
        anomalies = insights.get("anomalies", [])
        for anomaly in anomalies:
            if anomaly.get("severity") == "critical":
                return True
        return False


# Praval agent decorator
@agent(
    "quality_inspector",
    responds_to=["data_ready"],
    system_message="You are a medical quality auditor with expertise in radiology audits, patient safety, and clinical performance metrics.",
    auto_broadcast=False
)
def quality_inspector_handler(spore: Spore):
    """
    Handle data_ready Spores and generate quality insights.

    Args:
        spore: Spore with data_ready knowledge
    """
    import asyncio

    logger.info(f"Quality Inspector received spore: {spore.id}")

    # Extract knowledge from spore
    knowledge = spore.knowledge
    session_id = knowledge.get("session_id", "")
    query_results = knowledge.get("query_results", [])
    measures = knowledge.get("measures", [])
    dimensions = knowledge.get("dimensions", [])
    cube_used = knowledge.get("cube_used", "")
    metadata = knowledge.get("metadata", {})

    # Check for rejected queries or errors
    is_rejected = metadata.get("is_rejected", False)
    has_error = metadata.get("error") is not None

    if is_rejected or has_error:
        logger.info(f"Skipping analysis - rejected/error query (session {session_id})")
        insights = {
            "type": "insights_ready",
            "observations": [],
            "anomalies": [],
            "root_causes": [],
            "session_id": session_id,
            "is_rejected": is_rejected,
            "rejection_reason": metadata.get("rejection_reason", ""),
        }
        broadcast(insights)
        return

    logger.info(f"Analyzing data (session {session_id}): {len(query_results)} rows")

    # Initialize inspector
    inspector = QualityInspectorAgent()

    # Analyze data and generate insights
    insights = run_async(inspector.analyze_data(
        query_results,
        measures,
        dimensions,
        cube_used,
        session_id
    ))

    # Check for critical anomalies
    if inspector.detect_critical_anomalies(insights):
        logger.warning(f"Critical anomalies detected in session {session_id}")
        # Broadcast separate anomaly_detected Spore
        broadcast({
            "type": "anomaly_detected",
            "anomalies": [a for a in insights.get("anomalies", []) if a.get("severity") == "critical"],
            "session_id": session_id,
        })

    # Broadcast insights_ready
    logger.info(f"Broadcasting insights_ready: {len(insights.get('observations', []))} observations")
    broadcast(insights)

    return
