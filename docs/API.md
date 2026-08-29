# REST API Reference

> **Author:** Virender Dhiman

The Autonomous Agent exposes a REST API via FastAPI. Start it with:

```bash
uvicorn autonomous_agent.api.app:app --reload
```

Base URL: `http://localhost:8000`

## Endpoints

### `GET /`

Root endpoint. Returns service info.

**Response:**
```json
{
  "service": "autonomous-agent",
  "version": "0.1.0",
  "status": "running"
}
```

### `GET /health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

### `POST /tasks`

Create and run a new task. The agent will autonomously work through the full lifecycle.

**Request Body:**
```json
{
  "problem": "Fix the broken login form validation",
  "repository": "owner/repo",
  "branch": "main",
  "environment": "development",
  "provider": "mock",
  "constraints": ["Do not break existing auth"]
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `problem` | string | ✅ | — | The problem to solve |
| `repository` | string | ❌ | null | Repository path or owner/repo |
| `branch` | string | ❌ | `"main"` | Branch to work on |
| `environment` | string | ❌ | `"development"` | Target environment |
| `provider` | string | ❌ | null | AI provider (mock/opensource/n8n) |
| `constraints` | string[] | ❌ | `[]` | Constraints to respect |

**Response (200):**
```json
{
  "id": "abc-123-def",
  "problem": "Fix the broken login form validation",
  "status": "completed",
  "state": "resolved",
  "repository": "owner/repo",
  "branch": "main",
  "environment": "development",
  "agent_team": ["investigator", "developer", "qa"],
  "error_message": null
}
```

### `GET /tasks/{task_id}`

Get the status of a task, including quality score and evidence count.

**Response (200):**
```json
{
  "task": {
    "id": "abc-123-def",
    "problem": "Fix the broken login form validation",
    "status": "completed",
    "state": "resolved",
    "repository": "owner/repo",
    "branch": "main",
    "environment": "development",
    "agent_team": ["investigator", "developer", "qa"],
    "error_message": null
  },
  "quality_score": 100.0,
  "completion_gates": {
    "problem_understood": true,
    "acceptance_criteria_met": true,
    "tests_passed": true,
    "evidence_exists": true,
    "no_contradictions": true,
    "no_unresolved_failures": true
  },
  "evidence_count": 11
}
```

### `POST /tasks/{task_id}/resume`

Resume an interrupted task from its last persisted state.

**Response (200):** Same as `POST /tasks`.

**Error (404):** Task not found.

### `POST /tasks/{task_id}/cancel`

Cancel a running task.

**Response (200):**
```json
{
  "id": "abc-123-def",
  "status": "cancelled",
  "state": "cancelled",
  ...
}
```

### `GET /tasks/{task_id}/report`

Get the final evidence report for a task.

**Response (200):**
```json
{
  "task_id": "abc-123-def",
  "report": "# Evidence Report\n\n## Task: ..."
}
```

### `GET /tools`

List all available tools.

**Response (200):**
```json
[
  {
    "name": "file_read",
    "description": "Read the contents of a file at the given path",
    "permission": "read_only"
  },
  {
    "name": "shell",
    "description": "Execute a shell command",
    "permission": "development_write"
  }
]
```

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message here"
}
```

Common HTTP status codes:
- `200` — Success
- `404` — Task or report not found
- `422` — Validation error (invalid request body)
- `500` — Internal server error

## Interactive Docs

FastAPI provides interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
