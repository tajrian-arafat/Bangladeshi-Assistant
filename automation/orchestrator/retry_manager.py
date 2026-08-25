"""Retry policy for technical failures."""

from __future__ import annotations

from dataclasses import dataclass


TECHNICAL_FAILURE_MARKERS = (
    "timeout",
    "connection reset",
    "browser crash",
    "malformed artifact",
    "temporary service failure",
    "cursor execution failure",
    "rate limit",
)


@dataclass
class RetryDecision:
    should_retry: bool
    retry_count: int
    escalate: bool
    reason: str


class RetryManager:
    MAX_RETRIES = 3

    def evaluate(self, error_message: str, current_retry_count: int) -> RetryDecision:
        lowered = error_message.lower()
        is_technical = any(marker in lowered for marker in TECHNICAL_FAILURE_MARKERS)
        if not is_technical:
            return RetryDecision(False, current_retry_count, True, "Non-technical failure — escalate")
        nxt = current_retry_count + 1
        if nxt > self.MAX_RETRIES:
            return RetryDecision(False, nxt, True, f"Exceeded max retries ({self.MAX_RETRIES})")
        return RetryDecision(True, nxt, False, f"Technical failure — retry {nxt}/{self.MAX_RETRIES}")
