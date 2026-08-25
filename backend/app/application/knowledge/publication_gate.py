"""Claim publication gate, conflict gate, and answer-support evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from app.domain.enums import (
    AnswerSupportLevel,
    ClaimPipelineStatus,
    ClaimType,
    InformationClass,
)


# Official publication requires Tier 1–2 for hard requirements/fees.
MAX_OFFICIAL_AUTHORITY_TIER = 2

# Soft freshness defaults (days). Callers may override.
DEFAULT_FRESHNESS_DAYS = {
    ClaimType.APPLICATION_URL.value: 30,
    ClaimType.FEE.value: 90,
    ClaimType.DOCUMENT.value: 180,
    ClaimType.CONDITIONAL_DOCUMENT.value: 180,
    ClaimType.PROCEDURE_STEP.value: 180,
    ClaimType.PROCESSING_TIME.value: 90,
    ClaimType.DEADLINE.value: 30,
}


@dataclass
class GateResult:
    allowed: bool
    reasons: list[str] = field(default_factory=list)
    support_level: AnswerSupportLevel = AnswerSupportLevel.INSUFFICIENT_EVIDENCE


def _parse_dt(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    return None


def evaluate_official_publication(
    *,
    pipeline_status: str,
    information_class: str,
    claim_type: str,
    evidence: list[dict[str, Any]],
    authority_tiers: list[int],
    has_unresolved_conflict: bool,
    verified_at: Any = None,
    reviewer_approved: bool = False,
    provenance_complete: bool = False,
    content_hash_present: bool | None = None,
    retrieved_at: Any = None,
    now: datetime | None = None,
    freshness_days: int | None = None,
) -> GateResult:
    """Hard gate for VERIFIED + OFFICIAL publication into runtime fields.

    VERIFIED means evidence passed verification rules — never merely 'source found'.
    """
    reasons: list[str] = []
    now = now or datetime.now(timezone.utc)

    if pipeline_status != ClaimPipelineStatus.VERIFIED.value:
        reasons.append(
            f"pipeline_status must be VERIFIED (got {pipeline_status}); "
            "finding a source is not verification"
        )

    if information_class != InformationClass.OFFICIAL.value:
        reasons.append(
            f"information_class must be OFFICIAL for authoritative publish "
            f"(got {information_class})"
        )

    if not evidence:
        reasons.append("evidence is required")

    if has_unresolved_conflict:
        reasons.append("unresolved material conflict blocks publication")

    if not authority_tiers:
        reasons.append("authority tier missing on evidence sources")
    else:
        best = min(authority_tiers)
        if best > MAX_OFFICIAL_AUTHORITY_TIER:
            reasons.append(
                f"best authority tier {best} exceeds max {MAX_OFFICIAL_AUTHORITY_TIER} "
                "for OFFICIAL publication"
            )

    if not reviewer_approved and verified_at is None:
        reasons.append("reviewer approval / verified_at required")

    if not provenance_complete:
        reasons.append("provenance incomplete (Claim→Evidence→SourceVersion→Source)")

    if content_hash_present is False:
        reasons.append(
            "durable SourceVersion content_hash missing; snapshot not auditable"
        )

    # Freshness (only enforced when retrieved_at known)
    rt = _parse_dt(retrieved_at)
    max_age = freshness_days
    if max_age is None:
        max_age = DEFAULT_FRESHNESS_DAYS.get(claim_type, 180)
    if rt is not None:
        age_days = (now - rt).total_seconds() / 86400.0
        if age_days > max_age:
            reasons.append(
                f"evidence freshness exceeded ({age_days:.0f}d > {max_age}d for {claim_type})"
            )

    # Evidence must actually support (non-empty excerpt or strong locator)
    supporting = [
        e
        for e in evidence
        if (e.get("evidence_excerpt") or e.get("locator") or e.get("knowledge_chunk_id"))
    ]
    if evidence and not supporting:
        reasons.append("evidence does not include excerpt/locator supporting the claim")

    allowed = len(reasons) == 0
    support = (
        AnswerSupportLevel.VERIFIED
        if allowed
        else (
            AnswerSupportLevel.CONFLICTED
            if has_unresolved_conflict
            else AnswerSupportLevel.INSUFFICIENT_EVIDENCE
        )
    )
    return GateResult(allowed=allowed, reasons=reasons, support_level=support)


def can_populate_must_need(
    *,
    information_class: str,
    pipeline_status: str,
    gate: GateResult | None = None,
) -> GateResult:
    """Only VERIFIED OFFICIAL claims may populate MUST NEED checklist items."""
    reasons: list[str] = []
    if information_class != InformationClass.OFFICIAL.value:
        reasons.append("PRACTICAL/DISCOVERY claims cannot populate MUST NEED")
    if pipeline_status != ClaimPipelineStatus.VERIFIED.value:
        reasons.append("MUST NEED requires VERIFIED claim")
    if gate is not None and not gate.allowed:
        reasons.extend(gate.reasons)
    return GateResult(
        allowed=len(reasons) == 0,
        reasons=reasons,
        support_level=(
            AnswerSupportLevel.VERIFIED
            if not reasons
            else AnswerSupportLevel.INSUFFICIENT_EVIDENCE
        ),
    )


def can_populate_fee(*, gate: GateResult, information_class: str, claim_type: str) -> GateResult:
    reasons = list(gate.reasons)
    if information_class != InformationClass.OFFICIAL.value:
        reasons.append("fee publish requires OFFICIAL class")
    if claim_type != ClaimType.FEE.value:
        reasons.append(f"fee publish requires claim_type=fee (got {claim_type})")
    if not gate.allowed:
        # already captured
        pass
    allowed = gate.allowed and information_class == InformationClass.OFFICIAL.value and (
        claim_type == ClaimType.FEE.value
    )
    return GateResult(
        allowed=allowed,
        reasons=reasons if not allowed else [],
        support_level=(
            AnswerSupportLevel.VERIFIED if allowed else AnswerSupportLevel.INSUFFICIENT_EVIDENCE
        ),
    )


def can_populate_procedure_step(*, gate: GateResult, information_class: str) -> GateResult:
    reasons = list(gate.reasons)
    if information_class != InformationClass.OFFICIAL.value:
        reasons.append("procedure publish requires OFFICIAL class")
    allowed = gate.allowed and information_class == InformationClass.OFFICIAL.value
    return GateResult(
        allowed=allowed,
        reasons=reasons if not allowed else [],
        support_level=(
            AnswerSupportLevel.VERIFIED if allowed else AnswerSupportLevel.INSUFFICIENT_EVIDENCE
        ),
    )


def answer_support_for_service_claims(
    claims: list[dict[str, Any]],
) -> AnswerSupportLevel:
    """Derive answer support level from claim statuses for a service."""
    if not claims:
        return AnswerSupportLevel.INSUFFICIENT_EVIDENCE
    statuses = {c.get("pipeline_status") for c in claims}
    if ClaimPipelineStatus.CONFLICTING.value in statuses:
        return AnswerSupportLevel.CONFLICTED
    verified_official = [
        c
        for c in claims
        if c.get("pipeline_status") == ClaimPipelineStatus.VERIFIED.value
        and c.get("information_class") == InformationClass.OFFICIAL.value
        and c.get("is_published")
    ]
    if verified_official and len(verified_official) == len(
        [
            c
            for c in claims
            if c.get("information_class") == InformationClass.OFFICIAL.value
            and c.get("pipeline_status")
            not in {
                ClaimPipelineStatus.REJECTED.value,
                ClaimPipelineStatus.OUTDATED.value,
            }
        ]
    ):
        return AnswerSupportLevel.VERIFIED
    if verified_official:
        return AnswerSupportLevel.PARTIALLY_SUPPORTED
    return AnswerSupportLevel.INSUFFICIENT_EVIDENCE


def conflict_blocks_publication(status_a: str, status_b: str) -> bool:
    """Conflicting claims never silently enter authoritative runtime knowledge."""
    blocked = {
        ClaimPipelineStatus.CONFLICTING.value,
        ClaimPipelineStatus.PENDING_REVIEW.value,
    }
    return status_a in blocked or status_b in blocked


def assert_mapping_safe(
    *,
    catalogue_service_id: str,
    expected_runtime_slug: str | None,
    actual_runtime_slug: str | None,
    mapping_review_status: str,
    allow_overwrite_seed: bool,
    target_is_mvp_seed: bool,
) -> GateResult:
    reasons: list[str] = []
    if mapping_review_status == "BLOCKED":
        reasons.append("mapping is BLOCKED")
    if expected_runtime_slug and actual_runtime_slug and expected_runtime_slug != actual_runtime_slug:
        reasons.append(
            f"mapping targets wrong service: expected slug {expected_runtime_slug}, "
            f"got {actual_runtime_slug}"
        )
    if target_is_mvp_seed and not allow_overwrite_seed:
        reasons.append(
            "existing MVP seed cannot be silently overwritten "
            f"(catalogue_service_id={catalogue_service_id})"
        )
    return GateResult(allowed=len(reasons) == 0, reasons=reasons)
