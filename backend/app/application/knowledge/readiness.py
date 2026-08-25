"""Post-publication readiness — distinguish knowledge gaps from legacy seed blocks."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any
from uuid import UUID

from app.domain.enums import ClaimPipelineStatus, InformationClass
from app.domain.models.claims import Claim


class ReadinessLevel(StrEnum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"


class ReadinessBlockingReason(StrEnum):
    KNOWLEDGE_GAP = "KNOWLEDGE_GAP"
    LEGACY_DATA_REPLACEMENT_PENDING = "LEGACY_DATA_REPLACEMENT_PENDING"
    MIXED = "MIXED"


@dataclass
class ServiceReadinessDetail:
    """Extended readiness for a catalogue service after publication."""

    readiness: str
    knowledge_ready: bool
    legacy_replacement_pending: bool
    runtime_replacement_pending: bool
    blocking_reason: str | None
    verified_official_count: int = 0
    published_verified_count: int = 0
    seed_blocked_count: int = 0
    knowledge_gap_count: int = 0
    seed_blocked_claim_ids: list[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def compute_service_readiness(
    *,
    claims: list[Claim],
    published_official: int,
    critical_gaps: int,
    seed_blocked_claim_ids: set[UUID] | frozenset[UUID],
) -> ServiceReadinessDetail:
    """Classify readiness and separate knowledge gaps from legacy seed blocks."""
    verified_official = [
        c
        for c in claims
        if c.pipeline_status == ClaimPipelineStatus.VERIFIED.value
        and c.information_class == InformationClass.OFFICIAL.value
    ]
    if critical_gaps > 0:
        return ServiceReadinessDetail(
            readiness=ReadinessLevel.RED.value,
            knowledge_ready=False,
            legacy_replacement_pending=False,
            runtime_replacement_pending=False,
            blocking_reason=ReadinessBlockingReason.KNOWLEDGE_GAP.value,
            verified_official_count=len(verified_official),
            published_verified_count=sum(1 for c in verified_official if c.is_published),
            knowledge_gap_count=critical_gaps,
            seed_blocked_count=len(seed_blocked_claim_ids),
            seed_blocked_claim_ids=[str(i) for i in seed_blocked_claim_ids],
        )

    if not verified_official:
        return ServiceReadinessDetail(
            readiness=ReadinessLevel.RED.value,
            knowledge_ready=False,
            legacy_replacement_pending=False,
            runtime_replacement_pending=False,
            blocking_reason=ReadinessBlockingReason.KNOWLEDGE_GAP.value,
        )

    published_verified = [c for c in verified_official if c.is_published]
    unpublished = [c for c in verified_official if not c.is_published]
    seed_blocked = [c for c in unpublished if c.id in seed_blocked_claim_ids]
    knowledge_gap_unpublished = [c for c in unpublished if c.id not in seed_blocked_claim_ids]

    seed_count = len(seed_blocked)
    gap_count = len(knowledge_gap_unpublished)

    if len(published_verified) >= len(verified_official) and published_official > 0:
        return ServiceReadinessDetail(
            readiness=ReadinessLevel.GREEN.value,
            knowledge_ready=True,
            legacy_replacement_pending=False,
            runtime_replacement_pending=False,
            blocking_reason=None,
            verified_official_count=len(verified_official),
            published_verified_count=len(published_verified),
            seed_blocked_count=seed_count,
            knowledge_gap_count=gap_count,
            seed_blocked_claim_ids=[str(c.id) for c in seed_blocked],
        )

    if gap_count > 0 and seed_count > 0:
        blocking = ReadinessBlockingReason.MIXED.value
        knowledge_ready = False
    elif gap_count > 0:
        blocking = ReadinessBlockingReason.KNOWLEDGE_GAP.value
        knowledge_ready = False
    elif seed_count > 0:
        blocking = ReadinessBlockingReason.LEGACY_DATA_REPLACEMENT_PENDING.value
        knowledge_ready = True
    else:
        blocking = ReadinessBlockingReason.KNOWLEDGE_GAP.value
        knowledge_ready = False

    legacy_pending = seed_count > 0
    runtime_pending = legacy_pending and gap_count == 0

    readiness = ReadinessLevel.YELLOW.value if published_official > 0 else ReadinessLevel.RED.value

    return ServiceReadinessDetail(
        readiness=readiness,
        knowledge_ready=knowledge_ready,
        legacy_replacement_pending=legacy_pending,
        runtime_replacement_pending=runtime_pending,
        blocking_reason=blocking,
        verified_official_count=len(verified_official),
        published_verified_count=len(published_verified),
        seed_blocked_count=seed_count,
        knowledge_gap_count=gap_count,
        seed_blocked_claim_ids=[str(c.id) for c in seed_blocked],
    )
