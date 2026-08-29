"""Git operations tool."""

from __future__ import annotations

import logging
from typing import Any

from autonomous_agent.config.settings import PermissionLevel
from autonomous_agent.core.models import ToolResult
from autonomous_agent.tools.base import Tool

logger = logging.getLogger(__name__)


class GitTool(Tool):
    """Perform Git operations with safety checks."""

    name = "git"
    description = "Execute git commands (status, diff, log, branch, add, commit)"
    permission_level = PermissionLevel.DEVELOPMENT_WRITE
    timeout_seconds = 60

    def execute(self, **kwargs: Any) -> ToolResult:
        """Execute a git operation.

        Supported actions: status, diff, log, branch, add, commit, push,
        pull, stash, revert, reset_soft, branch_create, branch_switch.

        Dangerous operations (push, revert) require explicit approval.
        """
        action = kwargs.get("action", "status")
        cwd = kwargs.get("cwd", None)
        args = kwargs.get("args", "")

        from autonomous_agent.tools.shell import ShellTool

        shell = ShellTool()

        git_commands = {
            "status": "git status",
            "diff": "git diff",
            "diff_staged": "git diff --staged",
            "log": "git log --oneline -20",
            "branch": "git branch -a",
            "add": f"git add {args}" if args else "git add .",
            "commit": f'git commit -m "{args}"' if args else "git commit",
            "push": f"git push {args}" if args else "git push",
            "pull": "git pull",
            "branch_create": f"git checkout -b {args}" if args else "",
            "branch_switch": f"git checkout {args}" if args else "",
            "stash": "git stash",
            "stash_pop": "git stash pop",
            "revert": f"git revert {args}" if args else "",
            "reset_soft": f"git reset --soft {args}" if args else "",
        }

        # Safety check for destructive git operations
        destructive = {"push", "revert"}
        if action in destructive:
            logger.warning("Destructive git operation: %s", action)
            return ToolResult(
                success=False,
                error=f"Git operation '{action}' requires explicit approval",
            )

        command = git_commands.get(action)
        if not command:
            return ToolResult(success=False, error=f"Unknown git action: {action}")

        return shell.execute(command=command, cwd=cwd)
