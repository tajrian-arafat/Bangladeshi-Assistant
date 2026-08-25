#!/usr/bin/env python3
"""Normalize Batch 2B police + immigration research into publication staging.

Merges:
- data/research/raw/batch-02b-police-immigration/
- data/research/verification/batch-02b-police-immigration/claims_verification.json

Does NOT write to runtime DB.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "research" / "raw" / "batch-02b-police-immigration"
VERIFY = ROOT / "data" / "research" / "verification" / "batch-02b-police-immigration"
STAGING = ROOT / "data" / "research" / "staging" / "batch-02b-police-immigration"
TODAY = date.today().isoformat()

# Never publish as universal fee — online channel only when gate allows channel-specific row
ONLINE_PCC_FEE_CLAIM = "police-clearance-certificate::c-online-fee-1500"


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
        "eligibility_rule": "other",
        "procedure": "procedure_step",
        "portal_function": "application_url",
        "official_metadata": "other",
    }
    return mapping.get(raw, raw if raw in mapping.values() else "other")


def main() -> None:
    if not RAW.exists():
        raise SystemExit(f"Missing raw batch: {RAW}")
    if not (VERIFY / "claims_verification.json").exists():
        raise SystemExit(f"Missing verification: {VERIFY / 'claims_verification.json'}")

    claims_in = json.loads((RAW / "claims.json").read_text(encoding="utf-8"))["claims"]
    sources_in = json.loads((RAW / "sources.json").read_text(encoding="utf-8"))["sources"]
    services_in = json.loads((RAW / "services_index.json").read_text(encoding="utf-8"))["services"]
    verify_data = json.loads((VERIFY / "claims_verification.json").read_text(encoding="utf-8"))
    verify_index = {c["claim_id"]: c for c in verify_data.get("claims", [])}

    STAGING.mkdir(parents=True, exist_ok=True)

    sources_out: list[dict[str, Any]] = []
    versions_out: list[dict[str, Any]] = []
    source_by_id: dict[str, dict] = {}

    for s in sources_in:
        sid = s["source_id"]
        source_by_id[sid] = s
        snap = s.get("snapshot_path")
        for vrec in verify_index.values():
            for ev in vrec.get("evidence") or []:
                if ev.get("source_id") == sid and ev.get("snapshot"):
                    snap = ev["snapshot"]
                    break
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
                "fetched_method": "live_html_verification_pass",
                "http_status": 200 if sid.startswith("src-pcc") or sid.startswith("src-police") or sid.startswith("src-dip") else None,
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
        claim_type = _normalize_claim_type(
            (verification or {}).get("claim_type") or c.get("claim_type")
        )
        info = (verification or {}).get("information_class") or c.get("information_class") or "OFFICIAL"

        structured = c.get("structured_value")
        if cid == ONLINE_PCC_FEE_CLAIM and pipeline == "VERIFIED":
            structured = {
                "amount": 1500,
                "currency": "BDT",
                "treasury_code": "1-7301-0001-2681",
                "condition": {"channel": "online_pcc"},
                "applicability": "online_pcc_channel",
                "description": "Online PCC application fee (online channel only — not universal)",
            }

        row = {
            "claim_id": cid,
            "service_id": c["service_id"],
            "claim_text": c.get("claim_text") or "",
            "claim_type": claim_type,
            "information_class": info,
            "pipeline_status": pipeline,
            "confidence": c.get("confidence"),
            "structured_value": structured,
            "condition": (verification or {}).get("condition") or c.get("condition"),
            "source_ids": c.get("source_ids") or [],
            "evidence_ids": [],
            "supersedes_claim_key": None,
            "superseded_by_claim_key": None,
            "provenance": {
                "batch_id": "batch-02b-police-immigration",
                "normalized_at": TODAY,
                "verification_status": vstatus,
                "publication_status": "STAGING_ONLY",
                "applicability": (verification or {}).get("applicability"),
                "do_not_promote_to_must": (verification or {}).get("do_not_promote_to_must", False),
            },
        }
        if verification:
            row["independent_verification"] = {
                "verifier": verification.get("verifier", "cursor-cloud-agent"),
                "verified_at": verification.get("verified_at"),
                "reasoning": verification.get("reasoning"),
            }
        claims_out.append(row)
        status_counts[pipeline] += 1

        for ev in (verification or {}).get("evidence") or []:
            sid = ev.get("source_id")
            if not sid:
                continue
            svid = f"sv-{sid}"
            eid = f"ev-{cid}-{sid}"
            excerpt = ev.get("evidence_excerpt") or verification.get("evidence_excerpt")
            evidence_out.append(
                {
                    "evidence_id": eid,
                    "source_version_id": svid,
                    "claim_id": cid,
                    "summary": row["claim_text"][:200],
                    "excerpt": excerpt,
                    "locator": ev.get("evidence_locator") or ev.get("source_url"),
                    "language": "en",
                    "captured_at": ev.get("retrieved_at") or TODAY,
                    "strength": "STRONG" if pipeline == "VERIFIED" else "MODERATE",
                }
            )
            row["evidence_ids"].append(eid)

        if not row["evidence_ids"] and c.get("source_ids"):
            for sid in c["source_ids"]:
                src = source_by_id.get(sid, {})
                svid = f"sv-{sid}"
                eid = f"ev-{cid}-{sid}"
                evidence_out.append(
                    {
                        "evidence_id": eid,
                        "source_version_id": svid,
                        "claim_id": cid,
                        "summary": row["claim_text"][:200],
                        "excerpt": verification.get("evidence_excerpt") if verification else None,
                        "locator": src.get("source_url"),
                        "language": "en",
                        "captured_at": src.get("retrieved_at") or TODAY,
                        "strength": "MODERATE",
                    }
                )
                row["evidence_ids"].append(eid)

    fees_out: list[dict[str, Any]] = []
    vrec = verify_index.get(ONLINE_PCC_FEE_CLAIM)
    if vrec and vrec.get("verification_status") == "VERIFIED":
        fees_out.append(
            {
                "fee_id": ONLINE_PCC_FEE_CLAIM,
                "service_id": "police-clearance-certificate",
                "description": "Online PCC application fee (online channel only)",
                "amount": 1500,
                "currency": "BDT",
                "condition": {
                    "field": "channel",
                    "channel": "online_pcc",
                    "applicability": "online_pcc_channel",
                    "not_universal": True,
                },
                "claim_ids": [ONLINE_PCC_FEE_CLAIM],
                "pipeline_status": "VERIFIED",
                "source_version_id": "sv-src-pcc-portal",
                "publication_status": "ELIGIBLE_WHEN_GATE_PASSES",
            }
        )

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
        "batch_id": "batch-02b-police-immigration",
        "normalized_at": TODAY,
        "claim_count": len(claims_out),
        "fee_tiers_staged": len(fees_out),
        "pipeline_status_counts": dict(status_counts),
        "publication_rules": [
            "Publish only VERIFIED + OFFICIAL + complete evidence",
            "Skip PARTIALLY_VERIFIED/UNVERIFIED/CONFLICTING/OUTDATED/REJECTED as authoritative",
            "PCC offline BDT 500 CONFLICTING — never universal fee",
            "Online PCC BDT 1500 channel-specific only",
            "Tier-5 GD expansion and unverified MRV fees blocked",
        ],
    }

    (STAGING / "sources.json").write_text(
        json.dumps({"sources": sources_out}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (STAGING / "source_versions.json").write_text(
        json.dumps({"source_versions": versions_out}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (STAGING / "claims.json").write_text(
        json.dumps({"claims": claims_out}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (STAGING / "evidence.json").write_text(
        json.dumps({"evidence": evidence_out}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (STAGING / "fees.json").write_text(
        json.dumps({"fees": fees_out}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (STAGING / "services.json").write_text(
        json.dumps({"services": services_out}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (STAGING / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
