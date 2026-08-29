# How to Use — Autonomous Agent

> **Author:** Virender Dhiman

This guide walks you through installing, configuring, and running the Autonomous Agent system from scratch.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Installation](#2-installation)
3. [First Run (Zero Config)](#3-first-run-zero-config)
4. [CLI Commands](#4-cli-commands)
5. [REST API](#5-rest-api)
6. [Provider Setup](#6-provider-setup)
7. [Configuration](#7-configuration)
8. [Docker Usage](#8-docker-usage)
9. [Building Standalone Executables](#9-building-standalone-executables)
10. [Running Tests](#10-running-tests)
11. [Examples](#11-examples)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. Prerequisites

| Requirement | Minimum Version | Check Command |
|-------------|----------------|---------------|
| Python | 3.11+ | `python --version` |
| pip | Latest | `pip --version` |
| Git | 2.30+ | `git --version` |

Optional (for advanced features):
- **Docker** — for containerized deployment
- **Ollama** — for local AI inference (no API key needed)
- **Redis** — for task queue persistence
- **PostgreSQL** — for production database

---

## 2. Installation

### Option A: Install from source (recommended)

```bash
# Clone the repository
git clone https://github.com/your-org/autonomous-agent.git
cd autonomous-agent

# Install in development mode
pip install -e ".[dev]"

# Verify installation
agent --version
```

### Option B: Install with all extras

```bash
pip install -e ".[dev,postgres,playwright]"
```

### Option C: Just the core (no dev tools)

```bash
pip install -e .
```

---

## 3. First Run (Zero Config)

The system works **out of the box** with the mock provider — no API keys, no external services.

```bash
# Run the agent on a problem
agent run "Fix the broken login validation"

# That's it. The agent will autonomously:
# 1. Understand the problem
# 2. Classify it (software bug, infrastructure, etc.)
# 3. Investigate the codebase
# 4. Diagnose root cause
# 5. Plan a solution
# 6. Implement the fix
# 7. Run tests
# 8. Review for regressions
# 9. Produce a quality score
```

### What you'll see

```
🤖 Autonomous Agent v0.1.0
─────────────────────────
Problem:    Fix the broken login validation
Environment: development
Branch:     main
Task ID:    abc123-def456-...
Provider:   MockProvider

▶ Running lifecycle...
  ✓ Understanding problem
  ✓ Classifying problem
  ✓ Investigating codebase
  ✓ Diagnosing root cause
  ✓ Planning solution
  ✓ Implementing fix
  ✓ Running tests
  ✓ Regression testing
  ✓ Security review
  ✓ Code review
  ✓ Adversarial review
  ✓ Acceptance check
  ✓ Documentation
  ✓ Evidence gate

─────────────────────────
✅ RESOLVED

Quality Score: 10.0/10

Completion Gates:
  all_critical_passed    ✅
  no_unresolved_failures ✅
  evidence_sufficient    ✅
  no_contradictions      ✅
```

---

## 4. CLI Commands

### `agent run` — Run the agent on a problem

```bash
# Basic usage
agent run "Fix the broken login page"

# With specific provider
agent run --provider mock "Fix the API timeout"

# With repository path
agent run -r /path/to/repo "Fix the database query"

# With constraints
agent run "Add user profile page" \
  --constraint "Do not break existing auth" \
  --constraint "Must work on mobile"

# With environment
agent run -e production "Check for security vulnerabilities"

# Full options
agent run \
  --provider opensource \
  --repository /path/to/repo \
  --branch main \
  --environment development \
  --constraint "Keep backward compatibility" \
  "Fix the order calculation bug"
```

| Flag | Description | Default |
|------|-------------|---------|
| `--provider`, `-p` | AI provider (mock/opensource/n8n) | mock |
| `--repository`, `-r` | Repository path or owner/repo | current dir |
| `--branch`, `-b` | Git branch to work on | main |
| `--environment`, `-e` | Target environment | development |
| `--constraint`, `-c` | Constraints (repeatable) | none |

### `agent status` — Check task status

```bash
agent status abc123-def456-789
```

### `agent report` — View final report

```bash
agent report abc123-def456-789
```

### `agent resume` — Resume an interrupted task

```bash
agent resume abc123-def456-789
```

### `agent cancel` — Cancel a running task

```bash
agent cancel abc123-def456-789
```

### `agent tools` — List available tools

```bash
agent tools
```

Output:
```
Available Tools
───────────────
Name        Description                    Permission
shell       Execute shell commands         development_write
git         Git operations                 safe_write
filesystem  File read/write operations     safe_write
```

### `agent info` — Show system configuration

```bash
agent info
```

Output:
```
System Configuration
────────────────────
Setting       Value
Provider      mock
AI Model      llama3
Environment   development
Database URL  sqlite:///./agent.db
Max Retries   3
Task Timeout  3600s
```

---

## 5. REST API

### Start the server

```bash
# Development (auto-reload)
uvicorn autonomous_agent.api.app:app --reload

# Production
uvicorn autonomous_agent.api.app:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Endpoints

#### Health check
```bash
curl http://localhost:8000/health
```
Response:
```json
{"status": "healthy"}
```

#### Create a task
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "problem": "Fix the broken API endpoint",
    "repository": "owner/repo",
    "branch": "main",
    "environment": "development",
    "constraints": ["Do not break auth"]
  }'
```
Response:
```json
{
  "task_id": "abc123-def456-789",
  "status": "new",
  "problem": "Fix the broken API endpoint"
}
```

#### Get task status
```bash
curl http://localhost:8000/tasks/abc123-def456-789
```

#### Get task report
```bash
curl http://localhost:8000/tasks/abc123-def456-789/report
```

#### List all tasks
```bash
curl http://localhost:8000/tasks
```

#### Delete a task
```bash
curl -X DELETE http://localhost:8000/tasks/abc123-def456-789
```

### Interactive API docs

Once the server is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 6. Provider Setup

### Mock (default — zero config)

No setup needed. Returns deterministic responses for testing.

```bash
agent run "Fix the login bug"
# Uses mock provider automatically
```

### OpenSource (Ollama / vLLM / LM Studio)

**Step 1:** Install and start Ollama
```bash
# Install Ollama: https://ollama.ai
ollama pull llama3
ollama serve
```

**Step 2:** Configure the agent
```bash
# Option A: Environment variables
export AGENT_PROVIDER=opensource
export AI_BASE_URL=http://localhost:11434/v1
export AI_MODEL=llama3

# Option B: .env file (create in project root)
cat > .env << 'EOF'
AGENT_PROVIDER=opensource
AI_BASE_URL=http://localhost:11434/v1
AI_MODEL=llama3
EOF
```

**Step 3:** Run
```bash
agent run --provider opensource "Fix the database query"
```

**Other compatible providers:**
| Provider | Base URL | Notes |
|----------|----------|-------|
| Ollama | `http://localhost:11434/v1` | Default |
| vLLM | `http://localhost:8000/v1` | OpenAI-compatible |
| LM Studio | `http://localhost:1234/v1` | OpenAI-compatible |
| LocalAI | `http://localhost:8080/v1` | OpenAI-compatible |
| Together.ai | `https://api.together.xyz/v1` | Cloud |
| Groq | `https://api.groq.com/openai/v1` | Cloud |

### n8n

**Step 1:** Set up n8n instance (self-hosted or cloud)

**Step 2:** Configure
```bash
export AGENT_PROVIDER=n8n
export N8N_BASE_URL=https://your-n8n-instance.com
export N8N_API_KEY=your-api-key
```

**Step 3:** Run
```bash
agent run --provider n8n "Automate the invoice processing"
```

---

## 7. Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AGENT_PROVIDER` | `mock` | AI provider (mock/opensource/n8n/hybrid) |
| `AI_BASE_URL` | `http://localhost:11434/v1` | OpenAI-compatible API endpoint |
| `AI_API_KEY` | (empty) | API key for the AI provider |
| `AI_MODEL` | `llama3` | Model name to use |
| `N8N_BASE_URL` | (empty) | n8N instance URL |
| `N8N_API_KEY` | (empty) | n8N API key |
| `GITHUB_TOKEN` | (empty) | GitHub personal access token |
| `DATABASE_URL` | `sqlite+aiosqlite:///./agent.db` | Database connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |
| `ENVIRONMENT` | `development` | Current environment (local/development/test/staging/production) |
| `MAX_RETRIES` | `3` | Maximum retry attempts |
| `TASK_TIMEOUT` | `3600` | Task timeout in seconds |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG/INFO/WARNING/ERROR) |
| `WORK_DIR` | `./agent-work` | Working directory for task data |
| `PROMPTS_DIR` | `./prompts` | Directory for prompt templates |

### Using a .env file

Create a `.env` file in the project root:

```env
# Provider
AGENT_PROVIDER=mock

# AI (for opensource provider)
AI_BASE_URL=http://localhost:11434/v1
AI_API_KEY=
AI_MODEL=llama3

# Database
DATABASE_URL=sqlite+aiosqlite:///./agent.db

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO

# Retries
MAX_RETRIES=3
TASK_TIMEOUT=3600
```

### Permission Levels

| Level | Description |
|-------|-------------|
| `read_only` | Can only read files and data |
| `safe_write` | Can write to project files |
| `development_write` | Can execute dev commands |
| `test_write` | Can run tests |
| `staging_write` | Can modify staging |
| `production_approval_required` | Needs approval for production |
| `destructive` | Destructive operations (always needs approval) |

---

## 8. Docker Usage

### Quick start with Docker Compose

```bash
# Full stack: agent + PostgreSQL + Redis + Ollama
docker compose --profile full up -d

# API only: agent API server
docker compose --profile api up -d

# OpenSource: agent + Ollama (no external DB)
docker compose --profile opensource up -d
```

### Build the Docker image

```bash
docker build -t autonomous-agent .
docker run -it autonomous-agent agent run "Fix the login bug"
```

### Docker Compose profiles

| Profile | Services | Use Case |
|---------|----------|----------|
| `full` | agent + postgres + redis + ollama | Full local stack |
| `api` | agent API server | API-only deployment |
| `opensource` | agent + ollama | Local LLM inference |

---

## 9. Building Standalone Executables

### Windows (.exe)

```bash
# Run the build script
build.bat

# Output: dist\autonomous-agent.exe
```

The `.exe` is standalone — no Python installation needed on the target machine.

### macOS (.app / .dmg)

```bash
# Run the build script
./build.sh

# Output:
#   dist/AutonomousAgent.app (portable app)
#   dist/AutonomousAgent.dmg (installer)
```

### Linux (AppImage)

```bash
# Run the build script
./build.sh

# Output: dist/AutonomousAgent-x86_64.AppImage
```

### What the build scripts do

1. Create a virtual environment
2. Install all dependencies
3. Run the full test suite
4. Build a standalone executable with PyInstaller
5. Create platform-specific packages (.exe / .app / .dmg / AppImage)
6. Verify the executable works

---

## 10. Running Tests

### Run all tests

```bash
python -m pytest tests/ -v
```

### Run specific test categories

```bash
# Unit tests only
python -m pytest tests/ -m unit -v

# Integration tests only
python -m pytest tests/ -m integration -v

# End-to-end tests
python -m pytest tests/ -m e2e -v

# Tests for a specific module
python -m pytest tests/test_state.py -v
python -m pytest tests/test_orchestrator.py -v
python -m pytest tests/test_evidence.py -v
```

### Run with coverage

```bash
python -m pytest tests/ --cov=autonomous_agent --cov-report=html
# Open htmlcov/index.html in browser
```

### Run benchmark (10/10 quality proof)

```bash
python -m pytest tests/test_benchmark_10_10.py -v
```

---

## 11. Examples

### Example 1: Fix a bug in a Python project

```bash
cd /path/to/your/python-project
agent run "Fix the order total calculation — it doesn't include tax"
```

### Example 2: Fix a bug with constraints

```bash
agent run \
  --constraint "Do not change the API response format" \
  --constraint "Keep backward compatibility" \
  "Fix the user search — it returns duplicate results"
```

### Example 3: Run on a specific branch

```bash
agent run \
  --branch feature/checkout \
  --environment staging \
  "The checkout button doesn't respond to clicks"
```

### Example 4: Use a real AI provider

```bash
# Start Ollama
ollama serve &

# Run with OpenSource provider
agent run \
  --provider opensource \
  "Optimize the database queries in the report generator"
```

### Example 5: Use the REST API with Python

```python
import httpx

# Create a task
response = httpx.post("http://localhost:8000/tasks", json={
    "problem": "Fix the broken email notification",
    "repository": "my-org/my-repo",
    "environment": "development"
})
task_id = response.json()["task_id"]

# Check status
status = httpx.get(f"http://localhost:8000/tasks/{task_id}")
print(status.json())

# Get report
report = httpx.get(f"http://localhost:8000/tasks/{task_id}/report")
print(report.json())
```

### Example 6: Use the REST API with curl

```bash
# Create task
curl -s -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"problem": "Fix the broken API endpoint"}' | jq .

# Poll status until resolved
while true; do
  STATUS=$(curl -s http://localhost:8000/tasks/$TASK_ID | jq -r .status)
  echo "Status: $STATUS"
  if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
    break
  fi
  sleep 5
done

# Get final report
curl -s http://localhost:8000/tasks/$TASK_ID/report | jq .
```

### Example 7: Docker usage

```bash
# Start the full stack
docker compose --profile full up -d

# Run a task via the API
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"problem": "Fix the slow query in the dashboard"}'

# View logs
docker compose logs -f agent
```

---

## 12. Troubleshooting

### "ModuleNotFoundError: No module named 'autonomous_agent'"

```bash
# Reinstall in development mode
pip install -e ".[dev]"
```

### "agent: command not found"

```bash
# Make sure the scripts directory is in your PATH
pip install -e ".[dev]"
# Or run directly:
python -m autonomous_agent.cli:main run "Fix the bug"
```

### "Connection refused" (Ollama)

```bash
# Make sure Ollama is running
ollama serve

# Verify it's accessible
curl http://localhost:11434/api/tags
```

### "Task not found" (resume/status)

```bash
# Tasks are stored in ./agent-work/tasks/
# Check what tasks exist:
ls ./agent-work/tasks/

# The task ID is shown when you run `agent run`
```

### Tests fail with import errors

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run with verbose output
python -m pytest tests/ -v --tb=long
```

### Docker build fails

```bash
# Make sure Docker is running
docker info

# Build without cache
docker build --no-cache -t autonomous-agent .
```

### API server won't start

```bash
# Check if port 8000 is in use
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Use a different port
uvicorn autonomous_agent.api.app:app --port 8001
```

---

## Quick Reference Card

```bash
# Install
pip install -e ".[dev]"

# Run (zero config)
agent run "Fix the bug"

# Run with provider
agent run --provider opensource "Fix the bug"

# Check status
agent status <task-id>

# View report
agent report <task-id>

# Resume interrupted task
agent resume <task-id>

# List tools
agent tools

# Show config
agent info

# Run tests
python -m pytest tests/ -v

# Start API
uvicorn autonomous_agent.api.app:app --reload

# Build exe (Windows)
build.bat

# Build app (macOS/Linux)
./build.sh
```

---

**Built by Virender Dhiman**
