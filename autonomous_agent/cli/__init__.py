"""CLI entry point for the autonomous agent system."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from autonomous_agent import __version__

console = Console()


def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


@click.group()
@click.version_option(version=__version__, prog_name="autonomous-agent")
@click.option("--log-level", default="INFO", help="Log level")
def main(log_level: str) -> None:
    """Universal Autonomous Agentic Engineering System.

    An autonomous engineering worker that investigates problems, uses tools,
    changes systems, tests its work, and proves when problems are solved.
    """
    setup_logging(log_level)


@main.command()
@click.argument("problem")
@click.option("--repository", "-r", default=None, help="Repository path or owner/repo")
@click.option("--branch", "-b", default="main", help="Branch to work on")
@click.option("--environment", "-e", default="development", help="Target environment")
@click.option("--provider", "-p", default=None, help="AI provider (opensource/n8n/mock)")
@click.option("--constraint", "-c", multiple=True, help="Constraints (repeatable)")
def run(problem: str, repository: str | None, branch: str, environment: str, provider: str | None, constraint: tuple[str, ...]) -> None:
    """Run the autonomous agent on a problem."""
    from autonomous_agent.config.settings import ProviderType
    from autonomous_agent.core.models import Task
    from autonomous_agent.core.orchestrator import Orchestrator
    from autonomous_agent.providers.router import create_provider

    console.print(Panel(f"[bold green]🤖 Autonomous Agent v{__version__}[/bold green]", title="Starting"))
    console.print(f"[bold]Problem:[/bold] {problem}")
    console.print(f"[bold]Environment:[/bold] {environment}")
    console.print(f"[bold]Branch:[/bold] {branch}")

    # Create task
    task = Task(
        problem=problem,
        repository=repository,
        branch=branch,
        environment=environment,
        constraints=list(constraint),
    )
    console.print(f"[bold]Task ID:[/bold] {task.id}")

    # Create provider
    ptype = ProviderType(provider) if provider else None
    ai_provider = create_provider(ptype)
    console.print(f"[bold]Provider:[/bold] {type(ai_provider).__name__}")

    # Run orchestrator
    console.print("\n[cyan]▶ Running lifecycle...[/cyan]")
    orch = Orchestrator(task=task, provider=ai_provider)
    result = orch.run()

    # Display results
    console.print()
    if result.status.value == "completed":
        console.print(Panel("[bold green]✅ RESOLVED[/bold green]", title="Result"))
    elif result.status.value == "blocked":
        console.print(Panel("[bold yellow]⚠️ HUMAN ACTION REQUIRED[/bold yellow]", title="Result"))
    else:
        console.print(Panel(f"[bold red]❌ {result.status.value.upper()}[/bold red]", title="Result"))

    # Show quality score
    quality = orch.evidence_engine.calculate_quality()
    console.print(f"\n[bold]Quality Score:[/bold] {quality.display_score}")

    # Show gates
    gates = orch.evidence_engine.verify_completion()
    gate_table = Table(title="Completion Gates")
    gate_table.add_column("Gate", style="bold")
    gate_table.add_column("Status")
    for gate, passed in gates.items():
        icon = "✅" if passed else "❌"
        gate_table.add_row(gate, icon)
    console.print(gate_table)

    # Show report location
    report_path = orch.work_dir / "FINAL_REPORT.md"
    if report_path.exists():
        console.print(f"\n[bold]Report:[/bold] {report_path}")

    if result.error_message:
        console.print(f"\n[bold red]Error:[/bold red] {result.error_message}")


@main.command()
@click.argument("task_id")
def status(task_id: str) -> None:
    """Show the status of a task."""
    task_path = Path("./agent-work/tasks") / task_id / "task.json"
    if not task_path.exists():
        console.print(f"[red]Task not found: {task_id}[/red]")
        sys.exit(1)

    task_data = json.loads(task_path.read_text(encoding="utf-8"))
    table = Table(title=f"Task {task_id}")
    table.add_column("Field", style="bold")
    table.add_column("Value")
    for key, value in task_data.items():
        table.add_row(key, str(value))
    console.print(table)


@main.command()
@click.argument("task_id")
def report(task_id: str) -> None:
    """Show the final report of a task."""
    report_path = Path("./agent-work/tasks") / task_id / "FINAL_REPORT.md"
    if not report_path.exists():
        console.print(f"[red]Report not found for task: {task_id}[/red]")
        sys.exit(1)

    content = report_path.read_text(encoding="utf-8")
    console.print(Panel(content, title="Final Report"))


@main.command()
@click.argument("task_id")
def resume(task_id: str) -> None:
    """Resume a previously interrupted task."""
    from autonomous_agent.core.orchestrator import Orchestrator
    from autonomous_agent.providers.router import create_provider

    console.print(f"[cyan]▶ Resuming task {task_id}...[/cyan]")
    ai_provider = create_provider()
    orch = Orchestrator.resume(task_id, ai_provider)
    result = orch.run()

    if result.status.value == "completed":
        console.print("[bold green]✅ RESOLVED[/bold green]")
    else:
        console.print(f"[bold]Status: {result.status.value}[/bold]")


@main.command()
@click.argument("task_id")
def cancel(task_id: str) -> None:
    """Cancel a running task."""
    from autonomous_agent.core.state import TaskState

    task_path = Path("./agent-work/tasks") / task_id / "task.json"
    if not task_path.exists():
        console.print(f"[red]Task not found: {task_id}[/red]")
        sys.exit(1)

    task_data = json.loads(task_path.read_text(encoding="utf-8"))
    task_data["status"] = "cancelled"
    task_data["state"] = TaskState.CANCELLED.value
    task_path.write_text(json.dumps(task_data, indent=2, default=str), encoding="utf-8")
    console.print(f"[green]Task {task_id} cancelled.[/green]")


@main.command()
def tools() -> None:
    """List available tools."""
    from autonomous_agent.tools import get_registry

    registry = get_registry()
    table = Table(title="Available Tools")
    table.add_column("Name", style="bold")
    table.add_column("Description")
    table.add_column("Permission")
    for tool_info in registry.list_tools():
        table.add_row(tool_info["name"], tool_info["description"], tool_info["permission"])
    console.print(table)


@main.command()
def info() -> None:
    """Show system information."""
    from autonomous_agent.config.settings import get_settings

    settings = get_settings()
    table = Table(title="System Configuration")
    table.add_column("Setting", style="bold")
    table.add_column("Value")
    table.add_row("Provider", settings.agent_provider.value)
    table.add_row("AI Model", settings.ai_model)
    table.add_row("Environment", settings.environment.value)
    table.add_row("Database URL", settings.database_url.split("@")[-1] if "@" in settings.database_url else settings.database_url)
    table.add_row("Max Retries", str(settings.max_retries))
    table.add_row("Task Timeout", f"{settings.task_timeout}s")
    console.print(table)


if __name__ == "__main__":
    main()
