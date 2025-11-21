"""Tool functions for Praval agents to enhance capabilities."""
import json
import math
import statistics
from typing import Dict, Any, List, Optional
import httpx
from config import settings
import logging

logger = logging.getLogger(__name__)


class ManufacturingTools:
    """Tools for Manufacturing Advisor agent."""

    @staticmethod
    def manufacturing_glossary(term: str) -> str:
        """
        Look up manufacturing terminology.

        Args:
            term: Manufacturing term to look up

        Returns:
            Definition or explanation
        """
        glossary = {
            "OEE": "Overall Equipment Effectiveness - Product of Availability × Performance × Quality. Industry standard is 85%.",
            "SMED": "Single-Minute Exchange of Die - Rapid die changeover methodology. Goal is <10 minutes.",
            "springback": "Material's tendency to return to original shape after forming. Common in high-strength steels.",
            "burr": "Unwanted raised edge or material on a part, typically from cutting or stamping.",
            "tonnage": "Force applied by press during forming operation, measured in tons (800T, 1200T).",
            "first pass yield": "Percentage of parts that pass quality inspection on first try, without rework.",
            "cycle time": "Total time to produce one part, from material feed to part ejection.",
            "die wear": "Gradual degradation of die surface from repeated contact with material.",
            "PLC": "Programmable Logic Controller - computer controlling press operations.",
            "coil": "Roll of sheet metal used as raw material for stamping operations."
        }

        term_lower = term.lower()
        for key, definition in glossary.items():
            if key.lower() == term_lower or key.lower() in term_lower:
                return f"{key}: {definition}"

        return f"Term '{term}' not found in glossary. This is specialized manufacturing terminology."


class StatisticalTools:
    """Statistical calculation tools for Quality Inspector agent."""

    @staticmethod
    def calculate_z_score(value: float, mean: float, std_dev: float) -> float:
        """
        Calculate z-score for anomaly detection.

        Z-score > 3 or < -3 indicates outlier (>99.7% confidence).

        Args:
            value: Observed value
            mean: Population mean
            std_dev: Population standard deviation

        Returns:
            Z-score
        """
        if std_dev == 0:
            return 0.0
        return (value - mean) / std_dev

    @staticmethod
    def calculate_control_limits(data: List[float], sigma: int = 3) -> Dict[str, float]:
        """
        Calculate statistical process control limits.

        Args:
            data: List of measurements
            sigma: Number of standard deviations (typically 3)

        Returns:
            Dict with mean, UCL (upper control limit), LCL (lower control limit)
        """
        if not data:
            return {"mean": 0, "ucl": 0, "lcl": 0}

        mean = statistics.mean(data)
        std_dev = statistics.stdev(data) if len(data) > 1 else 0

        return {
            "mean": round(mean, 2),
            "ucl": round(mean + (sigma * std_dev), 2),  # Upper Control Limit
            "lcl": round(mean - (sigma * std_dev), 2),  # Lower Control Limit
            "std_dev": round(std_dev, 2)
        }

    @staticmethod
    def calculate_cpk(data: List[float], usl: float, lsl: float) -> float:
        """
        Calculate Process Capability Index (Cpk).

        Cpk > 1.33 is considered acceptable process capability.
        Cpk > 1.67 is world-class.

        Args:
            data: Process measurements
            usl: Upper Specification Limit
            lsl: Lower Specification Limit

        Returns:
            Cpk value
        """
        if not data or len(data) < 2:
            return 0.0

        mean = statistics.mean(data)
        std_dev = statistics.stdev(data)

        if std_dev == 0:
            return 0.0

        cpu = (usl - mean) / (3 * std_dev)
        cpl = (mean - lsl) / (3 * std_dev)

        return round(min(cpu, cpl), 2)

    @staticmethod
    def detect_outliers_iqr(data: List[float]) -> List[int]:
        """
        Detect outliers using Interquartile Range (IQR) method.

        Args:
            data: List of values

        Returns:
            List of indices of outlier values
        """
        if len(data) < 4:
            return []

        sorted_data = sorted(data)
        q1_idx = len(sorted_data) // 4
        q3_idx = 3 * len(sorted_data) // 4

        q1 = sorted_data[q1_idx]
        q3 = sorted_data[q3_idx]
        iqr = q3 - q1

        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3 + (1.5 * iqr)

        outliers = []
        for i, value in enumerate(data):
            if value < lower_bound or value > upper_bound:
                outliers.append(i)

        return outliers


class CubeJsTools:
    """Tools for interacting with Cube.js semantic layer."""

    @staticmethod
    async def get_available_cubes() -> List[str]:
        """
        Get list of available cubes from Cube.js.

        Returns:
            List of cube names
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.cubejs_api_url}/meta",
                    headers={"Authorization": settings.cubejs_api_secret},
                    timeout=10.0
                )
                response.raise_for_status()
                meta = response.json()
                return [cube["name"] for cube in meta.get("cubes", [])]
        except Exception as e:
            logger.error(f"Error fetching Cube.js meta: {e}")
            return []

    @staticmethod
    async def get_cube_measures(cube_name: str) -> List[str]:
        """
        Get available measures for a cube.

        Args:
            cube_name: Name of the cube

        Returns:
            List of measure names
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.cubejs_api_url}/meta",
                    headers={"Authorization": settings.cubejs_api_secret},
                    timeout=10.0
                )
                response.raise_for_status()
                meta = response.json()

                for cube in meta.get("cubes", []):
                    if cube["name"] == cube_name:
                        return [m["name"] for m in cube.get("measures", [])]
                return []
        except Exception as e:
            logger.error(f"Error fetching cube measures: {e}")
            return []

    @staticmethod
    async def get_cube_dimensions(cube_name: str) -> List[str]:
        """
        Get available dimensions for a cube.

        Args:
            cube_name: Name of the cube

        Returns:
            List of dimension names
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.cubejs_api_url}/meta",
                    headers={"Authorization": settings.cubejs_api_secret},
                    timeout=10.0
                )
                response.raise_for_status()
                meta = response.json()

                for cube in meta.get("cubes", []):
                    if cube["name"] == cube_name:
                        return [d["name"] for d in cube.get("dimensions", [])]
                return []
        except Exception as e:
            logger.error(f"Error fetching cube dimensions: {e}")
            return []


class CalculatorTools:
    """General calculation tools for all agents."""

    @staticmethod
    def calculate_oee(availability: float, performance: float, quality: float) -> float:
        """
        Calculate Overall Equipment Effectiveness.

        OEE = Availability × Performance × Quality

        Args:
            availability: % of planned time equipment was available
            performance: % of max speed achieved
            quality: % of good parts produced

        Returns:
            OEE as percentage (0-100)
        """
        # Convert to decimals if given as percentages
        if availability > 1:
            availability /= 100
        if performance > 1:
            performance /= 100
        if quality > 1:
            quality /= 100

        oee = availability * performance * quality * 100
        return round(oee, 2)

    @staticmethod
    def calculate_defect_rate(defect_count: int, total_parts: int) -> float:
        """
        Calculate defect rate as percentage.

        Args:
            defect_count: Number of defective parts
            total_parts: Total parts produced

        Returns:
            Defect rate as percentage
        """
        if total_parts == 0:
            return 0.0
        return round((defect_count / total_parts) * 100, 2)

    @staticmethod
    def calculate_first_pass_yield(good_parts: int, total_parts: int) -> float:
        """
        Calculate first pass yield.

        Args:
            good_parts: Parts passing first inspection
            total_parts: Total parts produced

        Returns:
            First pass yield as percentage
        """
        if total_parts == 0:
            return 0.0
        return round((good_parts / total_parts) * 100, 2)


# Tool registry for easy access
TOOL_REGISTRY = {
    "manufacturing_advisor": {
        "manufacturing_glossary": ManufacturingTools.manufacturing_glossary,
    },
    "quality_inspector": {
        "calculate_z_score": StatisticalTools.calculate_z_score,
        "calculate_control_limits": StatisticalTools.calculate_control_limits,
        "calculate_cpk": StatisticalTools.calculate_cpk,
        "detect_outliers_iqr": StatisticalTools.detect_outliers_iqr,
    },
    "analytics_specialist": {
        "get_available_cubes": CubeJsTools.get_available_cubes,
        "get_cube_measures": CubeJsTools.get_cube_measures,
        "get_cube_dimensions": CubeJsTools.get_cube_dimensions,
    },
    "all": {
        "calculate_oee": CalculatorTools.calculate_oee,
        "calculate_defect_rate": CalculatorTools.calculate_defect_rate,
        "calculate_first_pass_yield": CalculatorTools.calculate_first_pass_yield,
    }
}


def get_agent_tools(agent_name: str) -> Dict[str, Any]:
    """
    Get tools available for a specific agent.

    Args:
        agent_name: Name of the agent

    Returns:
        Dictionary of tool functions
    """
    tools = {}

    # Add agent-specific tools
    if agent_name in TOOL_REGISTRY:
        tools.update(TOOL_REGISTRY[agent_name])

    # Add common tools
    tools.update(TOOL_REGISTRY["all"])

    return tools
