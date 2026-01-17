"""Cube.js API client wrapper with error handling."""
import logging
from typing import Any, Optional
import httpx
from schemas.models import CubeQuery
from config import settings

logger = logging.getLogger(__name__)


class CubeJSClient:
    """Client for interacting with Cube.js API."""

    def __init__(self, api_url: Optional[str] = None, api_secret: Optional[str] = None):
        """Initialize Cube.js client."""
        self.api_url = api_url or settings.cubejs_api_url
        self.api_secret = api_secret or settings.cubejs_api_secret
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": self.api_secret
        }

    async def execute_query(self, query: CubeQuery) -> dict[str, Any]:
        """Execute a Cube.js query and return results."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_url}/load",
                    json={"query": query.model_dump(exclude_none=True)},
                    headers=self.headers
                )
                response.raise_for_status()
                result = response.json()

                logger.info(f"Query executed successfully: {query.measures or query.dimensions}")
                return result

        except httpx.HTTPStatusError as e:
            logger.error(f"Cube.js HTTP error: {e.response.status_code} - {e.response.text}")
            raise ValueError(f"Cube.js query failed: {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"Cube.js connection error: {str(e)}")
            raise ConnectionError(f"Cannot connect to Cube.js: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error executing query: {str(e)}")
            raise

    async def get_meta(self) -> dict[str, Any]:
        """Fetch Cube.js metadata (available cubes, measures, dimensions)."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.api_url}/meta",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Error fetching metadata: {str(e)}")
            raise

    async def health_check(self) -> bool:
        """Check if Cube.js is accessible."""
        try:
            await self.get_meta()
            return True
        except Exception:
            return False


# Global client instance
cubejs_client = CubeJSClient()
