"""Tests for the orchestrator."""

import json
from pathlib import Path

from autonomous_agent.core.models import Task, TaskStatus
from autonomous_agent.core.orchestrator import Orchestrator
from autonomous_agent.providers.mock import MockProvider


class TestOrchestrator:
    def setup_method(self):
        self.provider = MockProvider()

    def test_full_lifecycle_resolves(self, tmp_path):
        task = Task(problem="Fix the broken login")
        orch = Orchestrator(task=task, provider=self.provider, work_dir=tmp_path / "task1")
        result = orch.run()

        assert result.status == TaskStatus.COMPLETED
        assert result.state == "resolved"
        assert result.completed_at is not None

    def test_full_lifecycle_persists_state(self, tmp_path):
        task = Task(problem="Fix the bug")
        work_dir = tmp_path / "persist_test"
        orch = Orchestrator(task=task, provider=self.provider, work_dir=work_dir)
        orch.run()

        # Check task.json exists
        task_file = work_dir / "task.json"
        assert task_file.exists()
        data = json.loads(task_file.read_text())
        assert data["status"] == "completed"

        # Check evidence.json exists
        evidence_file = work_dir / "evidence.json"
        assert evidence_file.exists()

        # Check audit.json exists
        audit_file = work_dir / "audit.json"
        assert audit_file.exists()

    def test_full_lifecycle_creates_report(self, tmp_path):
        task = Task(problem="Add new feature")
        orch = Orchestrator(task=task, provider=self.provider, work_dir=tmp_path / "report_test")
        orch.run()

        report_file = tmp_path / "report_test" / "FINAL_REPORT.md"
        assert report_file.exists()
        content = report_file.read_text(encoding="utf-8")
        assert "Evidence Report" in content

    def test_evidence_engine_populated(self, tmp_path):
        task = Task(problem="Debug the error")
        orch = Orchestrator(task=task, provider=self.provider, work_dir=tmp_path / "ev_test")
        orch.run()

        assert len(orch.evidence_engine.evidence) > 0
        assert len(orch.evidence_engine.test_results) > 0
        assert len(orch.evidence_engine.agent_runs) > 0

    def test_audit_log_populated(self, tmp_path):
        task = Task(problem="Investigate issue")
        orch = Orchestrator(task=task, provider=self.provider, work_dir=tmp_path / "audit_test")
        orch.run()

        assert len(orch.audit_log) > 0
        actions = [a.action for a in orch.audit_log]
        assert "understand" in actions
        assert "classify" in actions

    def test_quality_score_calculated(self, tmp_path):
        task = Task(problem="Fix something")
        orch = Orchestrator(task=task, provider=self.provider, work_dir=tmp_path / "quality_test")
        orch.run()

        quality = orch.evidence_engine.calculate_quality()
        assert quality.total >= 0.0

    def test_classification_stored(self, tmp_path):
        task = Task(problem="Fix the broken login")
        orch = Orchestrator(task=task, provider=self.provider, work_dir=tmp_path / "class_test")
        orch.run()

        assert task.classification is not None

    def test_agent_team_set(self, tmp_path):
        task = Task(problem="Fix the bug")
        orch = Orchestrator(task=task, provider=self.provider, work_dir=tmp_path / "team_test")
        orch.run()

        assert len(task.agent_team) > 0

    def test_feature_request_classifies_correctly(self, tmp_path):
        task = Task(problem="Add a new dashboard feature")
        orch = Orchestrator(task=task, provider=self.provider, work_dir=tmp_path / "feature_test")
        orch.run()

        assert task.classification is not None
        assert task.classification.problem_type.value == "feature_request"
