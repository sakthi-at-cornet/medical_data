"""Data Analyst Agent: Translates natural language to Cube.js queries."""
import json
import logging
from typing import Any, Optional
from openai import AsyncOpenAI
from schemas.models import CubeQuery, ChartData
from config import settings

logger = logging.getLogger(__name__)


class DataAnalystAgent:
    """Agent that translates NL questions to Cube.js queries."""

    def __init__(self):
        """Initialize the Data Analyst Agent."""
        self.client = AsyncOpenAI(
            api_key=settings.groq_api_key,
            base_url=settings.groq_base_url
        )
        self.model = settings.groq_model

        # Import schema dynamically from centralized definition
        from schemas.radiology import RADIOLOGY_DATA_SCHEMA
        
        # Use the dynamically generated schema context
        self.schema_context = f"""
Medical Radiology Analytics Schema:

{RADIOLOGY_DATA_SCHEMA}

Use for: Quality analysis, radiologist performance (scores, TAT), modality comparisons, demographic analysis
"""

    async def translate_to_query(self, user_question: str, context: str = "") -> tuple[CubeQuery, str]:
        """
        Translate natural language question to Cube.js query.

        Returns:
            Tuple of (CubeQuery, chart_type)
        """
        system_prompt = f"""You are a data analyst for a medical radiology analytics system.
Your job is to translate user questions into Cube.js queries.

{self.schema_context}

Chart Type Selection:
- "bar": Use for comparisons (modality vs modality, category vs category)
- "line": Use for time-series data (trends over time)
- "table": Use for detailed data, multiple metrics, or when uncertain
- "kpi": Use for single aggregate numbers

Respond with a JSON object containing:
- "query": A Cube.js query object with measures, dimensions, filters, timeDimensions, order, limit
- "chart_type": One of "bar", "line", "table", "kpi"
- "reasoning": Brief explanation of the query

Example Responses:

1. Modality comparison query:
{{
  "query": {{
    "measures": ["RadiologyAudits.avgQualityScore", "RadiologyAudits.avgSafetyScore", "RadiologyAudits.count"],
    "dimensions": ["RadiologyAudits.modality"]
  }},
  "chart_type": "bar",
  "reasoning": "Comparing quality and safety scores between CT and MRI"
}}

2. CAT Rating distribution:
{{
  "query": {{
    "measures": ["RadiologyAudits.count"],
    "dimensions": ["RadiologyAudits.finalOutput"],
    "order": {{
      "RadiologyAudits.count": "desc"
    }}
  }},
  "chart_type": "bar",
  "reasoning": "Showing distribution of cases by CAT rating"
}}

3. Quality trend over time:
{{
  "query": {{
    "measures": ["RadiologyAudits.avgQualityScore"],
    "timeDimensions": [{{
      "dimension": "RadiologyAudits.reportDate",
      "granularity": "day"
    }}]
  }},
  "chart_type": "line",
  "reasoning": "Showing daily trend of average quality score"
}}

4. Radiologist performance analysis:
{{
  "query": {{
    "measures": ["RadiologyAudits.avgQualityScore", "RadiologyAudits.cat5Count", "RadiologyAudits.count"],
    "dimensions": ["RadiologyAudits.originalRadiologist"],
    "order": {{
      "RadiologyAudits.avgQualityScore": "asc"
    }},
    "limit": 10
  }},
  "chart_type": "table",
  "reasoning": "List of radiologists ordered by lowest quality score to identify training needs"
}}

5. Body part analysis:
{{
  "query": {{
    "measures": ["RadiologyAudits.avgQualityScore", "RadiologyAudits.count"],
    "dimensions": ["RadiologyAudits.bodyPartCategory"]
  }},
  "chart_type": "bar",
  "reasoning": "Quality score comparison by body part category"
}}"""

        user_prompt = f"""Question: {user_question}

{f"Context from previous conversation: {context}" if context else ""}

Generate the Cube.js query and chart type."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=settings.groq_temperature,
                max_tokens=settings.groq_max_tokens,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            result = json.loads(content)

            query = CubeQuery(**result["query"])
            chart_type = result.get("chart_type", "table")

            logger.info(f"Translated query - Reasoning: {result.get('reasoning', 'N/A')}")
            return query, chart_type

        except Exception as e:
            logger.error(f"Error translating query: {str(e)}")
            # Fallback to default query
            return CubeQuery(
                measures=["RadiologyAudits.count", "RadiologyAudits.avgQualityScore"],
                dimensions=["RadiologyAudits.modality"]
            ), "table"

    def format_chart_data(
        self,
        cube_response: dict[str, Any],
        chart_type: str,
        query: CubeQuery
    ) -> Optional[ChartData]:
        """Format Cube.js response into chart data."""
        try:
            data = cube_response.get("data", [])
            if not data:
                return None

            # Determine axes from query
            x_axis = None
            y_axis = None

            if query.dimensions:
                x_axis = query.dimensions[0].split(".")[-1]

            if query.measures:
                y_axis = query.measures[0].split(".")[-1]

            # Generate title
            title = self._generate_title(query)

            return ChartData(
                chart_type=chart_type,
                data=data,
                x_axis=x_axis,
                y_axis=y_axis,
                title=title
            )

        except Exception as e:
            logger.error(f"Error formatting chart data: {str(e)}")
            return None

    def _generate_title(self, query: CubeQuery) -> str:
        """Generate a descriptive title from the query."""
        parts = []

        if query.measures:
            measure_names = [m.split(".")[-1] for m in query.measures]
            parts.append(" & ".join(measure_names))

        if query.dimensions:
            dim_names = [d.split(".")[-1] for d in query.dimensions]
            parts.append(f"by {' & '.join(dim_names)}")

        return " ".join(parts).title() if parts else "Results"

    async def generate_insights(
        self,
        user_question: str,
        cube_response: dict[str, Any]
    ) -> list[str]:
        """Generate insights from the query results."""
        data = cube_response.get("data", [])
        if not data:
            return ["No data available for this query."]

        try:
            prompt = f"""Given this medical radiology data query and results:

Question: {user_question}
Results: {json.dumps(data[:5], indent=2)}

Generate 2-3 concise insights (one sentence each) about the data. Focus on:
- Key findings (highest/lowest values)
- Comparisons between categories
- Notable patterns or trends

Respond with a JSON array of insight strings."""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            result = json.loads(content)
            return result.get("insights", ["Analysis complete."])

        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return ["Results retrieved successfully."]


# Global agent instance
data_analyst_agent = DataAnalystAgent()
