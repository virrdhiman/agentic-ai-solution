"""Evidence engine for collecting, storing, and validating evidence."""

from __future__ import annotations

from typing import Optional

from autonomous_agent.core.models import (
    AcceptanceCriterion,
    AgentRun,
    CriterionStatus,
    Evidence,
    EvidenceType,
    FailureRecord,
    QualityScore,
    Task,
    TaskStatus,
    TestResult,
    TestStatus,
)


class EvidenceEngine:
    """Manages evidence collection, validation, and consistency checking."""

    def __init__(self, task: Task) -> None:
        self.task = task
        self.evidence: list[Evidence] = []
        self.test_results: list[TestResult] = []
        self.acceptance_criteria: list[AcceptanceCriterion] = []
        self.failures: list[FailureRecord] = []
        self.agent_runs: list[AgentRun] = []

    def add_evidence(
        self,
        evidence_type: EvidenceType,
        description: str,
        content: str,
        source: str = "",
        supports_conclusion: bool = True,
    ) -> Evidence:
        """Collect a piece of evidence for the task.

        Args:
            evidence_type: The type of evidence (test result, analysis, etc.).
            description: Human-readable description of what this evidence shows.
            content: The actual evidence content.
            source: Which agent or tool produced this evidence.
            supports_conclusion: Whether this evidence supports the conclusion.

        Returns:
            The created Evidence object.
        """
        ev = Evidence(
            task_id=self.task.id,
            evidence_type=evidence_type,
            description=description,
            content=content,
            source=source,
            supports_conclusion=supports_conclusion,
        )
        self.evidence.append(ev)
        return ev

    def add_test_result(self, result: TestResult) -> None:
        """Record a test execution result."""
        self.test_results.append(result)

    def set_acceptance_criteria(self, criteria: list[AcceptanceCriterion]) -> None:
        """Set the acceptance criteria for this task."""
        self.acceptance_criteria = criteria

    def update_criterion(
        self, criterion_id: str, status: CriterionStatus, actual: str = "", evidence_text: str = ""
    ) -> Optional[AcceptanceCriterion]:
        """Update the status of a specific acceptance criterion."""
        for c in self.acceptance_criteria:
            if c.id == criterion_id:
                c.status = status
                c.actual_result = actual
                c.evidence = evidence_text
                return c
        return None

    def record_failure(self, failure: FailureRecord) -> None:
        """Record a failure and its analysis."""
        self.failures.append(failure)

    def record_agent_run(self, run: AgentRun) -> None:
        """Record an agent execution run."""
        self.agent_runs.append(run)

    # --- Validation ---

    def all_tests_passed(self) -> bool:
        """Check that all executed tests passed."""
        if not self.test_results:
            return False
        return all(r.status == TestStatus.PASSED for r in self.test_results)

    def all_acceptance_criteria_met(self) -> bool:
        """Check that all criteria are PASS or N/A."""
        if not self.acceptance_criteria:
            return False
        for c in self.acceptance_criteria:
            if c.status not in (CriterionStatus.PASS, CriterionStatus.NOT_APPLICABLE):
                return False
        return True

    def has_evidence(self) -> bool:
        """Check that at least some evidence exists."""
        return len(self.evidence) > 0

    def contradiction_check(self) -> list[str]:
        """Check for contradictions between claims and evidence.

        Returns list of contradiction descriptions (empty = no contradictions).
        """
        contradictions: list[str] = []

        # Check: if tests failed but agent claims resolved
        has_test_failures = any(
            r.status in (TestStatus.FAILED, TestStatus.ERROR) for r in self.test_results
        )
        agent_claims_resolved = any(
            "resolved" in run.output_summary.lower() or "pass" in run.output_summary.lower()
            for run in self.agent_runs
            if run.output_summary
        )
        if has_test_failures and agent_claims_resolved:
            contradictions.append(
                "Agent claims success but test results show failures"
            )

        # Check: if acceptance criteria fail but quality is high
        criteria_failed = any(
            c.status == CriterionStatus.FAIL for c in self.acceptance_criteria
        )
        if criteria_failed:
            contradictions.append("Some acceptance criteria have failed status")

        # Check: no evidence at all
        if not self.evidence:
            contradictions.append("No evidence collected — cannot verify any claims")

        return contradictions

    def calculate_quality(self) -> QualityScore:
        """Calculate quality score based on collected evidence."""
        score = QualityScore()

        # Functional correctness: based on test results
        if self.test_results:
            passed = sum(1 for r in self.test_results if r.status == TestStatus.PASSED)
            score.functional_correctness = round(
                (passed / len(self.test_results)) * 100, 1
            )

        # Acceptance criteria
        if self.acceptance_criteria:
            met = sum(
                1
                for c in self.acceptance_criteria
                if c.status in (CriterionStatus.PASS, CriterionStatus.NOT_APPLICABLE)
            )
            score.acceptance_criteria = round(
                (met / len(self.acceptance_criteria)) * 100, 1
            )

        # Testing: full credit when enough tests executed
        if self.test_results:
            passed = sum(1 for r in self.test_results if r.status == TestStatus.PASSED)
            total = len(self.test_results)
            if total >= 3 and passed == total:
                score.testing = 100.0
            elif total >= 1:
                score.testing = min(100.0, (passed / max(total, 1)) * 100.0)
            else:
                score.testing = 0.0

        # Regression safety: inverse of failures
        if self.failures:
            unresolved = sum(1 for f in self.failures if not f.fix_result)
            score.regression_safety = max(
                0.0, 100.0 - (unresolved / max(len(self.failures), 1)) * 100.0
            )
        else:
            score.regression_safety = 100.0

        # Code quality: full credit when sufficient evidence collected
        if len(self.evidence) >= 5:
            score.code_quality = 100.0
        elif len(self.evidence) >= 1:
            score.code_quality = min(100.0, len(self.evidence) * 20.0)
        else:
            score.code_quality = 0.0

        # Security: no failures = good
        security_failures = [f for f in self.failures if "security" in f.category.value]
        score.security = 100.0 if not security_failures else 50.0

        # Architecture: full credit when sufficient agent runs completed
        if len(self.agent_runs) >= 5:
            score.architecture = 100.0
        elif len(self.agent_runs) >= 1:
            score.architecture = min(100.0, len(self.agent_runs) * 20.0)
        else:
            score.architecture = 0.0

        # Documentation: full credit if documentation agent ran
        doc_runs = [r for r in self.agent_runs if r.agent_role.value == "documentation"]
        if len(doc_runs) >= 1:
            score.documentation = 100.0
        else:
            score.documentation = 0.0

        # Maintainability: based on evidence diversity and agent coverage
        has_evidence = len(self.evidence) >= 3
        has_agent_coverage = len(self.agent_runs) >= 3
        if has_evidence and has_agent_coverage:
            score.maintainability = 100.0
        elif has_evidence or has_agent_coverage:
            score.maintainability = 50.0
        else:
            score.maintainability = 0.0

        score.calculate()
        return score

    def verify_completion(self) -> dict[str, bool]:
        """Check all hard gates for completion."""
        return {
            "problem_understood": self.task.classification is not None,
            "acceptance_criteria_met": self.all_acceptance_criteria_met(),
            "tests_passed": self.all_tests_passed() if self.test_results else False,
            "evidence_exists": self.has_evidence(),
            "no_contradictions": len(self.contradiction_check()) == 0,
            "no_unresolved_failures": all(f.fix_result for f in self.failures)
            if self.failures
            else True,
        }

    def is_resolved(self) -> bool:
        """Check if all hard gates pass."""
        gates = self.verify_completion()
        return all(gates.values())

    def build_report(self) -> str:
        """Build a human-readable evidence report."""
        lines = ["# Evidence Report", ""]

        lines.append(f"## Task: {self.task.problem}")
        lines.append(f"## Status: {self.task.status.value}")
        lines.append("")

        # Test results
        lines.append("## Test Results")
        if self.test_results:
            for r in self.test_results:
                lines.append(f"- [{r.status.value}] {r.test_name}: {r.actual or r.expected}")
        else:
            lines.append("- No tests executed")
        lines.append("")

        # Acceptance criteria
        lines.append("## Acceptance Criteria")
        for c in self.acceptance_criteria:
            lines.append(f"- [{c.status.value}] {c.description}")
            if c.actual_result:
                lines.append(f"  Actual: {c.actual_result}")
        lines.append("")

        # Failures
        lines.append("## Failures")
        if self.failures:
            for f in self.failures:
                lines.append(f"- {f.category.value}: {f.root_cause or f.symptom}")
                if f.fix_result:
                    lines.append(f"  Fix result: {f.fix_result}")
        else:
            lines.append("- No failures recorded")
        lines.append("")

        # Contradictions
        contradictions = self.contradiction_check()
        lines.append("## Contradiction Check")
        if contradictions:
            for c in contradictions:
                lines.append(f"- ⚠️ {c}")
        else:
            lines.append("- ✅ No contradictions detected")
        lines.append("")

        # Quality
        quality = self.calculate_quality()
        lines.append("## Quality Score")
        lines.append(f"- Functional Correctness: {quality.functional_correctness}%")
        lines.append(f"- Acceptance Criteria: {quality.acceptance_criteria}%")
        lines.append(f"- Testing: {quality.testing}%")
        lines.append(f"- Regression Safety: {quality.regression_safety}%")
        lines.append(f"- Code Quality: {quality.code_quality}%")
        lines.append(f"- Security: {quality.security}%")
        lines.append(f"- Total: {quality.display_score}")
        lines.append("")

        # Gates
        gates = self.verify_completion()
        lines.append("## Completion Gates")
        for gate, passed in gates.items():
            icon = "✅" if passed else "❌"
            lines.append(f"- {icon} {gate}")

        return "\n".join(lines)
