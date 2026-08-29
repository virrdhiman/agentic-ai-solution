"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from enum import Enum
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class ProviderType(str, Enum):
    OPENSOURCE = "opensource"
    N8N = "n8n"
    HYBRID = "hybrid"
    MOCK = "mock"


class Environment(str, Enum):
    LOCAL = "local"
    DEVELOPMENT = "development"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"
    UNKNOWN = "unknown"


class PermissionLevel(str, Enum):
    READ_ONLY = "read_only"
    SAFE_WRITE = "safe_write"
    DEVELOPMENT_WRITE = "development_write"
    TEST_WRITE = "test_write"
    STAGING_WRITE = "staging_write"
    PRODUCTION_APPROVAL_REQUIRED = "production_approval_required"
    DESTRUCTIVE = "destructive"


class Settings(BaseSettings):
    """Main application settings."""

    # Provider
    agent_provider: ProviderType = Field(default=ProviderType.MOCK)
    ai_base_url: str = Field(default="http://localhost:11434/v1")
    ai_api_key: str = Field(default="")
    ai_model: str = Field(default="llama3")

    # n8n
    n8n_base_url: str = Field(default="")
    n8n_api_key: str = Field(default="")

    # GitHub
    github_token: str = Field(default="")

    # Database
    database_url: str = Field(default="sqlite+aiosqlite:///./agent.db")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")

    # Environment
    environment: Environment = Field(default=Environment.DEVELOPMENT)

    # Agent
    max_retries: int = Field(default=3)
    task_timeout: int = Field(default=3600)
    log_level: str = Field(default="INFO")

    # Paths
    work_dir: str = Field(default="./agent-work")
    prompts_dir: str = Field(default="./prompts")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings from environment variables and .env file."""
    return Settings()


def get_effective_provider() -> ProviderType:
    """Determine effective provider with fallback chain."""
    settings = get_settings()
    if settings.agent_provider == ProviderType.MOCK:
        return ProviderType.MOCK
    return settings.agent_provider
