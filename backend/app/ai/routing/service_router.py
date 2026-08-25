"""Intent-aware service candidate retrieval, scoring, and disambiguation."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse

from rapidfuzz import fuzz
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai.routing.domain_entities import DomainEntities, extract_domain_entities
from app.ai.routing.intent_classifier import IntentResult
from app.ai.routing.loader import (
    capability_profiles_by_slug,
    domain_category,
    intent_claim_types,
    load_phrase_hints,
)
from app.domain.models.claims import Claim
from app.domain.models.knowledge import Service


@dataclass
class CandidateScore:
    service: Service
    score: float
    reasons: list[str] = field(default_factory=list)


@dataclass
class ServiceRoutingResult:
    service: Service | None
    method: str
    score: float
    candidates: list[CandidateScore] = field(default_factory=list)
    clarification: str | None = None
    domain_entities: DomainEntities | None = None


def _query_is_passport_verification_context(text: str) -> bool:
    if "pcc" in text or "clearance certificate" in text:
        return False
    return "passport verification" in text or (
        "verification" in text and "passport" in text and "police" in text
    )


def _query_is_gd_context(text: str) -> bool:
    return bool(re.search(r"\bgd\b", text)) or "general diary" in text or "genaral diary" in text


def _query_is_driving_licence_context(text: str) -> bool:
    if _query_is_brta_03c_context(text):
        return False
    markers = [
        "driving licence",
        "driving license",
        "learner licence",
        "learner license",
        "brta",
        "bsp.brta",
        "bsp register",
        "smart card licence",
        "smart card license",
        "dctc",
        "dctb",
        "instructor licence",
        "instructor license",
        "ড্রাইভিং",
        "ড্রাইভিং লাইসেন্স",
        "ড্রাইভিং লাইসেন্স",
        "শিক্ষানবিশ",
    ]
    return any(m in text for m in markers)


def _query_is_dctc_result_context(text: str) -> bool:
    return "dctc" in text or "dctb" in text or (
        "driving test" in text and "result" in text
    ) or ("field test" in text and "result" in text)


def _query_is_fitness_context(text: str) -> bool:
    return any(
        m in text
        for m in (
            "fitness",
            "e-fitness",
            "efitness",
            "ফিটনেস",
            "fit certificate",
            "vehicle inspection",
            "inspection frequency",
            "fitness reinspection",
        )
    )


def _query_is_tax_token_context(text: str) -> bool:
    if "tax token registration" in text or "tax token included" in text:
        return False
    return any(
        m in text
        for m in (
            "tax token",
            "tax-token",
            "ট্যাক্স টোকেন",
            "e-tax token",
            "etax token",
        )
    )


def _query_is_mv_tax_context(text: str) -> bool:
    return any(
        m in text
        for m in (
            "mv tax",
            "motor vehicle tax",
            "mvtax",
            "mvtax_brta",
            "brta.cnsbd.com",
        )
    )


def _query_is_route_permit_context(text: str) -> bool:
    return any(
        m in text
        for m in (
            "route permit",
            "route-permit",
            "রুট পারমিট",
            "inter-district route",
            "transport route permit",
        )
    )


def _query_is_brta_fee_calculator_context(text: str) -> bool:
    if "nid" in text:
        return False
    return any(
        m in text
        for m in (
            "fee calculator",
            "feecalculator",
            "feecalculator",
            "bsp fee calculator",
        )
    ) or "feecalculator" in text.replace("-", "")


def _query_is_vehicle_modification_context(text: str) -> bool:
    return any(
        m in text
        for m in (
            "engine change",
            "color change",
            "colour change",
            "tire size",
            "tyre size",
            "tyre width",
            "rong change",
            "gari rong",
            "ইঞ্জিন",
            "রং পরিবর্তন",
            "টায়ার",
        )
    )


def _query_is_driving_school_context(text: str) -> bool:
    return any(
        m in text
        for m in (
            "driving school",
            "training school",
            "motor driving training",
            "training centre",
        )
    )


def _query_is_brta_03c_context(text: str) -> bool:
    return (
        _query_is_fitness_context(text)
        or _query_is_tax_token_context(text)
        or _query_is_mv_tax_context(text)
        or _query_is_route_permit_context(text)
        or _query_is_brta_fee_calculator_context(text)
        or _query_is_vehicle_modification_context(text)
        or _query_is_driving_school_context(text)
        or "advance income tax" in text
        or "ait payment" in text
        or "ait motor" in text
        or "payment verification bsp" in text
        or "bsp transaction" in text
        or "bsp user registration" in text
        or "owner account" in text
    )


def _query_mentions_police_verification(text: str) -> bool:
    markers = [
        "police verification",
        "police verif",
        "police clearance",
        "police station",
        "police charter",
        " pv ",
        "পুলিশ ভেরিফিকেশন",
    ]
    return any(m in text for m in markers)


class ServiceRouter:
    AMBiguity_MARGIN = 5.0
    MIN_SCORE = 35.0

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._profiles = capability_profiles_by_slug()

    async def route(
        self,
        message: str,
        *,
        intents: IntentResult,
        clarifications: dict[str, Any] | None = None,
    ) -> ServiceRoutingResult:
        text = message.lower()
        clarifications = clarifications or {}
        domain_entities = extract_domain_entities(text)
        if clarifications.get("domain"):
            domain = str(clarifications["domain"])
            if domain not in domain_entities.domains:
                domain_entities.domains.append(domain)

        services = (
            await self.session.execute(
                select(Service).options(selectinload(Service.service_links))
            )
        ).scalars().all()
        by_slug = {s.slug: s for s in services}

        # 1) Phrase hints (data-driven, longest first)
        hinted_slug = self._phrase_hint_match(text, by_slug, clarifications)
        if hinted_slug:
            svc = by_slug[hinted_slug]
            return ServiceRoutingResult(
                service=svc,
                method="phrase_hint",
                score=100.0,
                candidates=[CandidateScore(service=svc, score=100.0, reasons=["phrase_hint"])],
                domain_entities=domain_entities,
            )

        # 2) URL host match
        url_match = self._url_host_match(text, services)
        if url_match:
            return ServiceRoutingResult(
                service=url_match,
                method="url_host",
                score=95.0,
                candidates=[CandidateScore(service=url_match, score=95.0, reasons=["url_host"])],
                domain_entities=domain_entities,
            )

        # 3) Domain pre-filter
        candidates = self._filter_candidates(services, domain_entities, text)

        # 4) Claim coverage by intent
        claim_counts = await self._published_claim_counts(
            [s.id for s in candidates], intents
        )

        scored: list[CandidateScore] = []
        for service in candidates:
            result = self._score_service(
                service,
                text=text,
                intents=intents,
                entities=domain_entities,
                claim_count=claim_counts.get(service.id, 0),
                clarifications=clarifications,
            )
            if result.score >= self.MIN_SCORE:
                scored.append(result)

        scored.sort(key=lambda c: c.score, reverse=True)

        if not scored:
            # Fallback: best fuzzy across all services (legacy safety net)
            fallback = self._fallback_fuzzy(services, text, claim_counts, intents)
            if fallback:
                return ServiceRoutingResult(
                    service=fallback.service,
                    method="fallback_fuzzy",
                    score=fallback.score,
                    candidates=[fallback],
                    domain_entities=domain_entities,
                )
            return ServiceRoutingResult(
                service=None,
                method="none",
                score=0.0,
                candidates=[],
                domain_entities=domain_entities,
            )

        top = scored[0]
        clarification = self._maybe_clarify(scored, intents, domain_entities, clarifications)
        if clarification:
            return ServiceRoutingResult(
                service=None,
                method="clarification",
                score=top.score,
                candidates=scored[:5],
                clarification=clarification,
                domain_entities=domain_entities,
            )

        return ServiceRoutingResult(
            service=top.service,
            method="intent_aware_ranking",
            score=top.score,
            candidates=scored[:5],
            domain_entities=domain_entities,
        )

    def _phrase_hint_match(
        self,
        text: str,
        by_slug: dict[str, Service],
        clarifications: dict[str, Any] | None = None,
    ) -> str | None:
        clarifications = clarifications or {}
        driving_slugs = {
            "brta-learner-driving-license",
            "driving-licence-renewal",
            "brta-duplicate-driving-license",
            "brta-smart-card-driving-license",
            "brta-driving-instructor-license",
            "brta-dctc-exam-result",
        }
        firearms_ctx = (
            clarifications.get("topic") == "firearms"
            or clarifications.get("domain") == "firearms"
            or any(
                w in text
                for w in ("firearms", "fire arms", "gun license", "arms license", "আগ্নেয়াস্ত্র")
            )
        )
        ambiguous_driving_phrases = {
            "licence renewal",
            "license renewal",
            "licence renew",
            "license renew",
        }
        for phrase, slug in load_phrase_hints():
            if phrase not in text or slug not in by_slug:
                continue
            if slug in driving_slugs and phrase in ambiguous_driving_phrases:
                if firearms_ctx or (
                    "document" in text and not _query_is_driving_licence_context(text)
                ):
                    continue
            return slug
        return None

    def _url_host_match(self, text: str, services: list[Service]) -> Service | None:
        for svc in services:
            for link in svc.service_links or []:
                host = urlparse(link.url).netloc.lower()
                if host and host in text:
                    return svc
        return None

    def _filter_candidates(
        self,
        services: list[Service],
        entities: DomainEntities,
        text: str,
    ) -> list[Service]:
        if entities.domains:
            allowed_categories = {
                domain_category(d) for d in entities.domains if domain_category(d)
            }
            filtered: list[Service] = []
            for service in services:
                profile = self._profiles.get(service.slug)
                if profile:
                    if profile.get("domain") in entities.domains:
                        filtered.append(service)
                elif service.category in allowed_categories:
                    filtered.append(service)
            if filtered:
                return filtered

        # No domain detected — services with capability profiles matching tokens
        if "passport" in text or "পাসপোর্ট" in text:
            cat = domain_category("passport")
            passport = [
                s
                for s in services
                if self._profiles.get(s.slug, {}).get("domain") == "passport"
                or (s.slug not in self._profiles and s.category == cat)
            ]
            if passport and "police" not in entities.domains:
                return passport

        if "police" in entities.domains:
            police = [
                s
                for s in services
                if self._profiles.get(s.slug, {}).get("domain") == "police"
                or s.category in {"POLICE", "EXPATRIATE", "LICENCES"}
            ]
            if police:
                return police

        if "immigration" in entities.domains:
            immigration = [
                s
                for s in services
                if self._profiles.get(s.slug, {}).get("domain") == "immigration"
                or s.category == domain_category("immigration")
            ]
            if immigration:
                return immigration

        if "firearms" in entities.domains:
            firearms = [
                s
                for s in services
                if self._profiles.get(s.slug, {}).get("domain") == "police"
                and self._profiles.get(s.slug, {}).get("service_type") == "licence"
                and "firearms" in s.slug
            ]
            if firearms:
                return firearms

        if "transport" in entities.domains or _query_is_driving_licence_context(text):
            transport = [
                s
                for s in services
                if self._profiles.get(s.slug, {}).get("domain") == "transport"
                or "brta" in s.slug
                or s.slug == "driving-licence-renewal"
            ]
            if transport:
                return transport

        if "land" in entities.domains:
            land = [
                s
                for s in services
                if self._profiles.get(s.slug, {}).get("domain") == "land"
            ]
            if land:
                return land

        if "education" in entities.domains:
            education = [
                s
                for s in services
                if self._profiles.get(s.slug, {}).get("domain") == "education"
            ]
            if education:
                return education

        if "social_protection" in entities.domains:
            social = [
                s
                for s in services
                if self._profiles.get(s.slug, {}).get("domain") == "social_protection"
            ]
            if social:
                return social

        if "tax" in entities.domains:
            tax = [
                s
                for s in services
                if self._profiles.get(s.slug, {}).get("domain") == "tax"
            ]
            if tax:
                return tax

        return services

    async def _published_claim_counts(
        self, service_ids: list, intents: IntentResult
    ) -> dict[Any, int]:
        if not service_ids:
            return {}
        claim_types: set[str] = set()
        for intent in intents.all_intents:
            claim_types.update(intent_claim_types(intent))
        if not claim_types:
            return {}

        rows = (
            await self.session.execute(
                select(Claim.service_id, func.count(Claim.id))
                .where(
                    Claim.service_id.in_(service_ids),
                    Claim.is_published.is_(True),
                    Claim.claim_type.in_(sorted(claim_types)),
                )
                .group_by(Claim.service_id)
            )
        ).all()
        return {service_id: count for service_id, count in rows}

    def _score_service(
        self,
        service: Service,
        *,
        text: str,
        intents: IntentResult,
        entities: DomainEntities,
        claim_count: int,
        clarifications: dict[str, Any],
    ) -> CandidateScore:
        profile = self._profiles.get(service.slug, {})
        score = 0.0
        reasons: list[str] = []

        primary = intents.primary

        # Intent compatibility
        intent_caps = profile.get("intent_capabilities") or []
        if primary in intent_caps:
            boost = (profile.get("intent_boost") or {}).get(primary, 25)
            score += boost
            reasons.append(f"intent:{primary}+{boost}")
        elif primary in {"fee_inquiry", "payment"} and profile.get("service_type") == "fee_payment":
            score += 35
            reasons.append("service_type:fee_payment")
        elif primary == "status" and profile.get("service_type") == "status":
            score += 40
            reasons.append("service_type:status")
        elif primary == "appointment" and profile.get("service_type") == "appointment":
            score += 40
            reasons.append("service_type:appointment")
        elif primary == "processing_time" and profile.get("service_type") == "verification":
            score += 45
            reasons.append("service_type:verification_timeline")
        elif not profile:
            pass
        else:
            # Intent incompatible penalty
            if primary == "fee_inquiry" and profile.get("service_type") in {
                "application",
                "verification",
                "office",
            }:
                score -= 35
                reasons.append("penalty:fee_vs_application")
            if primary == "status" and profile.get("service_type") not in {"status", None}:
                score -= 30
                reasons.append("penalty:status_mismatch")
            if primary == "appointment" and profile.get("service_type") not in {"appointment", None}:
                score -= 30
                reasons.append("penalty:appointment_mismatch")

        # Alias matches
        for alias in profile.get("aliases_en") or []:
            if alias.lower() in text:
                score += 45
                reasons.append(f"alias_en:{alias}")
        for alias in profile.get("aliases_bn") or []:
            if alias in message_if_bn(text, alias):
                score += 45
                reasons.append(f"alias_bn:{alias[:20]}")
        for alias in profile.get("aliases_banglish") or []:
            if alias.lower() in text:
                score += 40
                reasons.append(f"alias_banglish:{alias}")

        # DB aliases
        for alias in service.aliases or []:
            al = (alias or "").lower()
            if al and al in text:
                score += 35
                reasons.append(f"db_alias:{al}")

        # Capability keywords
        for kw in profile.get("capability_keywords") or []:
            if kw.lower() in text:
                score += 6
                reasons.append(f"kw:{kw}")

            # Variant / entity alignment
        variants = profile.get("variants") or {}
        score += self._variant_alignment(
            variants, entities, reasons, service_slug=service.slug
        )

        # Slug token overlap (weak signal)
        slug_tokens = set(service.slug.split("-"))
        overlap = len(slug_tokens & entities.tokens)
        if overlap:
            score += overlap * 4
            reasons.append(f"slug_overlap:{overlap}")

        # Claim coverage (only after semantic compatibility) — capped secondary signal
        if claim_count and score > 0:
            coverage_boost = min(claim_count * 4, 16)
            score += coverage_boost
            reasons.append(f"claim_coverage:+{coverage_boost}")

        # Cross-domain fee hijack guard: fee intent without domain must not win on claims alone
        if intents.primary == "fee_inquiry" and not entities.domains:
            if profile.get("domain") == "passport" and "birth" in text:
                score -= 60
                reasons.append("penalty:passport_fee_without_passport_domain")
            if profile.get("service_type") == "fee_payment" and profile.get("domain") != "identity":
                if any(t in text for t in ("birth", "brth", "registration", "registraton", "jonmo", "nibondhon")):
                    score -= 50
                    reasons.append("penalty:fee_payment_domain_mismatch")

        # Fact-check / validation queries about NID correction fees
        if "is this" in text or "information correct" in text or "always" in text:
            if service.slug == "nid-correction":
                score += 45
                reasons.append("boost:nid_correction_validation")
            if service.slug == "nid-fee-calculator":
                score -= 35
                reasons.append("penalty:calculator_on_correction_validation")
        if entities.action == "correction" and "nid" in text and intents.primary == "fee_inquiry":
            if service.slug == "nid-correction":
                score += 30
                reasons.append("boost:nid_correction_action")
            if service.slug == "nid-fee-calculator" and ("correct" in text or "always" in text):
                score -= 25
                reasons.append("penalty:calculator_vs_correction_fee")

        # Religion disambiguation for registrar lists
        if "muslim" in text and "hindu" in service.slug:
            score -= 80
            reasons.append("penalty:religion_mismatch")
        if "hindu" in text and "muslim" in service.slug:
            score -= 80
            reasons.append("penalty:religion_mismatch")
        if "muslim" in text and "muslim" in service.slug:
            score += 30
            reasons.append("boost:religion_match")
        if "hindu" in text and "hindu" in service.slug:
            score += 30
            reasons.append("boost:religion_match")

        # Fee matrix / speed tier queries should hit fee payment service not urgent-only service
        if intents.primary == "fee_inquiry":
            if service.slug == "epassport-fee-payment" and entities.speed:
                score += 45
                reasons.append("boost:fee_payment_speed_tier")
            if service.slug == "epassport-urgent-super-express" and entities.speed in {
                "express",
                "super_express",
            }:
                score -= 55
                reasons.append("penalty:urgent_service_for_fee_matrix")

        # Mission fee questions stay on fee payment
        if intents.primary == "fee_inquiry" and entities.channel == "mission":
            if service.slug == "epassport-fee-payment":
                score += 35
                reasons.append("boost:mission_fee_payment")
            if service.slug == "passport-renewal":
                score -= 40
                reasons.append("penalty:renewal_for_fee_query")
        if intents.primary == "fee_inquiry" and any(w in text for w in ("extra", "10%", "surcharge", "abudhabi", "abu dhabi")):
            if service.slug == "epassport-fee-payment":
                score += 30
                reasons.append("boost:mission_surcharge_fee")
            if service.slug == "passport-renewal":
                score -= 35
                reasons.append("penalty:renewal_for_surcharge_fee")
        if intents.primary == "office_locator" and "character" in text and "certificate" in text:
            if service.slug == "local-character-certificate":
                score += 45
                reasons.append("boost:character_certificate")
            if "passport" in service.slug or "epassport" in service.slug:
                score -= 40
                reasons.append("penalty:passport_not_character_cert")

        # Police verification context overrides renewal/reissue affinity
        if _query_mentions_police_verification(text) or _query_is_passport_verification_context(text):
            if "police" in service.slug and "passport" in service.slug:
                score += 35
                reasons.append("boost:police_verification")
            if service.slug == "police-passport-verification" and any(
                w in text for w in ("sla", "charter", "timeline", "processing", "din", "day", "time", "urgent")
            ):
                score += 55
                reasons.append("boost:pv_sla_service")
            if service.slug == "police-passport-police-verification" and any(
                w in text for w in ("sla", "charter", "timeline", "urgent")
            ):
                score -= 30
                reasons.append("penalty:pv_passport_for_sla_query")
            if service.slug in {"passport-renewal", "passport-mrp-reissue", "passport-mrp-initial"}:
                score -= 40
                reasons.append("penalty:pv_over_renewal")
            if service.slug == "epassport-urgent-super-express" and _query_is_passport_verification_context(
                text
            ):
                score -= 65
                reasons.append("penalty:epassport_urgent_for_pv_sla")

        # Passport verification vs PCC comparison
        if "same as" in text and "passport verification" in text:
            if service.slug == "police-passport-verification":
                score += 45
                reasons.append("boost:pv_comparison")
            if service.slug == "police-clearance-certificate":
                score -= 25
                reasons.append("penalty:pcc_for_pv_comparison")

        # GD online channel preference
        if _query_is_gd_context(text) and entities.channel == "online":
            if service.slug == "police-general-diary-online":
                score += 35
                reasons.append("boost:gd_online_channel")
            if service.slug == "police-general-diary":
                score -= 25
                reasons.append("penalty:gd_offline_for_online_query")

        # Firearms vs driving licence disambiguation
        if "firearms" in entities.domains or any(
            w in text for w in ("firearms", "fire arms", "gun license", "arms license", "আগ্নেয়াস্ত্র")
        ):
            if service.slug == "police-firearms-license":
                score += 45
                reasons.append("boost:firearms_licence")
            if service.slug == "driving-licence-renewal":
                score -= 80
                reasons.append("penalty:driving_for_firearms")
            if "brta" in service.slug and "firearms" in entities.domains:
                score -= 60
                reasons.append("penalty:brta_for_firearms")

        # Generic licence word must not alone select driving when firearms context present
        if "license" in text or "licence" in text:
            if "firearms" in entities.domains or "gun" in text or "fire arms" in text:
                if service.slug == "driving-licence-renewal":
                    score -= 50
                    reasons.append("penalty:generic_licence_firearms_bleed")

        # Batch 2B police + immigration routing — handled via service_capabilities.json,
        # phrase_hints.json, and domain_entities channel variants (no inline phrase hacks).

        # Batch 3A BRTA driving licence cross-domain guards
        if _query_is_driving_licence_context(text):
            brta_slugs = {
                "brta-learner-driving-license",
                "driving-licence-renewal",
                "brta-duplicate-driving-license",
                "brta-smart-card-driving-license",
                "brta-driving-instructor-license",
                "brta-dctc-exam-result",
            }
            if service.slug in brta_slugs:
                score += 15
                reasons.append("boost:brta_driving_family")
            if service.slug == "epassport-fee-payment" and intents.primary == "fee_inquiry":
                score -= 70
                reasons.append("penalty:passport_fee_for_driving_fee")
            if service.slug == "epassport-application-status" and _query_is_dctc_result_context(text):
                score -= 80
                reasons.append("penalty:passport_status_for_dctc")
            if service.slug == "epassport-rpo-secretariat" and _query_is_dctc_result_context(text):
                score -= 80
                reasons.append("penalty:passport_office_for_dctc")
            if service.slug == "civil-birth-death-verify" and (
                "bsp" in text or ("register" in text and "driver" in text)
            ):
                score -= 75
                reasons.append("penalty:birth_verify_for_bsp_register")
            if _query_is_gd_context(text) and (
                entities.licence_type == "duplicate"
                or any(w in text for w in ("licence", "license", "driving", "dl"))
            ):
                if service.slug == "police-general-diary":
                    score -= 40
                    reasons.append("penalty:gd_over_duplicate_licence")
                if service.slug == "brta-duplicate-driving-license":
                    score += 35
                    reasons.append("boost:duplicate_over_gd")
            if _query_is_dctc_result_context(text) and service.slug == "brta-dctc-exam-result":
                score += 45
                reasons.append("boost:dctc_result_service")
            if entities.licence_type == "learner" and service.slug == "brta-learner-driving-license":
                score += 30
                reasons.append("boost:learner_variant")
            if entities.licence_type == "renewal" and service.slug == "driving-licence-renewal":
                score += 30
                reasons.append("boost:renewal_variant")
            if entities.licence_type == "duplicate" and service.slug == "brta-duplicate-driving-license":
                score += 30
                reasons.append("boost:duplicate_variant")
            if entities.licence_type == "smart_card" and service.slug == "brta-smart-card-driving-license":
                score += 30
                reasons.append("boost:smart_card_variant")
            if entities.licence_type == "instructor" and service.slug == "brta-driving-instructor-license":
                score += 30
                reasons.append("boost:instructor_variant")

        # Minor applicant → new e-passport application
        if any(w in text for w in ["minor", "child", "parent nid", "বাচ্চা", "শিশু"]):
            if service.slug == "epassport-new-application":
                score += 25
                reasons.append("boost:minor_application")
            if service.slug == "passport-renewal":
                score -= 15
                reasons.append("penalty:minor_not_reissue")
        name_candidates = [
            service.slug.replace("-", " "),
            service.name_en.lower(),
            service.name_bn or "",
        ]
        fuzzy_best = 0.0
        for cand in name_candidates:
            if not cand:
                continue
            if cand in text:
                fuzzy_best = max(fuzzy_best, 20.0)
            else:
                fuzzy_best = max(fuzzy_best, float(fuzz.partial_ratio(cand, text)) * 0.12)
        score += min(fuzzy_best, 18.0)

        # Clarification boosts
        if clarifications.get("passport_type") == "mrp" and "mrp" in service.slug:
            score += 20
        if clarifications.get("passport_type") == "e_passport" and "epassport" in service.slug:
            score += 20
        if clarifications.get("topic") == "firearms" and service.slug == "police-firearms-license":
            score += 40
            reasons.append("boost:clarification_firearms")
        if clarifications.get("domain") == "passport" and service.slug == "epassport-fee-payment":
            score += 35
            reasons.append("boost:clarification_passport_fee")
        if clarifications.get("domain") == "transport" and service.slug == "driving-licence-renewal":
            score += 35
            reasons.append("boost:clarification_driving_renewal")
        if clarifications.get("domain") == "transport" and service.slug == "passport-renewal":
            score -= 40
            reasons.append("penalty:passport_renewal_for_transport_clarification")

        # Default e-passport when passport domain without explicit MRP / express product
        vague_passport = text.strip() in {"passport", "e passport", "epassport", "e-passport"}
        if "passport" in entities.domains and entities.passport_type != "mrp" and not vague_passport:
            express_product = entities.speed in {"express", "super_express"} or any(
                w in text for w in ("super express", "urgent pickup", "urgent", "express passport")
            )
            mrp_product = "mrp" in text or "machine readable" in text
            if not express_product and not mrp_product:
                if service.slug == "epassport-new-application":
                    score += 25
                    reasons.append("boost:default_epassport")
                if service.slug == "passport-mrp-initial" and "mrp" not in text:
                    score -= 30
                    reasons.append("penalty:mrp_without_explicit_type")
            if express_product and service.slug == "epassport-urgent-super-express":
                if intents.primary == "fee_inquiry":
                    score -= 25
                    reasons.append("penalty:express_product_for_fee_matrix")
                else:
                    score += 35
                    reasons.append("boost:express_passport_product")
            if intents.primary == "fee_inquiry" and express_product and service.slug == "epassport-fee-payment":
                score += 35
                reasons.append("boost:express_fee_matrix")
            if express_product and service.slug == "epassport-new-application" and intents.primary != "fee_inquiry":
                score -= 25
                reasons.append("penalty:generic_app_for_express_product")
            if mrp_product and service.slug == "passport-mrp-initial":
                score += 35
                reasons.append("boost:mrp_product")

        # Police station selection for passport verification
        if "police station" in text and "passport" in text:
            if service.slug == "police-passport-police-verification":
                score += 45
                reasons.append("boost:passport_pv_station_selection")
            if service.slug == "epassport-new-application":
                score -= 35
                reasons.append("penalty:epassport_for_pv_station_selection")

        # Passport issuance timeline vs police verification timeline
        if "passport" in entities.domains and intents.primary == "processing_time":
            if not _query_mentions_police_verification(text) and "verification" not in text:
                if service.slug == "epassport-new-application":
                    score += 35
                    reasons.append("boost:passport_issuance_timeline")
                if service.slug == "police-passport-police-verification":
                    score -= 45
                    reasons.append("penalty:pv_for_passport_issuance_time")
                if service.slug == "police-passport-verification":
                    score -= 25
                    reasons.append("penalty:pv_sla_for_passport_issuance_time")

        # Passport / police verification fee vs e-passport fee payment portal
        if "verification" in text and "fee" in text and "passport" in text:
            if service.slug == "police-passport-verification":
                score += 45
                reasons.append("boost:passport_verification_fee")
            if service.slug == "epassport-fee-payment":
                score -= 50
                reasons.append("penalty:epassport_fee_for_verification_fee")

        # Domain-scoped fee routing — do not bleed passport fee portal
        if intents.primary == "fee_inquiry":
            passport_fee_ctx = (
                "passport" in entities.domains
                or "passport" in text
                or "epassprt" in text
                or entities.speed in {"express", "super_express"}
            )
            if passport_fee_ctx and service.slug == "epassport-fee-payment":
                score += 40
                reasons.append("boost:passport_fee_portal")
            if not passport_fee_ctx:
                if service.slug == "epassport-fee-payment":
                    score -= 70
                    reasons.append("penalty:passport_fee_portal_off_domain")
            if "land" in entities.domains and service.slug == "land-mutation-apply":
                score += 40
                reasons.append("boost:land_mutation_fee")
            if "tax" in entities.domains and service.slug == "tin-registration":
                score += 40
                reasons.append("boost:tin_registration_fee")

        # Validity queries for passport products
        if intents.primary in {"validity", "eligibility"}:
            if ("pcc" in text or "clearance" in text or "পিসিসি" in text or "ক্লিয়ারেন্স" in text):
                if service.slug == "police-clearance-certificate":
                    score += 50
                    reasons.append("boost:pcc_passport_validity")
                if service.slug == "epassport-new-application":
                    score -= 55
                    reasons.append("penalty:epassport_for_pcc_validity")
            elif "passport" in entities.domains or "passport" in text:
                if service.slug == "epassport-new-application":
                    score += 35
                    reasons.append("boost:passport_validity")

        # Generic verification status without passport application context
        if intents.primary == "status" and "verification" in text:
            if "passport" not in text and "epassport" not in text:
                if service.slug in {"police-passport-verification", "police-employment-verification"}:
                    score += 35
                    reasons.append("boost:generic_verification_status")
                if service.slug == "epassport-application-status":
                    score -= 45
                    reasons.append("penalty:passport_status_for_generic_verification")

        # NID application documents → correction over new voter registration
        if "nid" in text and "application" in text and "document" in text:
            if service.slug == "nid-correction":
                score += 30
                reasons.append("boost:nid_application_documents")
            if service.slug == "nid-new-voter-registration":
                score -= 20
                reasons.append("penalty:new_voter_for_nid_application_docs")

        # Batch 3C BRTA fitness / tax / route permit / modification routing
        brta_03c_slugs = {
            "brta-fitness-certificate",
            "brta-tax-token",
            "brta-route-permit",
            "brta-fee-calculator",
            "brta-mv-tax-payment",
            "brta-advance-income-tax",
            "brta-engine-change",
            "brta-color-change",
            "brta-tire-size-change",
            "brta-driving-school-registration",
            "transport-route-permit",
            "transport-driving-school-licence",
            "brta-e-document-verification",
            "brta-bsp-user-registration",
            "brta-payment-verification",
        }
        if _query_is_fitness_context(text):
            if service.slug == "brta-fitness-certificate":
                score += 55
                reasons.append("boost:fitness_certificate")
            if service.slug in {"driving-licence-renewal", "passport-renewal", "epassport-application-status"}:
                score -= 70
                reasons.append("penalty:renewal_status_for_fitness")
            if service.slug == "brta-new-vehicle-registration":
                score -= 40
                reasons.append("penalty:registration_for_fitness")

        if _query_is_tax_token_context(text):
            if service.slug == "brta-tax-token":
                score += 55
                reasons.append("boost:tax_token")
            if "verify" in text and service.slug == "brta-e-document-verification":
                score += 60
                reasons.append("boost:tax_token_verify_edocument")
            if "verify" in text and service.slug == "brta-tax-token":
                score -= 40
                reasons.append("penalty:tax_token_for_verify_query")
            if service.slug == "brta-new-vehicle-registration":
                score -= 45
                reasons.append("penalty:registration_for_tax_token")
            if service.slug in {"driving-licence-renewal", "passport-renewal"}:
                score -= 60
                reasons.append("penalty:renewal_for_tax_token")

        if _query_is_mv_tax_context(text):
            if service.slug == "brta-mv-tax-payment":
                score += 55
                reasons.append("boost:mv_tax")
            if service.slug == "brta-tax-token" and "mv tax" in text:
                score -= 25
                reasons.append("penalty:tax_token_for_mv_tax")

        if "advance income tax" in text or "ait payment" in text or "ait motor" in text:
            if service.slug == "brta-advance-income-tax":
                score += 55
                reasons.append("boost:advance_income_tax")
            if service.slug == "brta-new-vehicle-registration":
                score -= 50
                reasons.append("penalty:registration_for_ait")

        if _query_is_route_permit_context(text):
            if service.slug == "brta-route-permit":
                score += 50
                reasons.append("boost:route_permit_portal")
            if service.slug == "transport-route-permit" and any(
                w in text for w in ("bsp", "operator", "transport route")
            ):
                score += 45
                reasons.append("boost:transport_route_permit_bsp")
            if service.slug in {"driving-licence-renewal", "passport-renewal", "brta-new-vehicle-registration"}:
                score -= 50
                reasons.append("penalty:wrong_service_for_route_permit")

        if _query_is_brta_fee_calculator_context(text):
            if service.slug == "brta-fee-calculator":
                score += 55
                reasons.append("boost:brta_fee_calculator")
            if service.slug == "brta-new-vehicle-registration":
                score -= 55
                reasons.append("penalty:registration_for_fee_calculator")
            if service.slug == "nid-fee-calculator":
                score -= 40
                reasons.append("penalty:nid_calculator_for_brta_fee")

        if _query_is_vehicle_modification_context(text):
            mod_slug = None
            if "engine" in text or "ইঞ্জিন" in text:
                mod_slug = "brta-engine-change"
            elif "color" in text or "colour" in text or "rong" in text or "রং" in text:
                mod_slug = "brta-color-change"
            elif "tire" in text or "tyre" in text or "টায়ার" in text:
                mod_slug = "brta-tire-size-change"
            if mod_slug and service.slug == mod_slug:
                score += 55
                reasons.append(f"boost:vehicle_modification:{mod_slug}")
            if mod_slug and service.slug == "brta-vehicle-info-correction":
                score -= 30
                reasons.append("penalty:rc_correction_for_modification")

        if _query_is_driving_school_context(text):
            if "licence" in text or "license" in text:
                if service.slug == "transport-driving-school-licence":
                    score += 50
                    reasons.append("boost:driving_school_licence")
                if service.slug == "brta-driving-school-registration":
                    score += 20
                    reasons.append("boost:driving_school_registration_secondary")
            else:
                if service.slug == "brta-driving-school-registration":
                    score += 50
                    reasons.append("boost:driving_school_registration")
            if service.slug == "brta-ownership-transfer":
                score -= 50
                reasons.append("penalty:ownership_for_driving_school")

        if "payment verification" in text and "bsp" in text:
            if service.slug == "brta-payment-verification":
                score += 50
                reasons.append("boost:bsp_payment_verification")

        if "bsp user registration" in text or "owner account" in text:
            if service.slug == "brta-bsp-user-registration":
                score += 50
                reasons.append("boost:bsp_user_registration")

        if "e-tax token verify" in text or "e-tax token verification" in text or "etax token verify" in text:
            if service.slug == "brta-e-document-verification":
                score += 50
                reasons.append("boost:e_document_verification")

        if _query_is_brta_03c_context(text) and service.slug in brta_03c_slugs:
            score += 12
            reasons.append("boost:brta_03c_family")

        if _query_is_driving_licence_context(text):
            if service.slug == "brta-e-document-verification":
                score -= 75
                reasons.append("penalty:edocument_for_driving_licence")
            if service.slug in brta_03c_slugs and not _query_is_brta_03c_context(text):
                score -= 40
                reasons.append("penalty:brta_03c_without_03c_context")

        # Generic licence renewal without passport → driving, not passport reissue
        if re.search(r"\b(licence|license)\s+renew(al)?\b", text) and "passport" not in text:
            firearms_ctx = (
                clarifications.get("topic") == "firearms"
                or "firearms" in entities.domains
                or any(w in text for w in ("firearms", "fire arms", "gun license", "arms license"))
            )
            document_listing = "document" in text and not _query_is_driving_licence_context(text)
            if not firearms_ctx and not document_listing and not _query_is_brta_03c_context(text):
                if service.slug == "driving-licence-renewal":
                    score += 38
                    reasons.append("boost:generic_licence_renewal_driving")
                if service.slug == "passport-renewal":
                    score -= 42
                    reasons.append("penalty:passport_renewal_for_licence_renewal")

        # BSP learner apply online
        if "bsp" in text and "learner" in text and any(w in text for w in ("apply", "online")):
            if service.slug == "brta-learner-driving-license":
                score += 45
                reasons.append("boost:bsp_learner_apply")
            if service.slug == "epassport-new-application":
                score -= 50
                reasons.append("penalty:epassport_for_bsp_learner")

        # Penalize BRTA family when query has no driving/BRTA context
        brta_slugs = {
            "brta-learner-driving-license",
            "driving-licence-renewal",
            "brta-duplicate-driving-license",
            "brta-smart-card-driving-license",
            "brta-driving-instructor-license",
            "brta-dctc-exam-result",
        }
        if service.slug in brta_slugs and not _query_is_driving_licence_context(text):
            score -= 80
            reasons.append("penalty:brta_without_driving_context")

        return CandidateScore(service=service, score=score, reasons=reasons)

    def _variant_alignment(
        self,
        variants: dict[str, Any],
        entities: DomainEntities,
        reasons: list[str],
        *,
        service_slug: str,
    ) -> float:
        bonus = 0.0
        if entities.passport_type:
            types = variants.get("passport_type") or []
            if entities.passport_type in types:
                bonus += 18
                reasons.append(f"variant:passport_type={entities.passport_type}")
            elif types and entities.passport_type not in types:
                bonus -= 15
                reasons.append("penalty:passport_type_mismatch")

        if entities.action:
            actions = variants.get("actions") or []
            action_map = {
                "renewal": "renewal",
                "reissue": "reissue",
                "lost": "lost",
                "correction": "correction",
                "fee": "fee",
                "payment": "payment",
                "status": "status",
                "appointment": "appointment",
                "new": "new",
            }
            mapped = action_map.get(entities.action)
            if mapped and mapped in actions:
                bonus += 15
                reasons.append(f"variant:action={mapped}")
            elif mapped == "correction" and entities.passport_type == "e_passport":
                if service_slug in {"passport-renewal", "epassport-new-application"}:
                    bonus += 20
                    reasons.append("variant:e_passport_correction")

        if entities.speed:
            speeds = variants.get("speeds") or []
            if entities.speed in speeds:
                bonus += 12
                reasons.append(f"variant:speed={entities.speed}")

        if entities.channel:
            channels = variants.get("channels") or []
            if entities.channel in channels:
                bonus += 12
                reasons.append(f"variant:channel={entities.channel}")
            elif channels and entities.channel == "online" and "online" not in channels:
                bonus -= 18
                reasons.append("penalty:channel_online_mismatch")
            elif channels and entities.channel not in channels:
                bonus -= 8
                reasons.append(f"penalty:channel={entities.channel}")

        if entities.licence_type:
            licence_types = variants.get("licence_type") or []
            if entities.licence_type in licence_types:
                bonus += 22
                reasons.append(f"variant:licence_type={entities.licence_type}")
            elif licence_types and entities.licence_type not in licence_types:
                bonus -= 18
                reasons.append("penalty:licence_type_mismatch")

        return bonus

    def _fallback_fuzzy(
        self,
        services: list[Service],
        text: str,
        claim_counts: dict[Any, int],
        intents: IntentResult,
    ) -> CandidateScore | None:
        best: CandidateScore | None = None
        for service in services:
            profile = self._profiles.get(service.slug)
            if profile and intents.primary not in (profile.get("intent_capabilities") or []):
                if intents.primary == "fee_inquiry" and profile.get("service_type") != "fee_payment":
                    continue
            candidates = [
                service.slug.replace("-", " "),
                service.name_en.lower(),
            ]
            score = 0.0
            for cand in candidates:
                if cand in text:
                    score = max(score, 80.0)
                else:
                    score = max(score, float(fuzz.partial_ratio(cand, text)))
            score += min(claim_counts.get(service.id, 0) * 5, 20)
            if best is None or score > best.score:
                best = CandidateScore(service=service, score=score, reasons=["fallback_fuzzy"])
        if best and best.score >= 75:
            return best
        return None

    def _maybe_clarify(
        self,
        scored: list[CandidateScore],
        intents: IntentResult,
        entities: DomainEntities,
        clarifications: dict[str, Any],
    ) -> str | None:
        if len(scored) < 2:
            return None
        top, second = scored[0], scored[1]
        if top.score - second.score > self.AMBiguity_MARGIN:
            return None

        # Passport fee ambiguity: MRP vs e-passport
        if intents.primary == "fee_inquiry" and "passport" in entities.domains:
            if not entities.passport_type and "passport_type" not in clarifications:
                slugs = {top.service.slug, second.service.slug}
                if slugs & {"epassport-fee-payment", "passport-mrp-initial", "passport-mrp-reissue"}:
                    return "MRP naki e-passport-er fee jante chacchen?"

        # Generic passport type ambiguity for application flows
        if intents.primary in {"application", "document_list", "renewal", "reissue"}:
            if not entities.passport_type and "passport_type" not in clarifications:
                ep = any("epassport" in c.service.slug or "passport-renewal" == c.service.slug for c in scored[:2])
                mrp = any("mrp" in c.service.slug for c in scored[:2])
                if ep and mrp:
                    return "MRP naki e-passport? Please specify which passport type you mean."

        return None


def message_if_bn(text: str, alias: str) -> str:
    return text if alias in text else ""
