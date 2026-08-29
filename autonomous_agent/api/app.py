"""REST API for the autonomous agent system."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from autonomous_agent import __version__

app = FastAPI(
    title="Autonomous Agent API",
    version=__version__,
    description="Universal Autonomous Agentic Engineering System API",
)


# --- Request / Response Models ---


class TaskRequest(BaseModel):
    """Request to create a new task."""

    problem: str
    repository: str | None = None
    branch: str = "main"
    environment: str = "development"
    provider: str | None = None
    constraints: list[str] = Field(default_factory=list)


class TaskResponse(BaseModel):
    """Response with task details."""

    id: str
    problem: str
    status: str
    state: str
    repository: str | None = None
    branch: str = "main"
    environment: str = "development"
    agent_team: list[str] = Field(default_factory=list)
    error_message: str | None = None


class StatusResponse(BaseModel):
    """Task status response."""

    task: TaskResponse
    quality_score: float = 0.0
    completion_gates: dict[str, bool] = Field(default_factory=dict)
    evidence_count: int = 0


class RunResponse(BaseModel):
    """Response from running a task."""

    task: TaskResponse
    quality_score: str = "0.0"
    display_score: str = "0.0/10"
    completion_gates: dict[str, bool] = Field(default_factory=dict)
    report_path: str | None = None


# --- Endpoints ---


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "autonomous-agent", "version": __version__, "status": "running"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.post("/tasks", response_model=TaskResponse)
def create_task(request: TaskRequest) -> TaskResponse:
    """Create and run a new task."""
    from autonomous_agent.config.settings import ProviderType
    from autonomous_agent.core.models import Task
    from autonomous_agent.core.orchestrator import Orchestrator
    from autonomous_agent.providers.router import create_provider

    task = Task(
        problem=request.problem,
        repository=request.repository,
        branch=request.branch,
        environment=request.environment,
        constraints=request.constraints,
    )

    ptype = ProviderType(request.provider) if request.provider else None
    provider = create_provider(ptype)

    orch = Orchestrator(task=task, provider=provider)
    result = orch.run()

    return TaskResponse(
        id=result.id,
        problem=result.problem,
        status=result.status.value,
        state=result.state,
        repository=result.repository,
        branch=result.branch,
        environment=result.environment,
        agent_team=result.agent_team,
        error_message=result.error_message,
    )


@app.get("/tasks/{task_id}", response_model=StatusResponse)
def get_task_status(task_id: str) -> StatusResponse:
    """Get the status of a task."""
    task_path = Path("./agent-work/tasks") / task_id / "task.json"
    if not task_path.exists():
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")

    task_data = json.loads(task_path.read_text(encoding="utf-8"))
    task_resp = TaskResponse(
        id=task_data["id"],
        problem=task_data["problem"],
        status=task_data["status"],
        state=task_data["state"],
        repository=task_data.get("repository"),
        branch=task_data.get("branch", "main"),
        environment=task_data.get("environment", "development"),
        agent_team=task_data.get("agent_team", []),
        error_message=task_data.get("error_message"),
    )

    # Load evidence
    evidence_path = Path("./agent-work/tasks") / task_id / "evidence.json"
    evidence_count = 0
    quality_score = 0.0
    completion_gates: dict[str, bool] = {}
    if evidence_path.exists():
        evidence_data = json.loads(evidence_path.read_text(encoding="utf-8"))
        evidence_count = len(evidence_data.get("evidence", []))

    return StatusResponse(
        task=task_resp,
        quality_score=quality_score,
        completion_gates=completion_gates,
        evidence_count=evidence_count,
    )


@app.post("/tasks/{task_id}/resume", response_model=TaskResponse)
def resume_task(task_id: str) -> TaskResponse:
    """Resume an interrupted task."""
    from autonomous_agent.core.orchestrator import Orchestrator
    from autonomous_agent.providers.router import create_provider

    try:
        provider = create_provider()
        orch = Orchestrator.resume(task_id, provider)
        result = orch.run()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")

    return TaskResponse(
        id=result.id,
        problem=result.problem,
        status=result.status.value,
        state=result.state,
        repository=result.repository,
        branch=result.branch,
        environment=result.environment,
        agent_team=result.agent_team,
        error_message=result.error_message,
    )


@app.post("/tasks/{task_id}/cancel", response_model=TaskResponse)
def cancel_task(task_id: str) -> TaskResponse:
    """Cancel a running task."""
    task_path = Path("./agent-work/tasks") / task_id / "task.json"
    if not task_path.exists():
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")

    task_data = json.loads(task_path.read_text(encoding="utf-8"))
    task_data["status"] = "cancelled"
    task_data["state"] = "cancelled"
    task_path.write_text(json.dumps(task_data, indent=2, default=str), encoding="utf-8")

    return TaskResponse(
        id=task_data["id"],
        problem=task_data["problem"],
        status="cancelled",
        state="cancelled",
        repository=task_data.get("repository"),
        branch=task_data.get("branch", "main"),
        environment=task_data.get("environment", "development"),
        agent_team=task_data.get("agent_team", []),
    )


@app.get("/tasks/{task_id}/report")
def get_task_report(task_id: str) -> dict[str, str]:
    """Get the final report of a task."""
    report_path = Path("./agent-work/tasks") / task_id / "FINAL_REPORT.md"
    if not report_path.exists():
        raise HTTPException(status_code=404, detail=f"Report not found for task: {task_id}")

    return {"task_id": task_id, "report": report_path.read_text(encoding="utf-8")}


@app.get("/tools")
def list_tools() -> list[dict[str, str]]:
    """List available tools."""
    from autonomous_agent.tools import get_registry

    return get_registry().list_tools()
