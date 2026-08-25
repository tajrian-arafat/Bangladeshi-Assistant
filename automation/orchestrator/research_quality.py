"""Service-level research quality model — detects false completion and scores completeness."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

BOILERPLATE_CLAIM_SUFFIXES = frozenset(
    {"c-application-portal", "c-responsible-authority", "c-official-source"}
)
GENERIC_BUILDER_MARKERS = frozenset({"generic_research_builder", "generic_verification_builder"})
GENERIC_CLAIM_PATTERNS = (
    re.compile(r"^this is a government service\.?$", re.I),
    re.compile(r"^application portal exists\.?$", re.I),
    re.compile(r"^authority is bangladesh government\.?$", re.I),
    re.compile(r"^apply online\.?$", re.I),
    re.compile(r"^catalogue official source documented", re.I),
    re.compile(r"^responsible authority:", re.I),
)
HAND_RESEARCH_BATCH_SLUGS = frozenset(
    {
        "batch-01",
        "batch-01-identity-civil-registration",
        "batch-02a-passport",
        "batch-02b-police-immigration",
        "batch-03a-brta-driving-licence",
        "batch-03b-brta-vehicle",
        "batch-03c-brta-fitness-tax-permit",
    }
)


@dataclass
class ClaimClassification:
    claim_id: str
    service_id: str
    claim_class: str
    meaningful: bool
    reasons: list[str] = field(default_factory=list)


@dataclass
class ServiceResearchEvaluation:
    service_id: str
    profile_key: str
    research_status: str
    completeness_score: float
    meaningful_claims: int
    verified_claims: int
    service_specific_sources: int
    catalogue_metadata_claims: int
    false_completion_risk: bool
    flags: list[str] = field(default_factory=list)
    dimension_coverage: dict[str, bool] = field(default_factory=dict)
    missing_dimensions: list[str] = field(default_factory=list)
    score_breakdown: dict[str, float] = field(default_factory=dict)


@dataclass
class BatchQualityReport:
    batch_id: str
    batch_slug: str
    complete: bool
    services_total: int
    services_research_complete: int
    false_completion_count: int
    missing: list[str] = field(default_factory=list)
    service_evaluations: list[ServiceResearchEvaluation] = field(default_factory=list)


def load_profiles(repo_root: Path) -> dict[str, Any]:
    path = repo_root / "data" / "research" / "service_research_profiles.json"
    if not path.exists():
        return {"profiles": {}, "authority_domain_hints": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def _claim_suffix(claim_id: str) -> str:
    return claim_id.split("::")[-1] if "::" in claim_id else claim_id


def _domain(url: str) -> str:
    if not url:
        return ""
    try:
        host = urlparse(url if "://" in url else f"https://{url}").netloc.lower()
        return host[4:] if host.startswith("www.") else host
    except Exception:
        return ""


def resolve_profile_key(catalogue_entry: dict[str, Any], profiles_doc: dict[str, Any]) -> str:
    category_id = str(catalogue_entry.get("category_id") or "")
    authority_id = str(catalogue_entry.get("authority_id") or "")
    profiles = profiles_doc.get("profiles") or {}

    for key, profile in profiles.items():
        if key == "OTHER":
            continue
        cat_ids = profile.get("category_ids") or []
        auth_ids = profile.get("authority_ids") or []
        if category_id in cat_ids:
            return key
        if authority_id in auth_ids:
            return key

    category_map = {
        "land": "LAND",
        "education": "EDUCATION",
        "health": "HEALTH",
        "social_protection": "SOCIAL_PROTECTION",
        "disability": "DISABILITY",
        "tax": "TAX",
        "vat": "VAT",
        "customs": "CUSTOMS",
        "local_government": "LOCAL_GOVERNMENT",
        "judiciary": "JUDICIARY",
        "legal_aid": "JUDICIARY",
        "agriculture": "AGRICULTURE",
        "livestock": "LIVESTOCK",
        "fisheries": "FISHERIES",
        "employment": "EMPLOYMENT",
        "expatriate": "EMPLOYMENT",
        "business": "BUSINESS",
        "trade": "BUSINESS",
        "registrations": "BUSINESS",
        "professional": "PROFESSIONAL",
        "utilities": "UTILITIES",
        "transport": "BRTA",
        "passport": "PASSPORT",
        "passport_immigration": "POLICE",
        "police": "POLICE",
        "civil_registration": "IDENTITY_CIVIL",
        "identity": "IDENTITY_CIVIL",
    }
    return category_map.get(category_id, "OTHER")


def classify_claim(
    claim: dict[str, Any],
    *,
    catalogue_entry: dict[str, Any] | None = None,
    sources_by_id: dict[str, dict[str, Any]] | None = None,
    profiles_doc: dict[str, Any] | None = None,
) -> ClaimClassification:
    claim_id = str(claim.get("claim_id") or "")
    service_id = str(claim.get("service_id") or "")
    suffix = _claim_suffix(claim_id)
    text = (claim.get("claim_text") or "").strip()
    info_class = str(claim.get("information_class") or claim.get("claim_class") or "")
    source_ids = list(claim.get("source_ids") or [])
    reasons: list[str] = []

    if info_class in {"CATALOGUE_METADATA", "DISCOVERY_ONLY"}:
        return ClaimClassification(claim_id, service_id, info_class, False, ["explicit_non_authoritative_class"])

    if suffix in BOILERPLATE_CLAIM_SUFFIXES:
        reasons.append("boilerplate_claim_suffix")
        return ClaimClassification(claim_id, service_id, "CATALOGUE_METADATA", False, reasons)

    for pattern in GENERIC_CLAIM_PATTERNS:
        if pattern.search(text):
            reasons.append(f"generic_pattern:{pattern.pattern}")
            return ClaimClassification(claim_id, service_id, "CATALOGUE_METADATA", False, reasons)

    if "nbr e-service portal" in text.lower() and "nbr" not in service_id and "tax" not in service_id and "vat" not in service_id and "customs" not in service_id:
        reasons.append("wrong_authority_nbr_bleed")
        return ClaimClassification(claim_id, service_id, "CATALOGUE_METADATA", False, reasons)

    if source_ids == ["src-catalogue"] or (len(source_ids) == 1 and source_ids[0] == "src-catalogue"):
        reasons.append("catalogue_only_source")
        return ClaimClassification(claim_id, service_id, "CATALOGUE_METADATA", False, reasons)

    sources_by_id = sources_by_id or {}
    if catalogue_entry and profiles_doc:
        profile_key = resolve_profile_key(catalogue_entry, profiles_doc)
        profile = (profiles_doc.get("profiles") or {}).get(profile_key, {})
        forbidden = profile.get("forbidden_authority_domains") or []
        for sid in source_ids:
            src = sources_by_id.get(sid) or {}
            domain = _domain(str(src.get("url") or ""))
            if domain and any(domain.endswith(f) or f in domain for f in forbidden):
                reasons.append(f"forbidden_domain:{domain}")
                return ClaimClassification(claim_id, service_id, "CATALOGUE_METADATA", False, reasons)

    claim_type = str(claim.get("claim_type") or "")
    tier = min(
        (int((sources_by_id.get(sid) or {}).get("tier") or 7) for sid in source_ids),
        default=7,
    )
    if tier >= 5 and claim_type not in {"procedure_step", "document", "fee", "eligibility", "application_url"}:
        return ClaimClassification(claim_id, service_id, "DISCOVERY_ONLY", False, ["low_tier_discovery_source"])

    if len(text) < 25 and claim_type in {"", "eligibility"}:
        reasons.append("too_short_non_specific")
        return ClaimClassification(claim_id, service_id, "CATALOGUE_METADATA", False, reasons)

    meaningful_types = {
        "document",
        "document_requirement",
        "fee",
        "fee_schedule",
        "eligibility",
        "procedure",
        "procedure_step",
        "application_url",
        "processing_time",
        "office",
        "legal_requirement",
        "status_check",
    }
    if claim_type in meaningful_types or any(k in text.lower() for k in ("required", "fee", "document", "apply", "step", "office", "eligible")):
        return ClaimClassification(claim_id, service_id, "SERVICE_SPECIFIC", True, reasons or ["service_specific_content"])

    return ClaimClassification(claim_id, service_id, "DISCOVERY_ONLY", False, reasons or ["insufficient_specificity"])


def source_is_service_specific(
    source: dict[str, Any],
    catalogue_entry: dict[str, Any],
    profiles_doc: dict[str, Any],
) -> bool:
    if source.get("source_id") == "src-catalogue":
        return False
    if source.get("source_type") == "CATALOGUE_METADATA":
        return False
    if source.get("scaffolding_only"):
        return False
    url = str(source.get("url") or "")
    if url.endswith("services.json"):
        return False
    domain = _domain(url)
    if not domain:
        return False

    profile_key = resolve_profile_key(catalogue_entry, profiles_doc)
    profile = (profiles_doc.get("profiles") or {}).get(profile_key, {})
    forbidden = profile.get("forbidden_authority_domains") or []
    if any(domain.endswith(f) or f in domain for f in forbidden):
        return False

    service_id = str(catalogue_entry.get("service_id") or "")
    source_id = str(source.get("source_id") or "")
    if source.get("service_id") == service_id or service_id in source_id:
        tier = int(source.get("tier") or 7)
        return tier <= 4

    authority_id = str(catalogue_entry.get("authority_id") or "")
    hints = profiles_doc.get("authority_domain_hints") or {}
    expected = hints.get(authority_id) or profile.get("expected_domain_patterns") or []
    if expected and any(domain.endswith(p.replace("www.", "")) or p in domain for p in expected):
        tier = int(source.get("tier") or 7)
        return tier <= 4

    service_name = (catalogue_entry.get("service_name_en") or "").lower()
    title = str((source.get("probe") or {}).get("title") or source.get("title") or "").lower()
    if service_name and (service_name[:12] in title or service_id in url):
        tier = int(source.get("tier") or 7)
        return tier <= 4

    return False


def _verification_status(claim: dict[str, Any], verification: dict[str, Any] | None = None) -> str:
    if verification:
        return str(verification.get("verification_status") or "UNKNOWN").upper()
    for key in ("pipeline_status", "verification_status", "independent_verification_status"):
        val = claim.get(key)
        if val:
            status = str(val).upper()
            if status in {"VERIFIED", "FULLY_VERIFIED", "PARTIALLY_VERIFIED", "CONFLICTING", "REJECTED"}:
                return status
    return "UNKNOWN"


def evaluate_service_research(
    service_id: str,
    catalogue_entry: dict[str, Any],
    claims: list[dict[str, Any]],
    sources: list[dict[str, Any]],
    verifications: dict[str, dict[str, Any]] | None = None,
    profiles_doc: dict[str, Any] | None = None,
    e2e_metrics: dict[str, Any] | None = None,
) -> ServiceResearchEvaluation:
    profiles_doc = profiles_doc or {"profiles": {}}
    profile_key = resolve_profile_key(catalogue_entry, profiles_doc)
    profile = (profiles_doc.get("profiles") or {}).get(profile_key, {})
    sources_by_id = {s["source_id"]: s for s in sources if s.get("source_id")}

    meaningful = 0
    verified = 0
    metadata_claims = 0
    flags: list[str] = []
    dimension_coverage: dict[str, bool] = defaultdict(bool)

    for claim in claims:
        classification = classify_claim(
            claim,
            catalogue_entry=catalogue_entry,
            sources_by_id=sources_by_id,
            profiles_doc=profiles_doc,
        )
        if classification.claim_class == "SERVICE_SPECIFIC" and classification.meaningful:
            meaningful += 1
            ctype = str(claim.get("claim_type") or "")
            if "url" in ctype or ctype == "application_url":
                dimension_coverage["official_url"] = True
            if ctype in {"document", "document_requirement"}:
                dimension_coverage["documents"] = True
            if ctype in {"fee", "fee_schedule"}:
                dimension_coverage["fees"] = True
            if ctype in {"procedure", "procedure_step"}:
                dimension_coverage["procedure"] = True
            if ctype == "eligibility":
                dimension_coverage["eligibility"] = True
            if ctype in {"office", "processing_time"}:
                dimension_coverage["office"] = True
        elif classification.claim_class == "CATALOGUE_METADATA":
            metadata_claims += 1

        v = (verifications or {}).get(str(claim.get("claim_id")))
        status = _verification_status(claim, v)
        if status in {"VERIFIED", "FULLY_VERIFIED"}:
            verified += 1

    dimension_coverage["identity"] = bool(catalogue_entry.get("service_name_en"))
    dimension_coverage["authority"] = bool(catalogue_entry.get("responsible_authority") or catalogue_entry.get("authority_id"))

    service_specific_sources = sum(
        1 for s in sources if source_is_service_specific(s, catalogue_entry, profiles_doc)
    )
    # Also count sources referenced by meaningful claims
    for claim in claims:
        classification = classify_claim(
            claim, catalogue_entry=catalogue_entry, sources_by_id=sources_by_id, profiles_doc=profiles_doc
        )
        if classification.meaningful:
            for sid in claim.get("source_ids") or []:
                src = sources_by_id.get(sid)
                if src and src.get("source_id") != "src-catalogue" and int(src.get("tier") or 7) <= 4:
                    service_specific_sources = max(service_specific_sources, 1)
                    break

    min_meaningful = int(profile.get("minimum_meaningful_claims") or 2)
    min_sources = int(profile.get("minimum_service_specific_sources") or 1)
    min_verified = int(profile.get("minimum_verified_claims") or 1)

    false_completion = False
    if metadata_claims >= 2 and meaningful == 0:
        false_completion = True
        flags.append("FALSE_COMPLETION_RISK")
    if meaningful < min_meaningful:
        flags.append("INSUFFICIENT_MEANINGFUL_CLAIMS")
    if service_specific_sources < min_sources:
        flags.append("MISSING_SERVICE_SPECIFIC_SOURCE")
    if verified < min_verified:
        flags.append("INSUFFICIENT_VERIFIED_CLAIMS")

    required_dims = profile.get("required_dimensions") or ["identity", "authority", "official_url"]
    missing_dims = [d for d in required_dims if not dimension_coverage.get(d)]
    if missing_dims:
        flags.append("MISSING_REQUIRED_DIMENSIONS")

    weights = profiles_doc.get("completeness_scoring_weights") or {
        "research_quality": 0.25,
        "verification_quality": 0.2,
        "knowledge_coverage": 0.2,
        "e2e_supported_coverage": 0.15,
        "source_quality": 0.1,
        "citation_integrity": 0.1,
    }

    research_quality = min(1.0, meaningful / max(min_meaningful, 1))
    verification_quality = min(1.0, verified / max(min_verified, 1))
    knowledge_coverage = min(1.0, len([d for d in required_dims if dimension_coverage.get(d)]) / max(len(required_dims), 1))
    source_quality = min(1.0, service_specific_sources / max(min_sources, 1))
    e2e_supported = 0.0
    if e2e_metrics:
        total = int(e2e_metrics.get("total") or 0)
        supported = int(e2e_metrics.get("answer_supported") or e2e_metrics.get("passed") or 0)
        if total > 0:
            e2e_supported = supported / total
    citation_integrity = 1.0 if "CITATION_FAILURE" not in flags else 0.0

    score_breakdown = {
        "research_quality": round(research_quality * weights.get("research_quality", 0.25), 4),
        "verification_quality": round(verification_quality * weights.get("verification_quality", 0.2), 4),
        "knowledge_coverage": round(knowledge_coverage * weights.get("knowledge_coverage", 0.2), 4),
        "e2e_supported_coverage": round(e2e_supported * weights.get("e2e_supported_coverage", 0.15), 4),
        "source_quality": round(source_quality * weights.get("source_quality", 0.1), 4),
        "citation_integrity": round(citation_integrity * weights.get("citation_integrity", 0.1), 4),
    }
    completeness_score = round(sum(score_breakdown.values()), 4)

    if false_completion:
        research_status = "FALSE_COMPLETION_RISK"
    elif meaningful >= min_meaningful and service_specific_sources >= min_sources and not missing_dims:
        if verified >= min_verified:
            research_status = "RESEARCH_COMPLETE"
        else:
            research_status = "PARTIAL"
    elif meaningful > 0:
        research_status = "PARTIAL"
    else:
        research_status = "RESEARCH_REQUIRED"

    return ServiceResearchEvaluation(
        service_id=service_id,
        profile_key=profile_key,
        research_status=research_status,
        completeness_score=completeness_score,
        meaningful_claims=meaningful,
        verified_claims=verified,
        service_specific_sources=service_specific_sources,
        catalogue_metadata_claims=metadata_claims,
        false_completion_risk=false_completion or "FALSE_COMPLETION_RISK" in flags,
        flags=flags,
        dimension_coverage=dict(dimension_coverage),
        missing_dimensions=missing_dims,
        score_breakdown=score_breakdown,
    )


def evaluate_batch_research_quality(
    repo_root: Path,
    batch: dict[str, Any],
) -> BatchQualityReport:
    from automation.orchestrator.batch_manager import BatchManager
    from automation.orchestrator.phase_completion import batch_slug, raw_research_dir

    slug = batch_slug(batch)
    profiles_doc = load_profiles(repo_root)
    catalogue_list = BatchManager(repo_root).load_catalogue()
    catalogue = {s.get("service_id") or s.get("id"): s for s in catalogue_list}

    raw = raw_research_dir(repo_root, batch)
    claims_doc = json.loads((raw / "claims.json").read_text(encoding="utf-8")) if (raw / "claims.json").exists() else {"claims": []}
    sources_doc = json.loads((raw / "sources.json").read_text(encoding="utf-8")) if (raw / "sources.json").exists() else {"sources": []}
    all_claims = claims_doc.get("claims") or []
    all_sources = sources_doc.get("sources") or []

    verify_path = repo_root / "data" / "research" / "verification" / slug / "claims_verification.json"
    verifications: dict[str, dict[str, Any]] = {}
    if verify_path.exists():
        vdoc = json.loads(verify_path.read_text(encoding="utf-8"))
        for v in vdoc.get("verifications") or []:
            verifications[str(v.get("claim_id"))] = v

    evaluations: list[ServiceResearchEvaluation] = []
    service_ids = list(batch.get("service_ids") or [])
    false_count = 0
    complete_count = 0

    for sid in service_ids:
        entry = catalogue.get(sid) or {"service_id": sid}
        svc_claims = [c for c in all_claims if c.get("service_id") == sid]
        svc_sources = [s for s in all_sources if s.get("service_id") == sid or s.get("source_id", "").endswith(sid)]
        ev = evaluate_service_research(sid, entry, svc_claims, svc_sources, verifications, profiles_doc)
        evaluations.append(ev)
        if ev.false_completion_risk:
            false_count += 1
        if ev.research_status == "RESEARCH_COMPLETE":
            complete_count += 1

    missing: list[str] = []
    if false_count > 0:
        missing.append(f"{false_count} services have FALSE_COMPLETION_RISK")

    hand_researched = slug in HAND_RESEARCH_BATCH_SLUGS or any(
        slug.startswith(h + "-") for h in HAND_RESEARCH_BATCH_SLUGS
    )
    batch_complete = false_count == 0 and (
        (complete_count == len(service_ids))
        or (hand_researched and complete_count + sum(1 for e in evaluations if e.research_status == "PARTIAL" and e.meaningful_claims >= 2) >= len(service_ids))
    )
    if not batch_complete and not hand_researched:
        missing.append(f"only {complete_count}/{len(service_ids)} services RESEARCH_COMPLETE")

    return BatchQualityReport(
        batch_id=batch["batch_id"],
        batch_slug=slug,
        complete=batch_complete,
        services_total=len(service_ids),
        services_research_complete=complete_count,
        false_completion_count=false_count,
        missing=missing,
        service_evaluations=evaluations,
    )


def detect_generic_claims_across_services(
    repo_root: Path,
    audits: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build generic-claim-detection.json payload."""
    if audits is None:
        audit_path = repo_root / "data" / "audit" / "final-service-completeness.json"
        if audit_path.exists():
            doc = json.loads(audit_path.read_text(encoding="utf-8"))
            audits = doc.get("services") or []
        else:
            audits = []

    claim_text_index: dict[str, list[str]] = defaultdict(list)
    url_index: dict[str, list[str]] = defaultdict(list)
    results: list[dict[str, Any]] = []

    raw_root = repo_root / "data" / "research" / "raw"
    for batch_dir in sorted(raw_root.iterdir()) if raw_root.is_dir() else []:
        claims_path = batch_dir / "claims.json"
        sources_path = batch_dir / "sources.json"
        if not claims_path.exists():
            continue
        claims = json.loads(claims_path.read_text(encoding="utf-8")).get("claims") or []
        sources = json.loads(sources_path.read_text(encoding="utf-8")).get("sources") if sources_path.exists() else []
        sources_by_id = {s["source_id"]: s for s in (sources or [])}

        for claim in claims:
            sid = str(claim.get("service_id") or "")
            text = (claim.get("claim_text") or "").strip().lower()
            if text:
                claim_text_index[text].append(sid)
            for src_id in claim.get("source_ids") or []:
                url = str((sources_by_id.get(src_id) or {}).get("url") or "")
                if url:
                    url_index[url].append(sid)

    for audit in audits:
        sid = audit.get("service_id", "")
        flags = list(audit.get("flags") or [])
        classification = "VALID"
        reasons: list[str] = []

        if "FALSE_COMPLETION_RISK" in flags or audit.get("completeness") == "FALSE_COMPLETION_RISK":
            classification = "FALSE_COMPLETION_RISK"
            reasons.append("audit_false_completion_flag")
        elif audit.get("boilerplate_claims", 0) == audit.get("total_claims", 0) and audit.get("total_claims", 0) > 0:
            classification = "FALSE_COMPLETION_RISK"
            reasons.append("boilerplate_only")
        elif audit.get("service_specific_claims", 0) == 0 and audit.get("total_claims", 0) > 0:
            classification = "SUSPICIOUS"
            reasons.append("no_service_specific_claims")

        results.append(
            {
                "service_id": sid,
                "classification": classification,
                "reasons": reasons,
                "batch_slug": audit.get("batch_slug"),
                "boilerplate_claims": audit.get("boilerplate_claims"),
                "service_specific_claims": audit.get("service_specific_claims"),
            }
        )

    duplicate_texts = {t: sids for t, sids in claim_text_index.items() if len(set(sids)) > 3}
    duplicate_urls = {u: sids for u, sids in url_index.items() if len(set(sids)) > 5 and "catalogue" not in u}

    return {
        "generated_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "services_analyzed": len(results),
        "classification_counts": dict(Counter(r["classification"] for r in results)),
        "duplicate_claim_texts": {k: list(set(v))[:10] for k, v in list(duplicate_texts.items())[:20]},
        "duplicate_urls_across_unrelated": {k: list(set(v))[:10] for k, v in list(duplicate_urls.items())[:20]},
        "services": results,
    }


def evaluation_to_dict(ev: ServiceResearchEvaluation) -> dict[str, Any]:
    return asdict(ev)
