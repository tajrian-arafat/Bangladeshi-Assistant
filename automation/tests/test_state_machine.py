"""State machine transition tests."""

from __future__ import annotations

import pytest

from automation.schemas.state import WorkflowStatus, assert_transition


def test_ready_to_running() -> None:
    assert_transition(WorkflowStatus.READY, WorkflowStatus.RUNNING)


def test_illegal_transition_raises() -> None:
    with pytest.raises(ValueError):
        assert_transition(WorkflowStatus.READY, WorkflowStatus.COMPLETE)


def test_validating_to_auto_continue() -> None:
    assert_transition(WorkflowStatus.VALIDATING_RESULT, WorkflowStatus.AUTO_CONTINUE)
