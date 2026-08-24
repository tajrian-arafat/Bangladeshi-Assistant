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

        services = (
            await self.session.execute(
                select(Service).options(selectinload(Service.service_links))
            )
        ).scalars().all()
        by_slug = {s.slug: s for s in services}

        # 1) Phrase hints (data-driven, longest first)
        hinted_slug = self._phrase_hint_match(text, by_slug)
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

    def _phrase_hint_match(self, text: str, by_slug: dict[str, Service]) -> str | None:
        for phrase, slug in load_phrase_hints():
            if phrase in text and slug in by_slug:
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
                score += 25
                reasons.append("boost:fee_payment_speed_tier")
            if service.slug == "epassport-urgent-super-express" and entities.speed in {
                "express",
                "super_express",
            }:
                score -= 35
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
