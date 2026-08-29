# Configuration

> **Author:** Virender Dhiman

The Autonomous Agent is configured via environment variables and a `.env` file.

## Quick Start

```bash
cp .env.example .env
# Edit .env with your settings
```

## Environment Variables

### Provider Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `AGENT_PROVIDER` | `mock` | AI provider: `mock`, `opensource`, `n8n`, `hybrid` |
| `AI_BASE_URL` | `http://localhost:11434/v1` | OpenAI-compatible API base URL |
| `AI_API_KEY` | `""` | API key for the AI provider |
| `AI_MODEL` | `llama3` | Model name to use |

### Provider-Specific

| Variable | Default | Description |
|----------|---------|-------------|
| `N8N_BASE_URL` | `""` | n8N instance URL (for n8n provider) |
| `N8N_API_KEY` | `""` | n8N API key (for n8n provider) |
| `GITHUB_TOKEN` | `""` | GitHub personal access token |

### Database

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./agent.db` | Database connection URL |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |

### Agent Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `development` | Current environment: `local`, `development`, `test`, `staging`, `production` |
| `MAX_RETRIES` | `3` | Maximum retry attempts |
| `TASK_TIMEOUT` | `3600` | Task timeout in seconds (1 hour) |
| `LOG_LEVEL` | `INFO` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |

### Paths

| Variable | Default | Description |
|----------|---------|-------------|
| `WORK_DIR` | `./agent-work` | Working directory for task artifacts |
| `PROMPTS_DIR` | `./prompts` | Directory for prompt templates |

## Example `.env`

```env
# Use mock provider for testing (no API needed)
AGENT_PROVIDER=mock

# Or use Ollama locally
# AGENT_PROVIDER=opensource
# AI_BASE_URL=http://localhost:11434/v1
# AI_MODEL=llama3

# Or use OpenAI
# AGENT_PROVIDER=opensource
# AI_BASE_URL=https://api.openai.com/v1
# AI_API_KEY=sk-...
# AI_MODEL=gpt-4

# Database (SQLite for dev, PostgreSQL for production)
DATABASE_URL=sqlite+aiosqlite:///./agent.db
# DATABASE_URL=postgresql+asyncpg://user:pass@localhost/agentdb

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO
```

## Provider Modes

### Mock Mode (Default)

No external dependencies. Returns deterministic responses. Ideal for testing and development.

```env
AGENT_PROVIDER=mock
```

### OpenSource Mode

Connects to any OpenAI-compatible API. Works with Ollama, vLLM, LM Studio, LocalAI, etc.

```env
AGENT_PROVIDER=opensource
AI_BASE_URL=http://localhost:11434/v1
AI_MODEL=llama3
AI_API_KEY=not-needed
```

### n8N Mode

Delegates workflow orchestration to an n8N instance. Requires n8N API access.

```env
AGENT_PROVIDER=n8n
N8N_BASE_URL=https://your-n8n-instance.com
N8N_API_KEY=your-key-here
```

### Hybrid Mode

Uses different providers for different tasks. Currently defaults to opensource with fallback to mock.

```env
AGENT_PROVIDER=hybrid
AI_BASE_URL=http://localhost:11434/v1
AI_MODEL=llama3
```

## Docker Configuration

The Docker Compose setup reads from `.env` and provides profiles:

```bash
# Full stack (API + PostgreSQL + Redis + Ollama)
docker compose --profile full up

# API only
docker compose --profile api up

# API + local LLM
docker compose --profile opensource up
```

## Permission Levels

The tool layer enforces permission levels per environment:

| Level | Description | Allowed Environments |
|-------|-------------|---------------------|
| `read_only` | Read-only operations | All |
| `safe_write` | Safe file writes | All |
| `development_write` | Code changes | Development, Test |
| `test_write` | Test modifications | Development, Test |
| `staging_write` | Staging changes | Development, Test, Staging |
| `production_approval_required` | Production changes | Requires approval |
| `destructive` | Destructive operations | Requires explicit approval |
