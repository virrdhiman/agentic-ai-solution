"""Tests for the evidence engine."""

from autonomous_agent.core.evidence import EvidenceEngine
from autonomous_agent.core.models import (
    AcceptanceCriterion,
    AgentRole,
    AgentRun,
    CriterionStatus,
    EvidenceType,
    FailureRecord,
    Task,
    TestResult,
    TestStatus,
)


class TestEvidenceEngine:
    def setup_method(self):
        self.task = Task(problem="Fix the login bug")
        self.engine = EvidenceEngine(self.task)

    def test_initial_state(self):
        assert len(self.engine.evidence) == 0
        assert len(self.engine.test_results) == 0
        assert len(self.engine.acceptance_criteria) == 0

    def test_add_evidence(self):
        ev = self.engine.add_evidence(
            evidence_type=EvidenceType.TEST_RESULT,
            description="Test passed",
            content="All tests passed",
        )
        assert len(self.engine.evidence) == 1
        assert ev.task_id == self.task.id

    def test_add_test_result(self):
        tr = TestResult(task_id=self.task.id, test_name="test_1", status=TestStatus.PASSED)
        self.engine.add_test_result(tr)
        assert len(self.engine.test_results) == 1

    def test_all_tests_passed(self):
        self.engine.add_test_result(
            TestResult(task_id=self.task.id, test_name="t1", status=TestStatus.PASSED)
        )
        self.engine.add_test_result(
            TestResult(task_id=self.task.id, test_name="t2", status=TestStatus.PASSED)
        )
        assert self.engine.all_tests_passed() is True

    def test_all_tests_passed_with_failure(self):
        self.engine.add_test_result(
            TestResult(task_id=self.task.id, test_name="t1", status=TestStatus.PASSED)
        )
        self.engine.add_test_result(
            TestResult(task_id=self.task.id, test_name="t2", status=TestStatus.FAILED)
        )
        assert self.engine.all_tests_passed() is False

    def test_all_tests_passed_empty(self):
        assert self.engine.all_tests_passed() is False

    def test_acceptance_criteria(self):
        ac = AcceptanceCriterion(task_id=self.task.id, description="Login works")
        self.engine.set_acceptance_criteria([ac])
        assert len(self.engine.acceptance_criteria) == 1
        assert self.engine.all_acceptance_criteria_met() is False

    def test_acceptance_criteria_met(self):
        ac = AcceptanceCriterion(
            task_id=self.task.id,
            description="Login works",
            status=CriterionStatus.PASS,
        )
        self.engine.set_acceptance_criteria([ac])
        assert self.engine.all_acceptance_criteria_met() is True

    def test_acceptance_criteria_with_na(self):
        ac = AcceptanceCriterion(
            task_id=self.task.id,
            description="N/A criterion",
            status=CriterionStatus.NOT_APPLICABLE,
        )
        self.engine.set_acceptance_criteria([ac])
        assert self.engine.all_acceptance_criteria_met() is True

    def test_update_criterion(self):
        ac = AcceptanceCriterion(task_id=self.task.id, description="Test")
        self.engine.set_acceptance_criteria([ac])
        updated = self.engine.update_criterion(ac.id, CriterionStatus.PASS, "worked")
        assert updated is not None
        assert updated.status == CriterionStatus.PASS
        assert updated.actual_result == "worked"

    def test_contradiction_check_no_contradictions(self):
        self.engine.add_test_result(
            TestResult(task_id=self.task.id, test_name="t1", status=TestStatus.PASSED)
        )
        self.engine.add_evidence(EvidenceType.ANALYSIS, "analysis", "evidence content")
        assert len(self.engine.contradiction_check()) == 0

    def test_contradiction_check_test_fail_agent_claim_pass(self):
        self.engine.add_test_result(
            TestResult(task_id=self.task.id, test_name="t1", status=TestStatus.FAILED)
        )
        self.engine.agent_runs.append(
            AgentRun(
                task_id=self.task.id,
                agent_role=AgentRole.DEVELOPER,
                output_summary="Task resolved successfully",
            )
        )
        contradictions = self.engine.contradiction_check()
        assert any("test results show failures" in c for c in contradictions)

    def test_contradiction_check_no_evidence(self):
        contradictions = self.engine.contradiction_check()
        assert any("No evidence" in c for c in contradictions)

    def test_calculate_quality_no_data(self):
        score = self.engine.calculate_quality()
        # With no failures, regression_safety and security are 100, so total > 0
        assert score.total > 0.0
        assert score.functional_correctness == 0.0
        assert score.acceptance_criteria == 0.0

    def test_calculate_quality_with_tests(self):
        self.engine.add_test_result(
            TestResult(task_id=self.task.id, test_name="t1", status=TestStatus.PASSED)
        )
        self.engine.add_test_result(
            TestResult(task_id=self.task.id, test_name="t2", status=TestStatus.PASSED)
        )
        score = self.engine.calculate_quality()
        assert score.functional_correctness == 100.0
        assert score.testing > 0

    def test_verify_completion_empty(self):
        gates = self.engine.verify_completion()
        # No classification, no tests, no evidence — most gates false
        assert gates["problem_understood"] is False
        assert gates["tests_passed"] is False
        assert gates["evidence_exists"] is False

    def test_is_resolved_empty(self):
        assert self.engine.is_resolved() is False

    def test_build_report(self):
        self.engine.add_test_result(
            TestResult(task_id=self.task.id, test_name="t1", status=TestStatus.PASSED)
        )
        self.engine.set_acceptance_criteria([
            AcceptanceCriterion(
                task_id=self.task.id,
                description="Works",
                status=CriterionStatus.PASS,
            )
        ])
        report = self.engine.build_report()
        assert "# Evidence Report" in report
        assert "Fix the login bug" in report
        assert "[passed]" in report
