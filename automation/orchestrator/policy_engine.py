"""Unattended escalation policy — defer local issues, block only global safety risks."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class EscalationPolicy(StrEnum):
    AUTO_DEFER_AND_CONTINUE = "AUTO_DEFER_AND_CONTINUE"
    HUMAN_APPROVAL_REQUIRED_FOR_CURRENT_ITEM = "HUMAN_APPROVAL_REQUIRED_FOR_CURRENT_ITEM"
    BLOCKED_GLOBAL = "BLOCKED_GLOBAL"
    DEFERRED_HUMAN_REVIEW = "DEFERRED_HUMAN_REVIEW"


GLOBAL_BLOCK_MARKERS = (
    "corrupt",
    "corruption",
    "deployment_allowed",
    "deployment lock",
    "illegal workflow transition",
    "repository corruption",
    "provenance corruption",
    "state machine",
    "unrecoverable",
)

LOCAL_DEFER_MARKERS = (
    "conflicting fee",
    "conflict",
    "missing document",
    "outdated url",
    "unverified",
    "partial",
    "legacy seed",
    "seed replacement",
    "runtime_replacement_pending",
    "knowledge gap",
    "regression",
    "supervisor review",
)


@dataclass
class PolicyDecision:
    policy: EscalationPolicy
    reason: str
    continue_workflow: bool
    block_publication: bool = False
    record_deferred_review: bool = False


class PolicyEngine:
    """Apply unattended decision hierarchy for knowledge-construction runs."""

    def evaluate_phase_outcome(
        self,
        *,
        phase: str,
        result: dict[str, Any],
        workflow_status: str,
        retry_count: int,
        max_retries: int = 3,
    ) -> PolicyDecision:
        summary = (result.get("summary") or "").lower()
        hallucinations = int(result.get("hallucinations") or 0)
        citation_failures = int(result.get("citation_failures") or 0)
        critical_conflicts = int(result.get("critical_conflicts") or 0)
        regressions = int(result.get("regressions") or 0)
        status = (result.get("status") or "").upper()

        if any(marker in summary for marker in GLOBAL_BLOCK_MARKERS):
            return PolicyDecision(
                policy=EscalationPolicy.BLOCKED_GLOBAL,
                reason=f"Global safety marker in phase outcome: {summary[:120]}",
                continue_workflow=False,
            )

        if hallucinations > 0 or citation_failures > 0:
            if retry_count < max_retries and phase in {"E2E", "REGRESSION"}:
                return PolicyDecision(
                    policy=EscalationPolicy.AUTO_DEFER_AND_CONTINUE,
                    reason="Quality gate failure — retry phase before deferral",
                    continue_workflow=True,
                    block_publication=True,
                )
            return PolicyDecision(
                policy=EscalationPolicy.BLOCKED_GLOBAL,
                reason="Hallucination or citation integrity failure after retries",
                continue_workflow=False,
                block_publication=True,
            )

        if critical_conflicts > 0 and phase == "PUBLICATION":
            return PolicyDecision(
                policy=EscalationPolicy.DEFERRED_HUMAN_REVIEW,
                reason="Critical publication conflict — defer item, continue catalogue",
                continue_workflow=True,
                block_publication=True,
                record_deferred_review=True,
            )

        if "legacy seed" in summary or "seed replacement" in summary:
            return PolicyDecision(
                policy=EscalationPolicy.DEFERRED_HUMAN_REVIEW,
                reason="Legacy seed replacement pending human review",
                continue_workflow=True,
                block_publication=False,
                record_deferred_review=True,
            )

        if regressions > 0 or status in {"BLOCKED", "FAILED"} or workflow_status == "SUPERVISOR_REVIEW":
            if phase in {"E2E", "REGRESSION"} and retry_count < max_retries:
                return PolicyDecision(
                    policy=EscalationPolicy.AUTO_DEFER_AND_CONTINUE,
                    reason=f"Recoverable {phase} failure — auto-retry",
                    continue_workflow=True,
                )
            if phase in {"E2E", "REGRESSION"}:
                return PolicyDecision(
                    policy=EscalationPolicy.DEFERRED_HUMAN_REVIEW,
                    reason=f"{phase} failed after retry limit — defer batch item",
                    continue_workflow=False,
                    record_deferred_review=True,
                )

        if any(marker in summary for marker in LOCAL_DEFER_MARKERS):
            return PolicyDecision(
                policy=EscalationPolicy.AUTO_DEFER_AND_CONTINUE,
                reason="Local knowledge issue — defer unsafe claims and continue",
                continue_workflow=True,
                block_publication=True,
                record_deferred_review=True,
            )

        if result.get("requires_escalation"):
            return PolicyDecision(
                policy=EscalationPolicy.DEFERRED_HUMAN_REVIEW,
                reason=result.get("summary") or "Escalation flagged — deferred human review",
                continue_workflow=True,
                record_deferred_review=True,
            )

        return PolicyDecision(
            policy=EscalationPolicy.AUTO_DEFER_AND_CONTINUE,
            reason="Phase outcome safe to continue",
            continue_workflow=True,
        )

    def evaluate_service_issue(self, issue: str) -> PolicyDecision:
        lowered = issue.lower()
        if any(marker in lowered for marker in GLOBAL_BLOCK_MARKERS):
            return PolicyDecision(
                policy=EscalationPolicy.BLOCKED_GLOBAL,
                reason=issue,
                continue_workflow=False,
            )
        return PolicyDecision(
            policy=EscalationPolicy.AUTO_DEFER_AND_CONTINUE,
            reason=f"Service-local issue deferred: {issue}",
            continue_workflow=True,
            block_publication=True,
            record_deferred_review=True,
        )
