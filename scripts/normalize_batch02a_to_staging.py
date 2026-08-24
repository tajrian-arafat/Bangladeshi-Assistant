#!/usr/bin/env python3
"""Normalize Batch 2A passport research into staging with merged verification.

Merges:
- data/research/raw/batch-02a-passport/
- data/research/verification/batch-02a-passport/claims_verification.json
- data/research/verification/batch-02a-passport-gap-closure/new_claims.json

Does NOT write to runtime DB. Preserves historical OUTDATED claims with explicit
supersedes/superseded_by keys linking to gap-closure current claims.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "research" / "raw" / "batch-02a-passport"
VERIFY = ROOT / "data" / "research" / "verification" / "batch-02a-passport"
GAP = ROOT / "data" / "research" / "verification" / "batch-02a-passport-gap-closure"
STAGING = ROOT / "data" / "research" / "staging" / "batch-02a-passport"
TODAY = date.today().isoformat()

# Regular-tier OUTDATED March 2023 fees → July 2026 gap-closure current claims
FEE_SUPERSESSION: dict[str, str] = {
    "epassport-fee-payment::c-fee-48p-5y-regular": "gap-closure::c-fee-domestic-48p_5y-regular-current",
    "epassport-fee-payment::c-fee-48p-10y-regular": "gap-closure::c-fee-domestic-48p_10y-regular-current",
    "epassport-fee-payment::c-fee-64p-5y-regular": "gap-closure::c-fee-domestic-64p_5y-regular-current",
    "epassport-fee-payment::c-fee-64p-10y-regular": "gap-closure::c-fee-domestic-64p_10y-regular-current",
}

PAYMENT_SUPERSESSION = {
    "epassport-fee-payment::c-payment-ekpay-official": "gap-closure::c-payment-gateways-achallan-dgepay-shurjopay",
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


def _info_class(claim_type: str, verification: dict | None, staging: dict) -> str:
    if verification and verification.get("information_class"):
        return verification["information_class"]
    ic = (staging.get("information_class") or "OFFICIAL").upper()
    if claim_type in {"practical_tip", "community_tip"}:
        return "PRACTICAL"
    return ic


def _normalize_claim_type(raw: str | None) -> str:
    if not raw:
        return "other"
    mapping = {
        "conditional_document": "conditional_document",
        "application_url": "application_url",
        "procedure_step": "procedure_step",
        "document": "document",
        "fee": "fee",
        "payment_method": "other",
        "eligibility_rule": "other",
        "procedure": "procedure_step",
        "portal_function": "application_url",
        "official_metadata": "other",
        "procedure_gap": "other",
        "mission_evidence": "other",
    }
    return mapping.get(raw, raw if raw in mapping.values() else "other")


def main() -> None:
    if not RAW.exists():
        raise SystemExit(f"Missing raw batch: {RAW}")

    claims_in = json.loads((RAW / "claims.json").read_text(encoding="utf-8"))["claims"]
    sources_in = json.loads((RAW / "sources.json").read_text(encoding="utf-8"))["sources"]
    services_in = json.loads((RAW / "services_index.json").read_text(encoding="utf-8"))["services"]
    verify_data = json.loads((VERIFY / "claims_verification.json").read_text(encoding="utf-8"))
    verify_index = {c["claim_id"]: c for c in verify_data.get("claims", [])}

    gap_claims: list[dict] = []
    gap_sources: list[dict] = []
    if (GAP / "new_claims.json").exists():
        gap_claims = json.loads((GAP / "new_claims.json").read_text(encoding="utf-8")).get("claims", [])
    if (GAP / "new_sources.json").exists():
        gap_sources = json.loads((GAP / "new_sources.json").read_text(encoding="utf-8")).get("sources", [])

    STAGING.mkdir(parents=True, exist_ok=True)

    # --- sources + source_versions ---
    sources_out: list[dict[str, Any]] = []
    versions_out: list[dict[str, Any]] = []
    source_by_id: dict[str, dict] = {}

    for s in sources_in:
        sid = s["source_id"]
        source_by_id[sid] = s
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
        snap = None
        for vrec in verify_index.values():
            for ev in vrec.get("evidence", []):
                if ev.get("source_id") == sid and ev.get("snapshot"):
                    snap = ev["snapshot"]
                    break
        versions_out.append(
            {
                "source_version_id": f"sv-{sid}",
                "source_id": sid,
                "url": s.get("source_url"),
                "canonical_url": s.get("source_url"),
                "content_hash": _hash_file(snap),
                "retrieved_at": s.get("retrieved_at") or TODAY,
                "fetched_method": "manual_research_fetch",
                "http_status": None,
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
                "responsible_body": "Department of Immigration and Passports (DIP)",
                "published_date": s.get("source_last_updated"),
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
                "http_status": 200,
                "raw_pointer": s.get("snapshot"),
                "source_last_updated": s.get("source_last_updated"),
            }
        )

    # --- claims (original + gap closure) ---
    claims_out: list[dict[str, Any]] = []
    evidence_out: list[dict[str, Any]] = []
    status_counts: Counter[str] = Counter()
    supersession_pairs: list[dict[str, str]] = []

    def append_claim(
        claim_id: str,
        service_id: str,
        claim_text: str,
        claim_type: str,
        verification: dict | None,
        *,
        structured_value: dict | None = None,
        condition: dict | None = None,
        source_ids: list[str] | None = None,
        evidence_excerpt: str | None = None,
        supersedes_claim_key: str | None = None,
        superseded_by_claim_key: str | None = None,
        information_class: str | None = None,
    ) -> None:
        vstatus = (verification or {}).get("verification_status")
        pipeline = _pipeline_from_verification(vstatus)
        info = information_class or _info_class(claim_type, verification, {"information_class": "OFFICIAL"})
        row = {
            "claim_id": claim_id,
            "service_id": service_id,
            "claim_text": claim_text,
            "claim_type": _normalize_claim_type(claim_type),
            "information_class": info,
            "pipeline_status": pipeline,
            "confidence": verification.get("confidence") if verification else None,
            "structured_value": structured_value,
            "condition": condition or (verification or {}).get("condition"),
            "source_ids": source_ids or [],
            "evidence_ids": [],
            "supersedes_claim_key": supersedes_claim_key,
            "superseded_by_claim_key": superseded_by_claim_key,
            "provenance": {
                "batch_id": "batch-02a-passport",
                "normalized_at": TODAY,
                "verification_status": vstatus,
                "publication_status": "STAGING_ONLY",
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

        # Evidence from verification
        for ev in (verification or {}).get("evidence", []):
            sid = ev.get("source_id")
            if not sid:
                continue
            svid = f"sv-{sid}"
            eid = f"ev-{claim_id}-{sid}"
            excerpt = ev.get("evidence_excerpt") or evidence_excerpt or verification.get("evidence_excerpt")
            evidence_out.append(
                {
                    "evidence_id": eid,
                    "source_version_id": svid,
                    "claim_id": claim_id,
                    "summary": claim_text[:200],
                    "excerpt": excerpt,
                    "locator": ev.get("evidence_location") or ev.get("source_url"),
                    "language": "en",
                    "captured_at": ev.get("retrieved_at") or TODAY,
                    "strength": "STRONG" if pipeline == "VERIFIED" else "MODERATE",
                }
            )
            row["evidence_ids"].append(eid)

        # Gap-closure source-only evidence
        if not (verification or {}).get("evidence") and source_ids:
            for sid in source_ids:
                src = source_by_id.get(sid, {})
                svid = f"sv-{sid}"
                eid = f"ev-{claim_id}-{sid}"
                evidence_out.append(
                    {
                        "evidence_id": eid,
                        "source_version_id": svid,
                        "claim_id": claim_id,
                        "summary": claim_text[:200],
                        "excerpt": evidence_excerpt or src.get("snapshot"),
                        "locator": src.get("source_url"),
                        "language": "en",
                        "captured_at": src.get("retrieved_at") or TODAY,
                        "strength": "STRONG" if pipeline == "VERIFIED" else "MODERATE",
                    }
                )
                row["evidence_ids"].append(eid)

    # Original 55 claims
    for c in claims_in:
        cid = c["claim_id"]
        verification = verify_index.get(cid)
        superseded_by = FEE_SUPERSESSION.get(cid) or PAYMENT_SUPERSESSION.get(cid)
        supersedes = None
        append_claim(
            cid,
            c["service_id"],
            c.get("claim_text") or c.get("claim") or "",
            c.get("claim_type") or "other",
            verification,
            structured_value=c.get("structured_value"),
            condition=c.get("condition"),
            source_ids=c.get("source_ids") or [],
            superseded_by_claim_key=superseded_by,
        )
        if superseded_by:
            supersession_pairs.append({"old": cid, "current": superseded_by})

    # Gap-closure claims (23)
    for gc in gap_claims:
        cid = gc["claim_id"]
        if any(x["claim_id"] == cid for x in claims_out):
            continue
        supersedes = None
        for prior in gc.get("related_prior_claim_ids") or []:
            if prior in FEE_SUPERSESSION and FEE_SUPERSESSION[prior] == cid:
                supersedes = prior
        if gc.get("conflicts_with_prior_claim_ids"):
            for prior in gc["conflicts_with_prior_claim_ids"]:
                if prior in PAYMENT_SUPERSESSION and PAYMENT_SUPERSESSION[prior] == cid:
                    supersedes = prior

        structured = None
        fm = gc.get("fee_metadata")
        if fm and gc.get("claim_type") == "fee":
            structured = {
                "amount": fm.get("amount_bdt"),
                "currency": "BDT",
                "pages": fm.get("pages"),
                "validity_years": fm.get("validity_years"),
                "delivery": fm.get("delivery"),
                "effective_evidence_date": fm.get("effective_evidence_date"),
                "vat_included": fm.get("vat_included"),
            }
        elif gc.get("claim_type") == "application_url" and gc.get("link_type"):
            structured = {"link_type": gc.get("link_type")}

        verification = {
            "claim_id": cid,
            "verification_status": gc.get("verification_status"),
            "information_class": "OFFICIAL",
            "claim_type": _normalize_claim_type(gc.get("claim_type", "other")),
            "reasoning": gc.get("evidence_excerpt") or gc.get("note"),
            "evidence_excerpt": gc.get("evidence_excerpt"),
            "verified_at": datetime.now(timezone.utc).isoformat(),
            "evidence": [
                {
                    "source_id": sid,
                    "source_url": source_by_id.get(sid, {}).get("source_url"),
                    "authority_tier": source_by_id.get(sid, {}).get("authority_tier", 1),
                    "retrieved_via": source_by_id.get(sid, {}).get("retrieval_method"),
                    "snapshot": source_by_id.get(sid, {}).get("snapshot"),
                    "retrieved_at": source_by_id.get(sid, {}).get("retrieved_at"),
                    "evidence_excerpt": gc.get("evidence_excerpt"),
                }
                for sid in (gc.get("source_ids") or [])
            ],
            "condition": gc.get("condition"),
            "applicability": gc.get("applicability"),
        }

        append_claim(
            cid,
            gc["service_id"],
            gc.get("claim_text") or "",
            gc.get("claim_type") or "other",
            verification,
            structured_value=structured,
            source_ids=gc.get("source_ids") or [],
            evidence_excerpt=gc.get("evidence_excerpt"),
            supersedes_claim_key=supersedes,
        )
        if supersedes:
            supersession_pairs.append({"old": supersedes, "current": cid})

    # --- fees.json (July 2026 VERIFIED matrix only) ---
    fees_out: list[dict[str, Any]] = []
    for gc in gap_claims:
        if gc.get("claim_type") != "fee":
            continue
        if gc.get("verification_status") != "VERIFIED":
            continue
        fm = gc.get("fee_metadata") or {}
        if not fm.get("amount_bdt"):
            continue
        pages = fm.get("pages")
        years = fm.get("validity_years")
        delivery = fm.get("delivery", "regular")
        fees_out.append(
            {
                "fee_id": gc["claim_id"],
                "service_id": gc["service_id"],
                "description": (
                    f"Inside Bangladesh: {pages}-page / {years}-year e-Passport "
                    f"{delivery.replace('_', ' ')} delivery (incl. 15% VAT)"
                ),
                "amount": fm["amount_bdt"],
                "currency": "BDT",
                "condition": {
                    "field": "delivery_tier",
                    "pages": pages,
                    "validity_years": years,
                    "delivery": delivery,
                    "applicability": "domestic_inside_bangladesh",
                },
                "claim_ids": [gc["claim_id"]],
                "pipeline_status": "VERIFIED",
                "effective_evidence_date": fm.get("effective_evidence_date"),
                "source_version_id": "sv-src-gap-epassport-fees-browser",
                "publication_status": "ELIGIBLE_WHEN_GATE_PASSES",
            }
        )

    # --- services.json ---
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
        "batch_id": "batch-02a-passport",
        "normalized_at": TODAY,
        "claim_count": len(claims_out),
        "original_claims": len(claims_in),
        "gap_closure_claims": len(gap_claims),
        "fee_tiers_staged": len(fees_out),
        "supersession_pairs": supersession_pairs,
        "pipeline_status_counts": dict(status_counts),
        "publication_rules": [
            "Publish only VERIFIED + OFFICIAL + complete evidence",
            "Skip OUTDATED/PARTIAL/UNVERIFIED/REJECTED as authoritative",
            "Skip claims with superseded_by_claim_key",
            "July 2026 fees from gap-closure browser snapshot only",
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
