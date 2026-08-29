"""Shell execution tool with safety controls."""

from __future__ import annotations

import logging
import subprocess
import time
from typing import Any

from autonomous_agent.config.settings import PermissionLevel
from autonomous_agent.core.models import ToolResult
from autonomous_agent.tools.base import Tool

logger = logging.getLogger(__name__)

# Commands that require special approval
DESTRUCTIVE_COMMANDS = {
    "rm -rf", "rm -r", "rmdir", "mkfs", "dd ", "format",
    "shutdown", "reboot", "halt", "init 0", "init 6",
    "git push --force", "git reset --hard", "git clean -f",
    "drop table", "truncate", "delete from",
}


class ShellTool(Tool):
    """Execute shell commands with safety controls."""

    name = "shell"
    description = "Execute a shell command"
    permission_level = PermissionLevel.DEVELOPMENT_WRITE
    timeout_seconds = 120

    def validate_permissions(self, environment: str) -> bool:
        """Block shell execution in production and unknown environments."""
        if environment in ("production", "unknown"):
            logger.warning("Shell execution not recommended in %s", environment)
            return False
        return True

    def execute(self, **kwargs: Any) -> ToolResult:
        command = kwargs.get("command", "")
        cwd = kwargs.get("cwd", None)
        timeout = kwargs.get("timeout", self.timeout_seconds)

        if not command:
            return ToolResult(success=False, error="No command provided")

        # Check for destructive commands
        cmd_lower = command.lower().strip()
        for destructive in DESTRUCTIVE_COMMANDS:
            if destructive in cmd_lower:
                logger.warning("Destructive command detected: %s", command)
                return ToolResult(
                    success=False,
                    error=f"Destructive command requires explicit approval: {command}",
                )

        try:
            start = time.time()
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
            )
            duration = time.time() - start

            output = result.stdout
            if result.stderr:
                output += f"\n[stderr]\n{result.stderr}"

            return ToolResult(
                success=result.returncode == 0,
                output=output.strip(),
                error=result.stderr.strip() if result.returncode != 0 else "",
                exit_code=result.returncode,
                duration_seconds=round(duration, 3),
            )
        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                error=f"Command timed out after {timeout}s: {command}",
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))
