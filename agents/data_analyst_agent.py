"""Data Analyst Agent: Translates natural language to Cube.js queries."""
import json
import logging
from typing import Any, Optional
from openai import AsyncOpenAI
from models import CubeQuery, ChartData
from config import settings

logger = logging.getLogger(__name__)


class DataAnalystAgent:
    """Agent that translates NL questions to Cube.js queries."""

    def __init__(self):
        """Initialize the Data Analyst Agent."""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

        # Domain knowledge: Available cubes and their measures/dimensions
        self.schema_context = """
Automotive Press Manufacturing Analytics Schema:

1. PressOperations Cube (fact_press_operations):
   - Measures: count, passedCount, failedCount, passRate, avgOee, avgAvailability, avgPerformance, avgQualityRate,
              avgTonnage, avgCycleTime, avgStrokeRate, totalCost, avgCostPerPart, avgMaterialCost, avgLaborCost,
              avgEnergyCost, avgSurfaceDeviation, defectCount, reworkCount
   - Dimensions: partFamily (Door_Outer_Left, Door_Outer_Right, Bonnet_Outer), pressLineId, lineName, dieId,
                partType (Door/Bonnet), materialGrade (CRS_SPCC, HSLA_350, DP600), coilId, shiftId, operatorId,
                qualityStatus, defectType, defectSeverity, tonnageCategory, oeeCategory, productionDate, isWeekend
   - Use for: Production-level analysis, OEE breakdown, defect analysis, shift comparison, die/coil traceability

2. PartFamilyPerformance Cube (agg_part_family_performance):
   - Measures: totalPartsProduced, partsPassed, partsFailed, firstPassYield, reworkRate, uniqueDefectTypes,
              avgOee, avgAvailability, avgPerformance, avgQualityRate, avgTonnage, avgCycleTime,
              avgCostPerPart, totalProductionCost, avgMaterialCost, avgLaborCost, avgCoilDefectRate,
              avgMaterialYieldStrength, avgMaterialTensileStrength, productionDays
   - Dimensions: partFamily, partType (Door/Bonnet), materialGrade
   - Use for: Part family comparison (Door Left vs Door Right vs Bonnet), material grade performance,
             first pass yield analysis, cost per part optimization

3. PressLineUtilization Cube (agg_press_line_utilization):
   - Measures: totalPartsProduced, totalPartsPassed, totalPartsFailed, avgPassRate, overallAvgOee,
              overallAvgAvailability, overallAvgPerformance, overallAvgQualityRate, avgTonnage, avgCycleTime,
              totalCost, avgCostPerUnit, totalProductionDays, totalBatches, totalOperatorShifts, totalDefects,
              totalRework, weekendParts, weekdayParts, weekendProductionPct, morningShiftParts, afternoonShiftParts,
              nightShiftParts, utilizationRate
   - Dimensions: pressLineId, lineName (LINE_A/LINE_B), partType
   - Use for: Press line capacity planning, shift utilization, weekend vs weekday analysis,
             Line A (800T) vs Line B (1200T) comparison

Automotive Manufacturing Domain:
- OEE (Overall Equipment Effectiveness) = Availability × Performance × Quality Rate
- Availability: Uptime / Planned production time
- Performance: Actual output / Target output (at design cycle time)
- Quality Rate: Good parts / Total parts produced
- SMED: Single-Minute Exchange of Die (changeover time)
- Tonnage: Press force (Line A: 600-650T, Line B: 900-1100T)
- Cycle Time: Time per part (Line A: 1.2-1.5s, Line B: 1.5-2.0s)
- Defect Types: Springback, Wrinkling, Necking, Splitting, Surface Defects, Dimensional Variation
- Material Grades: CRS_SPCC (cold rolled steel), HSLA_350 (high-strength low-alloy), DP600 (dual-phase steel)
- Part Types: Door outer panels (LEFT/RIGHT on Line A), Bonnet outer panel (Line B)

Query Patterns:
- "OEE" or "efficiency" → use avgOee, avgAvailability, avgPerformance, avgQualityRate
- "pass rate" or "quality" → use passRate or avgPassRate
- "by part" or "which part" → use PressOperations.partFamily or PartFamilyPerformance.partFamily
- "by line" or "press line" → use PressLineUtilization.lineName or PressOperations.pressLineId
- "by shift" → use PressOperations.shiftId dimension
- "defect" or "failure" → use defectCount, defectType, defectSeverity
- "cost" → use avgCostPerPart, totalCost, avgMaterialCost, avgLaborCost
- "tonnage" → use avgTonnage measure
- "cycle time" or "speed" → use avgCycleTime or avgStrokeRate
- "material" or "coil" → use materialGrade dimension or coilId for traceability
- "die" → use dieId dimension
- "over time" or "trends" → use productionDate timeDimension
- "weekend" or "weekday" → use isWeekend dimension or weekendParts/weekdayParts measures
- "shift analysis" → use morningShiftParts, afternoonShiftParts, nightShiftParts
- "best" or "highest" → add order desc
- "worst" or "lowest" → add order asc
"""

    async def translate_to_query(self, user_question: str, context: str = "") -> tuple[CubeQuery, str]:
        """
        Translate natural language question to Cube.js query.

        Returns:
            Tuple of (CubeQuery, chart_type)
        """
        system_prompt = f"""You are a data analyst for a manufacturing analytics system.
Your job is to translate user questions into Cube.js queries.

{self.schema_context}

Chart Type Selection:
- "bar": Use for comparisons (component vs component, material vs material)
- "line": Use for time-series data (trends over time, hourly/daily changes)
- "table": Use for detailed data, multiple metrics, or when uncertain

Respond with a JSON object containing:
- "query": A Cube.js query object with measures, dimensions, filters, timeDimensions, order, limit
- "chart_type": One of "bar", "line", or "table"
- "reasoning": Brief explanation of the query

Example Responses:

1. Part family comparison query:
{{
  "query": {{
    "measures": ["PartFamilyPerformance.totalPartsProduced", "PartFamilyPerformance.firstPassYield", "PartFamilyPerformance.avgCostPerPart"],
    "dimensions": ["PartFamilyPerformance.partFamily"]
  }},
  "chart_type": "bar",
  "reasoning": "Comparing part families (Door Left/Right vs Bonnet) by production volume, yield, and cost"
}}

2. OEE breakdown by press line:
{{
  "query": {{
    "measures": ["PressLineUtilization.overallAvgOee", "PressLineUtilization.overallAvgAvailability", "PressLineUtilization.overallAvgPerformance", "PressLineUtilization.overallAvgQualityRate"],
    "dimensions": ["PressLineUtilization.lineName"]
  }},
  "chart_type": "bar",
  "reasoning": "Showing OEE components breakdown for Line A vs Line B"
}}

3. Time-series quality trends:
{{
  "query": {{
    "measures": ["PressOperations.passRate", "PressOperations.avgOee"],
    "dimensions": ["PressOperations.partFamily"],
    "timeDimensions": [{{
      "dimension": "PressOperations.productionDate",
      "granularity": "day"
    }}]
  }},
  "chart_type": "line",
  "reasoning": "Showing daily quality and OEE trends by part family"
}}

4. Shift performance analysis:
{{
  "query": {{
    "measures": ["PressLineUtilization.morningShiftParts", "PressLineUtilization.afternoonShiftParts", "PressLineUtilization.nightShiftParts"],
    "dimensions": ["PressLineUtilization.lineName"]
  }},
  "chart_type": "bar",
  "reasoning": "Comparing shift productivity across press lines"
}}

5. Defect analysis:
{{
  "query": {{
    "measures": ["PressOperations.defectCount", "PressOperations.reworkCount"],
    "dimensions": ["PressOperations.defectType"],
    "order": {{
      "PressOperations.defectCount": "desc"
    }},
    "limit": 10
  }},
  "chart_type": "bar",
  "reasoning": "Top 10 defect types by frequency with rework count"
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
                temperature=settings.openai_temperature,
                max_tokens=settings.openai_max_tokens,
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
                measures=["PartFamilyPerformance.totalPartsProduced", "PartFamilyPerformance.firstPassYield"],
                dimensions=["PartFamilyPerformance.partFamily"]
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
            prompt = f"""Given this manufacturing data query and results:

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
