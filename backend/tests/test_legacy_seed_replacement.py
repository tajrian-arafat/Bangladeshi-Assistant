"""Tests for legacy seed readiness distinction and replacement workflow."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.application.knowledge.readiness import (
    ReadinessBlockingReason,
    ReadinessLevel,
    compute_service_readiness,
)
from app.domain.enums import ClaimPipelineStatus, ClaimType, InformationClass
from app.domain.models.claims import Claim


def _claim(*, published: bool = False, claim_type: str = ClaimType.FEE.value) -> Claim:
    return Claim(
        id=uuid4(),
        service_id=uuid4(),
        research_claim_key=f"test::{claim_type}",
        claim_type=claim_type,
        subject="s",
        predicate="p",
        value="v",
        information_class=InformationClass.OFFICIAL.value,
        pipeline_status=ClaimPipelineStatus.VERIFIED.value,
        verified_at=datetime.now(timezone.utc),
        is_published=published,
    )


def test_readiness_green_when_all_verified_published() -> None:
    claims = [_claim(published=True), _claim(published=True, claim_type=ClaimType.APPLICATION_URL.value)]
    detail = compute_service_readiness(
        claims=claims,
        published_official=2,
        critical_gaps=0,
        seed_blocked_claim_ids=frozenset(),
    )
    assert detail.readiness == ReadinessLevel.GREEN.value
    assert detail.knowledge_ready is True
    assert detail.legacy_replacement_pending is False


def test_readiness_legacy_block_not_knowledge_gap() -> None:
    fee = _claim(published=False)
    url = _claim(published=True, claim_type=ClaimType.APPLICATION_URL.value)
    detail = compute_service_readiness(
        claims=[fee, url],
        published_official=1,
        critical_gaps=0,
        seed_blocked_claim_ids=frozenset({fee.id}),
    )
    assert detail.readiness == ReadinessLevel.YELLOW.value
    assert detail.knowledge_ready is True
    assert detail.legacy_replacement_pending is True
    assert detail.runtime_replacement_pending is True
    assert detail.blocking_reason == ReadinessBlockingReason.LEGACY_DATA_REPLACEMENT_PENDING.value


def test_readiness_knowledge_gap_when_unpublished_not_seed_blocked() -> None:
    doc = _claim(published=False, claim_type=ClaimType.DOCUMENT.value)
    detail = compute_service_readiness(
        claims=[doc],
        published_official=0,
        critical_gaps=0,
        seed_blocked_claim_ids=frozenset(),
    )
    assert detail.readiness == ReadinessLevel.RED.value
    assert detail.knowledge_ready is False
    assert detail.blocking_reason == ReadinessBlockingReason.KNOWLEDGE_GAP.value


def test_readiness_mixed_block() -> None:
    fee = _claim(published=False)
    doc = _claim(published=False, claim_type=ClaimType.DOCUMENT.value)
    url = _claim(published=True, claim_type=ClaimType.APPLICATION_URL.value)
    detail = compute_service_readiness(
        claims=[fee, doc, url],
        published_official=1,
        critical_gaps=0,
        seed_blocked_claim_ids=frozenset({fee.id}),
    )
    assert detail.blocking_reason == ReadinessBlockingReason.MIXED.value
    assert detail.knowledge_ready is False
    assert detail.legacy_replacement_pending is True
