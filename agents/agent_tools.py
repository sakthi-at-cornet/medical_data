"""Tool functions for Praval agents to enhance capabilities."""
import json
import math
import statistics
from typing import Dict, Any, List, Optional
import httpx
from config import settings
import logging

logger = logging.getLogger(__name__)


class RadiologyTools:
    """Tools for Medical Domain Expert agent."""

    @staticmethod
    def medical_glossary(term: str) -> str:
        """
        Look up medical radiology terminology.

        Args:
            term: Medical term to look up

        Returns:
            Definition or explanation
        """
        glossary = {
            "TAT": "Turnaround Time - Time from scan completion to final report generation.",
            "CAT Rating": "Category Rating - Peer review score (CAT1: Good, CAT2: Minor, CAT3: Moderate, CAT4: Major, CAT5: Severe).",
            "CAT1": "Concurrence - Diagnosis is correct and report is accurate.",
            "CAT5": "Severe Discrepancy - Missed diagnosis with potential for serious clinical impact.",
            "Modality": "Imaging technique used (e.g., CT, MRI, X-ray, Ultrasound).",
            "Accession Number": "Unique identifier for a specific imaging procedure.",
            "PACS": "Picture Archiving and Communication System - Stores medical images.",
            "RIS": "Radiology Information System - Manages patient data and scheduling.",
            "Sub-specialty": "Radiologist's area of expertise (e.g., Neuroradiology, MSK, Body).",
            "Quality Score": "Composite score (0-100) assessing accuracy, clarity, and completeness of a report."
        }

        term_lower = term.lower()
        for key, definition in glossary.items():
            if key.lower() in term_lower:
                return f"{key}: {definition}"

        return f"Term '{term}' not found in medical glossary."


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


class MedicalCalculatorTools:
    """General calculation tools for all medical agents."""

    @staticmethod
    def calculate_tat_efficiency(accession_time: float, target_time: float) -> float:
        """
        Calculate TAT efficiency percentage.
        
        Args:
            accession_time: Actual time taken (hours)
            target_time: Target time (hours)
            
        Returns:
            Efficiency percentile (higher is better, capped at 100%)
        """
        if target_time <= 0:
            return 0.0
        
        # If faster than target, efficiency > 100% (but typically capped for scoring)
        efficiency = (target_time / accession_time) * 100
        return round(min(efficiency, 150.0), 2)  # Cap at 150%

    @staticmethod
    def normalize_score(raw_score: float, max_score: float = 17) -> float:
        """
        Normalize a raw score to 0-100 scale.
        
        Args:
            raw_score: The raw score (e.g., 15/17)
            max_score: Maximum possible score
            
        Returns:
            Normalized score (0-100)
        """
        if max_score <= 0:
            return 0.0
        return round((raw_score / max_score) * 100, 2)

    @staticmethod
    def calculate_discrepancy_rate(discrepant_cases: int, total_cases: int) -> float:
        """
        Calculate error/discrepancy rate.
        
        Args:
            discrepant_cases: Count of CAT3+CAT4+CAT5
            total_cases: Total audited cases
            
        Returns:
            Rate percentage
        """
        if total_cases == 0:
            return 0.0
        return round((discrepant_cases / total_cases) * 100, 2)


# Tool registry for easy access
# Tool registry for easy access
TOOL_REGISTRY = {
    "expert": {
        "medical_glossary": RadiologyTools.medical_glossary,
    },
    "quality_inspector": {
        "calculate_z_score": StatisticalTools.calculate_z_score,
        "calculate_control_limits": StatisticalTools.calculate_control_limits,
        "calculate_cpk": StatisticalTools.calculate_cpk,  # Still useful for process capability
        "detect_outliers_iqr": StatisticalTools.detect_outliers_iqr,
    },
    "analytics_specialist": {
        "get_available_cubes": CubeJsTools.get_available_cubes,
        "get_cube_measures": CubeJsTools.get_cube_measures,
        "get_cube_dimensions": CubeJsTools.get_cube_dimensions,
    },
    "all": {
        "calculate_tat_efficiency": MedicalCalculatorTools.calculate_tat_efficiency,
        "normalize_score": MedicalCalculatorTools.normalize_score,
        "calculate_discrepancy_rate": MedicalCalculatorTools.calculate_discrepancy_rate,
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
