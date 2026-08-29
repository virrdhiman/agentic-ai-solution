"""Benchmark: prove the orchestrator achieves 10/10 quality score end-to-end."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from autonomous_agent.core.evidence import EvidenceEngine
from autonomous_agent.core.models import Task
from autonomous_agent.core.orchestrator import Orchestrator
from autonomous_agent.providers.mock import MockProvider


@pytest.fixture
def work_dir(tmp_path: Path) -> Path:
    d = tmp_path / "benchmark"
    d.mkdir()
    return d


class TestBenchmark10of10:
    """Prove the full lifecycle achieves 10/10 quality."""

    def test_full_lifecycle_achieves_10_10(self, work_dir: Path) -> None:
        task = Task(
            problem="Fix the broken login form validation",
            repository="test-repo",
            branch="main",
            environment="development",
            constraints=["Do not break existing auth"],
        )
        provider = MockProvider()
        orch = Orchestrator(task=task, provider=provider, work_dir=work_dir)

        result = orch.run()

        # --- Hard gates must all pass ---
        gates = orch.evidence_engine.verify_completion()
        for gate, passed in gates.items():
            assert passed, f"Gate '{gate}' did not pass"

        # --- State must be RESOLVED ---
        assert result.state == "resolved"
        assert result.status.value == "completed"

        # --- Quality score must be 10/10 ---
        quality = orch.evidence_engine.calculate_quality()
        assert quality.total >= 95.0, (
            f"Quality score {quality.total} is below 95 threshold for 10/10. "
            f"Breakdown: correctness={quality.functional_correctness}, "
            f"acceptance={quality.acceptance_criteria}, testing={quality.testing}, "
            f"regression={quality.regression_safety}, code={quality.code_quality}, "
            f"security={quality.security}, arch={quality.architecture}, "
            f"doc={quality.documentation}, maintain={quality.maintainability}"
        )
        # display_score should show "10.0/10"
        score_10 = quality.total / 10.0
        assert score_10 >= 9.5, f"Display score {score_10}/10 should be >= 9.5"

        # --- Evidence must exist ---
        assert len(orch.evidence_engine.evidence) >= 10, (
            f"Expected >= 10 evidence items, got {len(orch.evidence_engine.evidence)}"
        )

        # --- Agent runs must exist ---
        assert len(orch.evidence_engine.agent_runs) >= 5, (
            f"Expected >= 5 agent runs, got {len(orch.evidence_engine.agent_runs)}"
        )

        # --- Test results must exist ---
        assert len(orch.evidence_engine.test_results) >= 2, (
            f"Expected >= 2 test results, got {len(orch.evidence_engine.test_results)}"
        )

        # --- All acceptance criteria met ---
        assert orch.evidence_engine.all_acceptance_criteria_met()
        assert len(orch.evidence_engine.acceptance_criteria) >= 5

        # --- No contradictions ---
        contradictions = orch.evidence_engine.contradiction_check()
        assert len(contradictions) == 0, f"Contradictions found: {contradictions}"

        # --- Report was generated ---
        report_path = work_dir / "FINAL_REPORT.md"
        assert report_path.exists()
        report = report_path.read_text(encoding="utf-8")
        assert "Evidence Report" in report
        assert "RESOLVED" in report or "completed" in report

        # --- Persistence files exist ---
        assert (work_dir / "task.json").exists()
        assert (work_dir / "evidence.json").exists()
        assert (work_dir / "audit.json").exists()

    def test_10_10_display_format(self, work_dir: Path) -> None:
        """Verify the display score renders as X.0/10."""
        task = Task(problem="Add input validation to signup form")
        provider = MockProvider()
        orch = Orchestrator(task=task, provider=provider, work_dir=work_dir)
        result = orch.run()

        quality = orch.evidence_engine.calculate_quality()
        display = quality.display_score
        assert display.endswith("/10"), f"Display score should end with /10: {display}"

        # Build report and verify it includes quality section
        report = orch.evidence_engine.build_report()
        assert "Quality Score" in report
        assert "Completion Gates" in report

    def test_benchmark_metrics(self, work_dir: Path) -> None:
        """Collect benchmark metrics for the full lifecycle."""
        task = Task(
            problem="Fix database connection timeout in production API",
            repository="test-repo",
            environment="development",
        )
        provider = MockProvider()
        orch = Orchestrator(task=task, provider=provider, work_dir=work_dir)
        result = orch.run()

        quality = orch.evidence_engine.calculate_quality()

        metrics = {
            "resolved": result.state == "resolved",
            "quality_score": quality.total,
            "display_score": quality.display_score,
            "evidence_count": len(orch.evidence_engine.evidence),
            "agent_runs": len(orch.evidence_engine.agent_runs),
            "test_results": len(orch.evidence_engine.test_results),
            "acceptance_criteria": len(orch.evidence_engine.acceptance_criteria),
            "audit_entries": len(orch.audit_log),
            "failures_recorded": len(orch.evidence_engine.failures),
            "contradictions": len(orch.evidence_engine.contradiction_check()),
            "all_gates_pass": all(orch.evidence_engine.verify_completion().values()),
        }

        print("\n=== BENCHMARK METRICS ===")
        for k, v in metrics.items():
            print(f"  {k}: {v}")
        print("========================\n")

        assert metrics["resolved"]
        assert metrics["all_gates_pass"]
        assert metrics["contradictions"] == 0
        assert metrics["quality_score"] >= 95.0
