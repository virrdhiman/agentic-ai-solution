FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[dev]" 2>/dev/null || pip install --no-cache-dir pydantic pydantic-settings sqlalchemy aiosqlite httpx fastapi uvicorn click rich pyyaml structlog gitpython aiofiles jinja2

# Copy source
COPY . .

# Install the package
RUN pip install --no-cache-dir -e .

# Create work directory
RUN mkdir -p /app/agent-work/tasks

EXPOSE 8000

CMD ["python", "-m", "autonomous_agent.cli", "--help"]
