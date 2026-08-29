"""Tests for the task state machine."""

import pytest

from autonomous_agent.core.state import (
    InvalidStateTransition,
    TaskState,
    VALID_TRANSITIONS,
    can_transition,
    transition,
)


class TestTaskState:
    def test_all_states_exist(self):
        assert len(TaskState) == 21
        assert TaskState.NEW.value == "new"
        assert TaskState.RESOLVED.value == "resolved"

    def test_new_to_understanding(self):
        assert can_transition(TaskState.NEW, TaskState.UNDERSTANDING)

    def test_new_to_cancelled(self):
        assert can_transition(TaskState.NEW, TaskState.CANCELLED)

    def test_invalid_new_to_resolved(self):
        assert not can_transition(TaskState.NEW, TaskState.RESOLVED)

    def test_full_happy_path_transitions(self):
        path = [
            TaskState.NEW,
            TaskState.UNDERSTANDING,
            TaskState.CLASSIFYING,
            TaskState.INVESTIGATING,
            TaskState.REPRODUCING,
            TaskState.DIAGNOSING,
            TaskState.PLANNING,
            TaskState.IMPLEMENTING,
            TaskState.TESTING,
            TaskState.REGRESSION_TESTING,
            TaskState.SECURITY_REVIEW,
            TaskState.CODE_REVIEW,
            TaskState.ADVERSARIAL_REVIEW,
            TaskState.ACCEPTANCE_CHECK,
            TaskState.EVIDENCE_CHECK,
            TaskState.RESOLVED,
        ]
        for i in range(len(path) - 1):
            assert can_transition(path[i], path[i + 1]), f"Failed: {path[i]} -> {path[i+1]}"

    def test_transition_returns_target_state(self):
        result = transition(TaskState.NEW, TaskState.UNDERSTANDING)
        assert result == TaskState.UNDERSTANDING

    def test_transition_raises_on_invalid(self):
        with pytest.raises(InvalidStateTransition) as exc_info:
            transition(TaskState.NEW, TaskState.RESOLVED)
        assert exc_info.value.from_state == TaskState.NEW
        assert exc_info.value.to_state == TaskState.RESOLVED

    def test_resolved_has_no_transitions(self):
        assert VALID_TRANSITIONS[TaskState.RESOLVED] == set()

    def test_cancelled_has_no_transitions(self):
        assert VALID_TRANSITIONS[TaskState.CANCELLED] == set()

    def test_repair_can_go_back_to_diagnosing(self):
        assert can_transition(TaskState.REPAIRING, TaskState.DIAGNOSING)

    def test_failed_can_go_to_investigating(self):
        assert can_transition(TaskState.FAILED, TaskState.INVESTIGATING)

    def test_human_action_can_resume_to_multiple_states(self):
        targets = VALID_TRANSITIONS[TaskState.HUMAN_ACTION_REQUIRED]
        assert TaskState.INVESTIGATING in targets
        assert TaskState.PLANNING in targets
        assert TaskState.IMPLEMENTING in targets
        assert TaskState.REPAIRING in targets
        assert TaskState.CANCELLED in targets
