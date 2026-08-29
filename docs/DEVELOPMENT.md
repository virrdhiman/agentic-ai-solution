# Development Guide

> **Author:** Virender Dhiman

## Prerequisites

- Python 3.11+
- pip
- git

## Setup

```bash
# Clone
git clone <repo-url>
cd "Agentic AI Solution"

# Virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Install with dev dependencies
pip install -e ".[dev]"
```

## Running Tests

```bash
# All tests
python -m pytest tests/ -v

# Specific file
python -m pytest tests/test_state.py -v

# With coverage
python -m pytest tests/ --cov=autonomous_agent --cov-report=term-missing

# Benchmark (proves 10/10 quality)
python -m pytest tests/test_benchmark_10_10.py -v -s
```

## Using the CLI

```bash
# Show help
agent --help

# Run on a problem
agent run "Fix the broken login validation"

# With a specific provider
agent run --provider mock "Add input validation"

# Check system info
agent info

# List tools
agent tools
```

## Using the API

```bash
# Start the server
uvicorn autonomous_agent.api.app:app --reload

# Create a task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"problem": "Fix the broken API endpoint"}'

# Check status
curl http://localhost:8000/tasks/{task-id}

# Get report
curl http://localhost:8000/tasks/{task-id}/report

# Interactive docs
open http://localhost:8000/docs
```

## Project Layout

```
autonomous_agent/
├── __init__.py           # Package init, version, author
├── config/
│   ├── __init__.py
│   └── settings.py       # Pydantic settings from env vars
├── core/
│   ├── __init__.py
│   ├── models.py         # All domain models (Pydantic)
│   ├── state.py          # State machine (20 states, transitions)
│   ├── orchestrator.py   # Central control loop
│   ├── evidence.py       # Evidence collection + quality scoring
│   └── router.py         # Universal Problem Router
├── providers/
│   ├── __init__.py
│   ├── base.py           # AIProvider ABC
│   ├── mock.py           # MockProvider (deterministic)
│   ├── opensource.py     # OpenSourceProvider (Ollama, etc.)
│   ├── n8n.py            # N8NProvider (requires credentials)
│   └── router.py         # Provider factory + fallback
├── tools/
│   ├── __init__.py
│   ├── base.py           # Tool ABC + ToolRegistry
│   ├── filesystem.py     # FileRead, FileWrite, ListDirectory
│   ├── shell.py          # Shell execution with safety
│   └── git.py            # Git operations
├── api/
│   ├── __init__.py
│   └── app.py            # FastAPI REST API
├── db/
│   ├── __init__.py       # Async SQLAlchemy engine
│   └── models.py         # Database table models
├── cli/
│   └── __init__.py       # Click CLI entry point
tests/
├── test_state.py
├── test_models.py
├── test_providers.py
├── test_evidence.py
├── test_router.py
├── test_tools.py
├── test_orchestrator.py
└── test_benchmark_10_10.py
docs/
├── ARCHITECTURE.md
├── API.md
├── CONFIGURATION.md
├── CONTRIBUTING.md
└── DEVELOPMENT.md
policies/
└── permissions.yaml
build.bat                # Windows build script
build.sh                 # macOS/Linux build script
Dockerfile
docker-compose.yml
pyproject.toml
.env.example
README.md
LICENSE
```

## Key Concepts

### State Machine

Every task goes through a strict state machine. Invalid transitions raise `InvalidStateTransition`. The orchestrator enforces the flow.

### Evidence-Based Completion

The system never claims success without evidence. Every conclusion must be supported by:
- Test results
- Acceptance criteria
- Agent runs
- Evidence items

### Quality Scoring

The 9-dimension quality score (0-100, displayed as X/10) measures:
1. Functional correctness (tests passing)
2. Acceptance criteria (all met)
3. Testing (sufficient tests run)
4. Regression safety (no unresolved failures)
5. Code quality (evidence collected)
6. Security (no security failures)
7. Architecture (agent coverage)
8. Documentation (report generated)
9. Maintainability (evidence + agent diversity)

### Repair Loop

When tests fail, the orchestrator enters a repair loop with strategy escalation:
- Level 1: Implementation correction
- Level 2: Reinvestigation
- Level 3: Architecture review
- ... up to Level 8: Human action required

## Building Standalone Executables

```bash
# Windows
build.bat

# macOS/Linux
chmod +x build.sh
./build.sh
```

## Docker

```bash
# Build and run
docker compose --profile api up --build

# Full stack with database
docker compose --profile full up --build
```
