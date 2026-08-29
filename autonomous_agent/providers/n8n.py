"""n8N provider — delegates workflow orchestration to n8N.

NOTE: This provider requires an n8N instance with API access.
When n8N is unavailable, the system falls back to the configured fallback provider.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from autonomous_agent.config.settings import get_settings
from autonomous_agent.providers.base import AIProvider

logger = logging.getLogger(__name__)


class N8NProvider(AIProvider):
    """Provider that delegates to n8N for workflow orchestration.

    REQUIRES: N8N_BASE_URL and N8N_API_KEY environment variables.
    """

    def __init__(self, **kwargs: Any) -> None:
        settings = get_settings()
        self.base_url = settings.n8n_base_url
        self.api_key = settings.n8n_api_key
        if not self.base_url or not self.api_key:
            raise RuntimeError(
                "N8NProvider requires N8N_BASE_URL and N8N_API_KEY. "
                "Set them in .env or environment."
            )
        self._client = httpx.Client(timeout=120.0)
        logger.info("n8N provider initialized: %s", self.base_url)

    def _trigger_workflow(self, workflow_id: str, data: dict[str, Any]) -> Any:
        """Trigger an n8N workflow."""
        url = f"{self.base_url.rstrip('/')}/api/v1/workflows/{workflow_id}/run"
        headers = {"X-N8N-API-KEY": self.api_key, "Content-Type": "application/json"}
        try:
            response = self._client.post(url, json={"data": data}, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error("n8N workflow trigger failed: %s", e)
            raise

    def analyze(self, prompt: str, *, context: dict[str, Any] | None = None) -> Any:
        raise NotImplementedError("n8N workflow integration requires configured workflows")

    def plan(self, prompt: str, *, context: dict[str, Any] | None = None) -> Any:
        raise NotImplementedError("n8N workflow integration requires configured workflows")

    def generate(self, prompt: str, *, context: dict[str, Any] | None = None) -> Any:
        raise NotImplementedError("n8N workflow integration requires configured workflows")

    def debug(self, prompt: str, *, context: dict[str, Any] | None = None) -> Any:
        raise NotImplementedError("n8N workflow integration requires configured workflows")

    def review(self, prompt: str, *, context: dict[str, Any] | None = None) -> Any:
        raise NotImplementedError("n8N workflow integration requires configured workflows")

    def summarize(self, prompt: str, *, context: dict[str, Any] | None = None) -> Any:
        raise NotImplementedError("n8N workflow integration requires configured workflows")
