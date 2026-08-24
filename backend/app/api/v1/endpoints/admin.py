"""Admin API endpoints (RBAC to be added)."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.application.knowledge.claim_review_service import ClaimReviewService
from app.application.services.admin_service import AdminService
from app.schemas.admin import (
    AdminDashboardStats,
    AdminReviewListResponse,
    ClaimActionRequest,
    ClaimListResponse,
    ClaimOut,
    FeatureFlagOut,
    FeatureFlagUpdate,
    KnowledgeGapListResponse,
    KnowledgeGapOut,
    ProvenanceResponse,
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard", response_model=AdminDashboardStats)
async def admin_dashboard(
    session: AsyncSession = Depends(get_session),
) -> AdminDashboardStats:
    return await AdminService(session).get_dashboard_stats()


@router.get("/feature-flags", response_model=list[FeatureFlagOut])
async def list_feature_flags(
    session: AsyncSession = Depends(get_session),
) -> list[FeatureFlagOut]:
    return await AdminService(session).list_feature_flags()


@router.patch("/feature-flags/{key}", response_model=FeatureFlagOut)
async def update_feature_flag(
    key: str,
    payload: FeatureFlagUpdate,
    session: AsyncSession = Depends(get_session),
) -> FeatureFlagOut:
    return await AdminService(session).update_feature_flag(key, payload.enabled)


@router.get("/review-queue", response_model=AdminReviewListResponse)
async def list_review_queue(
    session: AsyncSession = Depends(get_session),
) -> AdminReviewListResponse:
    return await AdminService(session).list_review_queue()


@router.get("/claims", response_model=ClaimListResponse)
async def list_claims(
    service_id: UUID | None = None,
    pipeline_status: str | None = None,
    limit: int = Query(default=50, le=200),
    session: AsyncSession = Depends(get_session),
) -> ClaimListResponse:
    items = await ClaimReviewService(session).list_claims(
        service_id=service_id, pipeline_status=pipeline_status, limit=limit
    )
    return ClaimListResponse(items=[ClaimOut.model_validate(c) for c in items], total=len(items))


@router.get("/claims/{claim_id}", response_model=ClaimOut)
async def get_claim(
    claim_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> ClaimOut:
    claim = await ClaimReviewService(session).get_claim(claim_id)
    return ClaimOut.model_validate(claim)


@router.get("/claims/{claim_id}/provenance", response_model=ProvenanceResponse)
async def inspect_claim_provenance(
    claim_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> ProvenanceResponse:
    data = await ClaimReviewService(session).inspect_provenance(claim_id)
    return ProvenanceResponse(**data)


@router.post("/claims/{claim_id}/approve", response_model=ClaimOut)
async def approve_claim(
    claim_id: UUID,
    payload: ClaimActionRequest,
    session: AsyncSession = Depends(get_session),
) -> ClaimOut:
    claim = await ClaimReviewService(session).approve_claim(
        claim_id,
        admin_user_id=payload.admin_user_id,
        notes=payload.notes,
        force=payload.force,
    )
    return ClaimOut.model_validate(claim)


@router.post("/claims/{claim_id}/reject", response_model=ClaimOut)
async def reject_claim(
    claim_id: UUID,
    payload: ClaimActionRequest,
    session: AsyncSession = Depends(get_session),
) -> ClaimOut:
    claim = await ClaimReviewService(session).reject_claim(
        claim_id, admin_user_id=payload.admin_user_id, notes=payload.notes
    )
    return ClaimOut.model_validate(claim)


@router.post("/claims/{claim_id}/mark-conflict", response_model=ClaimOut)
async def mark_claim_conflict(
    claim_id: UUID,
    payload: ClaimActionRequest,
    session: AsyncSession = Depends(get_session),
) -> ClaimOut:
    claim = await ClaimReviewService(session).mark_conflict(
        claim_id, admin_user_id=payload.admin_user_id, notes=payload.notes
    )
    return ClaimOut.model_validate(claim)


@router.post("/claims/{claim_id}/request-evidence", response_model=ClaimOut)
async def request_claim_evidence(
    claim_id: UUID,
    payload: ClaimActionRequest,
    session: AsyncSession = Depends(get_session),
) -> ClaimOut:
    claim = await ClaimReviewService(session).request_more_evidence(
        claim_id, admin_user_id=payload.admin_user_id, notes=payload.notes
    )
    return ClaimOut.model_validate(claim)


@router.post("/claims/{claim_id}/mark-outdated", response_model=ClaimOut)
async def mark_claim_outdated(
    claim_id: UUID,
    payload: ClaimActionRequest,
    session: AsyncSession = Depends(get_session),
) -> ClaimOut:
    claim = await ClaimReviewService(session).mark_outdated(
        claim_id, admin_user_id=payload.admin_user_id, notes=payload.notes
    )
    return ClaimOut.model_validate(claim)


@router.get("/knowledge-gaps", response_model=KnowledgeGapListResponse)
async def list_knowledge_gaps(
    service_id: UUID | None = None,
    limit: int = Query(default=50, le=200),
    session: AsyncSession = Depends(get_session),
) -> KnowledgeGapListResponse:
    items = await ClaimReviewService(session).list_gaps(service_id=service_id, limit=limit)
    return KnowledgeGapListResponse(
        items=[KnowledgeGapOut.model_validate(g) for g in items], total=len(items)
    )
