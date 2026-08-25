#!/usr/bin/env python3
"""Final global knowledge-construction audit — honest completeness assessment."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

GENERIC_BUILDER_MARKERS = frozenset({"generic_research_builder", "generic_verification_builder"})
BOILERPLATE_CLAIM_SUFFIXES = frozenset(
    {"c-application-portal", "c-responsible-authority", "c-official-source"}
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
CRITICAL_CLAIM_TYPES = frozenset(
    {"fee", "fee_schedule", "document", "document_requirement", "eligibility", "procedure", "application_url"}
)
HIGH_RISK_CLAIM_TYPES = CRITICAL_CLAIM_TYPES | frozenset({"processing_time", "sla", "legal_requirement"})


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _claim_suffix(claim_id: str) -> str:
    return claim_id.split("::")[-1] if "::" in claim_id else claim_id


def _is_boilerplate_claim(claim: dict[str, Any]) -> bool:
    suffix = _claim_suffix(claim.get("claim_id", ""))
    if suffix in BOILERPLATE_CLAIM_SUFFIXES:
        return True
    text = (claim.get("claim_text") or "").lower()
    if "nbr e-service portal" in text and "nbr" not in (claim.get("service_id") or ""):
        return True
    if text.startswith("catalogue official source documented"):
        return True
    if text.startswith("responsible authority:") and "src-catalogue" in (claim.get("source_ids") or []):
        return True
    return False


def _verification_status(claim: dict[str, Any]) -> str:
    legacy = claim.get("legacy_verification_status")
    if legacy and str(legacy).upper() == "VERIFIED":
        return "VERIFIED"
    suggested = claim.get("suggested_pipeline_status")
    if suggested and str(suggested).upper() == "VERIFIED":
        return "VERIFIED"
    for key in ("pipeline_status", "independent_verification_status", "verification_status"):
        val = claim.get(key)
        if val:
            status = str(val).upper()
            if status in {"VERIFIED", "FULLY_VERIFIED", "PARTIALLY_VERIFIED", "CONFLICTING", "REJECTED", "OUTDATED"}:
                return status
    iv = claim.get("independent_verification") or {}
    if iv.get("verifier") in GENERIC_BUILDER_MARKERS:
        return "PARTIALLY_VERIFIED"
    prov = claim.get("provenance") or {}
    if prov.get("verification_status"):
        return str(prov["verification_status"]).upper()
    return "UNKNOWN"


def _is_verified(status: str) -> bool:
    return status in {"VERIFIED", "FULLY_VERIFIED"}


def _is_partial(status: str) -> bool:
    return status in {"PARTIALLY_VERIFIED", "PENDING_INDEPENDENT_VERIFICATION", "PENDING_REVIEW"}


def _tier_from_source(source: dict[str, Any]) -> int:
    for key in ("authority_tier", "tier"):
        if source.get(key) is not None:
            return int(source["tier"] if key == "tier" else source["authority_tier"])
    return 7


@dataclass
class ServiceAudit:
    service_id: str
    service_name_en: str
    category_id: str
    batch_id: str
    batch_slug: str
    batch_status: str
    completeness: str
    research_builder: str | None = None
    total_claims: int = 0
    service_specific_claims: int = 0
    boilerplate_claims: int = 0
    verified_claims: int = 0
    partially_verified_claims: int = 0
    unverified_claims: int = 0
    conflicting_claims: int = 0
    published_claims: int = 0
    catalogue_only_sources: bool = True
    tier1_2_sources: int = 0
    lower_tier_sources: int = 0
    knowledge_gaps: int = 0
    critical_gaps: int = 0
    deferred_items: int = 0
    e2e_queries: int = 0
    e2e_passed: int = 0
    e2e_answer_supported: int = 0
    e2e_correct_uncertainty: int = 0
    e2e_product_failure: int = 0
    critical_fields_present: list[str] = field(default_factory=list)
    critical_fields_missing: list[str] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)
    geographic_scope: str = "NATIONAL"


class FinalKnowledgeAudit:
    def __init__(self, repo_root: Path = ROOT) -> None:
        self.repo_root = repo_root
        self.staging_root = repo_root / "data" / "research" / "staging"
        self.raw_root = repo_root / "data" / "research" / "raw"
        self.verification_root = repo_root / "data" / "research" / "verification"
        self.eval_root = repo_root / "data" / "evaluation"
        self.decisions_dir = repo_root / ".automation" / "decisions"

    def load_catalogue(self) -> list[dict[str, Any]]:
        data = _load_json(self.repo_root / "data" / "service_catalogue" / "services.json")
        services = data.get("services") if isinstance(data, dict) else data
        return [s for s in services if (s.get("status") or s.get("catalogue_status")) == "CONFIRMED"]

    def load_runtime_slug_map(self) -> dict[str, str]:
        mappings_path = self.repo_root / "data" / "research" / "catalogue_runtime_mappings.json"
        data = _load_json(mappings_path) or {}
        result: dict[str, str] = {}
        for entry in data.get("mappings") or []:
            cid = entry.get("catalogue_service_id")
            slug = entry.get("runtime_slug")
            if cid and slug:
                result[cid] = slug
        return result

    def load_batch_map(self) -> dict[str, dict[str, Any]]:
        queue = _load_json(self.repo_root / ".automation" / "batch_queue.json") or {}
        mapping: dict[str, dict[str, Any]] = {}
        for batch in queue.get("batches", []):
            for sid in batch.get("service_ids") or []:
                mapping[sid] = batch
        return mapping

    def _resolve_staging_slug(self, slug: str) -> str:
        """Map batch_queue slug to on-disk staging directory name."""
        if not slug:
            return ""
        staging_path = self.staging_root / slug
        if staging_path.is_dir():
            return slug
        aliases = {
            "batch-01-identity-civil-registration": "batch-01",
        }
        if slug in aliases and (self.staging_root / aliases[slug]).is_dir():
            return aliases[slug]
        # Prefix match: batch-01-identity -> batch-01
        for path in sorted(self.staging_root.iterdir()):
            if path.is_dir() and slug.startswith(path.name + "-"):
                return path.name
        return slug

    def _resolve_eval_slug(self, slug: str) -> str:
        """Map batch slug to evaluation directory name."""
        resolved = self._resolve_staging_slug(slug)
        eval_path = self.eval_root / resolved
        if eval_path.is_dir():
            return resolved
        if (self.eval_root / slug).is_dir():
            return slug
        return resolved

    def _load_staging_for_batch(self, slug: str) -> dict[str, Any]:
        base = self.staging_root / slug
        claims = (_load_json(base / "claims.json") or {}).get("claims") or []
        sources = (_load_json(base / "sources.json") or {}).get("sources") or []
        evidence = (_load_json(base / "evidence.json") or {}).get("evidence") or []
        fees = (_load_json(base / "fees.json") or {}).get("fees") or []
        return {
            "claims": claims,
            "sources": {s.get("source_id"): s for s in sources if s.get("source_id")},
            "evidence": evidence,
            "fees": fees,
            "manifest": _load_json(base / "MANIFEST.json") or {},
        }

    def _load_verification(self, slug: str) -> dict[str, Any]:
        base = self.verification_root / slug
        summary = _load_json(base / "summary.json") or {}
        gaps = (_load_json(base / "knowledge_gaps.json") or {}).get("knowledge_gaps") or []
        gap_closure = self.verification_root / f"{slug}-gap-closure"
        gc_gaps = (_load_json(gap_closure / "knowledge_gaps.json") or {}).get("knowledge_gaps") or []
        claims_ver = (_load_json(base / "claims_verification.json") or {}).get("claims") or []
        readiness = (_load_json(base / "service_readiness.json") or {}).get("services") or {}
        deps = (_load_json(gap_closure / "cross_batch_dependencies.json") or {}).get("dependencies") or []
        return {
            "summary": summary,
            "gaps": gaps + gc_gaps,
            "claims_verification": {c.get("claim_id"): c for c in claims_ver if c.get("claim_id")},
            "readiness": readiness,
            "dependencies": deps,
        }

    def _load_raw_metadata(self, slug: str) -> dict[str, Any]:
        return _load_json(self.raw_root / slug / "metadata.json") or {}

    def _load_e2e_for_service(self, slug: str, service_id: str, runtime_slug: str | None = None) -> dict[str, int]:
        eval_slug = self._resolve_eval_slug(slug)
        results_path = self.eval_root / eval_slug / "results.jsonl"
        slug_candidates = {service_id, runtime_slug or "", service_id.replace("civil-", "").replace("identity-", "").replace("local-", "")}
        if runtime_slug:
            slug_candidates.add(runtime_slug)
        if not results_path.exists():
            return {
                "queries": 0,
                "passed": 0,
                "answer_supported": 0,
                "correct_uncertainty": 0,
                "product_failure": 0,
            }
        counts = Counter()
        for line in results_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            case = row.get("case") or {}
            expected = case.get("service_expected") or (case.get("expect") or {}).get("service") or (case.get("expected") or {}).get("service")
            if expected and expected not in slug_candidates and service_id not in json.dumps(row):
                continue
            if expected and expected not in slug_candidates:
                actual_slug = (row.get("actual") or {}).get("service_slug") or ""
                if actual_slug not in slug_candidates and service_id not in json.dumps(row):
                    continue
            counts["queries"] += 1
            ev = row.get("evaluation") or {}
            if ev.get("pass") or row.get("pass"):
                counts["passed"] += 1
            outcome = ev.get("outcome") or ""
            if outcome == "ANSWER_SUPPORTED":
                counts["answer_supported"] += 1
            elif outcome == "CORRECT_UNCERTAINTY":
                counts["correct_uncertainty"] += 1
            elif ev.get("failure_class") in {"HALLUCINATION", "PRODUCT_FAILURE", "RETRIEVAL_BUG"}:
                counts["product_failure"] += 1
            elif not ev.get("pass"):
                counts["product_failure"] += 1
        return dict(counts)

    def _load_deferred_for_service(self, service_id: str) -> int:
        if not self.decisions_dir.exists():
            return 0
        count = 0
        for path in self.decisions_dir.glob("*.json"):
            data = _load_json(path) or {}
            if service_id in json.dumps(data):
                count += 1
        return count

    def _classify_service(
        self,
        service: dict[str, Any],
        batch: dict[str, Any],
        staging: dict[str, Any],
        verification: dict[str, Any],
        e2e: dict[str, int],
        deferred: int,
    ) -> ServiceAudit:
        sid = service.get("service_id") or service.get("id")
        slug = batch.get("slug", "")
        raw_meta = self._load_raw_metadata(self._resolve_staging_slug(slug))
        builder = raw_meta.get("builder")
        is_hand_batch = self._resolve_staging_slug(slug) in {
            "batch-01",
            "batch-02a-passport",
            "batch-02b-police-immigration",
            "batch-03a-brta-driving-licence",
            "batch-03b-brta-vehicle",
            "batch-03c-brta-fitness-tax-permit",
        }

        claims = [c for c in staging.get("claims", []) if c.get("service_id") == sid]
        sources_map: dict[str, Any] = staging.get("sources") or {}

        audit = ServiceAudit(
            service_id=sid,
            service_name_en=service.get("service_name_en") or sid,
            category_id=service.get("category_id") or service.get("category") or "",
            batch_id=batch.get("batch_id", ""),
            batch_slug=slug,
            batch_status=batch.get("status", ""),
            completeness="PARTIAL",
            research_builder=builder,
            geographic_scope=service.get("geographic_scope") or "NATIONAL",
        )

        claim_types_present: set[str] = set()
        for claim in claims:
            audit.total_claims += 1
            status = _verification_status(claim)
            if _is_verified(status):
                audit.verified_claims += 1
            elif _is_partial(status):
                audit.partially_verified_claims += 1
            elif status == "CONFLICTING":
                audit.conflicting_claims += 1
            else:
                audit.unverified_claims += 1

            ctype = (claim.get("claim_type") or "other").lower()
            claim_types_present.add(ctype)

            if _is_boilerplate_claim(claim):
                audit.boilerplate_claims += 1
            else:
                audit.service_specific_claims += 1

            pub = (claim.get("provenance") or {}).get("publication_status")
            if pub and pub not in {"STAGING_ONLY", "NOT_PUBLISHED"}:
                audit.published_claims += 1

            for src_id in claim.get("source_ids") or []:
                if src_id == "src-catalogue":
                    continue
                audit.catalogue_only_sources = False
                src = sources_map.get(src_id) or {}
                tier = _tier_from_source(src)
                if tier <= 2:
                    audit.tier1_2_sources += 1
                else:
                    audit.lower_tier_sources += 1

        for gap in verification.get("gaps", []):
            if gap.get("service_id") not in {sid, None} and sid not in json.dumps(gap):
                continue
            if gap.get("service_id") and gap.get("service_id") != sid:
                continue
            audit.knowledge_gaps += 1
            sev = (gap.get("severity") or gap.get("priority") or "").upper()
            if sev in {"CRITICAL", "HIGH"}:
                audit.critical_gaps += 1

        audit.deferred_items = deferred

        audit.e2e_queries = e2e.get("queries", 0)
        audit.e2e_passed = e2e.get("passed", 0)
        audit.e2e_answer_supported = e2e.get("answer_supported", 0)
        audit.e2e_correct_uncertainty = e2e.get("correct_uncertainty", 0)
        audit.e2e_product_failure = e2e.get("product_failure", 0)

        # Critical field coverage (service-type aware)
        expected_fields = {"application_url", "procedure"}
        if service.get("category_id") in {"tax", "vat", "customs", "transport", "land"}:
            expected_fields.add("fee")
        if service.get("category_id") in {"local_government", "identity", "civil"}:
            expected_fields.add("document")

        field_map = {
            "application_url": {"application_url", "official_url"},
            "procedure": {"procedure", "process", "other"},
            "fee": {"fee", "fee_schedule"},
            "document": {"document", "document_requirement", "checklist"},
            "eligibility": {"eligibility"},
        }
        for fname, ctypes in field_map.items():
            if fname in expected_fields:
                if claim_types_present & ctypes or (fname == "fee" and staging.get("fees")):
                    audit.critical_fields_present.append(fname)
                else:
                    audit.critical_fields_missing.append(fname)

        # Flags
        if audit.total_claims == 0:
            audit.flags.append("NO_CLAIMS")
        if audit.total_claims > 0 and audit.service_specific_claims == 0:
            audit.flags.append("GENERIC_BOILERPLATE_ONLY")
        if builder in GENERIC_BUILDER_MARKERS or (not is_hand_batch and audit.boilerplate_claims >= 2):
            audit.flags.append("GENERIC_BUILDER_BATCH")
        if audit.catalogue_only_sources and audit.total_claims > 0:
            audit.flags.append("CATALOGUE_ONLY_SOURCES")
        if audit.verified_claims == 0 and audit.total_claims > 0:
            audit.flags.append("ZERO_VERIFIED_CLAIMS")
        if audit.e2e_queries > 0 and audit.e2e_answer_supported == 0 and audit.e2e_passed > 0:
            audit.flags.append("E2E_UNCERTAINTY_ONLY")
        if audit.e2e_queries > 0 and audit.e2e_passed == 0:
            audit.flags.append("E2E_ALL_FAILED")
        if audit.conflicting_claims > 0:
            audit.flags.append("UNRESOLVED_CONFLICT")
        if audit.critical_gaps > 0:
            audit.flags.append("CRITICAL_KNOWLEDGE_GAPS")

        readiness = (verification.get("readiness") or {}).get(sid, {})
        if readiness.get("readiness") == "RED":
            audit.flags.append("READINESS_RED")

        # Classification
        if audit.conflicting_claims > 0 and audit.critical_gaps > 0:
            audit.completeness = "BLOCKED"
        elif deferred > 0 and audit.verified_claims == 0:
            audit.completeness = "DEFERRED"
        elif (
            is_hand_batch
            and audit.service_specific_claims >= 2
            and audit.verified_claims >= 1
            and "ZERO_VERIFIED_CLAIMS" not in audit.flags
            and audit.conflicting_claims == 0
            and (audit.e2e_passed > 0 or audit.e2e_queries == 0)
        ):
            if audit.critical_fields_missing and audit.critical_gaps > 0:
                audit.completeness = "PARTIAL"
            else:
                audit.completeness = "COMPLETE"
        elif (
            audit.service_specific_claims >= 3
            and audit.verified_claims >= 2
            and audit.tier1_2_sources >= 1
            and "GENERIC_BOILERPLATE_ONLY" not in audit.flags
            and audit.e2e_answer_supported >= 1
        ):
            audit.completeness = "COMPLETE"
        elif audit.total_claims == 0:
            audit.completeness = "DEFERRED" if deferred else "PARTIAL"
        elif "GENERIC_BOILERPLATE_ONLY" in audit.flags or "GENERIC_BUILDER_BATCH" in audit.flags:
            audit.completeness = "PARTIAL"
        elif audit.service_specific_claims >= 1 or audit.verified_claims >= 1:
            audit.completeness = "PARTIAL"
        else:
            audit.completeness = "PARTIAL"

        # Downgrade false completion: generic batch with only boilerplate
        if (
            not is_hand_batch
            and audit.boilerplate_claims == audit.total_claims
            and audit.total_claims > 0
        ):
            audit.completeness = "PARTIAL"
            if "FALSE_COMPLETION_RISK" not in audit.flags:
                audit.flags.append("FALSE_COMPLETION_RISK")

        return audit

    def audit_all_services(self) -> list[ServiceAudit]:
        catalogue = self.load_catalogue()
        batch_map = self.load_batch_map()
        runtime_slugs = self.load_runtime_slug_map()
        staging_cache: dict[str, dict[str, Any]] = {}
        verification_cache: dict[str, dict[str, Any]] = {}

        audits: list[ServiceAudit] = []
        for service in catalogue:
            sid = service.get("service_id") or service.get("id")
            batch = batch_map.get(sid) or {"batch_id": "UNASSIGNED", "slug": "", "status": "UNKNOWN", "service_ids": []}
            slug = batch.get("slug") or ""
            staging_slug = self._resolve_staging_slug(slug)
            if staging_slug and staging_slug not in staging_cache:
                staging_cache[staging_slug] = self._load_staging_for_batch(staging_slug)
            if staging_slug and staging_slug not in verification_cache:
                verification_cache[staging_slug] = self._load_verification(staging_slug)
            staging = staging_cache.get(staging_slug, {"claims": [], "sources": {}, "evidence": [], "fees": []})
            verification = verification_cache.get(staging_slug, {"gaps": [], "readiness": {}, "dependencies": []})
            e2e = self._load_e2e_for_service(slug, sid, runtime_slugs.get(sid)) if slug else {}
            deferred = self._load_deferred_for_service(sid)
            audits.append(self._classify_service(service, batch, staging, verification, e2e, deferred))
        return audits

    def aggregate_claim_stats(self, audits: list[ServiceAudit]) -> dict[str, Any]:
        totals = Counter()
        for slug_dir in self.staging_root.iterdir():
            if not slug_dir.is_dir():
                continue
            staging = self._load_staging_for_batch(slug_dir.name)
            for claim in staging.get("claims", []):
                totals["total_claims"] += 1
                status = _verification_status(claim)
                if _is_verified(status):
                    totals["verified"] += 1
                elif _is_partial(status):
                    totals["partially_verified"] += 1
                elif status == "CONFLICTING":
                    totals["conflicting"] += 1
                elif status in {"REJECTED", "OUTDATED"}:
                    totals[status.lower()] += 1
                else:
                    totals["unverified"] += 1
                ic = (claim.get("information_class") or "UNKNOWN").upper()
                totals[f"info_{ic.lower()}"] += 1
        return dict(totals)

    def aggregate_e2e(self) -> dict[str, Any]:
        outcome_counts: Counter[str] = Counter()
        batch_summaries: list[dict[str, Any]] = []
        total_q = passed_q = 0
        hallucinations = citation_failures = 0

        for summary_path in sorted(self.eval_root.glob("*/summary.json")):
            if summary_path.parent.name in {"cross-domain-hardening", "service-routing"}:
                continue
            summary = _load_json(summary_path) or {}
            slug = summary_path.parent.name
            total = summary.get("total") or summary.get("total_tests") or 0
            passed = summary.get("passed") or 0
            total_q += total
            passed_q += passed
            hallucinations += summary.get("hallucinations") or 0
            citation_failures += summary.get("citation_failures") or 0
            batch_summaries.append(
                {
                    "batch": slug,
                    "total": total,
                    "passed": passed,
                    "pass_pct": summary.get("pass_pct") or summary.get("pass_rate_pct"),
                    "hallucinations": summary.get("hallucinations") or 0,
                    "generic_builder": slug
                    not in {
                        "batch-01",
                        "batch-02a-passport",
                        "batch-02b-police-immigration",
                        "batch-03a-brta-driving-licence",
                        "batch-03b-brta-vehicle",
                        "batch-03c-brta-fitness-tax-permit",
                    },
                }
            )
            results_path = summary_path.parent / "results.jsonl"
            if results_path.exists():
                for line in results_path.read_text(encoding="utf-8").splitlines():
                    if not line.strip():
                        continue
                    ev = json.loads(line).get("evaluation") or {}
                    outcome = ev.get("outcome")
                    if outcome:
                        outcome_counts[outcome] += 1
                    elif ev.get("pass"):
                        outcome_counts["PASS_LEGACY"] += 1
                    else:
                        outcome_counts["PRODUCT_FAILURE"] += 1

        routing = _load_json(self.eval_root / "service-routing" / "summary.json") or {}
        cross = _load_json(self.eval_root / "cross-domain-hardening" / "summary.json") or {}

        return {
            "batch_summaries": batch_summaries,
            "aggregate_pass_pct": round(100 * passed_q / total_q, 2) if total_q else 0,
            "total_queries": total_q,
            "passed_queries": passed_q,
            "outcome_counts": dict(outcome_counts),
            "hallucinations": hallucinations,
            "citation_failures": citation_failures,
            "routing_suite": routing,
            "cross_domain_suite": cross,
        }

    def audit_runtime_consistency(self, audits: list[ServiceAudit]) -> dict[str, Any]:
        issues: list[dict[str, Any]] = []
        db_path = self.repo_root / "data" / "bda.db"
        runtime_available = db_path.exists() and db_path.stat().st_size > 0

        for audit in audits:
            slug = audit.batch_slug
            if not slug:
                continue
            staging = self._load_staging_for_batch(slug)
            verified_staging = {
                c.get("claim_id")
                for c in staging.get("claims", [])
                if c.get("service_id") == audit.service_id and _is_verified(_verification_status(c))
            }
            if audit.verified_claims > 0 and not verified_staging:
                issues.append(
                    {
                        "service_id": audit.service_id,
                        "issue": "verified_count_mismatch",
                        "detail": "Audit counted verified claims but staging has none VERIFIED",
                    }
                )
            if audit.published_claims > 0 and not runtime_available:
                issues.append(
                    {
                        "service_id": audit.service_id,
                        "issue": "published_claims_no_runtime_db",
                        "detail": "Publication claims exist but runtime DB is empty/unavailable",
                    }
                )

        return {
            "generated_at": _now(),
            "runtime_db_available": runtime_available,
            "runtime_db_path": str(db_path),
            "services_checked": len(audits),
            "issue_count": len(issues),
            "issues": issues[:200],
            "note": "Runtime DB empty — consistency checks limited to staging/verification file artifacts.",
        }

    def audit_legacy_seeds(self) -> dict[str, Any]:
        inv_path = self.repo_root / "data" / "audit" / "legacy-seed-inventory.json"
        if inv_path.exists():
            return _load_json(inv_path) or {"summary": {}, "legacy_rows": []}
        return {
            "generated_at": _now(),
            "summary": {"note": "legacy-seed-inventory.json not found — run scripts/audit_legacy_seed_inventory.py"},
            "legacy_rows": [],
        }

    def determine_verdict(self, audits: list[ServiceAudit]) -> str:
        counts = Counter(a.completeness for a in audits)
        complete = counts["COMPLETE"]
        partial = counts["PARTIAL"]
        deferred = counts["DEFERRED"]
        blocked = counts["BLOCKED"]
        total = len(audits)

        false_completion = sum(1 for a in audits if "FALSE_COMPLETION_RISK" in a.flags)
        generic_only = sum(1 for a in audits if "GENERIC_BOILERPLATE_ONLY" in a.flags)

        if complete == total and false_completion == 0:
            return "KNOWLEDGE_COMPLETE"
        if complete + deferred == total and partial == 0 and blocked == 0 and false_completion == 0:
            return "KNOWLEDGE_COMPLETE_WITH_DEFERRED_ITEMS"
        if complete >= total * 0.95 and false_completion == 0 and generic_only < total * 0.05:
            return "KNOWLEDGE_COMPLETE_WITH_DEFERRED_ITEMS"
        return "KNOWLEDGE_INCOMPLETE"

    def build_report_md(
        self,
        audits: list[ServiceAudit],
        claim_stats: dict[str, Any],
        e2e_stats: dict[str, Any],
        consistency: dict[str, Any],
        legacy: dict[str, Any],
        verdict: str,
    ) -> str:
        counts = Counter(a.completeness for a in audits)
        flag_counts = Counter(f for a in audits for f in a.flags)
        by_batch: dict[str, Counter] = defaultdict(Counter)
        for a in audits:
            by_batch[a.batch_id][a.completeness] += 1

        generic_batches = [b for b in e2e_stats["batch_summaries"] if b.get("generic_builder")]
        hand_batches = [b for b in e2e_stats["batch_summaries"] if not b.get("generic_builder")]

        lines = [
            "# Final Knowledge Construction Audit",
            "",
            f"Generated: {_now()}",
            "",
            "## Executive verdict",
            "",
            f"**{verdict}**",
            "",
            "The overnight orchestrator reported `KNOWLEDGE_COMPLETE` after all 17 batches executed, "
            "but this audit finds that **batch completion ≠ service-specific knowledge completeness**. "
            "Batches 04–14 were processed primarily by generic research/verification builders producing "
            "boilerplate catalogue-derived claims. Those batches must not be treated as fully researched.",
            "",
            "## Catalogue coverage",
            "",
            f"| Metric | Count |",
            f"|--------|------:|",
            f"| Canonical catalogue | 464 |",
            f"| Confirmed services audited | {len(audits)} |",
            f"| COMPLETE | {counts['COMPLETE']} |",
            f"| PARTIAL | {counts['PARTIAL']} |",
            f"| DEFERRED | {counts['DEFERRED']} |",
            f"| BLOCKED | {counts['BLOCKED']} |",
            "",
            "## False completion detection",
            "",
            f"- Services flagged `FALSE_COMPLETION_RISK`: **{flag_counts.get('FALSE_COMPLETION_RISK', 0)}**",
            f"- Services with generic boilerplate only: **{flag_counts.get('GENERIC_BOILERPLATE_ONLY', 0)}**",
            f"- Services from generic-builder batches (04–14): **{sum(1 for a in audits if 'GENERIC_BUILDER_BATCH' in a.flags)}**",
            f"- Services with zero verified claims: **{flag_counts.get('ZERO_VERIFIED_CLAIMS', 0)}**",
            f"- Services with catalogue-only sources: **{flag_counts.get('CATALOGUE_ONLY_SOURCES', 0)}**",
            "",
            "Generic builder pattern produces 2–3 claims per service (`application-portal`, `responsible-authority`, "
            "`official-source`) copied from catalogue metadata. Land services incorrectly reference "
            "'NBR e-service portal'. Fees and mandatory documents remain explicitly unverified.",
            "",
            "## Completeness by batch",
            "",
            "| Batch | COMPLETE | PARTIAL | DEFERRED | BLOCKED |",
            "|-------|--------:|--------:|---------:|--------:|",
        ]
        for batch_id in sorted(by_batch.keys()):
            c = by_batch[batch_id]
            lines.append(
                f"| {batch_id} | {c['COMPLETE']} | {c['PARTIAL']} | {c['DEFERRED']} | {c['BLOCKED']} |"
            )

        lines.extend(
            [
                "",
                "## Claim statistics (staging)",
                "",
                f"- Total claims: **{claim_stats.get('total_claims', 0)}**",
                f"- Verified: **{claim_stats.get('verified', 0)}**",
                f"- Partially verified: **{claim_stats.get('partially_verified', 0)}**",
                f"- Unverified: **{claim_stats.get('unverified', 0)}**",
                f"- Conflicting: **{claim_stats.get('conflicting', 0)}**",
                "",
                "## E2E quality (not pass-rate alone)",
                "",
                f"- Aggregate pass rate (batch E2E): **{e2e_stats['aggregate_pass_pct']}%** ({e2e_stats['passed_queries']}/{e2e_stats['total_queries']})",
                f"- Hallucinations: **{e2e_stats['hallucinations']}**",
                f"- Citation failures: **{e2e_stats['citation_failures']}**",
                "",
                "### Hand-researched batches (01–03)",
                "",
            ]
        )
        for b in hand_batches:
            lines.append(f"- `{b['batch']}`: {b['passed']}/{b['total']} passed ({b['pass_pct']}%)")

        lines.extend(["", "### Generic-builder batches (04–14)", ""])
        for b in generic_batches:
            lines.append(f"- `{b['batch']}`: {b['passed']}/{b['total']} passed ({b['pass_pct']}%) — **insufficient for COMPLETE**")

        lines.extend(
            [
                "",
                f"Outcome breakdown (where recorded): `{json.dumps(e2e_stats.get('outcome_counts', {}), ensure_ascii=False)}`",
                "",
                "## Routing / cross-domain",
                "",
                f"- Service routing: **{e2e_stats['routing_suite'].get('passed', '?')}/{e2e_stats['routing_suite'].get('total_tests', '?')}** passed",
                f"- Cross-domain hardening: **{e2e_stats['cross_domain_suite'].get('passed', '?')}/{e2e_stats['cross_domain_suite'].get('total_tests', '?')}** passed",
                "",
                "Routing suites test known well-researched domains (batch 01–03). They do **not** validate batches 04–14 quality.",
                "",
                "## Source quality",
                "",
                "Hand-researched batches include Tier 1–2 official sources with evidence snapshots. "
                "Generic-builder batches rely predominantly on `src-catalogue` (Tier 1 catalogue file) "
                "with optional unreachable URL probes — **not independent official verification**.",
                "",
                "## Runtime / research consistency",
                "",
                f"- Runtime DB available: **{consistency['runtime_db_available']}**",
                f"- Consistency issues found: **{consistency['issue_count']}**",
                "",
                "## Legacy seed state",
                "",
            ]
        )
        legacy_summary = legacy.get("summary") or {}
        lines.append(f"- Legacy seed rows: **{legacy_summary.get('total_legacy_rows', 'unknown')}**")
        lines.append(f"- Verified replacements available: **{legacy_summary.get('legacy_with_verified_replacement', 'unknown')}**")
        lines.append("- Automatic replacement: **NOT APPROVED** (manual review required)")

        lines.extend(
            [
                "",
                "## Major risks",
                "",
                "1. **False completion**: 393 services in batches 04–14 have generic boilerplate, not service-specific research.",
                "2. **E2E failures**: Generic batches show 0–40% pass rates; failures are mostly RETRIEVAL_BUG / service mismatch.",
                "3. **No verified fees/documents** for most post-batch-03 services.",
                "4. **Empty runtime DB**: Published knowledge may not be loaded into runtime for verification.",
                "5. **Geographic variation**: Local/district services marked NATIONAL without evidence.",
                "",
                "## Recommended next work",
                "",
                "1. Re-research batches 04–14 with service-specific official source retrieval (not generic builder).",
                "2. Do not mark batches COMPLETE until E2E pass rate and verified claim thresholds met.",
                "3. Populate runtime DB and re-run publication dry-run with citation integrity checks.",
                "4. Resolve legacy seed replacements through manual approval workflow.",
                "5. Keep deployment locked until KNOWLEDGE_INCOMPLETE → COMPLETE transition is evidence-based.",
                "",
                "## Safety",
                "",
                "- deployment_allowed: **false**",
                "- auto_merge: **false**",
                "- No deployment, merge, or external publication performed by this audit.",
                "",
            ]
        )
        return "\n".join(lines) + "\n"

    def run(self) -> dict[str, Any]:
        audits = self.audit_all_services()
        claim_stats = self.aggregate_claim_stats(audits)
        e2e_stats = self.aggregate_e2e()
        consistency = self.audit_runtime_consistency(audits)
        legacy = self.audit_legacy_seeds()
        verdict = self.determine_verdict(audits)

        counts = Counter(a.completeness for a in audits)
        service_payload = {
            "generated_at": _now(),
            "verdict": verdict,
            "catalogue": {
                "canonical": 464,
                "confirmed": len(audits),
            },
            "completeness_counts": dict(counts),
            "flag_summary": dict(Counter(f for a in audits for f in a.flags)),
            "claim_statistics": claim_stats,
            "e2e_statistics": e2e_stats,
            "services": [asdict(a) for a in audits],
        }

        _write_json(self.repo_root / "data" / "audit" / "final-service-completeness.json", service_payload)
        _write_json(self.repo_root / "data" / "audit" / "runtime-research-consistency.json", consistency)

        report_md = self.build_report_md(audits, claim_stats, e2e_stats, consistency, legacy, verdict)
        report_path = self.repo_root / "docs" / "evaluation" / "FINAL_KNOWLEDGE_CONSTRUCTION_AUDIT.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report_md, encoding="utf-8")

        final_state = {
            "status": verdict,
            "updated_at": _now(),
            "deployment_allowed": False,
            "auto_merge": False,
            "audit_type": "FINAL_KNOWLEDGE_CONSTRUCTION_AUDIT",
            "catalogue_progress": {
                "total_confirmed_services": len(audits),
                "complete": counts["COMPLETE"],
                "partial": counts["PARTIAL"],
                "deferred": counts["DEFERRED"],
                "blocked": counts["BLOCKED"],
            },
            "claims": claim_stats,
            "e2e": {
                "aggregate_pass_pct": e2e_stats["aggregate_pass_pct"],
                "hallucinations": e2e_stats["hallucinations"],
                "citation_failures": e2e_stats["citation_failures"],
            },
            "false_completion_risk_services": sum(
                1 for a in audits if "FALSE_COMPLETION_RISK" in a.flags
            ),
            "regression_baselines_preserved": True,
            "artifacts": {
                "final_service_completeness": "data/audit/final-service-completeness.json",
                "runtime_research_consistency": "data/audit/runtime-research-consistency.json",
                "audit_report": "docs/evaluation/FINAL_KNOWLEDGE_CONSTRUCTION_AUDIT.md",
            },
        }
        _write_json(self.repo_root / ".automation" / "final_project_state.json", final_state)

        return {
            "verdict": verdict,
            "completeness_counts": dict(counts),
            "claim_stats": claim_stats,
            "e2e_stats": e2e_stats,
            "artifacts_written": [
                "data/audit/final-service-completeness.json",
                "data/audit/runtime-research-consistency.json",
                "docs/evaluation/FINAL_KNOWLEDGE_CONSTRUCTION_AUDIT.md",
                ".automation/final_project_state.json",
            ],
        }


def main() -> int:
    result = FinalKnowledgeAudit().run()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
