"""Deterministic AI orchestration pipeline."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai.pipeline.banglish import normalize_banglish
from app.ai.pipeline.confidence import calculate_confidence
from app.ai.pipeline.conflict import detect_conflicts
from app.ai.pipeline.entities import extract_entities
from app.ai.pipeline.intent import classify_intent
from app.ai.pipeline.language import detect_language
from app.ai.pipeline.safety import validate_safety
from app.application.engines.checklist_engine import ChecklistEngine
from app.application.engines.procedure_engine import ProcedureEngine
from app.application.knowledge.claim_review_service import ClaimReviewService
from app.application.services.conversation_context import ConversationContext, ConversationContextService
from app.domain.enums import AnswerSupportLevel, ClaimPipelineStatus, InformationClass
from app.domain.models.claims import Claim
from app.domain.models.knowledge import Service, ServiceLink
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
    support_level: AnswerSupportLevel = AnswerSupportLevel.INSUFFICIENT_EVIDENCE


class Orchestrator:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.search = HybridSearchService(session)
        self.checklist_engine = ChecklistEngine(session)
        self.procedure_engine = ProcedureEngine(session)

    async def run(
        self,
        request: ChatRequest,
        *,
        conversation_context: ConversationContext | None = None,
    ) -> tuple[AnswerPayload, str, str, list[CitationResponse], PipelineContext]:
        ctx = PipelineContext(
            message=request.message,
            normalized_message=request.message,
            language="auto",
            intent="unsupported",
        )
        conv_ctx = conversation_context or ConversationContext()

        ctx.language = detect_language(request.message, request.language_preference)
        ctx.normalized_message = normalize_banglish(request.message)
        ctx.intent = classify_intent(ctx.normalized_message, request.clarifications)
        # Also classify on raw message for Bangla script intents
        if ctx.intent == "general_info":
            ctx.intent = classify_intent(request.message, request.clarifications)
        if conv_ctx.intent and ctx.intent == "general_info":
            ctx.intent = conv_ctx.intent

        ctx.entities = await extract_entities(self.session, ctx.normalized_message)
        if not ctx.entities.get("service"):
            ctx.entities = await extract_entities(self.session, request.message.lower())

        if not ctx.entities.get("service") and conv_ctx.service_slug:
            if ConversationContextService.is_follow_up_message(request.message):
                svc = await self._service_by_slug(conv_ctx.service_slug)
                if svc:
                    ctx.entities["service"] = svc
                    ctx.entities["service_slug"] = svc.slug
                    ctx.entities["service_match_method"] = "conversation_context"

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
            ctx.evidence = await self.search.retrieve_for_service(
                ctx.service, ctx.normalized_message
            )
        else:
            ctx.evidence = await self.search.search(ctx.normalized_message, limit=5)

        ctx.conflicts = detect_conflicts(ctx.evidence)
        if ctx.service:
            ctx.support_level = await ClaimReviewService(self.session).service_answer_support(
                ctx.service.id
            )
            # Only force CONFLICTED when claim pipeline actually has conflicting rows
            if ctx.service.status == "CONFLICTED":
                claim_conflict = await self._has_conflicting_claims(ctx.service.id)
                if claim_conflict:
                    ctx.support_level = AnswerSupportLevel.CONFLICTED
        answer = await self._build_answer(ctx, request)
        ctx.confidence = calculate_confidence(
            ctx.service, ctx.evidence, ctx.conflicts, support_level=ctx.support_level
        )
        citations = await self._build_citations(ctx)
        validate_safety(answer.summary)

        return answer, ctx.confidence, ctx.intent, citations, ctx

    async def _has_conflicting_claims(self, service_id) -> bool:
        result = await self.session.execute(
            select(Claim.id).where(
                Claim.service_id == service_id,
                Claim.pipeline_status == ClaimPipelineStatus.CONFLICTING.value,
            ).limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def _service_by_slug(self, slug: str) -> Service | None:
        result = await self.session.execute(select(Service).where(Service.slug == slug))
        return result.scalar_one_or_none()

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
        if slug == "civil-birth-registration-correction" and "correction_type" not in clarifications:
            return [
                "Which birth certificate correction do you need (name, date of birth, or other field)?"
            ]
        if slug == "birth-registration" and "correction_type" not in clarifications:
            msg = (ctx.message + " " + ctx.normalized_message).lower()
            if any(w in msg for w in ("vul", "wrong", "correction", "correct", "সংশোধন", "ভুল", "naam", "name", "নাম")):
                return [
                    "Which birth certificate correction do you need (name, date of birth, or other field)?"
                ]
        return []

    def _clarification_prompt(self, ctx: PipelineContext) -> str:
        if ctx.language == "bn":
            return "Apnar jonno shothik tottho dite, ekti follow-up proshno ache."
        return "To provide accurate guidance, I need one follow-up answer."

    async def _build_answer(self, ctx: PipelineContext, request: ChatRequest) -> AnswerPayload:
        if not ctx.service:
            return AnswerPayload(
                summary=(
                    "I could not match your query to a government service in the catalog. "
                    "Try browsing the service catalog or rephrase your question."
                ),
                warnings=["No service match found."],
                support_level=AnswerSupportLevel.INSUFFICIENT_EVIDENCE.value,
            )

        clarifications = dict(request.clarifications or {})
        if ctx.language == "bn":
            clarifications["_lang"] = "bn"

        checklist = await self.checklist_engine.build(
            ctx.service, clarifications, authoritative_only=True
        )
        steps = await self.procedure_engine.build_steps(ctx.service, claim_linked_only=True)
        await self.session.refresh(ctx.service, ["fees", "service_links"])

        fees: list[FeeResponse] = []
        for fee in ctx.service.fees:
            if fee.claim_id is None:
                continue
            fee_mode = None
            label = fee.label_en
            if fee.amount == "USE_OFFICIAL_CALCULATOR":
                fee_mode = "calculator"
                label = fee.label_en or "Use official fee calculator"
            fees.append(
                FeeResponse(
                    amount=fee.amount,
                    currency=fee.currency,
                    evidence_id=str(fee.claim_id),
                    label=label,
                    fee_mode=fee_mode,
                )
            )

        seed_fees_hidden = [f for f in ctx.service.fees if f.claim_id is None]
        warnings = list(ctx.conflicts)

        if ctx.support_level == AnswerSupportLevel.CONFLICTED:
            warnings.append(
                "Conflicting information exists for this service. "
                "Authoritative fees/documents are withheld until review resolves the conflict."
            )
            fees = []
        elif ctx.support_level == AnswerSupportLevel.INSUFFICIENT_EVIDENCE:
            warnings.append(
                "Guidance below is incomplete or not yet verified from official sources. "
                "Confirm with the responsible government office."
            )
        elif ctx.support_level == AnswerSupportLevel.PARTIALLY_SUPPORTED:
            warnings.append(
                "Only some facts for this service are verified. Treat unverified parts as provisional."
            )

        if seed_fees_hidden:
            warnings.append(
                "Seed/placeholder fee rows are not shown as authoritative "
                "(they are not linked to VERIFIED claims)."
            )
        if not fees and ctx.intent == "fee_inquiry":
            warnings.append(
                "No verified official fee amount is available for this service in the knowledge base. "
                "Do not rely on unofficial quoted amounts."
            )
        elif not fees:
            warnings.append("Fee information is not yet verified. Confirm at the official office.")

        # Hallucination guard: user mentions a specific BDT amount not in verified fees
        asked_amounts = set(re.findall(r"\b(\d{2,5})\b", ctx.message))
        verified_amounts = {f.amount for f in fees if f.amount.isdigit() or f.amount.replace(".", "", 1).isdigit()}
        for amt in asked_amounts:
            if amt in {"10", "45", "5"}:  # common non-fee numbers (days/years)
                continue
            if amt not in verified_amounts and any(
                w in ctx.message.lower() for w in ["fee", "bdt", "টাকা", "koto", "charge", "500", "230", "345", "460"]
            ):
                warnings.append(
                    f"The amount BDT {amt} is NOT confirmed as an official verified fee in this knowledge base. "
                    "Do not treat it as authoritative. Use only verified fees or the official calculator when indicated."
                )
                break

        # Calculator guidance
        if any(f.fee_mode == "calculator" for f in fees):
            warnings.append(
                "OFFICIAL: Fee must be calculated on the official portal calculator "
                "(https://services.nidw.gov.bd/nid-pub/fees). Static third-party amounts are not published."
            )

        official_urls = [
            link.url
            for link in (ctx.service.service_links or [])
            if link.is_verified
        ]
        if not official_urls and not any(s.official_url for s in steps):
            warnings.append("Official application URLs are not yet verified for this service.")

        # Practical layer (never merged into MUST NEED)
        practical_notes = await self._practical_notes(ctx.service.id)

        if ctx.support_level == AnswerSupportLevel.VERIFIED:
            summary = (
                f"Here is verified structured guidance for {ctx.service.name_en}. "
                "Facts below are backed by verified official claims."
            )
            if ctx.language == "bn":
                summary = (
                    f"{ctx.service.name_bn} সম্পর্কে যাচাইকৃত তথ্য নিচে দেওয়া হয়েছে। "
                    "এই তথ্য verified official claim-এর উপর ভিত্তি করে।"
                )
        else:
            summary = (
                f"Here is available structured information for {ctx.service.name_en}. "
                "This is not fully verified official guidance yet."
            )
            if ctx.language == "bn":
                summary = (
                    f"{ctx.service.name_bn} সম্পর্কে উপলব্ধ তথ্য নিচে দেওয়া হয়েছে। "
                    "এটি এখনো fully verified official guidance নয়।"
                )

        if practical_notes:
            summary += (
                " PRACTICAL notes (commonly reported, NOT official MUST NEED) are listed separately."
            )

        return AnswerPayload(
            summary=summary,
            checklist=[
                ChecklistItemResponse(
                    item=c.label,
                    type=c.item_type,
                    evidence_id=c.evidence_id,
                    layer=c.layer,
                    claim_linked=c.claim_linked,
                )
                for c in checklist
            ],
            steps=steps,
            fees=fees,
            warnings=warnings,
            support_level=ctx.support_level.value,
            practical_notes=practical_notes,
            official_urls=official_urls,
        )

    async def _practical_notes(self, service_id) -> list[str]:
        result = await self.session.execute(
            select(Claim).where(
                Claim.service_id == service_id,
                Claim.information_class == InformationClass.PRACTICAL.value,
                Claim.is_published.is_(True),
            )
        )
        notes: list[str] = []
        for claim in result.scalars().all():
            notes.append(
                f"[PRACTICAL — not official MUST NEED] {claim.value}"
            )
        return notes

    async def _build_citations(self, ctx: PipelineContext) -> list[CitationResponse]:
        citations: list[CitationResponse] = []
        if ctx.service:
            await self.session.refresh(ctx.service, ["service_links"])
            for link in ctx.service.service_links or []:
                if not link.is_verified:
                    continue
                citations.append(
                    CitationResponse(
                        evidence_id=str(link.id),
                        source_title=link.label_en,
                        source_url=link.url,
                        tier=1,
                        last_verified_at=(
                            link.last_checked_at.isoformat() if link.last_checked_at else None
                        ),
                        excerpt=f"Verified official URL for {ctx.service.name_en}",
                    )
                )
            # Claim evidence citations for published official claims
            result = await self.session.execute(
                select(Claim)
                .where(
                    Claim.service_id == ctx.service.id,
                    Claim.is_published.is_(True),
                    Claim.information_class == InformationClass.OFFICIAL.value,
                )
                .options(selectinload(Claim.evidence_links))
                .limit(5)
            )
            for claim in result.scalars().all():
                for ev in claim.evidence_links[:1]:
                    citations.append(
                        CitationResponse(
                            evidence_id=str(ev.id),
                            source_title=claim.subject[:120],
                            source_url=ev.locator if ev.locator and str(ev.locator).startswith("http") else None,
                            tier=1,
                            last_verified_at=(
                                claim.verified_at.isoformat() if claim.verified_at else None
                            ),
                            excerpt=(ev.evidence_excerpt or claim.value)[:500],
                        )
                    )

        # Avoid decorative service-name-only citations when we already have real ones
        if citations:
            return citations[:5]

        for item in ctx.evidence[:3]:
            # Skip decorative citations that are just the service name with no URL
            if not item.get("source_url") and item.get("excerpt") == (
                ctx.service.name_en if ctx.service else None
            ):
                continue
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
        return citations[:5]
