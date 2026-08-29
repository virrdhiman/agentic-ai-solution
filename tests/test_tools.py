"""Tests for the tool layer."""

import tempfile
from pathlib import Path

from autonomous_agent.tools.base import ToolRegistry, get_registry
from autonomous_agent.tools.filesystem import FileReadTool, FileWriteTool, ListDirectoryTool
from autonomous_agent.tools.shell import ShellTool
from autonomous_agent.tools.git import GitTool
from autonomous_agent.core.models import ToolResult


class TestFileReadTool:
    def test_read_existing_file(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello world")
        tool = FileReadTool()
        result = tool.execute(path=str(f))
        assert result.success is True
        assert result.output == "hello world"

    def test_read_nonexistent_file(self):
        tool = FileReadTool()
        result = tool.execute(path="/nonexistent/file.txt")
        assert result.success is False
        assert "not found" in result.error.lower()

    def test_read_no_path(self):
        tool = FileReadTool()
        result = tool.execute()
        assert result.success is False


class TestFileWriteTool:
    def test_write_file(self, tmp_path):
        f = tmp_path / "output.txt"
        tool = FileWriteTool()
        result = tool.execute(path=str(f), content="test content")
        assert result.success is True
        assert f.read_text() == "test content"

    def test_write_creates_dirs(self, tmp_path):
        f = tmp_path / "sub" / "dir" / "file.txt"
        tool = FileWriteTool()
        result = tool.execute(path=str(f), content="nested")
        assert result.success is True
        assert f.read_text() == "nested"

    def test_write_no_path(self):
        tool = FileWriteTool()
        result = tool.execute(content="test")
        assert result.success is False


class TestListDirectoryTool:
    def test_list_directory(self, tmp_path):
        (tmp_path / "a.txt").write_text("a")
        (tmp_path / "b.txt").write_text("b")
        (tmp_path / "subdir").mkdir()
        tool = ListDirectoryTool()
        result = tool.execute(path=str(tmp_path))
        assert result.success is True
        assert "a.txt" in result.output
        assert "b.txt" in result.output
        assert "subdir" in result.output

    def test_list_nonexistent(self):
        tool = ListDirectoryTool()
        result = tool.execute(path="/nonexistent/path")
        assert result.success is False


class TestShellTool:
    def test_echo_command(self):
        tool = ShellTool()
        result = tool.execute(command="echo hello")
        assert result.success is True
        assert "hello" in result.output

    def test_failing_command(self):
        tool = ShellTool()
        result = tool.execute(command="false")
        assert result.success is False

    def test_destructive_command_blocked(self):
        tool = ShellTool()
        result = tool.execute(command="rm -rf /tmp/test")
        assert result.success is False
        assert "destructive" in result.error.lower() or "approval" in result.error.lower()

    def test_no_command(self):
        tool = ShellTool()
        result = tool.execute()
        assert result.success is False

    def test_cwd_option(self, tmp_path):
        tool = ShellTool()
        result = tool.execute(command="pwd", cwd=str(tmp_path))
        assert result.success is True
        assert len(result.output) > 0

    def test_permission_in_production(self):
        tool = ShellTool()
        result = tool.safe_execute(environment="production", command="echo test")
        assert result.success is False


class TestGitTool:
    def test_git_status(self):
        tool = GitTool()
        result = tool.execute(action="status")
        # May succeed or fail depending on git state, but shouldn't crash
        assert isinstance(result, ToolResult)

    def test_git_log(self):
        tool = GitTool()
        result = tool.execute(action="log")
        assert isinstance(result, ToolResult)

    def test_unknown_action(self):
        tool = GitTool()
        result = tool.execute(action="nonexistent_action")
        assert result.success is False
        assert "unknown" in result.error.lower()

    def test_push_blocked(self):
        tool = GitTool()
        result = tool.execute(action="push")
        assert result.success is False
        assert "approval" in result.error.lower()


class TestToolRegistry:
    def test_singleton(self):
        r1 = get_registry()
        r2 = get_registry()
        assert r1 is r2

    def test_built_in_tools_registered(self):
        registry = get_registry()
        tools = registry.list_tools()
        names = [t["name"] for t in tools]
        assert "file_read" in names
        assert "file_write" in names
        assert "list_directory" in names
        assert "shell" in names
        assert "git" in names

    def test_get_tool(self):
        registry = get_registry()
        tool = registry.get("shell")
        assert tool is not None
        assert tool.name == "shell"

    def test_get_nonexistent_tool(self):
        registry = get_registry()
        tool = registry.get("nonexistent")
        assert tool is None

    def test_execute_unknown_tool(self):
        registry = get_registry()
        result = registry.execute("nonexistent")
        assert result.success is False
        assert "not found" in result.error.lower()

    def test_custom_tool_registration(self):
        registry = ToolRegistry()

        class MyTool:
            name = "my_tool"
            description = "Custom"
            permission_level = __import__("autonomous_agent.config.settings", fromlist=["PermissionLevel"]).PermissionLevel.READ_ONLY

            def validate_permissions(self, env):
                return True

            def safe_execute(self, **kwargs):
                from autonomous_agent.core.models import ToolResult
                return ToolResult(success=True, output="custom")

        registry.register(MyTool())
        assert registry.get("my_tool") is not None
