"""Deterministic AI orchestration pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.pipeline.banglish import normalize_banglish
from app.ai.pipeline.confidence import calculate_confidence
from app.ai.pipeline.conflict import detect_conflicts
from app.ai.pipeline.entities import extract_entities
from app.ai.pipeline.intent import classify_intent
from app.ai.pipeline.language import detect_language
from app.ai.pipeline.safety import validate_safety
from app.application.engines.checklist_engine import ChecklistEngine
from app.application.engines.procedure_engine import ProcedureEngine
from app.domain.models.knowledge import Service
from app.retrieval.hybrid_search import HybridSearchService
from app.schemas.chat import (
    AnswerPayload,
    ChatRequest,
    ChecklistItemResponse,
    CitationResponse,
    FeeResponse,
    ProcedureStepResponse,
)


@dataclass
class PipelineContext:
    message: str
    normalized_message: str
    language: str
    intent: str
    entities: dict[str, Any] = field(default_factory=dict)
    service: Service | None = None
    evidence: list[dict[str, Any]] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    confidence: str = "low"
    clarifications_needed: list[str] = field(default_factory=list)


class Orchestrator:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.search = HybridSearchService(session)
        self.checklist_engine = ChecklistEngine(session)
        self.procedure_engine = ProcedureEngine(session)

    async def run(self, request: ChatRequest) -> tuple[AnswerPayload, str, str, list[CitationResponse], PipelineContext]:
        ctx = PipelineContext(
            message=request.message,
            normalized_message=request.message,
            language="auto",
            intent="unsupported",
        )

        ctx.language = detect_language(request.message, request.language_preference)
        ctx.normalized_message = normalize_banglish(request.message)
        ctx.intent = classify_intent(ctx.normalized_message, request.clarifications)
        ctx.entities = await extract_entities(self.session, ctx.normalized_message)
        ctx.service = ctx.entities.get("service")
        ctx.clarifications_needed = self._clarifications_needed(ctx, request)

        if ctx.clarifications_needed:
            return (
                AnswerPayload(
                    summary=self._clarification_prompt(ctx),
                    clarifications_needed=ctx.clarifications_needed,
                ),
                "medium",
                ctx.intent,
                [],
                ctx,
            )

        if ctx.service:
            ctx.evidence = await self.search.retrieve_for_service(ctx.service, ctx.normalized_message)
        else:
            ctx.evidence = await self.search.search(ctx.normalized_message, limit=5)

        ctx.conflicts = detect_conflicts(ctx.evidence)
        answer = await self._build_answer(ctx, request)
        ctx.confidence = calculate_confidence(ctx.service, ctx.evidence, ctx.conflicts)
        citations = self._build_citations(ctx.evidence)
        validate_safety(answer.summary)

        return answer, ctx.confidence, ctx.intent, citations, ctx

    def _clarifications_needed(self, ctx: PipelineContext, request: ChatRequest) -> list[str]:
        if not ctx.service:
            return []
        slug = ctx.service.slug
        clarifications = request.clarifications or {}
        if slug in {"passport-renewal", "passport-reissue"}:
            if "passport_type" not in clarifications:
                return ["Is this an e-passport or MRP passport?"]
            if "application_type" not in clarifications:
                return ["Is this renewal, reissue, or first-time application?"]
        if slug == "driving-licence-renewal" and "licence_class" not in clarifications:
            return ["Which licence class are you renewing (e.g., motorcycle, car)?"]
        return []

    def _clarification_prompt(self, ctx: PipelineContext) -> str:
        if ctx.language == "bn":
            return "Apnar jonno shothik tottho dite, ekti follow-up proshno ache."
        return "To provide accurate guidance, I need one follow-up answer."

    async def _build_answer(self, ctx: PipelineContext, request: ChatRequest) -> AnswerPayload:
        if not ctx.service:
            return AnswerPayload(
                summary=(
                    "I could not match your query to a verified government service. "
                    "Try browsing the service catalog or rephrase your question."
                ),
                warnings=["No verified service match found."],
            )

        checklist = await self.checklist_engine.build(ctx.service, request.clarifications or {})
        steps = await self.procedure_engine.build_steps(ctx.service)
        await self.session.refresh(ctx.service, ["fees"])
        fees = [
            FeeResponse(
                amount=fee.amount,
                currency=fee.currency,
                evidence_id=str(fee.evidence_chunk_id) if fee.evidence_chunk_id else None,
            )
            for fee in ctx.service.fees
        ]

        warnings = list(ctx.conflicts)
        if not fees:
            warnings.append("Fee information is not yet verified. Confirm at the official office.")
        if not any(s.official_url for s in steps):
            warnings.append("Official application URLs are not yet verified.")

        summary = (
            f"Here is verified structured guidance for {ctx.service.name_en}. "
            "All facts below come from our knowledge base."
        )
        if ctx.language == "bn":
            summary = (
                f"{ctx.service.name_bn} somporke verified tottho niche dewa hoyeche. "
                "Shob tottho amader knowledge base theke neya."
            )

        return AnswerPayload(
            summary=summary,
            checklist=[
                ChecklistItemResponse(item=c.label, type=c.item_type, evidence_id=c.evidence_id)
                for c in checklist
            ],
            steps=steps,
            fees=fees,
            warnings=warnings,
        )

    def _build_citations(self, evidence: list[dict[str, Any]]) -> list[CitationResponse]:
        citations: list[CitationResponse] = []
        for item in evidence[:5]:
            verified = item.get("last_verified_at")
            if verified is not None and not isinstance(verified, str):
                verified = verified.isoformat()
            citations.append(
                CitationResponse(
                    evidence_id=item.get("id", ""),
                    source_title=item.get("source_title", "Knowledge base"),
                    source_url=item.get("source_url"),
                    tier=item.get("tier", 6),
                    last_verified_at=verified,
                    excerpt=item.get("excerpt", "")[:500],
                )
            )
        return citations
