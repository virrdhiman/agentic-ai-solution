"""Core state machine for task lifecycle management."""

from __future__ import annotations

from enum import Enum


class TaskState(str, Enum):
    """All possible states for a task."""

    NEW = "new"
    UNDERSTANDING = "understanding"
    CLASSIFYING = "classifying"
    INVESTIGATING = "investigating"
    REPRODUCING = "reproducing"
    DIAGNOSING = "diagnosing"
    PLANNING = "planning"
    IMPLEMENTING = "implementing"
    TESTING = "testing"
    FAILED = "failed"
    REPAIRING = "repairing"
    REGRESSION_TESTING = "regression_testing"
    SECURITY_REVIEW = "security_review"
    CODE_REVIEW = "code_review"
    ADVERSARIAL_REVIEW = "adversarial_review"
    DOCUMENTING = "documenting"
    ACCEPTANCE_CHECK = "acceptance_check"
    EVIDENCE_CHECK = "evidence_check"
    RESOLVED = "resolved"
    HUMAN_ACTION_REQUIRED = "human_action_required"
    CANCELLED = "cancelled"


# Valid transitions: source -> set of allowed targets
VALID_TRANSITIONS: dict[TaskState, set[TaskState]] = {
    TaskState.NEW: {
        TaskState.UNDERSTANDING,
        TaskState.CANCELLED,
        TaskState.HUMAN_ACTION_REQUIRED,
    },
    TaskState.UNDERSTANDING: {
        TaskState.CLASSIFYING,
        TaskState.FAILED,
        TaskState.CANCELLED,
        TaskState.HUMAN_ACTION_REQUIRED,
    },
    TaskState.CLASSIFYING: {
        TaskState.INVESTIGATING,
        TaskState.FAILED,
        TaskState.CANCELLED,
        TaskState.HUMAN_ACTION_REQUIRED,
    },
    TaskState.INVESTIGATING: {
        TaskState.REPRODUCING,
        TaskState.DIAGNOSING,
        TaskState.PLANNING,
        TaskState.FAILED,
        TaskState.CANCELLED,
        TaskState.HUMAN_ACTION_REQUIRED,
    },
    TaskState.REPRODUCING: {
        TaskState.DIAGNOSING,
        TaskState.FAILED,
        TaskState.CANCELLED,
        TaskState.HUMAN_ACTION_REQUIRED,
    },
    TaskState.DIAGNOSING: {
        TaskState.PLANNING,
        TaskState.FAILED,
        TaskState.CANCELLED,
        TaskState.HUMAN_ACTION_REQUIRED,
    },
    TaskState.PLANNING: {
        TaskState.IMPLEMENTING,
        TaskState.FAILED,
        TaskState.CANCELLED,
        TaskState.HUMAN_ACTION_REQUIRED,
    },
    TaskState.IMPLEMENTING: {
        TaskState.TESTING,
        TaskState.FAILED,
        TaskState.REPAIRING,
        TaskState.CANCELLED,
        TaskState.HUMAN_ACTION_REQUIRED,
    },
    TaskState.TESTING: {
        TaskState.REGRESSION_TESTING,
        TaskState.REPAIRING,
        TaskState.FAILED,
        TaskState.CANCELLED,
        TaskState.HUMAN_ACTION_REQUIRED,
    },
    TaskState.FAILED: {
        TaskState.REPAIRING,
        TaskState.INVESTIGATING,
        TaskState.CANCELLED,
        TaskState.HUMAN_ACTION_REQUIRED,
    },
    TaskState.REPAIRING: {
        TaskState.TESTING,
        TaskState.IMPLEMENTING,
        TaskState.DIAGNOSING,
        TaskState.FAILED,
        TaskState.CANCELLED,
        TaskState.HUMAN_ACTION_REQUIRED,
    },
    TaskState.REGRESSION_TESTING: {
        TaskState.SECURITY_REVIEW,
        TaskState.REPAIRING,
        TaskState.FAILED,
        TaskState.CANCELLED,
        TaskState.HUMAN_ACTION_REQUIRED,
    },
    TaskState.SECURITY_REVIEW: {
        TaskState.CODE_REVIEW,
        TaskState.REPAIRING,
        TaskState.FAILED,
        TaskState.CANCELLED,
        TaskState.HUMAN_ACTION_REQUIRED,
    },
    TaskState.CODE_REVIEW: {
        TaskState.ADVERSARIAL_REVIEW,
        TaskState.REPAIRING,
        TaskState.FAILED,
        TaskState.CANCELLED,
        TaskState.HUMAN_ACTION_REQUIRED,
    },
    TaskState.ADVERSARIAL_REVIEW: {
        TaskState.ACCEPTANCE_CHECK,
        TaskState.REPAIRING,
        TaskState.FAILED,
        TaskState.CANCELLED,
        TaskState.HUMAN_ACTION_REQUIRED,
    },
    TaskState.DOCUMENTING: {
        TaskState.ACCEPTANCE_CHECK,
        TaskState.EVIDENCE_CHECK,
        TaskState.CANCELLED,
        TaskState.HUMAN_ACTION_REQUIRED,
    },
    TaskState.ACCEPTANCE_CHECK: {
        TaskState.DOCUMENTING,
        TaskState.EVIDENCE_CHECK,
        TaskState.REPAIRING,
        TaskState.FAILED,
        TaskState.CANCELLED,
        TaskState.HUMAN_ACTION_REQUIRED,
    },
    TaskState.EVIDENCE_CHECK: {
        TaskState.RESOLVED,
        TaskState.REPAIRING,
        TaskState.FAILED,
        TaskState.HUMAN_ACTION_REQUIRED,
    },
    TaskState.RESOLVED: set(),
    TaskState.HUMAN_ACTION_REQUIRED: {
        TaskState.INVESTIGATING,
        TaskState.PLANNING,
        TaskState.IMPLEMENTING,
        TaskState.REPAIRING,
        TaskState.CANCELLED,
    },
    TaskState.CANCELLED: set(),
}


class InvalidStateTransition(Exception):
    """Raised when a state transition is not allowed."""

    def __init__(self, from_state: TaskState, to_state: TaskState) -> None:
        self.from_state = from_state
        self.to_state = to_state
        super().__init__(
            f"Invalid transition: {from_state.value} -> {to_state.value}. "
            f"Allowed: {[s.value for s in VALID_TRANSITIONS.get(from_state, set())]}"
        )


def can_transition(from_state: TaskState, to_state: TaskState) -> bool:
    """Check if a state transition is valid."""
    return to_state in VALID_TRANSITIONS.get(from_state, set())


def transition(from_state: TaskState, to_state: TaskState) -> TaskState:
    """Perform a state transition, raising on invalid."""
    if not can_transition(from_state, to_state):
        raise InvalidStateTransition(from_state, to_state)
    return to_state
