"""Abstract base class for all AI providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional


class AIProvider(ABC):
    """Provider interface that all AI backends must implement.

    The Agent Core depends only on this interface, never on specific providers.
    """

    @abstractmethod
    def analyze(self, prompt: str, *, context: dict[str, Any] | None = None) -> Any:
        """Analyze a problem or situation."""
        ...

    @abstractmethod
    def plan(self, prompt: str, *, context: dict[str, Any] | None = None) -> Any:
        """Create an execution plan."""
        ...

    @abstractmethod
    def generate(self, prompt: str, *, context: dict[str, Any] | None = None) -> Any:
        """Generate code, text, or a response."""
        ...

    @abstractmethod
    def debug(self, prompt: str, *, context: dict[str, Any] | None = None) -> Any:
        """Debug a problem."""
        ...

    @abstractmethod
    def review(self, prompt: str, *, context: dict[str, Any] | None = None) -> Any:
        """Review code, tests, or results."""
        ...

    @abstractmethod
    def summarize(self, prompt: str, *, context: dict[str, Any] | None = None) -> Any:
        """Summarize information."""
        ...
