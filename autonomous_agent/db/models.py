"""SQLAlchemy ORM models for persistent storage."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from autonomous_agent.db import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TaskRow(Base):
    """Persistent task storage."""

    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    problem: Mapped[str] = mapped_column(Text)
    repository: Mapped[str | None] = mapped_column(String(500), nullable=True)
    branch: Mapped[str] = mapped_column(String(200), default="main")
    environment: Mapped[str] = mapped_column(String(50), default="development")
    status: Mapped[str] = mapped_column(String(50), default="active")
    state: Mapped[str] = mapped_column(String(50), default="new")
    agent_team: Mapped[str] = mapped_column(Text, default="[]")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    strategy_level: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AuditEntryRow(Base):
    """Audit log entries."""

    __tablename__ = "audit_entries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    task_id: Mapped[str] = mapped_column(String(36), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    agent: Mapped[str] = mapped_column(String(100), default="")
    provider: Mapped[str] = mapped_column(String(100), default="")
    tool: Mapped[str] = mapped_column(String(100), default="")
    action: Mapped[str] = mapped_column(String(200), default="")
    input_summary: Mapped[str] = mapped_column(Text, default="")
    output_summary: Mapped[str] = mapped_column(Text, default="")
    decision: Mapped[str] = mapped_column(Text, default="")
    result: Mapped[str] = mapped_column(Text, default="")


class EvidenceRow(Base):
    """Evidence storage."""

    __tablename__ = "evidence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    task_id: Mapped[str] = mapped_column(String(36), index=True)
    evidence_type: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(200), default="")
    supports_conclusion: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class TestResultRow(Base):
    """Test results storage."""

    __tablename__ = "test_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    task_id: Mapped[str] = mapped_column(String(36), index=True)
    test_name: Mapped[str] = mapped_column(String(200))
    command: Mapped[str] = mapped_column(Text, default="")
    expected: Mapped[str] = mapped_column(Text, default="")
    actual: Mapped[str] = mapped_column(Text, default="")
    exit_code: Mapped[int] = mapped_column(Integer, default=-1)
    logs: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(50), default="not_run")
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class QualityScoreRow(Base):
    """Quality scores storage."""

    __tablename__ = "quality_scores"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    task_id: Mapped[str] = mapped_column(String(36), index=True)
    functional_correctness: Mapped[float] = mapped_column(Float, default=0.0)
    acceptance_criteria: Mapped[float] = mapped_column(Float, default=0.0)
    testing: Mapped[float] = mapped_column(Float, default=0.0)
    regression_safety: Mapped[float] = mapped_column(Float, default=0.0)
    code_quality: Mapped[float] = mapped_column(Float, default=0.0)
    security: Mapped[float] = mapped_column(Float, default=0.0)
    architecture: Mapped[float] = mapped_column(Float, default=0.0)
    documentation: Mapped[float] = mapped_column(Float, default=0.0)
    maintainability: Mapped[float] = mapped_column(Float, default=0.0)
    total: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
