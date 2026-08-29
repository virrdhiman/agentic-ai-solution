"""Filesystem tools for reading, writing, and listing files."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from autonomous_agent.config.settings import PermissionLevel
from autonomous_agent.core.models import ToolResult
from autonomous_agent.tools.base import Tool


class FileReadTool(Tool):
    """Read the contents of a file."""

    name = "file_read"
    description = "Read the contents of a file at the given path"
    permission_level = PermissionLevel.READ_ONLY

    def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path", "")
        if not path:
            return ToolResult(success=False, error="No path provided")
        try:
            p = Path(path)
            if not p.exists():
                return ToolResult(success=False, error=f"File not found: {path}")
            if not p.is_file():
                return ToolResult(success=False, error=f"Not a file: {path}")
            content = p.read_text(encoding="utf-8", errors="replace")
            return ToolResult(success=True, output=content)
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class FileWriteTool(Tool):
    """Write content to a file."""

    name = "file_write"
    description = "Write content to a file at the given path (creates parent dirs)"
    permission_level = PermissionLevel.DEVELOPMENT_WRITE

    def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path", "")
        content = kwargs.get("content", "")
        if not path:
            return ToolResult(success=False, error="No path provided")
        try:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            return ToolResult(success=True, output=f"Written {len(content)} bytes to {path}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class ListDirectoryTool(Tool):
    """List files and directories in a path."""

    name = "list_directory"
    description = "List files and directories at the given path"
    permission_level = PermissionLevel.READ_ONLY

    def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path", ".")
        try:
            p = Path(path)
            if not p.exists():
                return ToolResult(success=False, error=f"Path not found: {path}")
            entries = sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
            lines = []
            for entry in entries:
                prefix = "📁" if entry.is_dir() else "📄"
                lines.append(f"{prefix} {entry.name}")
            return ToolResult(success=True, output="\n".join(lines))
        except Exception as e:
            return ToolResult(success=False, error=str(e))
