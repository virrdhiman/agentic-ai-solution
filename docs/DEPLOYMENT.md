# Deployment Guide

> **Author:** Virender Dhiman

## Standalone Executable

### Windows

```bash
# Build the .exe
build.bat

# The executable will be at:
dist\autonomous-agent.exe

# Run it
dist\autonomous-agent.exe run "Fix this problem"
dist\autonomous-agent.exe --help
```

### macOS

```bash
# Build
./build.sh

# Outputs:
# dist/autonomous-agent          (standalone binary)
# dist/autonomous-agent.app      (macOS app bundle)
# dist/autonomous-agent-0.1.0-macos-arm64.dmg  (disk image)

# Run the binary
./dist/autonomous-agent run "Fix this problem"

# Or install the .app
open dist/autonomous-agent.app

# Or mount the .dmg and drag to Applications
open dist/autonomous-agent-0.1.0-macos-arm64.dmg
```

### Linux

```bash
# Build
./build.sh

# Outputs:
# dist/autonomous-agent              (standalone binary)
# build/AppDir/                      (AppImage structure)

# Run the binary
./dist/autonomous-agent run "Fix this problem"

# If appimagetool is installed:
# dist/autonomous-agent-0.1.0-linux-x86_64.AppImage
```

## Docker

### Quick Start

```bash
# API only (lightweight)
docker compose --profile api up -d

# Full stack (API + PostgreSQL + Redis)
docker compose --profile full up -d

# With local LLM via Ollama
docker compose --profile opensource up -d
```

### Custom Configuration

Create a `.env` file:

```env
AGENT_PROVIDER=opensource
AI_BASE_URL=http://ollama:11434/v1
AI_MODEL=llama3
DATABASE_URL=postgresql+asyncpg://agent:agent@postgres:5432/agentdb
ENVIRONMENT=development
```

Then:

```bash
docker compose --profile full up -d
```

### Building the Docker Image

```bash
docker build -t autonomous-agent .
docker run -it autonomous-agent run "Fix this problem"
```

## Production Deployment

### Prerequisites

- Python 3.11+ or Docker
- PostgreSQL (recommended for production)
- Redis (for caching, optional)
- AI provider access (Ollama, OpenAI, etc.)

### Steps

1. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with production settings
   ```

2. **Set database:**
   ```env
   DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/agentdb
   ENVIRONMENT=production
   ```

3. **Run with systemd (Linux):**
   ```ini
   [Unit]
   Description=Autonomous Agent API
   After=network.target postgresql.service

   [Service]
   Type=simple
   User=agent
   WorkingDirectory=/opt/autonomous-agent
   Environment=PATH=/opt/autonomous-agent/.venv/bin
   ExecStart=/opt/autonomous-agent/.venv/bin/uvicorn autonomous_agent.api.app:app --host 0.0.0.0 --port 8000
   Restart=always
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
   ```

4. **Or run with Docker Compose:**
   ```bash
   docker compose --profile full up -d
   ```

### Environment Variables for Production

```env
AGENT_PROVIDER=opensource
AI_BASE_URL=https://your-ai-endpoint.com/v1
AI_API_KEY=your-key
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/agentdb
REDIS_URL=redis://host:6379/0
ENVIRONMENT=production
LOG_LEVEL=WARNING
MAX_RETRIES=5
TASK_TIMEOUT=7200
```

### Security Considerations

- Never expose the API without authentication in production
- Use environment variables for all secrets (never hardcode)
- The tool layer blocks destructive operations in production by default
- All operations are audit-logged
- Use PostgreSQL instead of SQLite for concurrent access
- Enable Redis for caching and rate limiting

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Docker health
docker compose ps
```

## Monitoring

The system persists all task data to disk:
- `agent-work/tasks/{task-id}/task.json` — Task state
- `agent-work/tasks/{task-id}/evidence.json` — Evidence
- `agent-work/tasks/{task-id}/audit.json` — Audit log
- `agent-work/tasks/{task-id}/FINAL_REPORT.md` — Report

Monitor by watching these directories or querying the API.
