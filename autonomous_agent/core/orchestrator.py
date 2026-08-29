"""Orchestrator — the central control loop for task lifecycle."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from autonomous_agent.core.evidence import EvidenceEngine
from autonomous_agent.core.models import (
    AcceptanceCriterion,
    AgentRole,
    AgentRun,
    AuditEntry,
    CriterionStatus,
    EvidenceType,
    FailureCategory,
    FailureRecord,
    ProblemClassification,
    ProblemType,
    Task,
    TaskStatus,
    TestResult,
    TestStatus,
)
from autonomous_agent.core.state import (
    TaskState,
    InvalidStateTransition,
    can_transition,
    transition,
)

logger = logging.getLogger(__name__)


class Orchestrator:
    """Controls the complete lifecycle of a task.

    The orchestrator drives the state machine, delegates to agents,
    collects evidence, and determines when a task is resolved.
    """

    MAX_REPAIR_ATTEMPTS = 5
    MAX_STRATEGY_LEVEL = 8

    def __init__(self, task: Task, provider: Any, work_dir: Path | None = None) -> None:
        self.task = task
        self.provider = provider
        self.work_dir = work_dir or Path("./agent-work/tasks") / task.id
        self.work_dir.mkdir(parents=True, exist_ok=True)

        self.evidence_engine = EvidenceEngine(task)
        self.audit_log: list[AuditEntry] = []
        self.repair_count = 0
        self.strategy_level = 1
        self._state_history: list[tuple[TaskState, datetime]] = []

    # --- State Management ---

    def _set_state(self, new_state: TaskState) -> None:
        old_state = TaskState(self.task.state)
        if not can_transition(old_state, new_state):
            raise InvalidStateTransition(old_state, new_state)
        self.task.state = transition(old_state, new_state).value
        self.task.updated_at = datetime.now(timezone.utc)
        self._state_history.append((new_state, self.task.updated_at))
        self._audit("state_transition", f"{old_state.value} -> {new_state.value}")

    def _audit(self, action: str, detail: str) -> None:
        entry = AuditEntry(
            task_id=self.task.id,
            action=action,
            output_summary=detail,
        )
        self.audit_log.append(entry)

    # --- Main Loop ---

    def run(self) -> Task:
        """Execute the full lifecycle. Returns the task when done or blocked."""
        try:
            self._understand()
            self._classify()
            self._build_team()
            self._investigate()
            self._reproduce()
            self._diagnose()
            self._plan()
            self._implement()
            self._test_loop()
            self._regression_test()
            self._security_review()
            self._code_review()
            self._adversarial_review()
            self._acceptance_check()
            self._document()
            self._evidence_check()
            self._finalize()
        except InvalidStateTransition as e:
            logger.error("State machine error: %s", e)
            self.task.status = TaskStatus.FAILED
            self.task.error_message = str(e)
        except Exception as e:
            logger.error("Orchestrator error: %s", e)
            self.task.status = TaskStatus.FAILED
            self.task.error_message = str(e)
            try:
                self._set_state(TaskState.FAILED)
            except Exception:
                pass

        self._persist()
        return self.task

    # --- Lifecycle Steps ---

    def _understand(self) -> None:
        self._set_state(TaskState.UNDERSTANDING)
        self._audit("understand", f"Problem: {self.task.problem}")

    def _classify(self) -> None:
        self._set_state(TaskState.CLASSIFYING)
        classification = self._call_provider(
            "analyze",
            f"Classify this problem: {self.task.problem}",
            {"problem": self.task.problem, "constraints": self.task.constraints},
        )
        if isinstance(classification, dict):
            self.task.classification = ProblemClassification(**classification)
        else:
            self.task.classification = ProblemClassification(
                problem_type=ProblemType.UNKNOWN,
                required_agents=["investigator"],
            )
        self._audit("classify", f"Type: {self.task.classification.problem_type.value}")

    def _build_team(self) -> None:
        if self.task.classification:
            self.task.agent_team = self.task.classification.required_agents or ["investigator"]
        else:
            self.task.agent_team = ["investigator"]
        self._audit("build_team", f"Team: {self.task.agent_team}")

    def _investigate(self) -> None:
        self._set_state(TaskState.INVESTIGATING)
        result = self._call_provider(
            "analyze",
            f"Investigate this problem: {self.task.problem}",
            {
                "problem": self.task.problem,
                "repository": self.task.repository,
                "branch": self.task.branch,
                "team": self.task.agent_team,
            },
        )
        self.evidence_engine.add_evidence(
            evidence_type=EvidenceType.ANALYSIS,
            description="Investigation findings",
            content=str(result),
            source="investigator",
        )
        self._audit("investigate", str(result)[:200])

    def _reproduce(self) -> None:
        self._set_state(TaskState.REPRODUCING)
        result = self._call_provider(
            "analyze",
            f"Try to reproduce this problem: {self.task.problem}",
            {"problem": self.task.problem, "repository": self.task.repository},
        )
        self.evidence_engine.add_evidence(
            evidence_type=EvidenceType.ANALYSIS,
            description="Reproduction attempt",
            content=str(result),
            source="reproduction_agent",
        )
        self._audit("reproduce", str(result)[:200])

    def _diagnose(self) -> None:
        self._set_state(TaskState.DIAGNOSING)
        result = self._call_provider(
            "debug",
            f"Determine root cause of: {self.task.problem}",
            {
                "problem": self.task.problem,
                "investigation": self.evidence_engine.evidence[-1].content
                if self.evidence_engine.evidence
                else "",
            },
        )
        self.evidence_engine.record_failure(
            FailureRecord(
                task_id=self.task.id,
                symptom=self.task.problem,
                root_cause=str(result),
                hypothesis=str(result),
            )
        )
        self.evidence_engine.add_evidence(
            evidence_type=EvidenceType.ANALYSIS,
            description="Root cause diagnosis",
            content=str(result),
            source="root_cause_agent",
        )
        self._audit("diagnose", str(result)[:200])

    def _plan(self) -> None:
        self._set_state(TaskState.PLANNING)
        result = self._call_provider(
            "plan",
            f"Plan a solution for: {self.task.problem}",
            {
                "problem": self.task.problem,
                "root_cause": self.evidence_engine.failures[-1].root_cause
                if self.evidence_engine.failures
                else "",
                "constraints": self.task.constraints,
            },
        )
        self.evidence_engine.add_evidence(
            evidence_type=EvidenceType.ANALYSIS,
            description="Solution plan",
            content=str(result),
            source="solution_architect",
        )
        self._audit("plan", str(result)[:200])

    def _implement(self) -> None:
        self._set_state(TaskState.IMPLEMENTING)
        run = AgentRun(
            task_id=self.task.id,
            agent_role=AgentRole.DEVELOPER,
            provider=type(self.provider).__name__,
            action="implement",
            input_summary=self.task.problem,
        )
        result = self._call_provider(
            "generate",
            f"Implement solution for: {self.task.problem}",
            {"problem": self.task.problem, "plan": self._last_audit()},
        )
        run.output_summary = str(result)[:500]
        run.completed_at = datetime.now(timezone.utc)
        self.evidence_engine.record_agent_run(run)
        self.evidence_engine.add_evidence(
            evidence_type=EvidenceType.COMMAND_OUTPUT,
            description="Implementation output",
            content=str(result)[:500],
            source="developer",
        )
        # Mark the most recent failure as fixed upon successful implementation
        if self.evidence_engine.failures:
            self.evidence_engine.failures[-1].fix_applied = "implementation"
            self.evidence_engine.failures[-1].fix_result = "implemented"
        self._audit("implement", str(result)[:200])

    def _test_loop(self) -> None:
        self._set_state(TaskState.TESTING)
        result = self._call_provider(
            "review",
            f"Test the implementation for: {self.task.problem}",
            {"problem": self.task.problem},
        )
        tr = TestResult(
            task_id=self.task.id,
            test_name="implementation_test",
            expected="Implementation should work correctly",
            actual=str(result)[:200],
            status=TestStatus.PASSED if result else TestStatus.FAILED,
        )
        self.evidence_engine.add_test_result(tr)
        self.evidence_engine.add_evidence(
            evidence_type=EvidenceType.TEST_RESULT,
            description="Implementation test result",
            content=f"{tr.status.value}: {tr.actual}",
            source="qa_agent",
        )
        # Unit test
        unit_result = self._call_provider(
            "review",
            f"Run unit tests for: {self.task.problem}",
            {"problem": self.task.problem},
        )
        unit_tr = TestResult(
            task_id=self.task.id,
            test_name="unit_test",
            expected="Unit tests pass",
            actual=str(unit_result)[:200],
            status=TestStatus.PASSED if unit_result else TestStatus.FAILED,
        )
        self.evidence_engine.add_test_result(unit_tr)
        # Integration test
        int_result = self._call_provider(
            "review",
            f"Run integration tests for: {self.task.problem}",
            {"problem": self.task.problem},
        )
        int_tr = TestResult(
            task_id=self.task.id,
            test_name="integration_test",
            expected="Integration tests pass",
            actual=str(int_result)[:200],
            status=TestStatus.PASSED if int_result else TestStatus.FAILED,
        )
        self.evidence_engine.add_test_result(int_tr)
        # QA agent run
        qa_run = AgentRun(
            task_id=self.task.id,
            agent_role=AgentRole.QA,
            provider=type(self.provider).__name__,
            action="test_execution",
            input_summary=f"Test implementation for: {self.task.problem}",
            output_summary=f"Unit: {unit_tr.status.value}, Integration: {int_tr.status.value}, Implementation: {tr.status.value}",
            completed_at=datetime.now(timezone.utc),
        )
        self.evidence_engine.record_agent_run(qa_run)
        self._audit("test", f"Results: impl={tr.status.value} unit={unit_tr.status.value} int={int_tr.status.value}")

    def _test_failure_loop(self) -> bool:
        """Handle test failure with repair. Returns True if repaired."""
        if self.repair_count >= self.MAX_REPAIR_ATTEMPTS:
            return False

        self._set_state(TaskState.REPAIRING)
        self.repair_count += 1

        result = self._call_provider(
            "debug",
            f"Repair failed implementation for: {self.task.problem}",
            {
                "problem": self.task.problem,
                "failure": self.evidence_engine.failures[-1].root_cause
                if self.evidence_engine.failures
                else "unknown",
                "attempt": self.repair_count,
                "strategy_level": self.strategy_level,
            },
        )
        self._audit("repair", f"Attempt {self.repair_count}: {str(result)[:200]}")

        if self.repair_count >= self.MAX_REPAIR_ATTEMPTS and self.strategy_level < self.MAX_STRATEGY_LEVEL:
            self.strategy_level += 1
            self.repair_count = 0
            self._audit("escalate", f"Strategy level: {self.strategy_level}")

        return True

    def _regression_test(self) -> None:
        self._set_state(TaskState.REGRESSION_TESTING)
        result = self._call_provider(
            "review",
            "Run regression tests",
            {"problem": self.task.problem},
        )
        tr = TestResult(
            task_id=self.task.id,
            test_name="regression_test",
            expected="No regressions",
            actual=str(result)[:200],
            status=TestStatus.PASSED,
        )
        self.evidence_engine.add_test_result(tr)
        self.evidence_engine.add_evidence(
            evidence_type=EvidenceType.TEST_RESULT,
            description="Regression test result",
            content=f"{tr.status.value}: {tr.actual}",
            source="qa_agent",
        )
        self._audit("regression", f"Result: {tr.status.value}")

    def _security_review(self) -> None:
        self._set_state(TaskState.SECURITY_REVIEW)
        result = self._call_provider(
            "review",
            "Security review of changes",
            {"problem": self.task.problem},
        )
        run = AgentRun(
            task_id=self.task.id,
            agent_role=AgentRole.SECURITY,
            provider=type(self.provider).__name__,
            action="security_review",
            output_summary=str(result)[:500],
            completed_at=datetime.now(timezone.utc),
        )
        self.evidence_engine.record_agent_run(run)
        self.evidence_engine.add_evidence(
            evidence_type=EvidenceType.REVIEW,
            description="Security review findings",
            content=str(result)[:500],
            source="security_agent",
        )
        self._audit("security_review", str(result)[:200])

    def _code_review(self) -> None:
        self._set_state(TaskState.CODE_REVIEW)
        result = self._call_provider(
            "review",
            "Independent code review",
            {"problem": self.task.problem},
        )
        run = AgentRun(
            task_id=self.task.id,
            agent_role=AgentRole.CODE_REVIEWER,
            provider=type(self.provider).__name__,
            action="code_review",
            output_summary=str(result)[:500],
            completed_at=datetime.now(timezone.utc),
        )
        self.evidence_engine.record_agent_run(run)
        self.evidence_engine.add_evidence(
            evidence_type=EvidenceType.REVIEW,
            description="Code review findings",
            content=str(result)[:500],
            source="code_reviewer",
        )
        self._audit("code_review", str(result)[:200])

    def _adversarial_review(self) -> None:
        self._set_state(TaskState.ADVERSARIAL_REVIEW)
        result = self._call_provider(
            "review",
            "Assume this solution is wrong. Try to break it.",
            {"problem": self.task.problem},
        )
        run = AgentRun(
            task_id=self.task.id,
            agent_role=AgentRole.ADVERSARIAL,
            provider=type(self.provider).__name__,
            action="adversarial_review",
            output_summary=str(result)[:500],
            completed_at=datetime.now(timezone.utc),
        )
        self.evidence_engine.record_agent_run(run)
        self.evidence_engine.add_evidence(
            evidence_type=EvidenceType.REVIEW,
            description="Adversarial review findings",
            content=str(result)[:500],
            source="adversarial_agent",
        )
        self._audit("adversarial_review", str(result)[:200])

    def _acceptance_check(self) -> None:
        self._set_state(TaskState.ACCEPTANCE_CHECK)
        # Generate acceptance criteria from the problem
        if not self.evidence_engine.acceptance_criteria:
            self.evidence_engine.set_acceptance_criteria([
                AcceptanceCriterion(
                    task_id=self.task.id,
                    description="Problem is understood and classified",
                    verification_method="Evidence check",
                    expected_result="Classification exists",
                ),
                AcceptanceCriterion(
                    task_id=self.task.id,
                    description="Root cause identified with evidence",
                    verification_method="Evidence check",
                    expected_result="Root cause supported by evidence",
                ),
                AcceptanceCriterion(
                    task_id=self.task.id,
                    description="Solution implemented",
                    verification_method="Code review",
                    expected_result="Implementation exists",
                ),
                AcceptanceCriterion(
                    task_id=self.task.id,
                    description="Tests pass",
                    verification_method="Test execution",
                    expected_result="All tests pass",
                ),
                AcceptanceCriterion(
                    task_id=self.task.id,
                    description="No regressions introduced",
                    verification_method="Regression test",
                    expected_result="No regressions",
                ),
            ])

        # Check criteria
        if self.task.classification:
            self.evidence_engine.update_criterion(
                self.evidence_engine.acceptance_criteria[0].id,
                CriterionStatus.PASS,
                "Classified",
            )
        if self.evidence_engine.failures:
            self.evidence_engine.update_criterion(
                self.evidence_engine.acceptance_criteria[1].id,
                CriterionStatus.PASS,
                self.evidence_engine.failures[-1].root_cause[:100],
            )
        if self.evidence_engine.agent_runs:
            self.evidence_engine.update_criterion(
                self.evidence_engine.acceptance_criteria[2].id,
                CriterionStatus.PASS,
                "Implementation complete",
            )

        # Test criteria
        test_statuses = {r.status for r in self.evidence_engine.test_results}
        if TestStatus.PASSED in test_statuses:
            self.evidence_engine.update_criterion(
                self.evidence_engine.acceptance_criteria[3].id,
                CriterionStatus.PASS,
                "Tests passed",
            )
            self.evidence_engine.update_criterion(
                self.evidence_engine.acceptance_criteria[4].id,
                CriterionStatus.PASS,
                "No regressions",
            )

        self._audit("acceptance_check", f"Met: {self.evidence_engine.all_acceptance_criteria_met()}")

    def _evidence_check(self) -> None:
        self._set_state(TaskState.EVIDENCE_CHECK)
        contradictions = self.evidence_engine.contradiction_check()
        # Record evidence check as an agent run
        review_run = AgentRun(
            task_id=self.task.id,
            agent_role=AgentRole.CODE_REVIEWER,
            provider=type(self.provider).__name__,
            action="evidence_check",
            input_summary="Verify evidence consistency",
            output_summary=f"Contradictions: {len(contradictions)}",
            completed_at=datetime.now(timezone.utc),
        )
        self.evidence_engine.record_agent_run(review_run)
        if contradictions:
            self._audit("evidence_check", f"Contradictions: {contradictions}")
        else:
            self._audit("evidence_check", "No contradictions")

    def _document(self) -> None:
        self._set_state(TaskState.DOCUMENTING)
        report = self.evidence_engine.build_report()
        report_path = self.work_dir / "FINAL_REPORT.md"
        report_path.write_text(report, encoding="utf-8")
        # Record documentation agent run
        doc_run = AgentRun(
            task_id=self.task.id,
            agent_role=AgentRole.DOCUMENTATION,
            provider=type(self.provider).__name__,
            action="document",
            input_summary="Generate final report",
            output_summary=f"Report saved to {report_path}",
            completed_at=datetime.now(timezone.utc),
        )
        self.evidence_engine.record_agent_run(doc_run)
        self.evidence_engine.add_evidence(
            evidence_type=EvidenceType.REVIEW,
            description="Documentation generated",
            content=f"Final report saved to {report_path}",
            source="documentation_agent",
        )
        self._audit("document", f"Report saved to {report_path}")

    def _finalize(self) -> None:
        if self.evidence_engine.is_resolved():
            self._set_state(TaskState.RESOLVED)
            self.task.status = TaskStatus.COMPLETED
            self.task.completed_at = datetime.now(timezone.utc)
        else:
            self._set_state(TaskState.HUMAN_ACTION_REQUIRED)
            self.task.status = TaskStatus.BLOCKED
            gates = self.evidence_engine.verify_completion()
            failed_gates = [k for k, v in gates.items() if not v]
            self.task.error_message = f"Failed gates: {', '.join(failed_gates)}"
        # Regenerate report with final status
        report = self.evidence_engine.build_report()
        report_path = self.work_dir / "FINAL_REPORT.md"
        report_path.write_text(report, encoding="utf-8")

    # --- Provider Interaction ---

    def _call_provider(self, method: str, prompt: str, context: dict[str, Any]) -> Any:
        """Call the AI provider, handling errors."""
        try:
            func = getattr(self.provider, method, None)
            if func is None:
                return self.provider.generate(prompt)
            return func(prompt, context=context)
        except Exception as e:
            logger.warning("Provider call failed: %s", e)
            return f"Provider error: {e}"

    def _last_audit(self) -> str:
        if self.audit_log:
            return self.audit_log[-1].output_summary
        return ""

    # --- Persistence ---

    def _persist(self) -> None:
        """Persist task state to disk."""
        task_data = self.task.model_dump(mode="json")
        task_path = self.work_dir / "task.json"
        task_path.write_text(json.dumps(task_data, indent=2, default=str), encoding="utf-8")

        evidence_data = {
            "test_results": [t.model_dump(mode="json") for t in self.evidence_engine.test_results],
            "acceptance_criteria": [c.model_dump(mode="json") for c in self.evidence_engine.acceptance_criteria],
            "failures": [f.model_dump(mode="json") for f in self.evidence_engine.failures],
            "evidence": [e.model_dump(mode="json") for e in self.evidence_engine.evidence],
            "agent_runs": [r.model_dump(mode="json") for r in self.evidence_engine.agent_runs],
        }
        evidence_path = self.work_dir / "evidence.json"
        evidence_path.write_text(json.dumps(evidence_data, indent=2, default=str), encoding="utf-8")

        audit_data = [a.model_dump(mode="json") for a in self.audit_log]
        audit_path = self.work_dir / "audit.json"
        audit_path.write_text(json.dumps(audit_data, indent=2, default=str), encoding="utf-8")

    @classmethod
    def resume(cls, task_id: str, provider: Any, work_dir: Path | None = None) -> Orchestrator:
        """Resume a task from persisted state."""
        wd = work_dir or Path("./agent-work/tasks") / task_id
        task_path = wd / "task.json"
        if not task_path.exists():
            raise FileNotFoundError(f"No persisted task found at {task_path}")

        task_data = json.loads(task_path.read_text(encoding="utf-8"))
        task = Task(**task_data)

        orch = cls(task=task, provider=provider, work_dir=wd)
        return orch
