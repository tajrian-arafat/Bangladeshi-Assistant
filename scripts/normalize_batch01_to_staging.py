#!/usr/bin/env python3
"""Normalize Batch 1 discovery dump into research/staging provenance chain.

IMPORTANT:
- Does NOT write to the runtime database.
- Does NOT emit pipeline_status=VERIFIED (verification phase has not run).
- Demotes premature VERIFIED labels from the discovery dump.
- Leaves data/seeds and backend models untouched.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / "data" / "knowledge" / "batch-01"
RAW_OUT = ROOT / "data" / "research" / "raw" / "batch-01"
STAGING = ROOT / "data" / "research" / "staging" / "batch-01"
TODAY = date.today().isoformat()

# Claim statuses that may appear in discovery dumps (legacy).
# Target statuses are the pipeline states required by the guardrail.


def _domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def demote_claim_status(
    legacy_status: str | None,
    *,
    authority_tier: int | None,
    information_class: str,
    has_excerpt: bool,
    in_conflict: bool,
    needs_manual: bool,
) -> str:
    """Never return VERIFIED — verification phase has not run."""
    if in_conflict:
        return "CONFLICTING"
    if needs_manual:
        return "PENDING_REVIEW"

    tier = authority_tier or 7
    info = (information_class or "DISCOVERY").upper()
    legacy = (legacy_status or "UNVERIFIED").upper()

    # Practical / community never advances past EXTRACTED in research phase.
    if info == "PRACTICAL" or tier >= 5:
        return "EXTRACTED" if has_excerpt or legacy in {"VERIFIED", "UNVERIFIED"} else "DISCOVERED"

    if info == "DISCOVERY":
        return "DISCOVERED"

    # OFFICIAL path during research only
    if legacy == "UNVERIFIED":
        return "PENDING_REVIEW" if tier <= 2 else "DISCOVERED"

    # Was incorrectly labeled VERIFIED in discovery dump
    if has_excerpt and tier <= 2:
        return "CROSS_CHECKED"
    if tier <= 2:
        return "NORMALIZED"
    if has_excerpt:
        return "EXTRACTED"
    return "DISCOVERED"


def confidence_for(status: str, tier: int | None, information_class: str) -> float:
    base = {
        "DISCOVERED": 0.25,
        "EXTRACTED": 0.4,
        "NORMALIZED": 0.55,
        "CROSS_CHECKED": 0.7,
        "PENDING_REVIEW": 0.5,
        "CONFLICTING": 0.35,
        "OUTDATED": 0.2,
        "REJECTED": 0.0,
        "VERIFIED": 0.9,  # should not appear; defensive
    }.get(status, 0.3)
    if (information_class or "").upper() == "PRACTICAL":
        base = min(base, 0.45)
    if tier and tier <= 2 and status in {"NORMALIZED", "CROSS_CHECKED"}:
        base = min(0.75, base + 0.05)
    return round(base, 2)


def main() -> None:
    if not LEGACY.exists():
        raise SystemExit(f"Missing legacy discovery dump: {LEGACY}")

    # Preserve raw discovery dump unchanged for audit.
    RAW_OUT.parent.mkdir(parents=True, exist_ok=True)
    if RAW_OUT.exists():
        shutil.rmtree(RAW_OUT)
    shutil.copytree(LEGACY, RAW_OUT)

    sources_in = json.loads((LEGACY / "sources.json").read_text(encoding="utf-8"))["sources"]
    claims_in = json.loads((LEGACY / "claims.json").read_text(encoding="utf-8"))["claims"]
    conflicts_in = json.loads((LEGACY / "conflicts.json").read_text(encoding="utf-8"))["conflicts"]
    meta_in = json.loads((LEGACY / "metadata.json").read_text(encoding="utf-8"))
    index_in = json.loads((LEGACY / "services_index.json").read_text(encoding="utf-8"))["services"]

    conflict_claim_ids: set[str] = set()
    for c in conflicts_in:
        # Prefer linking by service; claim IDs may not be listed — flag fee-related claims later.
        pass

    # Build sources + source_versions
    sources_out: list[dict[str, Any]] = []
    versions_out: list[dict[str, Any]] = []
    source_by_id: dict[str, dict[str, Any]] = {}
    version_by_source: dict[str, str] = {}

    for s in sources_in:
        sid = s["source_id"]
        url = s["source_url"]
        source_row = {
            "source_id": sid,
            "domain": _domain(url),
            "source_url": url,
            "source_title": s.get("source_title"),
            "source_type": s.get("source_type"),
            "authority_tier": s.get("authority_tier"),
            "responsible_body": s.get("responsible_body"),
            "published_date": s.get("published_date"),
            "language": s.get("language"),
            "retrieved_at": s.get("retrieved_at") or TODAY,
            "runtime_mapped": False,
            "notes": "Research staging only; not inserted into sources table.",
        }
        sources_out.append(source_row)
        source_by_id[sid] = source_row

        # Content hash intentionally null — raw HTML/PDF body was not archived this pass.
        svid = f"sv-{sid}"
        version_by_source[sid] = svid
        versions_out.append(
            {
                "source_version_id": svid,
                "source_id": sid,
                "url": url,
                "content_hash": None,
                "retrieved_at": s.get("retrieved_at") or TODAY,
                "fetched_method": "manual_research_fetch",
                "http_status": None,
                "raw_pointer": None,
                "is_published": False,
                "notes": (
                    "No durable SourceVersion body/hash captured. "
                    "Required before VERIFIED publication."
                ),
            }
        )

    # Conflict topics by service for demotion
    conflict_services = {c.get("service_id") for c in conflicts_in if c.get("service_id")}
    conflict_topics = {(c.get("service_id"), c.get("topic", "").lower()) for c in conflicts_in}

    evidence_out: list[dict[str, Any]] = []
    claims_out: list[dict[str, Any]] = []
    status_counts: Counter[str] = Counter()
    demotion_log: list[dict[str, Any]] = []

    # Index claims that appear in conflict narratives (fee-related heuristics)
    conflicting_claim_ids: set[str] = set()
    for c in claims_in:
        text = (c.get("claim") or "").lower()
        sid = c.get("service_id")
        if sid in conflict_services and any(
            k in text for k in ("fee", "bdt", "500", "230", "345", "460", "100", "50")
        ):
            # Only mark if topic matches roughly
            for svc, topic in conflict_topics:
                if svc == sid and ("fee" in topic or "amount" in topic):
                    conflicting_claim_ids.add(c["claim_id"])
                    break

    # Also mark the explicit conflict claim
    for c in claims_in:
        if "conflict" in (c.get("claim_id") or "") or "conflict" in (c.get("claim") or "").lower():
            if "500" in (c.get("claim") or "") or "conflicts" in (c.get("claim") or "").lower():
                conflicting_claim_ids.add(c["claim_id"])

    for c in claims_in:
        claim_id = c["claim_id"]
        # Ensure unique claim ids across services in staging
        staging_claim_id = f"{c.get('service_id', 'unknown')}::{claim_id}"

        source_ids = c.get("source_ids") or ([] if not c.get("source_id") else [c["source_id"]])
        if c.get("source_id") and c["source_id"] not in source_ids:
            source_ids = [c["source_id"], *source_ids]

        primary_source = source_ids[0] if source_ids else None
        tier = None
        if primary_source and primary_source in source_by_id:
            tier = source_by_id[primary_source].get("authority_tier")

        info_class = (c.get("information_class") or c.get("layer") or "OFFICIAL").upper()
        if info_class not in {"OFFICIAL", "PRACTICAL", "DISCOVERY"}:
            # Map legacy layers
            if info_class in {"PRACTICAL"}:
                pass
            elif "PRACTICAL" in info_class:
                info_class = "PRACTICAL"
            else:
                info_class = "OFFICIAL"

        excerpt = c.get("evidence_excerpt")
        has_excerpt = bool(excerpt and str(excerpt).strip())
        in_conflict = claim_id in conflicting_claim_ids or staging_claim_id in conflicting_claim_ids
        needs_manual = bool(c.get("requires_manual_verification")) or (
            (c.get("verification_status") or "").upper() == "UNVERIFIED"
            and info_class == "OFFICIAL"
            and (tier or 99) <= 2
            and "fee" in (c.get("claim") or "").lower()
        )

        legacy_status = c.get("verification_status")
        new_status = demote_claim_status(
            legacy_status,
            authority_tier=tier,
            information_class=info_class,
            has_excerpt=has_excerpt,
            in_conflict=in_conflict,
            needs_manual=needs_manual and not in_conflict,
        )
        status_counts[new_status] += 1

        if (legacy_status or "").upper() == "VERIFIED":
            demotion_log.append(
                {
                    "claim_id": staging_claim_id,
                    "legacy_status": "VERIFIED",
                    "new_pipeline_status": new_status,
                    "reason": (
                        "Discovery-phase VERIFIED label demoted; "
                        "dedicated verification/publication phase has not run."
                    ),
                }
            )

        evidence_ids: list[str] = []
        for src_id in source_ids:
            svid = version_by_source.get(src_id)
            if not svid:
                continue
            eid = f"ev-{staging_claim_id}-{src_id}"
            # sanitize id
            eid = eid.replace(" ", "_")[:180]
            evidence_ids.append(eid)
            evidence_out.append(
                {
                    "evidence_id": eid,
                    "source_version_id": svid,
                    "claim_id": staging_claim_id,
                    "summary": (c.get("claim") or "")[:280],
                    "excerpt": excerpt if src_id == primary_source else None,
                    "locator": None,
                    "language": source_by_id.get(src_id, {}).get("language"),
                    "captured_at": source_by_id.get(src_id, {}).get("retrieved_at") or TODAY,
                    "strength": "WEAK" if not (excerpt and src_id == primary_source) else "MODERATE",
                    "notes": (
                        None
                        if excerpt and src_id == primary_source
                        else "Excerpt missing or not captured for this source version."
                    ),
                }
            )

        claims_out.append(
            {
                "claim_id": staging_claim_id,
                "legacy_claim_id": claim_id,
                "service_id": c.get("service_id"),
                "claim_text": c.get("claim"),
                "claim_type": c.get("claim_type") or "other",
                "information_class": info_class,
                "pipeline_status": new_status,
                "confidence": confidence_for(new_status, tier, info_class),
                "evidence_ids": evidence_ids,
                "source_ids": source_ids,
                "source_version_ids": [version_by_source[s] for s in source_ids if s in version_by_source],
                "legacy_verification_status": legacy_status,
                "do_not_promote_to_must": bool(c.get("do_not_promote_to_must"))
                or info_class == "PRACTICAL",
                "provenance": {
                    "batch_id": "batch-01-identity-civil-registration",
                    "discovered_at": TODAY,
                    "normalized_at": TODAY,
                    "raw_pointer": f"data/research/raw/batch-01/claims.json#{claim_id}",
                    "verifier_id": None,
                    "verified_at": None,
                    "publication_status": "STAGING_ONLY",
                },
            }
        )

    # Service bindings from legacy service packs
    services_out: list[dict[str, Any]] = []
    requirements_out: list[dict[str, Any]] = []
    fees_out: list[dict[str, Any]] = []
    procedures_out: list[dict[str, Any]] = []

    for svc_meta in index_in:
        sid = svc_meta["service_id"]
        path = LEGACY / "services" / f"{sid}.json"
        pack = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

        manual = pack.get("manual_review_required") or []
        missing = pack.get("missing_information") or []
        svc_conflicts = [c for c in conflicts_in if c.get("service_id") == sid]

        if svc_conflicts:
            svc_pipeline = "CONFLICTING"
        elif manual:
            svc_pipeline = "PENDING_REVIEW"
        elif (svc_meta.get("research_status") or "").upper() == "SUBSTANTIAL":
            svc_pipeline = "CROSS_CHECKED"
        else:
            svc_pipeline = "NORMALIZED"

        services_out.append(
            {
                "service_id": sid,
                "catalogue_status": "CONFIRMED",
                "research_depth": svc_meta.get("research_status"),
                "pipeline_status": svc_pipeline,
                "publication_status": "STAGING_ONLY",
                "knowledge_quality_research_only": svc_meta.get("kqs"),
                "kqs_disclaimer": (
                    "Research-phase completeness heuristic only. "
                    "Not a publication readiness score. Not runtime confidence."
                ),
                "official_application_url": pack.get("official_application_url"),
                "official_information_urls": pack.get("official_information_urls"),
                "missing_information": missing,
                "manual_review_required": manual,
                "runtime_service_row": None,
                "notes": (
                    "Not written to services table. "
                    "MVP seed rows (if any) must not be overwritten by this pack."
                ),
            }
        )

        for i, req in enumerate(pack.get("requirements") or []):
            # Remap claim ids to staging ids
            claim_ids = [
                f"{sid}::{cid}" if "::" not in cid else cid for cid in (req.get("claim_ids") or [])
            ]
            classification = req.get("classification") or "MUST"
            # Guard: practical-linked requirements cannot be MUST for publication
            linked = [cl for cl in claims_out if cl["claim_id"] in claim_ids]
            if any(cl["do_not_promote_to_must"] for cl in linked) and classification == "MUST":
                classification = "RECOMMENDED"
            req_status = "PENDING_REVIEW" if manual else "NORMALIZED"
            if any(cl["pipeline_status"] == "CONFLICTING" for cl in linked):
                req_status = "CONFLICTING"
            requirements_out.append(
                {
                    "requirement_id": f"{sid}::{req.get('requirement_id', i)}",
                    "service_id": sid,
                    "name_en": req.get("name_en"),
                    "name_bn": req.get("name_bn"),
                    "classification": classification,
                    "condition": req.get("condition"),
                    "claim_ids": claim_ids,
                    "pipeline_status": req_status,
                    "publication_status": "STAGING_ONLY",
                    "maps_toward_runtime": "checklist_items",
                }
            )

        for i, fee in enumerate(pack.get("fees") or []):
            claim_ids = [
                f"{sid}::{cid}" if "::" not in cid else cid for cid in (fee.get("claim_ids") or [])
            ]
            linked = [cl for cl in claims_out if cl["claim_id"] in claim_ids]
            fee_status = (fee.get("verification_status") or "UNVERIFIED").upper()
            # Demote fee-level VERIFIED
            pipeline = "CONFLICTING" if any(
                cl["pipeline_status"] == "CONFLICTING" for cl in linked
            ) else (
                "CROSS_CHECKED"
                if fee_status == "VERIFIED"
                else "PENDING_REVIEW"
                if fee_status == "UNVERIFIED"
                else "NORMALIZED"
            )
            fees_out.append(
                {
                    "fee_id": f"{sid}::{fee.get('fee_id', i)}",
                    "service_id": sid,
                    "description": fee.get("description"),
                    "amount": fee.get("amount"),
                    "currency": fee.get("currency", "BDT"),
                    "condition": fee.get("condition"),
                    "claim_ids": claim_ids,
                    "pipeline_status": pipeline,
                    "legacy_verification_status": fee.get("verification_status"),
                    "publication_status": "STAGING_ONLY",
                    "maps_toward_runtime": "fees",
                    "warning": (
                        "Amount must not populate runtime Fee.amount until VERIFIED "
                        "and conflict-free."
                    ),
                }
            )

        steps = pack.get("procedure_steps") or pack.get("application_steps") or []
        for i, step in enumerate(steps):
            if isinstance(step, str):
                step = {"title_en": step, "order": i + 1}
            claim_ids = [
                f"{sid}::{cid}" if "::" not in cid else cid
                for cid in (step.get("claim_ids") or [])
            ]
            procedures_out.append(
                {
                    "step_id": f"{sid}::step-{step.get('order', i + 1)}",
                    "service_id": sid,
                    "order": step.get("order", i + 1),
                    "title_en": step.get("title_en") or step.get("title") or step.get("text"),
                    "title_bn": step.get("title_bn"),
                    "claim_ids": claim_ids,
                    "pipeline_status": "NORMALIZED" if claim_ids else "DISCOVERED",
                    "publication_status": "STAGING_ONLY",
                    "maps_toward_runtime": "procedure_steps",
                }
            )

    conflicts_out = []
    for c in conflicts_in:
        conflicts_out.append(
            {
                **c,
                "pipeline_status": "CONFLICTING",
                "resolution": c.get("resolution")
                if str(c.get("resolution", "")).startswith("UNRESOLVED")
                or c.get("resolution") == "UNRESOLVED"
                else c.get("resolution") or "UNRESOLVED",
                "publication_status": "STAGING_ONLY",
                "blocks_official_publication": True,
            }
        )

    STAGING.mkdir(parents=True, exist_ok=True)

    def dump(name: str, obj: Any) -> None:
        (STAGING / name).write_text(
            json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    dump("sources.json", {"sources": sources_out})
    dump("source_versions.json", {"source_versions": versions_out})
    dump("evidence.json", {"evidence": evidence_out})
    dump("claims.json", {"claims": claims_out})
    dump("services.json", {"services": services_out})
    dump("requirements.json", {"requirements": requirements_out})
    dump("fees.json", {"fees": fees_out})
    dump("procedure_steps.json", {"procedure_steps": procedures_out})
    dump("conflicts.json", {"conflicts": conflicts_out})
    dump(
        "demotion_log.json",
        {
            "rule": "No discovery-phase VERIFIED survives into staging.",
            "demotions": demotion_log,
            "count": len(demotion_log),
        },
    )

    # Runtime gap register
    dump(
        "runtime_gap_register.json",
        {
            "inspected_at": TODAY,
            "runtime_models_path": "backend/app/domain/models/knowledge.py",
            "present_reusable": [
                "Agency",
                "Service",
                "Procedure",
                "ProcedureStep",
                "ChecklistItem",
                "ChecklistCondition",
                "Fee",
                "Form",
                "ServiceLink",
                "ServiceOffice",
                "Source",
                "SourceVersion",
                "KnowledgeDocument",
                "KnowledgeChunk",
            ],
            "missing_for_provenance_chain": [
                {
                    "concept": "Claim",
                    "status": "MISSING",
                    "impact": "Cannot store atomic verified facts in DB",
                },
                {
                    "concept": "ClaimEvidence",
                    "status": "MISSING",
                    "impact": "Evidence links only exist as JSON staging / orphan evidence_ids",
                },
                {
                    "concept": "KnowledgeGap",
                    "status": "MISSING",
                    "impact": "Gaps tracked only in research JSON",
                },
                {
                    "concept": "Claim pipeline_status enum",
                    "status": "MISSING",
                    "impact": "backend/app/domain/enums.py has ServiceStatus/ReviewState only",
                },
                {
                    "concept": "Durable SourceVersion content_hash/body",
                    "status": "TABLE_EXISTS_BUT_EMPTY",
                    "impact": "Staging versions have null content_hash; cannot prove freshness",
                },
                {
                    "concept": "Research→DB loader with publish gate",
                    "status": "MISSING",
                    "impact": "No path from staging JSON to runtime without ad-hoc scripts",
                },
            ],
            "do_not_force_into_existing_fields": [
                "Do not stuff claims into Service.source_provenance without Claim table",
                "Do not set Fee.amount from CROSS_CHECKED research fees",
                "Do not set ChecklistItem from PRACTICAL reports",
                "Do not mark ServiceLink.is_verified=true from discovery fetch alone",
            ],
        },
    )

    pipeline_summary = {
        "batch_id": meta_in.get("batch_id"),
        "normalized_at": TODAY,
        "layer": "research/staging",
        "publication_status": "STAGING_ONLY",
        "published_to_runtime_db": False,
        "frontend_changed": False,
        "rag_implemented": False,
        "embeddings_generated": False,
        "counts": {
            "sources": len(sources_out),
            "source_versions": len(versions_out),
            "evidence": len(evidence_out),
            "claims": len(claims_out),
            "services": len(services_out),
            "requirements": len(requirements_out),
            "fees": len(fees_out),
            "procedure_steps": len(procedures_out),
            "conflicts": len(conflicts_out),
            "demoted_from_verified": len(demotion_log),
        },
        "claim_pipeline_status_counts": dict(status_counts),
        "verified_claims_emitted": 0,
        "raw_discovery_path": str(RAW_OUT.relative_to(ROOT)),
        "staging_path": str(STAGING.relative_to(ROOT)),
        "legacy_discovery_path_note": (
            "data/knowledge/batch-01 is a legacy discovery dump and must not be "
            "treated as verified SoT. Prefer data/research/staging/batch-01."
        ),
    }
    dump("pipeline_summary.json", pipeline_summary)

    # Fingerprint for audit
    blob = json.dumps(pipeline_summary, sort_keys=True).encode()
    dump(
        "MANIFEST.json",
        {
            "schema": "bda.research.staging/1.0.0",
            "batch_id": pipeline_summary["batch_id"],
            "summary_sha256": hashlib.sha256(blob).hexdigest(),
            "guardrail": (
                "STAGING_ONLY — not VERIFIED — not loaded into runtime DB"
            ),
        },
    )

    print(json.dumps(pipeline_summary, indent=2))


if __name__ == "__main__":
    main()
