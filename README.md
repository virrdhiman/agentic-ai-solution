# Autonomous Agent — Universal Agentic Engineering System

> An autonomous engineering worker that investigates problems, uses tools, changes systems, tests its work, learns from failure, repairs itself, documents the work, and proves when the problem is actually solved.

**Author:** Virender Dhiman

---

## What It Does

Receives **any digitally accessible problem statement** and autonomously:

```
UNDERSTAND → CLASSIFY → INVESTIGATE → REPRODUCE → DIAGNOSE → PLAN
→ EXECUTE → TEST → ANALYSE FAILURE → REPAIR → RETEST
→ REGRESSION TEST → REVIEW → CHALLENGE → VERIFY
→ DOCUMENT → UPDATE PROJECT → CLOSE
```

The system continues working until the problem is **objectively resolved**, not merely until an AI model says it is resolved.

## Architecture

```
                    ┌──────────────────────┐
                    │      USER / API      │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │ UNIVERSAL PROBLEM    │
                    │      ROUTER          │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │    AGENT CORE        │
                    │  Orchestrator        │
                    │  State Machine       │
                    │  Evidence Engine     │
                    │  Quality Engine      │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │  DYNAMIC AGENT TEAM  │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │   PROVIDER LAYER     │
                    │  Mock / OpenSource   │
                    │  n8n                 │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │      TOOL LAYER      │
                    │  Git / Shell / Files  │
                    │  Browser / Docker    │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │   TEST & QUALITY     │
                    │  Test → Repair Loop  │
                    │  Review → Verify     │
                    └──────────────────────┘
```

## Quick Start

### Install

```bash
pip install -e ".[dev]"
```

### Run

```bash
agent run "Fix the broken login page"
```

### With a specific provider

```bash
agent run --provider opensource "Fix the database query performance"
```

### Check status

```bash
agent status <task-id>
```

### View report

```bash
agent report <task-id>
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `agent run "problem"` | Run the agent on a problem |
| `agent status <id>` | Show task status |
| `agent report <id>` | Show final report |
| `agent resume <id>` | Resume an interrupted task |
| `agent cancel <id>` | Cancel a task |
| `agent tools` | List available tools |
| `agent info` | Show system configuration |

## REST API

```bash
# Start the API server
uvicorn autonomous_agent.api.app:app --reload

# Create a task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"problem": "Fix the broken API endpoint"}'

# Get task status
curl http://localhost:8000/tasks/{task-id}

# Get report
curl http://localhost:8000/tasks/{task-id}/report
```

## Configuration

Copy `.env.example` to `.env` and configure:

```env
AGENT_PROVIDER=mock          # mock | opensource | n8n
AI_BASE_URL=http://localhost:11434/v1
AI_MODEL=llama3
DATABASE_URL=sqlite+aiosqlite:///./agent.db
ENVIRONMENT=development
```

## Providers

| Provider | Description | Requirements |
|----------|-------------|--------------|
| **mock** | Deterministic test responses | None |
| **opensource** | Any OpenAI-compatible API (Ollama, vLLM, LM Studio) | AI_BASE_URL |
| **n8n** | n8N workflow orchestration | N8N_BASE_URL, N8N_API_KEY |

## Docker

```bash
# Full stack (agent + postgres + redis + ollama)
docker compose --profile full up

# Just the API
docker compose --profile api up

# With local LLM
docker compose --profile opensource up
```

## Problem Types

The system automatically classifies problems into categories:

- Software bugs, Feature requests
- Website / Browser problems
- API, Database, Data problems
- Infrastructure, Docker, Deployment
- Performance, Security, Configuration
- Dependencies, CI/CD, Documentation
- Unknown technical problems

## Quality Scoring

Every resolution is scored on 9 dimensions (100-point scale):

| Dimension | Weight |
|-----------|--------|
| Functional Correctness | 20% |
| Acceptance Criteria | 20% |
| Testing | 15% |
| Regression Safety | 10% |
| Code Quality | 10% |
| Security | 10% |
| Architecture | 5% |
| Documentation | 5% |
| Maintainability | 5% |

A task is only marked **RESOLVED — 10/10** when all hard completion gates pass.

## Documentation

| Document | Description |
|----------|-------------|
| **[How to Use](docs/HOW_TO_USE.md)** | **Step-by-step guide — start here** |
| [Architecture](docs/ARCHITECTURE.md) | System architecture and component design |
| [API Reference](docs/API.md) | REST API endpoints and examples |
| [Configuration](docs/CONFIGURATION.md) | Environment variables and provider setup |
| [Development Guide](docs/DEVELOPMENT.md) | How to develop and test locally |
| [Deployment](docs/DEPLOYMENT.md) | Deploy standalone, Docker, or production |
| [Contributing](docs/CONTRIBUTING.md) | How to contribute to the project |

## Safety

- Destructive commands require explicit approval
- Production actions are blocked by default
- Every operation is audit-logged
- Evidence always outranks AI opinion
- No false success claims allowed

## License

MIT License — see [LICENSE](LICENSE)

---

**Built by Virender Dhiman**
