"""Retry policy tests."""

from __future__ import annotations

from automation.orchestrator.retry_manager import RetryManager


def test_technical_failure_retries() -> None:
    rm = RetryManager()
    d = rm.evaluate("network timeout", 0)
    assert d.should_retry
    assert not d.escalate


def test_max_retries_escalates() -> None:
    rm = RetryManager()
    d = rm.evaluate("browser crash", 3)
    assert d.escalate


def test_non_technical_escalates_immediately() -> None:
    rm = RetryManager()
    d = rm.evaluate("critical fee conflict unresolved", 0)
    assert not d.should_retry
    assert d.escalate
