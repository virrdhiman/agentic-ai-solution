"""Tests for core domain models."""

from autonomous_agent.core.models import (
    AcceptanceCriterion,
    AgentRole,
    AgentRun,
    AuditEntry,
    Evidence,
    EvidenceType,
    FailureCategory,
    FailureRecord,
    ProblemClassification,
    ProblemType,
    QualityScore,
    RiskLevel,
    Task,
    TaskStatus,
    TestResult,
    TestStatus,
)


class TestTask:
    def test_create_task(self):
        task = Task(problem="Fix the bug")
        assert task.problem == "Fix the bug"
        assert task.id  # UUID auto-generated
        assert task.status == TaskStatus.ACTIVE
        assert task.state == "new"
        assert task.branch == "main"
        assert task.environment == "development"

    def test_task_with_constraints(self):
        task = Task(problem="Fix", constraints=["Don't break auth", "Keep API stable"])
        assert len(task.constraints) == 2

    def test_task_serialization(self):
        task = Task(problem="Test")
        data = task.model_dump()
        assert "problem" in data
        assert "id" in data
        restored = Task(**data)
        assert restored.problem == task.problem
        assert restored.id == task.id


class TestProblemClassification:
    def test_default_classification(self):
        pc = ProblemClassification()
        assert pc.problem_type == ProblemType.UNKNOWN
        assert pc.confidence == 0.0

    def test_classification_with_agents(self):
        pc = ProblemClassification(
            problem_type=ProblemType.SOFTWARE_BUG,
            required_agents=["investigator", "developer", "qa"],
            confidence=0.8,
        )
        assert pc.problem_type == ProblemType.SOFTWARE_BUG
        assert len(pc.required_agents) == 3


class TestQualityScore:
    def test_initial_score(self):
        qs = QualityScore()
        assert qs.total == 0.0

    def test_calculate_score(self):
        qs = QualityScore(
            functional_correctness=100.0,
            acceptance_criteria=100.0,
            testing=100.0,
            regression_safety=100.0,
            code_quality=100.0,
            security=100.0,
            architecture=100.0,
            documentation=100.0,
            maintainability=100.0,
        )
        total = qs.calculate()
        assert total == 100.0

    def test_display_score(self):
        qs = QualityScore(total=85.0)
        assert qs.display_score == "8.5/10"

    def test_weighted_calculation(self):
        qs = QualityScore(
            functional_correctness=100.0,  # 20%
            acceptance_criteria=100.0,     # 20%
            testing=100.0,                 # 15%
            regression_safety=100.0,       # 10%
            code_quality=100.0,            # 10%
            security=100.0,                # 10%
            architecture=100.0,            # 5%
            documentation=0.0,             # 5%
            maintainability=0.0,           # 5%
        )
        total = qs.calculate()
        # 20 + 20 + 15 + 10 + 10 + 10 + 5 + 0 + 0 = 90
        assert total == 90.0


class TestTestResult:
    def test_default_status(self):
        tr = TestResult(task_id="t1", test_name="test_1")
        assert tr.status == TestStatus.NOT_RUN

    def test_passed(self):
        tr = TestResult(task_id="t1", test_name="test_1", status=TestStatus.PASSED)
        assert tr.status == TestStatus.PASSED


class TestEvidence:
    def test_create_evidence(self):
        ev = Evidence(
            task_id="t1",
            evidence_type=EvidenceType.TEST_RESULT,
            description="Unit test passed",
            content="All 5 tests passed",
        )
        assert ev.supports_conclusion is True


class TestAcceptanceCriterion:
    def test_default_status(self):
        ac = AcceptanceCriterion(task_id="t1", description="Login works")
        assert ac.status == "not_tested"


class TestFailureRecord:
    def test_create_failure(self):
        fr = FailureRecord(
            task_id="t1",
            symptom="Login returns 500",
            root_cause="Database connection pool exhausted",
        )
        assert fr.category == FailureCategory.UNKNOWN


class TestEnums:
    def test_agent_roles(self):
        assert len(AgentRole) == 16
        assert AgentRole.ORCHESTRATOR.value == "orchestrator"

    def test_problem_types(self):
        assert len(ProblemType) == 19
        assert ProblemType.SOFTWARE_BUG.value == "software_bug"

    def test_risk_levels(self):
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.CRITICAL.value == "critical"

    def test_evidence_types(self):
        assert len(EvidenceType) == 9

    def test_test_statuses(self):
        assert TestStatus.PASSED.value == "passed"
        assert TestStatus.NOT_RUN.value == "not_run"

    def test_task_statuses(self):
        assert TaskStatus.ACTIVE.value == "active"
        assert TaskStatus.COMPLETED.value == "completed"
