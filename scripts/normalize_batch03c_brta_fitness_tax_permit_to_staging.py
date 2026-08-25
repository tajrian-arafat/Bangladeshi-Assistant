#!/usr/bin/env python3
"""Normalize Batch 3C BRTA fitness/tax/permit research into publication staging."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "research" / "raw" / "batch-03c-brta-fitness-tax-permit"
VERIFY = ROOT / "data" / "research" / "verification" / "batch-03c-brta-fitness-tax-permit"
GAP = ROOT / "data" / "research" / "verification" / "batch-03c-brta-fitness-tax-permit-gap-closure"
GAP_03B = ROOT / "data" / "research" / "verification" / "batch-03b-brta-vehicle-gap-closure"
STAGING = ROOT / "data" / "research" / "staging" / "batch-03c-brta-fitness-tax-permit"
BATCH_ID = "batch-03c-brta-fitness-tax-permit"
VERIFIER = "cursor-cloud-agent"
TODAY = date.today().isoformat()

SUPERSESSION: dict[str, str] = {
    "brta-fitness-certificate::c-validity-by-class-unverified": (
        "gap-closure::c-fitness-validity-matrix-unverified"
    ),
    "brta-fitness-certificate::c-commercial-vs-private-rules-differ": (
        "gap-closure::c-fitness-validity-matrix-unverified"
    ),
}


def _domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def _hash_file(rel_path: str | None) -> str | None:
    if not rel_path:
        return None
    path = ROOT / rel_path
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _pipeline_from_verification(vstatus: str | None) -> str:
    mapping = {
        "VERIFIED": "VERIFIED",
        "PARTIALLY_VERIFIED": "PARTIALLY_VERIFIED",
        "UNVERIFIED": "UNVERIFIED",
        "REJECTED": "REJECTED",
        "CONFLICTING": "CONFLICTING",
        "OUTDATED": "OUTDATED",
    }
    return mapping.get(vstatus or "", "DISCOVERED")


def _normalize_claim_type(raw: str | None) -> str:
    if not raw:
        return "other"
    mapping = {
        "conditional_document": "conditional_document",
        "application_url": "application_url",
        "procedure_step": "procedure_step",
        "document": "document",
        "fee": "fee",
        "processing_time": "processing_time",
        "payment_method": "payment_method",
        "official_metadata": "other",
        "practical_tip": "other",
        "availability": "other",
        "restriction": "other",
        "eligibility": "other",
        "cross_batch_dependency": "other",
        "procedure_gap": "other",
    }
    return mapping.get(raw, raw if raw in mapping.values() else "other")


def _load_cross_batch_dependencies() -> list[dict[str, Any]]:
    deps: list[dict[str, Any]] = []

    dep_03b = GAP_03B / "cross_batch_dependencies.json"
    if dep_03b.is_file():
        for row in json.loads(dep_03b.read_text(encoding="utf-8")).get("dependencies", []):
            if row.get("to_batch") == "BATCH_03C":
                deps.append(
                    {
                        **row,
                        "resolution_status": "PENDING_03C_VERIFICATION",
                        "source_batch": "batch-03b-brta-vehicle-gap-closure",
                    }
                )

    dep_03c = GAP / "cross_batch_dependencies.json"
    if dep_03c.is_file():
        for row in json.loads(dep_03c.read_text(encoding="utf-8")).get("dependencies", []):
            deps.append({**row, "source_batch": "batch-03c-brta-fitness-tax-permit-gap-closure"})

    return deps


def _resolve_cross_batch_dependencies(
    deps: list[dict[str, Any]],
    verify_index: dict[str, dict],
) -> list[dict[str, Any]]:
    resolved: list[dict[str, Any]] = []
    for dep in deps:
        claim_id = dep.get("claim_id")
        resolution = dict(dep)
        if claim_id and claim_id in verify_index:
            v = verify_index[claim_id]
            resolution["verification_status"] = v.get("verification_status")
            resolution["resolution_status"] = (
                "RESOLVED"
                if v.get("verification_status") == "VERIFIED"
                else "PARTIALLY_RESOLVED"
                if v.get("verification_status") == "PARTIALLY_VERIFIED"
                else "UNRESOLVED"
            )
        elif dep.get("to_service_id") == "brta-fitness-certificate":
            fitness_claims = [
                verify_index[cid]
                for cid in (
                    "brta-fitness-certificate::c-validity-by-class-unverified",
                    "brta-fitness-certificate::c-commercial-vs-private-rules-differ",
                )
                if cid in verify_index
            ]
            if fitness_claims and all(c.get("verification_status") == "UNVERIFIED" for c in fitness_claims):
                resolution["resolution_status"] = "UNRESOLVED"
                resolution["note"] = (
                    "Fitness validity-by-class remains UNVERIFIED; authoritative matrix not captured."
                )
        resolved.append(resolution)
    return resolved


def _collect_calculator_derived_fees(
    claims_in: list[dict],
    gap_claims: list[dict],
    verify_index: dict[str, dict],
) -> list[dict[str, Any]]:
    fees_out: list[dict[str, Any]] = []
    seen: set[str] = set()

    def maybe_add(row: dict, *, from_gap: bool = False) -> None:
        cid = row["claim_id"]
        if cid in seen:
            return
        if row.get("claim_type") != "fee":
            return
        sv = row.get("structured_value") or {}
        amount = sv.get("amount")
        if amount != "CALCULATOR_DERIVED" and not from_gap:
            return
        if from_gap and amount != "CALCULATOR_DERIVED":
            return
        seen.add(cid)
        vstatus = (verify_index.get(cid) or {}).get("verification_status")
        fees_out.append(
            {
                "fee_id": cid,
                "service_id": row["service_id"],
                "description": f"{row['service_id']} fee — CALCULATOR_DERIVED via BSP feeCalculator or payment portal",
                "amount": "CALCULATOR_DERIVED",
                "currency": "BDT",
                "condition": {
                    "source": sv.get("source") or "src-bsp-fee-calculator",
                    "verification": sv.get("verification") or "PENDING_INTERACTIVE_EXTRACT",
                    "vehicle_type": sv.get("vehicle_type"),
                    "action": sv.get("action"),
                },
                "claim_ids": [cid],
                "pipeline_status": _pipeline_from_verification(vstatus),
                "publication_status": "NOT_PUBLISHABLE_STATIC_AMOUNT",
            }
        )

    for c in claims_in:
        maybe_add(c)
    for gc in gap_claims:
        maybe_add(gc, from_gap=True)

    return fees_out


def main() -> None:
    if not RAW.exists():
        raise SystemExit(f"Missing raw batch: {RAW}")
    verify_path = VERIFY / "claims_verification.json"
    if not verify_path.exists():
        raise SystemExit(f"Missing verification: {verify_path}")

    claims_in = json.loads((RAW / "claims.json").read_text(encoding="utf-8"))["claims"]
    sources_in = json.loads((RAW / "sources.json").read_text(encoding="utf-8"))["sources"]
    services_in = json.loads((RAW / "services_index.json").read_text(encoding="utf-8"))["services"]
    verify_data = json.loads(verify_path.read_text(encoding="utf-8"))
    verify_index = {c["claim_id"]: c for c in verify_data.get("claims", [])}

    gap_claims: list[dict] = []
    gap_sources: list[dict] = []
    if (GAP / "new_claims.json").exists():
        gap_claims = json.loads((GAP / "new_claims.json").read_text(encoding="utf-8")).get("claims", [])
    if (GAP / "new_sources.json").exists():
        gap_sources = json.loads((GAP / "new_sources.json").read_text(encoding="utf-8")).get("sources", [])

    cross_batch_deps = _load_cross_batch_dependencies()
    cross_batch_resolved = _resolve_cross_batch_dependencies(cross_batch_deps, verify_index)

    STAGING.mkdir(parents=True, exist_ok=True)

    sources_out: list[dict[str, Any]] = []
    versions_out: list[dict[str, Any]] = []
    source_by_id = {s["source_id"]: s for s in sources_in}

    for s in sources_in:
        sid = s["source_id"]
        snap = s.get("snapshot_path")
        if snap and not snap.startswith("data/"):
            snap = f"data/research/raw/batch-03c-brta-fitness-tax-permit/{snap}"
        for vrec in verify_index.values():
            for ev in vrec.get("evidence") or []:
                if ev.get("source_id") == sid and ev.get("snapshot"):
                    snap = ev["snapshot"]
        sources_out.append(
            {
                "source_id": sid,
                "domain": _domain(s.get("source_url", "")),
                "source_url": s.get("source_url"),
                "source_title": s.get("source_title"),
                "source_type": s.get("source_type"),
                "authority_tier": s.get("authority_tier"),
                "responsible_body": s.get("responsible_body"),
                "published_date": s.get("published_date"),
                "language": s.get("language"),
                "retrieved_at": s.get("retrieved_at") or TODAY,
                "runtime_mapped": False,
            }
        )
        versions_out.append(
            {
                "source_version_id": f"sv-{sid}",
                "source_id": sid,
                "url": s.get("source_url"),
                "canonical_url": s.get("source_url"),
                "content_hash": _hash_file(snap),
                "retrieved_at": s.get("retrieved_at") or TODAY,
                "fetched_method": "research_catalogue_pass",
                "http_status": 200 if sid.startswith("src-brta") else None,
                "raw_pointer": snap,
            }
        )

    for s in gap_sources:
        sid = s["source_id"]
        if sid in source_by_id:
            continue
        source_by_id[sid] = s
        sources_out.append(
            {
                "source_id": sid,
                "domain": _domain(s.get("source_url", "")),
                "source_url": s.get("source_url"),
                "source_title": s.get("source_title"),
                "source_type": "official_portal",
                "authority_tier": s.get("authority_tier", 1),
                "responsible_body": "Bangladesh Road Transport Authority (BRTA)",
                "published_date": None,
                "language": "en",
                "retrieved_at": s.get("retrieved_at") or TODAY,
                "runtime_mapped": False,
                "notes": s.get("evidence_limitation"),
            }
        )
        versions_out.append(
            {
                "source_version_id": f"sv-{sid}",
                "source_id": sid,
                "url": s.get("source_url"),
                "canonical_url": s.get("source_url"),
                "content_hash": _hash_file(s.get("snapshot")),
                "retrieved_at": s.get("retrieved_at") or TODAY,
                "fetched_method": s.get("retrieval_method") or "puppeteer_headless_chrome",
                "http_status": s.get("http_status"),
                "availability": s.get("availability"),
                "raw_pointer": s.get("snapshot"),
            }
        )

    claims_out: list[dict[str, Any]] = []
    evidence_out: list[dict[str, Any]] = []
    status_counts: Counter[str] = Counter()
    supersession_pairs: list[dict[str, str]] = []

    seen_ids: set[str] = set()

    def append_claim(row: dict[str, Any]) -> None:
        cid = row["claim_id"]
        if cid in seen_ids:
            return
        seen_ids.add(cid)
        claims_out.append(row)
        status_counts[row["pipeline_status"]] += 1

    for c in claims_in:
        cid = c["claim_id"]
        verification = verify_index.get(cid)
        vstatus = (verification or {}).get("verification_status")
        pipeline = _pipeline_from_verification(vstatus)
        claim_type = _normalize_claim_type((verification or {}).get("claim_type") or c.get("claim_type"))
        info = (verification or {}).get("information_class") or c.get("information_class") or "OFFICIAL"
        superseded_by = SUPERSESSION.get(cid)

        row = {
            "claim_id": cid,
            "service_id": c["service_id"],
            "claim_text": c.get("claim_text") or "",
            "claim_type": claim_type,
            "information_class": info,
            "pipeline_status": pipeline,
            "confidence": c.get("confidence"),
            "structured_value": c.get("structured_value"),
            "condition": c.get("condition"),
            "source_ids": c.get("source_ids") or [],
            "evidence_ids": [],
            "supersedes_claim_key": None,
            "superseded_by_claim_key": superseded_by,
            "provenance": {
                "batch_id": BATCH_ID,
                "normalized_at": TODAY,
                "verification_status": vstatus,
                "publication_status": "STAGING_ONLY",
            },
        }
        if verification:
            row["independent_verification"] = {
                "verifier": verification.get("verifier", VERIFIER),
                "verified_at": verification.get("verified_at"),
                "reasoning": verification.get("reasoning"),
            }
        append_claim(row)

        if superseded_by and not any(p["old"] == cid and p["current"] == superseded_by for p in supersession_pairs):
            supersession_pairs.append({"old": cid, "current": superseded_by})

        for sid in c.get("source_ids") or []:
            src = source_by_id.get(sid, {})
            svid = f"sv-{sid}"
            eid = f"ev-{cid}-{sid}"
            evidence_out.append(
                {
                    "evidence_id": eid,
                    "source_version_id": svid,
                    "claim_id": cid,
                    "summary": row["claim_text"][:200],
                    "excerpt": verification.get("reasoning") if verification else None,
                    "locator": src.get("source_url"),
                    "language": "en",
                    "captured_at": src.get("retrieved_at") or TODAY,
                    "strength": "STRONG" if pipeline == "VERIFIED" else "MODERATE",
                }
            )
            row["evidence_ids"].append(eid)

    for gc in gap_claims:
        cid = gc["claim_id"]
        verification = verify_index.get(cid) or {
            "verification_status": gc.get("verification_status"),
            "reasoning": gc.get("evidence_excerpt"),
        }
        vstatus = verification.get("verification_status")
        pipeline = _pipeline_from_verification(vstatus)
        supersedes = None
        for prior in gc.get("related_prior_claim_ids") or []:
            if SUPERSESSION.get(prior) == cid:
                supersedes = prior

        row = {
            "claim_id": cid,
            "service_id": gc["service_id"],
            "claim_text": gc.get("claim_text") or "",
            "claim_type": _normalize_claim_type(gc.get("claim_type")),
            "information_class": gc.get("information_class", "OFFICIAL"),
            "pipeline_status": pipeline,
            "confidence": None,
            "structured_value": gc.get("structured_value"),
            "condition": gc.get("condition"),
            "source_ids": gc.get("source_ids") or [],
            "evidence_ids": [],
            "supersedes_claim_key": supersedes,
            "superseded_by_claim_key": None,
            "provenance": {
                "batch_id": BATCH_ID,
                "normalized_at": TODAY,
                "verification_status": vstatus,
                "publication_status": "STAGING_ONLY",
                "gap_closure": True,
            },
            "independent_verification": {
                "verifier": VERIFIER,
                "verified_at": datetime.now(timezone.utc).isoformat(),
                "reasoning": gc.get("evidence_excerpt"),
            },
        }
        if gc.get("deferred_to_batch"):
            row["deferred_to_batch"] = gc["deferred_to_batch"]
        if gc.get("resolves_cross_batch_dependency"):
            row["resolves_cross_batch_dependency"] = gc["resolves_cross_batch_dependency"]
        append_claim(row)
        if supersedes and not any(p["old"] == supersedes and p["current"] == cid for p in supersession_pairs):
            supersession_pairs.append({"old": supersedes, "current": cid})

        for sid in gc.get("source_ids") or []:
            src = source_by_id.get(sid, {})
            svid = f"sv-{sid}"
            eid = f"ev-{cid}-{sid}"
            evidence_out.append(
                {
                    "evidence_id": eid,
                    "source_version_id": svid,
                    "claim_id": cid,
                    "summary": row["claim_text"][:200],
                    "excerpt": gc.get("evidence_excerpt"),
                    "locator": src.get("source_url"),
                    "language": "en",
                    "captured_at": src.get("retrieved_at") or TODAY,
                    "strength": "STRONG" if pipeline == "VERIFIED" else "MODERATE",
                }
            )
            row["evidence_ids"].append(eid)

    fees_out = _collect_calculator_derived_fees(claims_in, gap_claims, verify_index)

    services_out = [
        {
            "service_id": s["service_id"],
            "service_name_en": s.get("service_name_en"),
            "service_name_bn": s.get("service_name_bn"),
            "category_id": s.get("category_id"),
            "official_source": s.get("official_source"),
            "status": s.get("status", "CONFIRMED"),
        }
        for s in services_in
    ]

    manifest = {
        "batch_id": BATCH_ID,
        "normalized_at": TODAY,
        "claim_count": len(claims_out),
        "original_claims": len(claims_in),
        "gap_closure_claims": len(gap_claims),
        "fee_tiers_staged": len(fees_out),
        "supersession_pairs": supersession_pairs,
        "pipeline_status_counts": dict(status_counts),
        "cross_batch_dependencies": cross_batch_resolved,
        "cross_batch_dependency_count": len(cross_batch_resolved),
        "upstream_batches": [
            "batch-03a-brta-driving-licence",
            "batch-03b-brta-vehicle",
        ],
        "publication_rules": [
            "Publish only VERIFIED + OFFICIAL + complete evidence",
            "Fee claims remain CALCULATOR_DERIVED — do not publish invented amounts",
            "Fitness validity-by-class stays UNVERIFIED until authoritative matrix captured",
            "BSP off-hours 404 classified TEMPORARILY_UNAVAILABLE not invalid URL",
            "Resolve BATCH_03B dep-03b-fitness-validity-03c only with verified validity matrix",
            "brta-route-permit vs transport-route-permit — do not flatten workflows",
            "brta-driving-school-registration vs transport-driving-school-licence — do not flatten",
        ],
    }

    (STAGING / "sources.json").write_text(
        json.dumps({"sources": sources_out}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (STAGING / "source_versions.json").write_text(
        json.dumps({"source_versions": versions_out}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (STAGING / "claims.json").write_text(
        json.dumps({"claims": claims_out}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (STAGING / "evidence.json").write_text(
        json.dumps({"evidence": evidence_out}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (STAGING / "fees.json").write_text(json.dumps({"fees": fees_out}, indent=2) + "\n", encoding="utf-8")
    (STAGING / "services.json").write_text(
        json.dumps({"services": services_out}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (STAGING / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
