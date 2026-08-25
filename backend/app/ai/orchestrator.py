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
from app.ai.pipeline.intent import classify_intent, classify_intents
from app.ai.pipeline.language import detect_language
from app.ai.pipeline.safety import validate_safety
from app.ai.routing.context_resolution import (
    apply_context_clarifications,
    merge_clarifications,
    resolve_follow_up_intent,
    should_inherit_service,
)
from app.ai.routing.claim_retrieval import ClaimRetrieval
from app.ai.routing.intent_canonical import public_intent
from app.ai.routing.intent_classifier import IntentResult
from app.ai.routing.query_sanitize import sanitize_for_routing
from app.application.engines.checklist_engine import ChecklistEngine
from app.application.engines.procedure_engine import ProcedureEngine
from app.application.knowledge.claim_review_service import ClaimReviewService
from app.application.services.conversation_context import ConversationContext, ConversationContextService
from app.domain.enums import AnswerSupportLevel, ClaimPipelineStatus, InformationClass
from app.domain.models.claims import Claim, ServiceCatalogueMapping
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


def _detect_pcc_fee_channel(message: str) -> str | None:
    msg = message.lower()
    if any(
        w in msg
        for w in (
            "online pcc",
            "online clearance",
            "pcc.police",
            "pcc portal",
            "online police clearance",
            "অনলাইন",
            "অনলাইনে",
        )
    ):
        return "online_pcc"
    if any(
        w in msg
        for w in (
            "offline",
            "paper",
            "chalan",
            "challan",
            "superintendent",
            "sp office",
            "commissioner",
        )
    ):
        return "offline_paper_pcc_channel"
    return None


def _query_asks_gd_all_types(message: str) -> bool:
    msg = message.lower()
    return any(
        w in msg
        for w in (
            "shob dhoron",
            "all types",
            "every type",
            "সব ধরন",
            "সকল ধরন",
            "all gd",
            "nationwide",
        )
    )


def _fee_is_channel_specific(fee, channel: str) -> bool:
    label = (fee.label_en or "").lower()
    notes = (fee.notes_en or "").lower()
    if channel == "online_pcc":
        return "online" in label or "online" in notes or fee.amount == "1500"
    return False


@dataclass
class PipelineContext:
    message: str
    normalized_message: str
    language: str
    intent: str
    intents: IntentResult | None = None
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
        routing_message = sanitize_for_routing(request.message)
        ctx.normalized_message = normalize_banglish(routing_message)
        merged_clarifications = merge_clarifications(request.clarifications, conv_ctx)
        merged_clarifications = apply_context_clarifications(
            request.message, merged_clarifications, conv_ctx
        )
        merged_clarifications.update(
            self._infer_clarifications(ctx.normalized_message, request.message)
        )
        ctx.intents = classify_intents(
            ctx.normalized_message,
            merged_clarifications,
            raw_message=routing_message,
        )
        # Bangla script may carry intents lost during romanization
        if ctx.intents.primary in {"general_info", "document_list"}:
            raw_intents = classify_intents(
                routing_message, merged_clarifications, raw_message=routing_message
            )
            if raw_intents.primary not in {"general_info"} or ctx.intents.primary == "general_info":
                if raw_intents.all_intents != ctx.intents.all_intents:
                    ctx.intents = raw_intents

        follow_up_intent = None
        if ConversationContextService.is_follow_up_message(request.message):
            follow_up_intent = resolve_follow_up_intent(
                request.message, conv_ctx, ctx.intents
            )
        if follow_up_intent:
            ctx.intents = follow_up_intent

        ctx.intent = public_intent(ctx.intents.primary, ctx.intents.secondary)
        if merged_clarifications.get("service") == "epassport-fee-payment" and merged_clarifications.get(
            "speed"
        ):
            ctx.intents = IntentResult(primary="fee_inquiry", secondary=["payment"])
            ctx.intent = "fee_inquiry"
        elif conv_ctx.intent and ctx.intent == "general_info" and should_inherit_service(
            request.message, conv_ctx
        ):
            ctx.intent = conv_ctx.intent
            ctx.intents = IntentResult(primary=conv_ctx.intent)

        ctx.entities = await extract_entities(
            self.session,
            ctx.normalized_message,
            intents=ctx.intents,
            clarifications=merged_clarifications,
        )
        if not ctx.entities.get("service") and not ctx.entities.get("routing_clarification"):
            ctx.entities = await extract_entities(
                self.session,
                routing_message,
                intents=ctx.intents,
                clarifications=merged_clarifications,
            )

        if merged_clarifications.get("service"):
            svc = await self._service_by_slug(str(merged_clarifications["service"]))
            if svc:
                ctx.entities["service"] = svc
                ctx.entities["service_slug"] = svc.slug
                ctx.entities["service_match_method"] = "clarification_context"

        if not ctx.entities.get("service") and conv_ctx.service_slug:
            if should_inherit_service(request.message, conv_ctx):
                svc = await self._service_by_slug(conv_ctx.service_slug)
                if svc:
                    ctx.entities["service"] = svc
                    ctx.entities["service_slug"] = svc.slug
                    ctx.entities["service_match_method"] = "conversation_context"

        clarifications = merged_clarifications
        ctx.service = ctx.entities.get("service")
        ctx.clarifications_needed = self._clarifications_needed(ctx, request)
        routing_clarification = ctx.entities.get("routing_clarification")
        if routing_clarification and not ctx.clarifications_needed:
            ctx.clarifications_needed = [routing_clarification]

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

    def _infer_clarifications(self, normalized_message: str, raw_message: str) -> dict[str, str]:
        """Infer clarification slots already present in the user message."""
        msg = f"{raw_message} {normalized_message}".lower()
        inferred: dict[str, str] = {}
        if any(w in msg for w in ("dob", "date of birth", "birth date", "জন্ম তারিখ", "tarikh")):
            inferred["correction_type"] = "dob"
        elif any(w in msg for w in ("name", "naam", "নাম", "name correction", "নাম ভুল")):
            inferred["correction_type"] = "name"
        if "super express" in msg or ("super" in msg and "express" in msg):
            inferred["speed"] = "super_express"
        elif "express" in msg or "tier" in msg:
            inferred["speed"] = "express"
        elif "regular" in msg:
            inferred["speed"] = "regular"
        if any(
            token in msg
            for token in (
                "e passport",
                "e-passport",
                "epassport",
                "ই-পাসপোর্ট",
                "ই পাসপোর্ট",
            )
        ):
            inferred["passport_type"] = "e_passport"
        elif any(token in msg for token in ("mrp", "machine readable")):
            inferred["passport_type"] = "mrp"
        if any(token in msg for token in ("reissue", "re-issue", "renewal", "renew")):
            inferred["application_type"] = "reissue"
        if infer_channel_from_message := self._infer_channel_clarification(msg):
            inferred["channel"] = infer_channel_from_message
            if "online" in infer_channel_from_message:
                inferred["pcc_channel"] = "online"
        return inferred

    def _infer_channel_clarification(self, msg: str) -> str | None:
        if "online channel" in msg or "online pcc" in msg:
            return "online"
        if "offline channel" in msg or "offline pcc" in msg:
            return "offline"
        return None

    def _clarifications_needed(self, ctx: PipelineContext, request: ChatRequest) -> list[str]:
        if not ctx.service:
            return []
        slug = ctx.service.slug
        clarifications = dict(request.clarifications or {})
        clarifications.update(self._infer_clarifications(ctx.normalized_message, ctx.message))
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

        intents = ctx.intents or IntentResult(primary=ctx.intent)
        claim_retrieval = ClaimRetrieval(self.session)
        primary_intent = intents.primary

        include_checklist = primary_intent in {
            "document_list",
            "eligibility",
            "correction",
            "lost_document",
            "damaged_document",
            "renewal",
            "reissue",
            "application",
        } or "document_list" in intents.secondary

        include_steps = primary_intent in {
            "procedure_inquiry",
            "status",
            "appointment",
            "application",
            "payment",
            "renewal",
            "reissue",
            "correction",
            "lost_document",
        } or any(
            i in intents.secondary
            for i in {"procedure_inquiry", "status", "appointment", "payment"}
        )

        include_fees = primary_intent in {
            "fee_inquiry",
            "payment",
            "renewal",
            "reissue",
            "lost_document",
            "procedure_inquiry",
        } or "fee_inquiry" in intents.secondary

        checklist = []
        if include_checklist:
            checklist = await self.checklist_engine.build(
                ctx.service, clarifications, authoritative_only=True
            )

        steps = []
        if include_steps:
            steps = await self.procedure_engine.build_steps(
                ctx.service, claim_linked_only=True
            )

        await self.session.refresh(ctx.service, ["fees", "service_links"])

        fees: list[FeeResponse] = []
        if include_fees:
            intent_fees = await claim_retrieval.fees_for_intent(ctx.service, intents)
            correction_type = clarifications.get("correction_type")
            for fee in intent_fees:
                label = fee.label_en or ""
                label_l = label.lower()
                if ctx.service.slug == "civil-birth-registration-correction" and correction_type:
                    if correction_type == "dob" and "dob" not in label_l and "date-of-birth" not in label_l:
                        continue
                    if correction_type == "name" and "dob" in label_l:
                        continue
                if ctx.service.slug == "epassport-fee-payment" and clarifications.get("speed"):
                    speed = clarifications["speed"]
                    if speed == "express" and "express" not in label_l:
                        continue
                    if speed == "super_express" and "super express" not in label_l:
                        continue
                    if speed == "regular" and "regular" not in label_l:
                        continue
                fee_mode = None
                display_label = label
                if fee.amount == "USE_OFFICIAL_CALCULATOR":
                    fee_mode = "calculator"
                    display_label = label or "Use official fee calculator"
                fees.append(
                    FeeResponse(
                        amount=fee.amount,
                        currency=fee.currency,
                        evidence_id=str(fee.claim_id),
                        label=display_label,
                        fee_mode=fee_mode,
                    )
                )

        seed_fees_hidden = [f for f in ctx.service.fees if f.claim_id is None]
        warnings = list(ctx.conflicts)
        msg_blob = f"{ctx.message} {ctx.normalized_message}".lower()
        pcc_channel = (
            _detect_pcc_fee_channel(msg_blob) if ctx.service.slug == "police-clearance-certificate" else None
        )

        if ctx.support_level == AnswerSupportLevel.CONFLICTED:
            if ctx.service.slug == "police-clearance-certificate" and pcc_channel == "online_pcc":
                channel_fees = [
                    f
                    for f in ctx.service.fees
                    if f.claim_id is not None and _fee_is_channel_specific(f, "online_pcc")
                ]
                if channel_fees:
                    fees = [
                        FeeResponse(
                            amount=f.amount,
                            currency=f.currency,
                            evidence_id=str(f.claim_id),
                            label=f.label_en or "Online PCC fee (online channel only)",
                        )
                        for f in channel_fees
                    ]
                    warnings.append(
                        "PCC fees differ between online and offline official sources. "
                        "Showing online-channel verified fee only — not a universal PCC fee."
                    )
                else:
                    fees = []
                    warnings.append(
                        "Conflicting PCC fee information exists. "
                        "No universal fee is published; online-channel amount not available."
                    )
            elif ctx.service.slug == "police-clearance-certificate" and pcc_channel == "offline_paper_pcc_channel":
                fees = []
                warnings.append(
                    "Offline/paper PCC fee sources conflict with the online portal (BDT 1,500). "
                    "BDT 500 on police.gov.bd is not published as the current universal fee."
                )
            elif ctx.service.slug == "police-clearance-certificate" and ctx.intent == "fee_inquiry":
                fees = []
                warnings.append(
                    "PCC fee differs between online (BDT 1,500 on pcc.police.gov.bd) and a legacy "
                    "offline police.gov.bd page (BDT 500). No single universal fee is published."
                )
            else:
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

        if ctx.service.slug in {"police-general-diary", "police-general-diary-online"} and _query_asks_gd_all_types(
            msg_blob
        ):
            warnings.append(
                "Whether every GD complaint type can be filed online nationwide is not verified "
                "from Tier 1–2 official sources. Charter confirms an online channel exists."
            )

        if ctx.service.slug == "migration-visa-application-dip" and any(
            w in msg_blob for w in ("mrv fee", "mrv", "visa fee koto", "visa fee")
        ):
            if not fees:
                warnings.append(
                    "MRV/visa fee amounts are not verified from machine-readable official sources."
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
        catalogue_urls = await self._catalogue_reference_urls(ctx.service)
        for url in catalogue_urls:
            if url not in official_urls:
                official_urls.append(url)
        if catalogue_urls and not any(
            link.is_verified for link in (ctx.service.service_links or [])
        ):
            warnings.append(
                "Application URL is from the service catalogue reference; live portal verification is pending."
            )
        if not official_urls and not any(s.official_url for s in steps):
            warnings.append("Official application URLs are not yet verified for this service.")

        # Practical layer (never merged into MUST NEED)
        practical_notes = await claim_retrieval.practical_notes(ctx.service.id)

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

    async def _catalogue_reference_urls(self, service: Service) -> list[str]:
        result = await self.session.execute(
            select(ServiceCatalogueMapping).where(
                ServiceCatalogueMapping.runtime_service_id == service.id
            )
        )
        urls: list[str] = []
        for row in result.scalars().all():
            prov = row.provenance_json or {}
            src = prov.get("official_source")
            if isinstance(src, str) and src.startswith("http") and src not in urls:
                urls.append(src)
        return urls

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
