"""Partial-knowledge taxonomy, user-value matrix, and bottleneck analysis."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from automation.orchestrator.research_quality import (
    evaluate_service_research,
    evaluation_to_dict,
    load_profiles,
    resolve_profile_key,
)

TAXONOMY_CATEGORIES = [
    "MISSING_ELIGIBILITY",
    "MISSING_MUST_NEED_DOCUMENTS",
    "MISSING_CONDITIONAL_DOCUMENTS",
    "MISSING_PROCEDURE",
    "MISSING_FEES",
    "MISSING_PAYMENT",
    "MISSING_OFFICIAL_URL",
    "MISSING_STATUS",
    "MISSING_PROCESSING_TIME",
    "MISSING_OFFICE_LOCATION",
    "MISSING_APPLICANT_VARIANTS",
    "MISSING_GEOGRAPHIC_VARIATION",
    "MISSING_LEGAL_BASIS",
    "MISSING_FRESHNESS",
    "MISSING_CLAIM_DENSITY",
    "MISSING_E2E_SUPPORTED_COVERAGE",
    "CONFLICTING_INFORMATION",
    "OFFICIAL_SOURCE_UNAVAILABLE",
    "JS_RENDERING_LIMITATION",
    "CALCULATOR_REQUIRED",
    "LOCAL_VARIATION",
    "RARE_SERVICE",
    "OTHER",
]

DIMENSION_TO_TAXONOMY: dict[str, str] = {
    "eligibility": "MISSING_ELIGIBILITY",
    "documents": "MISSING_MUST_NEED_DOCUMENTS",
    "conditional_documents": "MISSING_CONDITIONAL_DOCUMENTS",
    "procedure": "MISSING_PROCEDURE",
    "fees": "MISSING_FEES",
    "payment": "MISSING_PAYMENT",
    "official_url": "MISSING_OFFICIAL_URL",
    "status": "MISSING_STATUS",
    "processing_time": "MISSING_PROCESSING_TIME",
    "office": "MISSING_OFFICE_LOCATION",
    "variants": "MISSING_APPLICANT_VARIANTS",
    "geography": "MISSING_GEOGRAPHIC_VARIATION",
    "legal_basis": "MISSING_LEGAL_BASIS",
}

USER_VALUE_QUESTIONS: dict[str, dict[str, Any]] = {
    "A": {"label": "What is this service?", "dimensions": ["identity"], "always_relevant": True},
    "B": {"label": "Who is eligible?", "dimensions": ["eligibility"]},
    "C": {"label": "What do I need?", "dimensions": ["documents"]},
    "D": {"label": "What extra documents might apply?", "dimensions": ["conditional_documents"]},
    "E": {"label": "How do I apply?", "dimensions": ["procedure"]},
    "F": {"label": "How much does it cost?", "dimensions": ["fees"]},
    "G": {"label": "How do I pay?", "dimensions": ["payment"]},
    "H": {"label": "Where do I apply?", "dimensions": ["office"]},
    "I": {"label": "How long does it take?", "dimensions": ["processing_time"]},
    "J": {"label": "Where do I check status?", "dimensions": ["status"]},
    "K": {"label": "What if my situation is unusual?", "dimensions": ["variants", "geography"]},
}

HIGH_USAGE_SERVICE_IDS = frozenset(
    {
        "nid-new-voter-registration",
        "nid-download-copy",
        "land-mutation-apply",
        "education-ssc-certificate",
        "education-hsc-certificate",
        "passport-new-application",
        "tax-etin-registration",
        "local-passport-attestation",
        "snp-old-age-allowance",
    }
)

HIGH_RISK_SERVICE_IDS = frozenset(
    {
        "tax-income-return-file",
        "business-company-incorporation",
        "land-mutation-apply",
        "customs-import-export-control-licence",
        "permits-fire-noc-enoc",
        "nid-combined-correction",
    }
)


@dataclass
class PartialServiceAnalysis:
    service_id: str
    service_name_en: str
    category_id: str
    profile_key: str
    batch_slug: str
    partial_reasons: list[str] = field(default_factory=list)
    critical_missing: list[str] = field(default_factory=list)
    noncritical_missing: list[str] = field(default_factory=list)
    unresolvable_gaps: list[str] = field(default_factory=list)
    resolvable_gaps: list[str] = field(default_factory=list)
    dimension_coverage: dict[str, bool] = field(default_factory=dict)
    claim_counts: dict[str, int] = field(default_factory=dict)
    e2e_supported_rate: float = 0.0
    research_source: str = "staging"
    flags: list[str] = field(default_factory=list)


class PartialKnowledgeAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.profiles_doc = load_profiles(repo_root)
        self.catalogue = self._load_catalogue()

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _load_catalogue(self) -> dict[str, dict[str, Any]]:
        path = self.repo_root / "data" / "service_catalogue" / "services.json"
        if not path.exists():
            return {}
        doc = json.loads(path.read_text(encoding="utf-8"))
        services = doc.get("services") if isinstance(doc, dict) else doc
        if not isinstance(services, list):
            return {}
        return {s["service_id"]: s for s in services if isinstance(s, dict) and s.get("service_id")}

    def _find_rerun_artifact(self, service_id: str) -> Path | None:
        rerun_root = self.repo_root / "data" / "research" / "rerun"
        if not rerun_root.is_dir():
            return None
        best: Path | None = None
        for wave_dir in sorted(rerun_root.iterdir(), reverse=True):
            if not wave_dir.is_dir() or not wave_dir.name.startswith("wave-"):
                continue
            svc = wave_dir / service_id / "service.json"
            if svc.exists():
                return svc.parent
        pilot = self.repo_root / "data" / "research" / "pilot" / service_id / "service.json"
        if pilot.exists():
            return pilot.parent
        return best

    def _load_service_knowledge(
        self, service_id: str, batch_slug: str
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, dict[str, Any]], str]:
        rerun_dir = self._find_rerun_artifact(service_id)
        if rerun_dir:
            claims = json.loads((rerun_dir / "claims.json").read_text(encoding="utf-8")).get("claims") or []
            sources = json.loads((rerun_dir / "sources.json").read_text(encoding="utf-8")).get("sources") or []
            ver_path = rerun_dir / "verification" / "claims_verification.json"
            verifications: dict[str, dict[str, Any]] = {}
            if ver_path.exists():
                for v in json.loads(ver_path.read_text(encoding="utf-8")).get("verifications") or []:
                    verifications[v["claim_id"]] = v
            return claims, sources, verifications, "wave_rerun"

        staging = self.repo_root / "data" / "research" / "staging" / batch_slug
        claims_path = staging / "claims.json"
        sources_path = staging / "sources.json"
        claims: list[dict[str, Any]] = []
        sources: list[dict[str, Any]] = []
        if claims_path.exists():
            doc = json.loads(claims_path.read_text(encoding="utf-8"))
            claims = [c for c in doc.get("claims") or [] if c.get("service_id") == service_id]
        if sources_path.exists():
            sources = list(json.loads(sources_path.read_text(encoding="utf-8")).get("sources") or [])
        return claims, sources, {}, "staging"

    def _detect_js_limitation(self, sources: list[dict[str, Any]]) -> bool:
        for src in sources:
            probe = src.get("probe") or {}
            title = str(probe.get("title") or "")
            reachable = probe.get("reachable")
            content_hash = probe.get("content_hash")
            if reachable and title and not content_hash:
                return True
            if reachable and title.lower() in {"loading...", "home", ""}:
                return True
        return False

    def _detect_calculator_required(self, service_id: str, gaps: list[dict[str, Any]]) -> bool:
        fee_keywords = ("calculator", "variable fee", "assessment")
        if any(k in service_id for k in ("tax", "vat", "holding-tax", "stamp")):
            return True
        return any(fee_keywords[0] in (g.get("description") or "").lower() for g in gaps)

    def _build_partial_reasons(
        self,
        audit: dict[str, Any],
        evaluation: dict[str, Any],
        dimension_coverage: dict[str, bool],
        sources: list[dict[str, Any]],
        gaps: list[dict[str, Any]],
    ) -> list[str]:
        reasons: list[str] = []
        profile_key = evaluation.get("profile_key") or "OTHER"
        profile = (self.profiles_doc.get("profiles") or {}).get(profile_key, {})
        high_risk = set(profile.get("high_risk_dimensions") or [])
        required = set(profile.get("required_dimensions") or [])

        for dim, tax in DIMENSION_TO_TAXONOMY.items():
            mapped = dim
            if dim == "documents" and not dimension_coverage.get("documents"):
                reasons.append(tax)
            elif dim == "conditional_documents":
                has_cond = any(
                    (c.get("condition") or {}).get("requirement_class") == "CONDITIONAL"
                    for c in audit.get("_claims") or []
                )
                if not has_cond and "documents" in high_risk:
                    reasons.append(tax)
            elif not dimension_coverage.get(mapped if mapped in dimension_coverage else dim):
                if dim in high_risk or dim in required or dim.replace("_", "") in str(required):
                    key = mapped if mapped in {"eligibility", "procedure", "fees", "payment", "official_url", "status", "processing_time", "office", "geography", "legal_basis"} else dim
                    if not dimension_coverage.get(key):
                        tax_key = DIMENSION_TO_TAXONOMY.get(key, DIMENSION_TO_TAXONOMY.get(dim))
                        if tax_key and tax_key not in reasons:
                            reasons.append(tax_key)

        if int(audit.get("service_specific_claims") or 0) < 3:
            reasons.append("MISSING_CLAIM_DENSITY")
        if int(audit.get("e2e_answer_supported") or 0) == 0 and int(audit.get("e2e_queries") or 0) > 0:
            reasons.append("MISSING_E2E_SUPPORTED_COVERAGE")
        if int(audit.get("conflicting_claims") or 0) > 0:
            reasons.append("CONFLICTING_INFORMATION")
        if audit.get("catalogue_only_sources") or int(audit.get("tier1_2_sources") or 0) == 0:
            if not any(s.get("probe", {}).get("reachable") for s in sources):
                reasons.append("OFFICIAL_SOURCE_UNAVAILABLE")
        if self._detect_js_limitation(sources):
            reasons.append("JS_RENDERING_LIMITATION")
        if self._detect_calculator_required(audit.get("service_id", ""), gaps):
            if "MISSING_FEES" not in reasons:
                reasons.append("CALCULATOR_REQUIRED")
        geo = audit.get("geographic_scope") or self.catalogue.get(audit.get("service_id", ""), {}).get("geographic_scope")
        if geo and str(geo).upper() in {"UPAZILA", "DISTRICT", "UNION"} and not dimension_coverage.get("office"):
            if "LOCAL_VARIATION" not in reasons:
                reasons.append("LOCAL_VARIATION")
        if int(audit.get("total_claims") or 0) <= 1:
            reasons.append("MISSING_FRESHNESS")

        # dedupe preserve order
        seen: set[str] = set()
        ordered: list[str] = []
        for r in reasons:
            if r not in seen:
                seen.add(r)
                ordered.append(r)
        if not ordered:
            ordered.append("OTHER")
        return ordered

    def _user_value_for_service(
        self,
        service_id: str,
        profile_key: str,
        dimension_coverage: dict[str, bool],
        evaluation: dict[str, Any],
        e2e_supported_rate: float,
    ) -> dict[str, Any]:
        profile = (self.profiles_doc.get("profiles") or {}).get(profile_key, {})
        e2e_intents = set(profile.get("e2e_intents") or [])
        intent_to_dim = {
            "procedure": "procedure",
            "document_list": "documents",
            "fee": "fees",
            "eligibility": "eligibility",
            "status": "status",
            "payment": "payment",
        }
        expected_dims = {"identity", "authority", "official_url"}
        for intent in e2e_intents:
            if intent in intent_to_dim:
                expected_dims.add(intent_to_dim[intent])
        for dim in profile.get("high_risk_dimensions") or []:
            expected_dims.add(dim if dim != "conditions" else "variants")

        answers: dict[str, dict[str, Any]] = {}
        for qid, qmeta in USER_VALUE_QUESTIONS.items():
            relevant = bool(qmeta.get("always_relevant"))
            if not relevant:
                for dim in qmeta.get("dimensions") or []:
                    if dim in expected_dims or dim.replace("_documents", "") in expected_dims:
                        relevant = True
                        break
            if not relevant:
                answers[qid] = {"relevant": False, "answerable": None, "status": "NOT_APPLICABLE"}
                continue
            covered = True
            for dim in qmeta.get("dimensions") or ["identity"]:
                key = dim
                if dim == "conditional_documents":
                    key = "documents"
                if dim == "variants":
                    key = "variants" if dimension_coverage.get("variants") else "geography"
                if not dimension_coverage.get(key) and key not in {"identity", "authority"}:
                    if key == "identity":
                        covered = bool(dimension_coverage.get("identity"))
                    else:
                        covered = False
            if qid == "A":
                covered = dimension_coverage.get("identity", True)
            status = "SUPPORTED" if covered else "UNCERTAINTY"
            if qid in {"F", "G"} and not covered:
                status = "DEFERRED"
            answers[qid] = {"relevant": True, "answerable": covered, "status": status}

        supported = sum(1 for a in answers.values() if a.get("status") == "SUPPORTED" and a.get("relevant"))
        relevant_count = sum(1 for a in answers.values() if a.get("relevant"))
        return {
            "service_id": service_id,
            "profile_key": profile_key,
            "expected_question_ids": sorted(
                qid for qid, a in answers.items() if a.get("relevant")
            ),
            "answers": answers,
            "supported_answer_coverage": round(supported / max(relevant_count, 1), 4),
            "e2e_supported_rate": e2e_supported_rate,
        }

    def analyze_service(self, audit: dict[str, Any]) -> PartialServiceAnalysis:
        service_id = audit["service_id"]
        batch_slug = audit.get("batch_slug") or ""
        entry = self.catalogue.get(service_id) or {
            "service_id": service_id,
            "service_name_en": audit.get("service_name_en"),
            "category_id": audit.get("category_id"),
        }
        claims, sources, verifications, research_source = self._load_service_knowledge(service_id, batch_slug)
        audit_copy = dict(audit)
        audit_copy["_claims"] = claims

        e2e_total = int(audit.get("e2e_queries") or 0)
        e2e_supported = int(audit.get("e2e_answer_supported") or 0)
        e2e_rate = e2e_supported / e2e_total if e2e_total else 0.0

        evaluation = evaluate_service_research(
            service_id, entry, claims, sources, verifications, self.profiles_doc,
            {"total": e2e_total, "answer_supported": e2e_supported},
        )
        ev = evaluation_to_dict(evaluation)
        profile_key = ev.get("profile_key") or "OTHER"
        profile = (self.profiles_doc.get("profiles") or {}).get(profile_key, {})
        required_dims = profile.get("required_dimensions") or []
        high_risk_dims = profile.get("high_risk_dimensions") or []

        dim_cov = dict(ev.get("dimension_coverage") or {})
        gaps_path = self._find_rerun_artifact(service_id)
        gaps: list[dict[str, Any]] = []
        if gaps_path and (gaps_path / "knowledge_gaps.json").exists():
            gaps = json.loads((gaps_path / "knowledge_gaps.json").read_text(encoding="utf-8")).get("gaps") or []

        partial_reasons = self._build_partial_reasons(audit_copy, ev, dim_cov, sources, gaps)

        critical_missing = [
            d for d in high_risk_dims
            if not dim_cov.get(d if d != "conditions" else "variants")
            and d not in {"identity", "authority"}
        ]
        for d in required_dims:
            if d not in dim_cov or not dim_cov.get(d):
                if d not in critical_missing and d not in {"identity"}:
                    critical_missing.append(d)

        noncritical_missing = [
            d for d in ("processing_time", "legal_basis", "status", "payment")
            if d not in high_risk_dims and not dim_cov.get(d)
        ]

        unresolvable: list[str] = []
        resolvable: list[str] = []
        for g in gaps:
            desc = (g.get("description") or "").lower()
            gtype = g.get("gap_type") or ""
            if gtype == "CURRENT_FEE_MISSING" or "fee" in desc:
                if "CALCULATOR_REQUIRED" in partial_reasons:
                    unresolvable.append(g.get("gap_id") or gtype)
                else:
                    resolvable.append(g.get("gap_id") or gtype)
            elif gtype == "CURRENT_URL_MISSING" and "JS_RENDERING_LIMITATION" in partial_reasons:
                resolvable.append(g.get("gap_id") or gtype)
            elif gtype == "LOCAL_RULE_MISSING":
                resolvable.append(g.get("gap_id") or gtype)
            else:
                resolvable.append(g.get("gap_id") or gtype)

        if "OFFICIAL_SOURCE_UNAVAILABLE" in partial_reasons:
            unresolvable.extend(["official_source_access"])

        return PartialServiceAnalysis(
            service_id=service_id,
            service_name_en=audit.get("service_name_en") or service_id,
            category_id=audit.get("category_id") or "",
            profile_key=profile_key,
            batch_slug=batch_slug,
            partial_reasons=partial_reasons,
            critical_missing=critical_missing,
            noncritical_missing=noncritical_missing,
            unresolvable_gaps=unresolvable,
            resolvable_gaps=resolvable,
            dimension_coverage=dim_cov,
            claim_counts={
                "total": int(audit.get("total_claims") or 0),
                "service_specific": int(audit.get("service_specific_claims") or 0),
                "verified": int(audit.get("verified_claims") or 0),
            },
            e2e_supported_rate=round(e2e_rate, 4),
            research_source=research_source,
            flags=list(audit.get("flags") or []),
        )

    def run_full_analysis(self) -> dict[str, Any]:
        audit_path = self.repo_root / "data" / "audit" / "final-service-completeness.json"
        audit_doc = json.loads(audit_path.read_text(encoding="utf-8"))
        partial_audits = [s for s in audit_doc.get("services") or [] if s.get("completeness") == "PARTIAL"]

        analyses = [self.analyze_service(a) for a in partial_audits]
        taxonomy_records = []
        user_value_records = []

        reason_counter: Counter[str] = Counter()
        domain_counter: Counter[str] = Counter()
        category_counter: Counter[str] = Counter()

        for a in analyses:
            for r in a.partial_reasons:
                reason_counter[r] += 1
            domain_counter[a.category_id] += 1
            category_counter[a.profile_key] += 1
            taxonomy_records.append(
                {
                    "service_id": a.service_id,
                    "service_name_en": a.service_name_en,
                    "category_id": a.category_id,
                    "profile_key": a.profile_key,
                    "batch_slug": a.batch_slug,
                    "partial_reasons": a.partial_reasons,
                    "critical_missing": a.critical_missing,
                    "noncritical_missing": a.noncritical_missing,
                    "unresolvable_gaps": a.unresolvable_gaps,
                    "resolvable_gaps": a.resolvable_gaps,
                    "dimension_coverage": a.dimension_coverage,
                    "research_source": a.research_source,
                    "e2e_supported_rate": a.e2e_supported_rate,
                }
            )
            user_value_records.append(
                self._user_value_for_service(
                    a.service_id, a.profile_key, a.dimension_coverage,
                    {"profile_key": a.profile_key}, a.e2e_supported_rate,
                )
            )

        total = len(analyses)
        dim_missing_pct = {
            "fees": round(100 * reason_counter.get("MISSING_FEES", 0) / total, 1),
            "documents": round(100 * reason_counter.get("MISSING_MUST_NEED_DOCUMENTS", 0) / total, 1),
            "procedure": round(100 * reason_counter.get("MISSING_PROCEDURE", 0) / total, 1),
            "official_url": round(100 * reason_counter.get("MISSING_OFFICIAL_URL", 0) / total, 1),
            "eligibility": round(100 * reason_counter.get("MISSING_ELIGIBILITY", 0) / total, 1),
            "e2e_supported": round(100 * reason_counter.get("MISSING_E2E_SUPPORTED_COVERAGE", 0) / total, 1),
        }

        bottlenecks = self._infer_bottleneck(reason_counter, analyses, dim_missing_pct)

        return {
            "generated_at": self._now(),
            "total_partial_services": total,
            "taxonomy": {
                "categories": TAXONOMY_CATEGORIES,
                "services": taxonomy_records,
                "reason_frequency": dict(reason_counter.most_common()),
                "by_category": dict(category_counter.most_common()),
                "by_domain": dict(domain_counter.most_common()),
            },
            "user_value_matrix": {
                "questions": USER_VALUE_QUESTIONS,
                "services": user_value_records,
                "aggregate_supported_coverage": round(
                    sum(u["supported_answer_coverage"] for u in user_value_records) / max(total, 1), 4
                ),
            },
            "bottlenecks": bottlenecks,
            "dimension_missing_pct": dim_missing_pct,
        }

    def _infer_bottleneck(
        self,
        reason_counter: Counter[str],
        analyses: list[PartialServiceAnalysis],
        dim_missing_pct: dict[str, float],
    ) -> dict[str, Any]:
        scores = {
            "RESEARCH": reason_counter.get("MISSING_CLAIM_DENSITY", 0) + reason_counter.get("MISSING_PROCEDURE", 0),
            "SOURCE_DISCOVERY": reason_counter.get("MISSING_OFFICIAL_URL", 0),
            "SOURCE_ACCESS": reason_counter.get("OFFICIAL_SOURCE_UNAVAILABLE", 0) + reason_counter.get("JS_RENDERING_LIMITATION", 0),
            "VERIFICATION": sum(1 for a in analyses if a.claim_counts.get("verified", 0) == 0),
            "DATA_MODEL": reason_counter.get("MISSING_APPLICANT_VARIANTS", 0) + reason_counter.get("LOCAL_VARIATION", 0),
            "RETRIEVAL": reason_counter.get("MISSING_E2E_SUPPORTED_COVERAGE", 0),
            "E2E": reason_counter.get("MISSING_E2E_SUPPORTED_COVERAGE", 0),
            "GOVERNMENT_INFO_AVAILABILITY": reason_counter.get("CALCULATOR_REQUIRED", 0) + reason_counter.get("OFFICIAL_SOURCE_UNAVAILABLE", 0),
        }
        primary = max(scores, key=lambda k: scores[k])
        return {
            "primary_bottleneck": primary,
            "bottleneck_scores": scores,
            "top_missing_dimensions": dict(Counter(
                r for a in analyses for r in a.partial_reasons
            ).most_common(10)),
            "source_limitations": {
                "official_source_unavailable_pct": round(100 * reason_counter.get("OFFICIAL_SOURCE_UNAVAILABLE", 0) / max(len(analyses), 1), 1),
                "js_rendering_limitation_pct": round(100 * reason_counter.get("JS_RENDERING_LIMITATION", 0) / max(len(analyses), 1), 1),
                "calculator_required_pct": round(100 * reason_counter.get("CALCULATOR_REQUIRED", 0) / max(len(analyses), 1), 1),
            },
            "dimension_missing_pct": dim_missing_pct,
            "high_usage_partial": [
                a.service_id for a in analyses if a.service_id in HIGH_USAGE_SERVICE_IDS
            ][:20],
            "interpretation": (
                f"Primary bottleneck inferred as {primary} based on aggregated partial-reason frequencies, "
                "not guesswork. High rates of MISSING_E2E_SUPPORTED_COVERAGE indicate retrieval/E2E gap "
                "even when basic service-specific sources exist post-wave rerun."
            ),
        }

    def select_pilot_services(self) -> list[dict[str, Any]]:
        """Select 12 representative PARTIAL services for deep-research pilot."""
        selections = [
            ("high_usage", "nid-new-voter-registration"),
            ("high_usage", "education-ssc-certificate"),
            ("high_risk", "tax-income-return-file"),
            ("high_risk", "business-company-incorporation"),
            ("land", "land-mutation-apply"),
            ("land", "land-khatian-certified-copy"),
            ("education", "education-foreign-equivalency"),
            ("education", "education-duplicate-certificate"),
            ("social_protection", "snp-old-age-allowance"),
            ("disability", "disability-dis-registration"),
            ("health", "health-bmdc-full-registration"),
            ("judiciary", "judiciary-supreme-court-e-filing"),
        ]
        audit_path = self.repo_root / "data" / "audit" / "final-service-completeness.json"
        partial_ids = {
            s["service_id"]
            for s in json.loads(audit_path.read_text(encoding="utf-8")).get("services") or []
            if s.get("completeness") == "PARTIAL"
        }
        pilot = []
        for role, sid in selections:
            if sid in partial_ids:
                entry = self.catalogue.get(sid, {})
                pilot.append(
                    {
                        "service_id": sid,
                        "pilot_role": role,
                        "service_name_en": entry.get("service_name_en") or sid,
                        "category_id": entry.get("category_id"),
                    }
                )
        return pilot
