"""Tool base class and registry."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

from autonomous_agent.config.settings import PermissionLevel
from autonomous_agent.core.models import ToolResult

logger = logging.getLogger(__name__)


class Tool(ABC):
    """Base class for all tools.

    Every tool must define its name, description, permission level,
    and implement the execute method.
    """

    name: str = "base_tool"
    description: str = "Base tool"
    permission_level: PermissionLevel = PermissionLevel.READ_ONLY
    timeout_seconds: int = 60
    max_retries: int = 1

    @abstractmethod
    def execute(self, **kwargs: Any) -> ToolResult:
        """Execute the tool with the given arguments."""
        ...

    def validate_permissions(self, environment: str) -> bool:
        """Check if the tool is allowed in the given environment."""
        if environment == "production" and self.permission_level in (
            PermissionLevel.PRODUCTION_APPROVAL_REQUIRED,
            PermissionLevel.DESTRUCTIVE,
        ):
            logger.warning(
                "Tool %s requires approval in production environment", self.name
            )
            return False
        return True

    def safe_execute(self, environment: str = "development", **kwargs: Any) -> ToolResult:
        """Execute with permission checking and error handling."""
        if not self.validate_permissions(environment):
            return ToolResult(
                success=False,
                error=f"Tool {self.name} not permitted in {environment} environment",
            )
        try:
            return self.execute(**kwargs)
        except Exception as e:
            logger.error("Tool %s execution failed: %s", self.name, e)
            return ToolResult(success=False, error=str(e))


class ToolRegistry:
    """Central registry of all available tools.

    Provides tool lookup, listing, and execution with permission checking.
    A singleton instance is created by get_registry().
    """

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Register a tool in the registry."""
        self._tools[tool.name] = tool
        logger.debug("Registered tool: %s", tool.name)

    def get(self, name: str) -> Tool | None:
        """Look up a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> list[dict[str, str]]:
        """Return a list of all registered tools with their metadata."""
        return [
            {"name": t.name, "description": t.description, "permission": t.permission_level.value}
            for t in self._tools.values()
        ]

    def execute(self, tool_name: str, environment: str = "development", **kwargs: Any) -> ToolResult:
        """Execute a tool by name with permission checking."""
        tool = self.get(tool_name)
        if tool is None:
            return ToolResult(success=False, error=f"Tool not found: {tool_name}")
        return tool.safe_execute(environment=environment, **kwargs)


# Singleton registry
_registry: ToolRegistry | None = None


def get_registry() -> ToolRegistry:
    """Get or create the singleton tool registry.

    On first call, creates the registry and registers all built-in tools.
    """
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
        # Register built-in tools
        from autonomous_agent.tools.filesystem import FileReadTool, FileWriteTool, ListDirectoryTool
        from autonomous_agent.tools.shell import ShellTool
        from autonomous_agent.tools.git import GitTool

        _registry.register(FileReadTool())
        _registry.register(FileWriteTool())
        _registry.register(ListDirectoryTool())
        _registry.register(ShellTool())
        _registry.register(GitTool())
    return _registry
