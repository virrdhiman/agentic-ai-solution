"""Core domain models for the autonomous agent system."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


def _now() -> datetime:
    """Return the current UTC time."""
    return datetime.now(timezone.utc)


def _uuid() -> str:
    """Generate a new UUID4 string."""
    return str(uuid.uuid4())


# --- Problem Classification ---


class ProblemType(str, Enum):
    """Enumeration of all supported problem types.

    The Universal Problem Router uses these to classify incoming problems
    and determine the appropriate agent team.
    """

    SOFTWARE_BUG = "software_bug"
    FEATURE_REQUEST = "feature_request"
    WEBSITE_PROBLEM = "website_problem"
    BROWSER_PROBLEM = "browser_problem"
    API_PROBLEM = "api_problem"
    DATABASE_PROBLEM = "database_problem"
    DATA_PROBLEM = "data_problem"
    AUTOMATION_PROBLEM = "automation_problem"
    INTEGRATION_PROBLEM = "integration_problem"
    INFRASTRUCTURE_PROBLEM = "infrastructure_problem"
    DOCKER_PROBLEM = "docker_problem"
    DEPLOYMENT_PROBLEM = "deployment_problem"
    PERFORMANCE_PROBLEM = "performance_problem"
    SECURITY_PROBLEM = "security_problem"
    CONFIGURATION_PROBLEM = "configuration_problem"
    DEPENDENCY_PROBLEM = "dependency_problem"
    CICD_PROBLEM = "cicd_problem"
    DOCUMENTATION_PROBLEM = "documentation_problem"
    UNKNOWN = "unknown"


class RiskLevel(str, Enum):
    """Risk levels for problem classification.

    Higher risk levels may require additional review gates and approval
    before implementation.
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ProblemClassification(BaseModel):
    """Result of the Universal Problem Router."""

    problem_type: ProblemType = ProblemType.UNKNOWN
    affected_systems: list[str] = Field(default_factory=list)
    required_skills: list[str] = Field(default_factory=list)
    required_tools: list[str] = Field(default_factory=list)
    required_agents: list[str] = Field(default_factory=list)
    required_tests: list[str] = Field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.MEDIUM
    environment: str = "development"
    acceptance_criteria: list[str] = Field(default_factory=list)
    confidence: float = 0.0


# --- Task ---


class TaskStatus(str, Enum):
    """High-level task status.

    Tracks whether a task is actively being worked on, completed,
    failed, blocked, or cancelled.
    """

    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class Task(BaseModel):
    """Primary task entity."""

    id: str = Field(default_factory=_uuid)
    problem: str
    repository: Optional[str] = None
    branch: str = "main"
    environment: str = "development"
    constraints: list[str] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.ACTIVE
    state: str = "new"
    classification: Optional[ProblemClassification] = None
    agent_team: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    strategy_level: int = 1
    context: dict[str, Any] = Field(default_factory=dict)


# --- Agent ---


class AgentRole(str, Enum):
    """Roles that agents can assume in the dynamic agent team.

    Each role has specific responsibilities and is assigned based on
    the problem type and required skills.
    """

    ORCHESTRATOR = "orchestrator"
    BUSINESS_ANALYST = "business_analyst"
    INVESTIGATOR = "investigator"
    REPRODUCTION = "reproduction"
    ROOT_CAUSE = "root_cause"
    SOLUTION_ARCHITECT = "solution_architect"
    DEVELOPER = "developer"
    DATA = "data"
    BROWSER = "browser"
    INFRASTRUCTURE = "infrastructure"
    QA = "qa"
    SECURITY = "security"
    PERFORMANCE = "performance"
    CODE_REVIEWER = "code_reviewer"
    ADVERSARIAL = "adversarial"
    DOCUMENTATION = "documentation"


class AgentRun(BaseModel):
    """Record of an agent executing a step."""

    id: str = Field(default_factory=_uuid)
    task_id: str
    agent_role: AgentRole
    provider: str = "mock"
    action: str = ""
    input_summary: str = ""
    output_summary: str = ""
    files_changed: list[str] = Field(default_factory=list)
    decision: str = ""
    result: str = ""
    started_at: datetime = Field(default_factory=_now)
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


# --- Evidence ---


class EvidenceType(str, Enum):
    """Types of evidence that can be collected during a task.

    Evidence is used to support or contradict conclusions and is
    required for the quality scoring system.
    """

    TEST_RESULT = "test_result"
    GIT_DIFF = "git_diff"
    LOG_OUTPUT = "log_output"
    SCREENSHOT = "screenshot"
    API_RESPONSE = "api_response"
    FILE_CONTENT = "file_content"
    COMMAND_OUTPUT = "command_output"
    ANALYSIS = "analysis"
    REVIEW = "review"


class Evidence(BaseModel):
    """A piece of evidence for or against a conclusion."""

    id: str = Field(default_factory=_uuid)
    task_id: str
    evidence_type: EvidenceType
    description: str
    content: str
    source: str = ""
    supports_conclusion: bool = True
    created_at: datetime = Field(default_factory=_now)


# --- Acceptance Criteria ---


class CriterionStatus(str, Enum):
    """Status of an acceptance criterion.

    Criteria must reach PASS or NOT_APPLICABLE for the task to
    be considered resolved.
    """

    NOT_TESTED = "not_tested"
    PASS = "pass"
    FAIL = "fail"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class AcceptanceCriterion(BaseModel):
    """A single acceptance criterion."""

    id: str = Field(default_factory=_uuid)
    task_id: str
    description: str
    verification_method: str = ""
    expected_result: str = ""
    actual_result: str = ""
    evidence: str = ""
    status: CriterionStatus = CriterionStatus.NOT_TESTED


# --- Quality ---


class QualityScore(BaseModel):
    """Quality score breakdown."""

    functional_correctness: float = 0.0
    acceptance_criteria: float = 0.0
    testing: float = 0.0
    regression_safety: float = 0.0
    code_quality: float = 0.0
    security: float = 0.0
    architecture: float = 0.0
    documentation: float = 0.0
    maintainability: float = 0.0
    total: float = 0.0

    def calculate(self) -> float:
        self.total = round(
            self.functional_correctness * 0.20
            + self.acceptance_criteria * 0.20
            + self.testing * 0.15
            + self.regression_safety * 0.10
            + self.code_quality * 0.10
            + self.security * 0.10
            + self.architecture * 0.05
            + self.documentation * 0.05
            + self.maintainability * 0.05,
            1,
        )
        return self.total

    @property
    def display_score(self) -> str:
        score_10 = self.total / 10.0
        return f"{score_10:.1f}/10"


# --- Test ---


class TestStatus(str, Enum):
    """Status of a test execution."""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"
    NOT_RUN = "not_run"


class TestResult(BaseModel):
    """Result of a single test execution."""

    id: str = Field(default_factory=_uuid)
    task_id: str
    test_name: str
    command: str = ""
    environment: str = ""
    expected: str = ""
    actual: str = ""
    exit_code: int = -1
    logs: str = ""
    status: TestStatus = TestStatus.NOT_RUN
    timestamp: datetime = Field(default_factory=_now)


# --- Failure ---


class FailureCategory(str, Enum):
    """Categories for classifying failures.

    Used by the Failure Analysis Engine to determine the appropriate
    repair strategy.
    """

    CODE = "code"
    CONFIGURATION = "configuration"
    ENVIRONMENT = "environment"
    DEPENDENCY = "dependency"
    DATA = "data"
    NETWORK = "network"
    EXTERNAL_SERVICE = "external_service"
    TEST = "test"
    REQUIREMENT = "requirement"
    UNKNOWN = "unknown"


class FailureRecord(BaseModel):
    """Record of a failure and analysis."""

    id: str = Field(default_factory=_uuid)
    task_id: str
    category: FailureCategory = FailureCategory.UNKNOWN
    signature: str = ""
    symptom: str = ""
    direct_cause: str = ""
    root_cause: str = ""
    hypothesis: str = ""
    evidence: str = ""
    strategy_level: int = 1
    fix_applied: str = ""
    fix_result: str = ""
    created_at: datetime = Field(default_factory=_now)


# --- Tool ---


class ToolResult(BaseModel):
    """Result of a tool execution."""

    success: bool
    output: str = ""
    error: str = ""
    exit_code: int = 0
    duration_seconds: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


# --- Audit ---


class AuditEntry(BaseModel):
    """Audit log entry."""

    id: str = Field(default_factory=_uuid)
    task_id: str
    timestamp: datetime = Field(default_factory=_now)
    agent: str = ""
    provider: str = ""
    tool: str = ""
    action: str = ""
    input_summary: str = ""
    output_summary: str = ""
    files_changed: list[str] = Field(default_factory=list)
    decision: str = ""
    result: str = ""
