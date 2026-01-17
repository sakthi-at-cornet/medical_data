"""
Visualization Specialist Agent.

Data visualization expert with medical radiology audit experience.
Determines appropriate chart types and generates Chart.js specifications.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from praval import agent, broadcast, Spore
from openai import AsyncOpenAI
from config import settings
from async_utils import run_async

logger = logging.getLogger(__name__)


class VisualizationSpecialistAgent:
    """
    Visualization Specialist Agent.

    Chooses appropriate chart types and generates Chart.js specifications.
    """

    def __init__(self):
        """Initialize the Visualization Specialist Agent."""
        self.client = AsyncOpenAI(
            api_key=settings.groq_api_key,
            base_url=settings.groq_base_url
        )
        self.model = settings.groq_model
        logger.info("Visualization Specialist Agent initialized with Groq/Kimi K2")

    async def determine_chart_type(
        self,
        data: List[Dict[str, Any]],
        measures: List[str],
        dimensions: List[str],
        metadata: Dict[str, Any]
    ) -> str:
        """
        Use LLM to determine appropriate chart type based on data characteristics.

        Args:
            data: Query result rows
            measures: Measures in the query
            dimensions: Dimensions in the query
            metadata: Data shape metadata from Analytics Specialist

        Returns:
            Chart type (bar, line, table, kpi, grouped_bar, etc.)
        """
        row_count = metadata.get("row_count", 0)

        # Handle empty data
        if row_count == 0:
            return "empty"


        # Build data summary for LLM
        data_summary = self._summarize_for_chart_selection(data, measures, dimensions, metadata)

        prompt = f"""You are a data visualization expert. Select the most appropriate chart type for a medical radiology audit dashboard.

Data Characteristics:
{data_summary}

Available Chart Types:
- kpi: Single metric display (best for 1 value, e.g., "Average Quality Score: 4.8")
- bar: Simple bar chart (best for comparing 2-10 categories, e.g., modalities like CT, MRI)
- grouped_bar: Grouped/stacked bars (best for multi-dimensional comparisons, e.g., scores by modality and radiologist)
- line: Line chart (best for time series trends, e.g., monthly quality trends)
- donut: Donut/Pie chart (best for part-to-whole distribution of few categories, e.g., Gender M/F, CAT ratings)
- table: Data table (best for >15 rows or complex multi-column data like detailed audit logs)

Respond with JSON:
{{
    "chart_type": "kpi|bar|grouped_bar|line|donut|table",
    "reasoning": "brief explanation why this type fits the data"
}}

Guidelines:
- USE "kpi" for single aggregate scores like "Quality Score", "Safety Score" (1 row, 1 value).
- USE "donut" for simple categorical distributions (Gender, Modality split, CAT ratings) with < 6 categories.
- Bar charts work best for comparing categorical entities (modalities, body parts, radiologists)
- Grouped bars shine when comparing across 2 dimensions
- Line charts are for temporal trends
- Tables handle complexity and large datasets"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.2,
            )

            result = json.loads(response.choices[0].message.content)
            chart_type = result.get("chart_type", "table")
            reasoning = result.get("reasoning", "")

            logger.info(f"LLM selected chart type: {chart_type} - {reasoning}")
            return chart_type

        except Exception as e:
            logger.error(f"Error in LLM chart type selection: {e}")
            # Fallback to simple heuristic
            if row_count == 1:
                return "kpi"
            elif row_count <= 10:
                # If only 1 dimension and few rows, maybe Donut? Default to Bar.
                return "bar"
            else:
                return "table"

    def _summarize_for_chart_selection(
        self,
        data: List[Dict[str, Any]],
        measures: List[str],
        dimensions: List[str],
        metadata: Dict[str, Any]
    ) -> str:
        """Create concise data summary for chart type selection."""
        lines = []

        row_count = metadata.get("row_count", 0)
        column_count = metadata.get("column_count", 0)
        has_time_series = metadata.get("has_time_series", False)
        has_multiple_dimensions = metadata.get("has_multiple_dimensions", False)

        lines.append(f"Rows: {row_count}, Columns: {column_count}")
        lines.append(f"Measures: {', '.join(measures)}")
        lines.append(f"Dimensions: {', '.join(dimensions) if dimensions else 'None'}")
        lines.append(f"Time series: {'Yes' if has_time_series else 'No'}")
        lines.append(f"Multi-dimensional: {'Yes' if has_multiple_dimensions else 'No'}")
        
        # Check for specific patterns
        if "score" in (measures[0].lower() if measures else ""):
             lines.append("Metric appears to be a Score (0-100).")
        if "gender" in (dimensions[0].lower() if dimensions else ""):
             lines.append("Dimension matches 'Gender'.")

        # Sample data
        if data:
            lines.append(f"\nSample row: {data[0]}")
            if len(data) > 1:
                lines.append(f"Last row: {data[-1]}")

        return "\n".join(lines)

    def generate_chart_spec(
        self,
        data: List[Dict[str, Any]],
        measures: List[str],
        dimensions: List[str],
        chart_type: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate Chart.js specification.

        Args:
            data: Query result rows
            measures: List of measures
            dimensions: List of dimensions
            chart_type: Chart type to generate
            metadata: Data shape metadata

        Returns:
            Chart.js specification dictionary
        """
        if chart_type == "empty":
            return {
                "type": "empty",
                "message": "No data available for this query"
            }

        if chart_type == "kpi":
            return self._generate_kpi_card(data, measures)

        if chart_type == "table":
            return self._generate_table(data, dimensions, measures)

        if chart_type == "bar":
            return self._generate_bar_chart(data, dimensions, measures)

        if chart_type == "grouped_bar":
            return self._generate_grouped_bar_chart(data, dimensions, measures)

        if chart_type == "line":
            return self._generate_line_chart(data, dimensions, measures)

        if chart_type == "donut":
            return self._generate_donut_chart(data, dimensions, measures)

        # Default fallback
        return self._generate_table(data, dimensions, measures)

    def _generate_donut_chart(self, data: List[Dict[str, Any]], dimensions: List[str], measures: List[str]) -> Dict[str, Any]:
        """Generate donut chart specification."""
        if not data or not dimensions or not measures:
            return {"type": "empty", "message": "Insufficient data"}

        # Get keys from first row
        label_key = self._get_dimension_key(data[0], dimensions[0])
        value_key = self._get_measure_key(data[0], measures[0])

        # Extract labels and values
        labels = [str(row.get(label_key, "")) for row in data]
        values = [self._to_number(row.get(value_key)) for row in data]

        # 12 distinct colors for different categories
        colors = [
            "rgba(255, 99, 132, 0.8)",   # Red/Pink - ABDOMEN/PELVIS
            "rgba(54, 162, 235, 0.8)",   # Blue - CHEST
            "rgba(255, 206, 86, 0.8)",   # Yellow - HEAD AND NECK
            "rgba(75, 192, 192, 0.8)",   # Teal - MSK
            "rgba(153, 102, 255, 0.8)",  # Purple - NEURO
            "rgba(255, 159, 64, 0.8)",   # Orange - OTHER
            "rgba(46, 204, 113, 0.8)",   # Green - SPINE
            "rgba(142, 68, 173, 0.8)",   # Dark Purple
            "rgba(241, 196, 15, 0.8)",   # Gold
            "rgba(231, 76, 60, 0.8)",    # Dark Red
            "rgba(52, 73, 94, 0.8)",     # Dark Gray
            "rgba(26, 188, 156, 0.8)",   # Turquoise
        ]

        return {
            "type": "donut",
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": self._format_measure_label(value_key),
                    "data": values,
                    "backgroundColor": colors[:len(values)],
                    "borderWidth": 1
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": f"{self._format_measure_label(value_key)} by {self._format_dimension_label(label_key)}"
                    },
                    "legend": {
                        "display": True,
                        "position": "right"
                    }
                }
            }
        }

    def _generate_kpi_card(self, data: List[Dict[str, Any]], measures: List[str]) -> Dict[str, Any]:
        """Generate KPI card specification for single metric."""
        if not data:
            return {"type": "empty", "message": "No data"}

        row = data[0]
        # Get first measure value - pass the first measure string, not the entire list
        first_measure = measures[0] if measures else ""
        measure_key = self._get_measure_key(row, first_measure)
        value = row.get(measure_key, 0)

        return {
            "type": "kpi",
            "value": value,
            "label": self._format_measure_label(measure_key),
            "format": self._get_format_type(measure_key)
        }

    def _generate_table(self, data: List[Dict[str, Any]], dimensions: List[str], measures: List[str]) -> Dict[str, Any]:
        """Generate table specification."""
        if not data:
            return {"type": "empty", "message": "No data"}

        # Extract column headers
        columns = []
        for dim in dimensions:
            dim_key = self._get_dimension_key(data[0], dim)
            columns.append({
                "key": dim_key,
                "label": self._format_dimension_label(dim_key),
                "type": "string"
            })

        for measure in measures:
            measure_key = self._get_measure_key(data[0], measure)
            columns.append({
                "key": measure_key,
                "label": self._format_measure_label(measure_key),
                "type": "number",
                "format": self._get_format_type(measure_key)
            })

        return {
            "type": "table",
            "columns": columns,
            "data": data,
            "sortable": True,
            "pageSize": 10
        }

    def _generate_bar_chart(self, data: List[Dict[str, Any]], dimensions: List[str], measures: List[str]) -> Dict[str, Any]:
        """Generate bar chart specification."""
        if not data or not dimensions or not measures:
            return {"type": "empty", "message": "Insufficient data"}

        # Get keys from first row
        x_key = self._get_dimension_key(data[0], dimensions[0])
        y_key = self._get_measure_key(data[0], measures[0])

        # Extract labels and values (convert to proper types for Chart.js)
        labels = [str(row.get(x_key, "")) for row in data]
        values = [self._to_number(row.get(y_key)) for row in data]

        # 12 distinct colors for different bars
        bar_colors = [
            "rgba(255, 99, 132, 0.8)",   # Red/Pink
            "rgba(54, 162, 235, 0.8)",   # Blue
            "rgba(255, 206, 86, 0.8)",   # Yellow
            "rgba(75, 192, 192, 0.8)",   # Teal
            "rgba(153, 102, 255, 0.8)",  # Purple
            "rgba(255, 159, 64, 0.8)",   # Orange
            "rgba(46, 204, 113, 0.8)",   # Green
            "rgba(142, 68, 173, 0.8)",   # Dark Purple
            "rgba(241, 196, 15, 0.8)",   # Gold
            "rgba(231, 76, 60, 0.8)",    # Dark Red
            "rgba(52, 73, 94, 0.8)",     # Dark Gray
            "rgba(26, 188, 156, 0.8)",   # Turquoise
        ]
        
        # Assign different color to each bar
        colors_for_bars = [bar_colors[i % len(bar_colors)] for i in range(len(values))]
        border_colors = [c.replace("0.8", "1") for c in colors_for_bars]

        return {
            "type": "bar",
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": self._format_measure_label(y_key),
                    "data": values,
                    "backgroundColor": colors_for_bars,
                    "borderColor": border_colors,
                    "borderWidth": 1
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": f"{self._format_measure_label(y_key)} by {self._format_dimension_label(x_key)}"
                    },
                    "legend": {
                        "display": False
                    }
                },
                "scales": {
                    "y": {
                        "beginAtZero": True,
                        "title": {
                            "display": True,
                            "text": self._format_measure_label(y_key)
                        }
                    },
                    "x": {
                        "title": {
                            "display": True,
                            "text": self._format_dimension_label(x_key)
                        }
                    }
                }
            }
        }

    def _generate_grouped_bar_chart(self, data: List[Dict[str, Any]], dimensions: List[str], measures: List[str]) -> Dict[str, Any]:
        """Generate grouped bar chart for multi-dimensional comparison."""
        if not data or len(dimensions) < 2 or not measures:
            return self._generate_bar_chart(data, dimensions, measures)

        # Get keys
        x_key = self._get_dimension_key(data[0], dimensions[0])  # Primary dimension (e.g., defect_type)
        group_key = self._get_dimension_key(data[0], dimensions[1])  # Grouping dimension (e.g., part_family)
        y_key = self._get_measure_key(data[0], measures[0])

        # Group data by x_key and group_key
        grouped_data: Dict[str, Dict[str, float]] = {}
        group_names = set()

        for row in data:
            x_val = str(row.get(x_key, ""))
            group_val = str(row.get(group_key, ""))
            y_val = self._to_number(row.get(y_key))

            if x_val not in grouped_data:
                grouped_data[x_val] = {}
            grouped_data[x_val][group_val] = y_val
            group_names.add(group_val)

        # Extract labels (x-axis categories)
        labels = sorted(grouped_data.keys())
        group_names_list = sorted(group_names)

        # Build datasets (one per group)
        datasets = []
        # 12 distinct colors for grouped bars
        colors = [
            "rgba(255, 99, 132, 0.7)",   # Red/Pink
            "rgba(54, 162, 235, 0.7)",   # Blue
            "rgba(255, 206, 86, 0.7)",   # Yellow
            "rgba(75, 192, 192, 0.7)",   # Teal
            "rgba(153, 102, 255, 0.7)",  # Purple
            "rgba(255, 159, 64, 0.7)",   # Orange
            "rgba(46, 204, 113, 0.7)",   # Green
            "rgba(142, 68, 173, 0.7)",   # Dark Purple
            "rgba(241, 196, 15, 0.7)",   # Gold
            "rgba(231, 76, 60, 0.7)",    # Dark Red
            "rgba(52, 73, 94, 0.7)",     # Dark Gray
            "rgba(26, 188, 156, 0.7)",   # Turquoise
        ]

        for i, group_name in enumerate(group_names_list):
            color = colors[i % len(colors)]
            border_color = color.replace("0.6", "1")

            values = [self._to_number(grouped_data.get(label, {}).get(group_name)) for label in labels]

            datasets.append({
                "label": str(group_name),
                "data": values,
                "backgroundColor": color,
                "borderColor": border_color,
                "borderWidth": 1
            })

        return {
            "type": "bar",
            "data": {
                "labels": labels,
                "datasets": datasets
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": f"{self._format_measure_label(y_key)} by {self._format_dimension_label(x_key)} and {self._format_dimension_label(group_key)}"
                    },
                    "legend": {
                        "display": True,
                        "position": "top"
                    }
                },
                "scales": {
                    "y": {
                        "beginAtZero": True,
                        "title": {
                            "display": True,
                            "text": self._format_measure_label(y_key)
                        }
                    },
                    "x": {
                        "title": {
                            "display": True,
                            "text": self._format_dimension_label(x_key)
                        }
                    }
                }
            }
        }

    def _generate_line_chart(self, data: List[Dict[str, Any]], dimensions: List[str], measures: List[str]) -> Dict[str, Any]:
        """Generate line chart for time series."""
        if not data or not dimensions or not measures:
            return {"type": "empty", "message": "Insufficient data"}

        # Assume first dimension is time
        x_key = self._get_dimension_key(data[0], dimensions[0])
        y_key = self._get_measure_key(data[0], measures[0])

        # Extract labels and values (convert to proper types for Chart.js)
        labels = [str(row.get(x_key, "")) for row in data]
        values = [self._to_number(row.get(y_key)) for row in data]

        return {
            "type": "line",
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": self._format_measure_label(y_key),
                    "data": values,
                    "borderColor": "rgba(75, 192, 192, 1)",
                    "backgroundColor": "rgba(75, 192, 192, 0.2)",
                    "tension": 0.1,
                    "fill": True
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": f"{self._format_measure_label(y_key)} over Time"
                    },
                    "legend": {
                        "display": False
                    }
                },
                "scales": {
                    "y": {
                        "beginAtZero": True,
                        "title": {
                            "display": True,
                            "text": self._format_measure_label(y_key)
                        }
                    },
                    "x": {
                        "title": {
                            "display": True,
                            "text": "Time"
                        }
                    }
                }
            }
        }

    def _get_dimension_key(self, row: Dict[str, Any], dimension: str) -> str:
        """Get actual dimension key from row data (handles both full and short names)."""
        # Try full name first (e.g., "PressOperations.partFamily")
        if dimension in row:
            return dimension

        # Try short name (e.g., "partFamily")
        if "." in dimension:
            short_name = dimension.split(".")[-1]
            if short_name in row:
                return short_name

        # Fallback: return first string key
        for key in row.keys():
            if isinstance(row[key], str):
                return key

        return list(row.keys())[0] if row else ""

    def _get_measure_key(self, row: Dict[str, Any], measure: str) -> str:
        """Get actual measure key from row data."""
        # Try full name first
        if measure in row:
            return measure

        # Try short name
        if "." in measure:
            short_name = measure.split(".")[-1]
            if short_name in row:
                return short_name

        # Fallback: return first numeric key
        for key in row.keys():
            if isinstance(row[key], (int, float)):
                return key

        return list(row.keys())[0] if row else ""

    def _format_dimension_label(self, key: str) -> str:
        """Format dimension key into human-readable label."""
        if "." in key:
            key = key.split(".")[-1]

        # Convert camelCase or snake_case to Title Case
        label = key.replace("_", " ").replace(".", " ")
        return label.title()

    def _format_measure_label(self, key: str) -> str:
        """Format measure key into human-readable label."""
        if "." in key:
            key = key.split(".")[-1]

        # Handle common abbreviations
        replacements = {
            "avg": "Average",
            "tat": "TAT",
            "pct": "%",
            "q1": "Q1",
            "q2": "Q2", 
        }

        label = key
        for abbr, full in replacements.items():
            if abbr in label.lower():
                label = label.replace(abbr, full)

        label = label.replace("_", " ").replace(".", " ")
        return label.title()

    def _to_number(self, value: Any) -> float:
        """Safely convert value to float (handles strings from PostgreSQL decimal type)."""
        if value is None:
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except (ValueError, TypeError):
                return 0.0
        return 0.0

    def _get_format_type(self, key: str) -> str:
        """Determine format type for measure."""
        key_lower = key.lower()

        if "rate" in key_lower or "pct" in key_lower or "percentage" in key_lower:
            return "percent"

        if "cost" in key_lower:
            return "currency"
            
        if "score" in key_lower or "tat" in key_lower:
            return "number"

        if "time" in key_lower:
            return "time"

        return "number"


# Praval agent decorator
@agent(
    "visualization_specialist",
    responds_to=["data_ready"],
    system_message="You are a data visualization expert with medical radiology audit experience.",
    auto_broadcast=False  # We manually broadcast chart_ready
)
def visualization_specialist_handler(spore: Spore):
    """
    Handle data_ready Spores and generate chart specifications.

    Args:
        spore: Spore with data_ready knowledge
    """
    try:
        logger.info(f"Visualization Specialist received spore: {spore.id}")

        # Extract knowledge from spore
        knowledge = spore.knowledge
        logger.info(f"Knowledge type: {type(knowledge)}")
        logger.info(f"Knowledge keys: {knowledge.keys() if isinstance(knowledge, dict) else 'not a dict'}")

        session_id = knowledge.get("session_id", "")
        query_results = knowledge.get("query_results", [])
        measures = knowledge.get("measures", [])
        dimensions = knowledge.get("dimensions", [])
        metadata = knowledge.get("metadata", {})

        logger.info(f"Processing data_ready (session {session_id}): {len(query_results)} rows")
    except Exception as e:
        logger.error(f"Error in visualization_specialist_handler setup: {e}", exc_info=True)
        return

    import asyncio

    # Initialize specialist
    specialist = VisualizationSpecialistAgent()

    # Use LLM to determine chart type
    chart_type = run_async(specialist.determine_chart_type(
        query_results, measures, dimensions, metadata
    ))
    logger.info(f"LLM selected chart type: {chart_type}")

    # Generate actual chart specification with data
    # Ensure all parameters are correct types
    if not isinstance(metadata, dict):
        metadata = {}
    if isinstance(dimensions, str):
        dimensions = [dimensions] if dimensions else []
    if isinstance(measures, str):
        measures = [measures] if measures else []

    logger.info(f"Calling generate_chart_spec: chart_type={chart_type}, dimensions={dimensions}, measures={measures}")

    try:
        chart_spec = specialist.generate_chart_spec(
            data=query_results,
            measures=measures,
            dimensions=dimensions,
            chart_type=chart_type,
            metadata=metadata
        )
        logger.info(f"Generated chart spec: type={chart_spec.get('type')}")
    except Exception as e:
        logger.error(f"Error generating chart spec: {e}", exc_info=True)
        chart_spec = {"type": "empty", "message": "Chart generation failed"}

    # Broadcast chart_ready with full chart specification
    chart_ready = {
        "type": "chart_ready",
        "chart_type": str(chart_type),
        "chart_spec": chart_spec,
        "session_id": str(session_id),
    }

    logger.info(f"About to broadcast chart_ready with chart_spec")
    try:
        broadcast(chart_ready)
        logger.info("Successfully broadcasted chart_ready")
    except Exception as e:
        logger.error(f"Error broadcasting chart_ready: {e}", exc_info=True)

    return
