#!/usr/bin/env python3
"""Normalize Batch 3A BRTA driving licence research into publication staging."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "research" / "raw" / "batch-03a-brta-driving-licence"
VERIFY = ROOT / "data" / "research" / "verification" / "batch-03a-brta-driving-licence"
STAGING = ROOT / "data" / "research" / "staging" / "batch-03a-brta-driving-licence"
BATCH_ID = "batch-03a-brta-driving-licence"
VERIFIER = "cursor-cloud-agent"
TODAY = date.today().isoformat()


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
    }
    return mapping.get(raw, raw if raw in mapping.values() else "other")


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

    STAGING.mkdir(parents=True, exist_ok=True)

    sources_out: list[dict[str, Any]] = []
    versions_out: list[dict[str, Any]] = []
    source_by_id = {s["source_id"]: s for s in sources_in}

    for s in sources_in:
        sid = s["source_id"]
        snap = s.get("snapshot_path")
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
                "http_status": 200 if sid.startswith("src-bsp") or sid.startswith("src-brta") else None,
                "raw_pointer": snap,
            }
        )

    claims_out: list[dict[str, Any]] = []
    evidence_out: list[dict[str, Any]] = []
    status_counts: Counter[str] = Counter()

    for c in claims_in:
        cid = c["claim_id"]
        verification = verify_index.get(cid)
        vstatus = (verification or {}).get("verification_status")
        pipeline = _pipeline_from_verification(vstatus)
        claim_type = _normalize_claim_type((verification or {}).get("claim_type") or c.get("claim_type"))
        info = (verification or {}).get("information_class") or c.get("information_class") or "OFFICIAL"

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
            "superseded_by_claim_key": None,
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
        claims_out.append(row)
        status_counts[pipeline] += 1

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
        "fee_tiers_staged": 0,
        "pipeline_status_counts": dict(status_counts),
        "publication_rules": [
            "Publish only VERIFIED + OFFICIAL + complete evidence",
            "Fee claims remain PARTIALLY_VERIFIED until live BSP calculator confirmation",
            "Do not invent license fee amounts",
            "BSP sub-portal workflow gaps remain UNVERIFIED",
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
    (STAGING / "fees.json").write_text(json.dumps({"fees": []}, indent=2) + "\n", encoding="utf-8")
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
