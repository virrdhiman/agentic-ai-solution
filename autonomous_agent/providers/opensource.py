"""Open-source AI provider — connects to any OpenAI-compatible API.

Supports: Ollama, vLLM, LM Studio, LocalAI, and any OpenAI-compatible endpoint.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from autonomous_agent.config.settings import get_settings
from autonomous_agent.providers.base import AIProvider

logger = logging.getLogger(__name__)


class OpenSourceProvider(AIProvider):
    """Provider that calls an OpenAI-compatible API."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        settings = get_settings()
        self.base_url = (base_url or settings.ai_base_url).rstrip("/")
        self.api_key = api_key or settings.ai_api_key or "not-needed"
        self.model = model or settings.ai_model
        self._client = httpx.Client(timeout=120.0)

    def _chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        """Send a chat completion request to the OpenAI-compatible API.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            **kwargs: Optional overrides for temperature, max_tokens, etc.

        Returns:
            The assistant's response text.

        Raises:
            RuntimeError: If the API request fails.
        """
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.3),
            "max_tokens": kwargs.get("max_tokens", 4096),
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        try:
            response = self._client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except httpx.HTTPError as e:
            logger.error("Provider request failed: %s", e)
            raise RuntimeError(f"AI provider request failed: {e}") from e

    def _format_context(self, prompt: str, context: dict[str, Any] | None) -> list[dict[str, str]]:
        """Format a prompt and optional context into chat messages.

        Creates a system message with the agent persona and a user message
        containing the prompt and any additional context.
        """
        system_msg = "You are an autonomous engineering agent. Analyze problems, find root causes, and propose solutions. Be precise and evidence-based."
        user_content = prompt
        if context:
            user_content += "\n\nContext:\n"
            for k, v in context.items():
                user_content += f"- {k}: {v}\n"
        return [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_content},
        ]

    def analyze(self, prompt: str, *, context: dict[str, Any] | None = None) -> Any:
        """Analyze a problem via the AI API."""
        messages = self._format_context(prompt, context)
        response = self._chat(messages)
        return {"analysis": response}

    def plan(self, prompt: str, *, context: dict[str, Any] | None = None) -> Any:
        """Create an execution plan via the AI API."""
        messages = self._format_context(
            f"Create a step-by-step execution plan for:\n{prompt}", context
        )
        response = self._chat(messages)
        return {"plan": response}

    def generate(self, prompt: str, *, context: dict[str, Any] | None = None) -> Any:
        """Generate code or a response via the AI API."""
        messages = self._format_context(prompt, context)
        response = self._chat(messages)
        return {"generated": response}

    def debug(self, prompt: str, *, context: dict[str, Any] | None = None) -> Any:
        """Debug a problem and find root cause via the AI API."""
        messages = self._format_context(
            f"Debug and find root cause:\n{prompt}", context
        )
        response = self._chat(messages)
        return {"diagnosis": response}

    def review(self, prompt: str, *, context: dict[str, Any] | None = None) -> Any:
        """Review code, tests, or results via the AI API."""
        messages = self._format_context(
            f"Review this thoroughly:\n{prompt}", context
        )
        response = self._chat(messages)
        return {"review": response}

    def summarize(self, prompt: str, *, context: dict[str, Any] | None = None) -> Any:
        """Summarize information via the AI API."""
        messages = self._format_context(f"Summarize:\n{prompt}", context)
        response = self._chat(messages)
        return {"summary": response}

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass
