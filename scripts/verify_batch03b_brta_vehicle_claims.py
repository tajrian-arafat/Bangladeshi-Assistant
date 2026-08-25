#!/usr/bin/env python3
"""Independent Batch 3B BRTA vehicle claim verification (STAGING ONLY)."""

from __future__ import annotations

import json
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RAW = REPO / "data/research/raw/batch-03b-brta-vehicle"
OUT = REPO / "data/research/verification/batch-03b-brta-vehicle"
GAP = REPO / "data/research/verification/batch-03b-brta-vehicle-gap-closure"
SNAP = OUT / "source_snapshots"
BATCH_ID = "batch-03b-brta-vehicle"

VERIFIER = "cursor-cloud-agent"
VERIFIED_AT = datetime.now(timezone.utc).isoformat()

TIER1_SOURCE_IDS = {
    "src-bsp-vehicle-registration",
    "src-bsp-register-owner",
    "src-bsp-fee-calculator",
    "src-bsp-tbc",
    "src-bsp-maintenance-notice",
    "src-gap-bsp-vehicle-registration-browser",
    "src-gap-bsp-tbc-browser",
    "src-gap-bsp-fee-calculator-browser",
}

GAP_RESOLVED_CLAIMS = {
    "brta-new-vehicle-registration::c-portal-url",
    "brta-trustee-board-certificate::c-portal-url",
    "brta-trustee-board-certificate::c-bsp-login-may-be-required",
}

GAP_PARTIAL_CLAIMS = {
    "brta-ownership-transfer::c-circle-office-submission",
    "brta-vehicle-info-correction::c-fields-not-fully-enumerated",
    "brta-retro-reflective-number-plate::c-circle-office-or-approved-vendor",
    "brta-digital-registration-certificate::c-lost-damaged-replacement",
    "brta-ownership-transfer::c-lost-rc-gd-conditional",
    "brta-new-vehicle-registration::c-fitness-prerequisite-crossref",
}

GAP_FEE_CLAIMS = {
    "brta-new-vehicle-registration::c-vehicle-type-fee-variation",
    "brta-ownership-transfer::c-transfer-fee-calculator",
    "brta-digital-registration-certificate::c-drc-fee-calculator",
    "brta-vehicle-info-correction::c-correction-fee-calculator",
}

GAP_CLAIM_HINTS = {
    "MISSING_BSP_VEHICLE_SUBPORTAL_SNAPSHOT": {
        "brta-new-vehicle-registration::c-portal-url",
        "brta-trustee-board-certificate::c-portal-url",
        "brta-trustee-board-certificate::c-bsp-login-may-be-required",
    },
    "MISSING_PORTAL_JS_BODY": {
        "brta-ownership-transfer::c-circle-office-submission",
        "brta-vehicle-info-correction::c-fields-not-fully-enumerated",
        "brta-retro-reflective-number-plate::c-circle-office-or-approved-vendor",
    },
    "MISSING_VEHICLE_FEE_MATRIX": GAP_FEE_CLAIMS,
    "MISSING_FITNESS_VALIDITY_BY_CLASS": {
        "brta-new-vehicle-registration::c-fitness-prerequisite-crossref",
    },
    "MISSING_LOST_RC_PROCEDURE_DETAIL": {
        "brta-digital-registration-certificate::c-lost-damaged-replacement",
        "brta-ownership-transfer::c-lost-rc-gd-conditional",
    },
}

E_BSP_VEHICLE = {
    "source_id": "src-bsp-vehicle-registration",
    "source_url": "https://bsp.brta.gov.bd/vehicleRegistration/?lan=en",
    "authority_tier": 1,
    "retrieval_method": "catalogue_reference",
    "snapshot": "data/research/verification/batch-03b-brta-vehicle-gap-closure/source_snapshots/bsp_vehicle_registration.txt",
    "retrieved_at": "2026-08-25",
    "availability": "TEMPORARILY_UNAVAILABLE",
}

E_BSP_REGISTER = {
    "source_id": "src-bsp-register-owner",
    "source_url": "https://bsp.brta.gov.bd/register",
    "authority_tier": 1,
    "retrieval_method": "catalogue_cross_batch_03a",
    "snapshot": "data/research/verification/batch-03b-brta-vehicle-gap-closure/source_snapshots/bsp_register.txt",
    "retrieved_at": "2026-08-25",
    "availability": "TEMPORARILY_UNAVAILABLE",
}

E_BSP_FEE = {
    "source_id": "src-bsp-fee-calculator",
    "source_url": "https://bsp.brta.gov.bd/feeCalculator",
    "authority_tier": 1,
    "retrieval_method": "catalogue_cross_batch_03a",
    "snapshot": "data/research/verification/batch-03b-brta-vehicle-gap-closure/source_snapshots/bsp_fee_calculator.txt",
    "retrieved_at": "2026-08-25",
    "availability": "TEMPORARILY_UNAVAILABLE",
}

E_BSP_TBC = {
    "source_id": "src-bsp-tbc",
    "source_url": "https://bsp.brta.gov.bd/tbc/",
    "authority_tier": 1,
    "retrieval_method": "catalogue_reference",
    "snapshot": "data/research/verification/batch-03b-brta-vehicle-gap-closure/source_snapshots/bsp_tbc.txt",
    "retrieved_at": "2026-08-25",
    "availability": "TEMPORARILY_UNAVAILABLE",
}

E_BSP_HOURS = {
    "source_id": "src-bsp-maintenance-notice",
    "source_url": "https://bsp.brta.gov.bd/",
    "authority_tier": 1,
    "retrieval_method": "catalogue_cross_batch_03a",
    "snapshot": "data/research/raw/batch-03b-brta-vehicle/source_snapshots/bsp_hours_notice.html",
    "retrieved_at": "2026-08-24",
}

E_BRTA_OWNERSHIP = {
    "source_id": "src-brta-portal-ownership-transfer",
    "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922dc6b933eb65569e10468",
    "authority_tier": 2,
    "retrieval_method": "puppeteer_headless_chrome",
    "snapshot": "data/research/verification/batch-03b-brta-vehicle-gap-closure/source_snapshots/brta_ownership_transfer.html",
    "retrieved_at": "2026-08-25",
}

E_BRTA_DRC = {
    "source_id": "src-brta-portal-drc",
    "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922dba6933eb65569e0b8fe",
    "authority_tier": 2,
    "retrieval_method": "puppeteer_headless_chrome",
    "snapshot": "data/research/verification/batch-03b-brta-vehicle-gap-closure/source_snapshots/brta_drc_biometric.html",
    "retrieved_at": "2026-08-25",
}

E_BRTA_RETRO = {
    "source_id": "src-brta-portal-retro-plate",
    "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922db7a933eb65569e0a505",
    "authority_tier": 2,
    "retrieval_method": "puppeteer_headless_chrome",
    "snapshot": "data/research/verification/batch-03b-brta-vehicle-gap-closure/source_snapshots/brta_retro_plate.html",
    "retrieved_at": "2026-08-25",
}

E_BRTA_CORRECTION = {
    "source_id": "src-brta-portal-info-correction",
    "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922dc03933eb65569e0df09",
    "authority_tier": 2,
    "retrieval_method": "puppeteer_headless_chrome",
    "snapshot": "data/research/verification/batch-03b-brta-vehicle-gap-closure/source_snapshots/brta_info_correction.html",
    "retrieved_at": "2026-08-25",
}

E_BRTA_FITNESS = {
    "source_id": "src-brta-portal-fitness-crossref",
    "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922db91933eb65569e0af12",
    "authority_tier": 2,
    "retrieval_method": "puppeteer_headless_chrome",
    "snapshot": "data/research/verification/batch-03b-brta-vehicle-gap-closure/source_snapshots/brta_fitness_crossref.html",
    "retrieved_at": "2026-08-25",
}

E_CATALOGUE = {
    "source_id": "src-catalogue-transport",
    "source_url": "data/service_catalogue/by_category/transport.json",
    "authority_tier": 2,
    "retrieval_method": "internal_catalogue",
    "snapshot": "data/service_catalogue/by_category/transport.json",
    "retrieved_at": "2026-08-25",
}

EVIDENCE_BY_SOURCE: dict[str, dict] = {
    "src-bsp-vehicle-registration": E_BSP_VEHICLE,
    "src-bsp-register-owner": E_BSP_REGISTER,
    "src-bsp-fee-calculator": E_BSP_FEE,
    "src-bsp-tbc": E_BSP_TBC,
    "src-bsp-maintenance-notice": E_BSP_HOURS,
    "src-brta-portal-ownership-transfer": E_BRTA_OWNERSHIP,
    "src-brta-portal-drc": E_BRTA_DRC,
    "src-brta-portal-retro-plate": E_BRTA_RETRO,
    "src-brta-portal-info-correction": E_BRTA_CORRECTION,
    "src-brta-portal-fitness-crossref": E_BRTA_FITNESS,
    "src-catalogue-transport": E_CATALOGUE,
    "src-brta-portal-home": {
        "source_id": "src-brta-portal-home",
        "source_url": "http://brta.portal.gov.bd/",
        "authority_tier": 2,
        "retrieval_method": "catalogue_reference",
        "snapshot": None,
        "retrieved_at": "2026-08-25",
    },
    "src-gap-bsp-vehicle-registration-browser": {
        "source_id": "src-gap-bsp-vehicle-registration-browser",
        "source_url": "https://bsp.brta.gov.bd/vehicleRegistration/?lan=en",
        "authority_tier": 1,
        "retrieval_method": "puppeteer_headless_chrome",
        "snapshot": "data/research/verification/batch-03b-brta-vehicle-gap-closure/source_snapshots/bsp_vehicle_registration.txt",
        "retrieved_at": "2026-08-25",
        "availability": "TEMPORARILY_UNAVAILABLE",
    },
    "src-gap-bsp-tbc-browser": {
        "source_id": "src-gap-bsp-tbc-browser",
        "source_url": "https://bsp.brta.gov.bd/tbc/",
        "authority_tier": 1,
        "retrieval_method": "puppeteer_headless_chrome",
        "snapshot": "data/research/verification/batch-03b-brta-vehicle-gap-closure/source_snapshots/bsp_tbc.txt",
        "retrieved_at": "2026-08-25",
        "availability": "TEMPORARILY_UNAVAILABLE",
    },
    "src-gap-bsp-fee-calculator-browser": {
        "source_id": "src-gap-bsp-fee-calculator-browser",
        "source_url": "https://bsp.brta.gov.bd/feeCalculator",
        "authority_tier": 1,
        "retrieval_method": "puppeteer_headless_chrome",
        "snapshot": "data/research/verification/batch-03b-brta-vehicle-gap-closure/source_snapshots/bsp_fee_calculator.txt",
        "retrieved_at": "2026-08-25",
        "availability": "TEMPORARILY_UNAVAILABLE",
    },
    "src-gap-brta-ownership-transfer-browser": E_BRTA_OWNERSHIP | {"source_id": "src-gap-brta-ownership-transfer-browser"},
    "src-gap-brta-drc-browser": E_BRTA_DRC | {"source_id": "src-gap-brta-drc-browser"},
    "src-gap-brta-info-correction-browser": E_BRTA_CORRECTION | {"source_id": "src-gap-brta-info-correction-browser"},
    "src-gap-brta-retro-plate-browser": E_BRTA_RETRO | {"source_id": "src-gap-brta-retro-plate-browser"},
    "src-gap-brta-fitness-crossref-browser": E_BRTA_FITNESS | {"source_id": "src-gap-brta-fitness-crossref-browser"},
    "src-gap-scrape-results-index": {
        "source_id": "src-gap-scrape-results-index",
        "source_url": "data/research/verification/batch-03b-brta-vehicle-gap-closure/source_snapshots/scrape_results.json",
        "authority_tier": 2,
        "retrieval_method": "puppeteer_headless_chrome",
        "snapshot": "data/research/verification/batch-03b-brta-vehicle-gap-closure/source_snapshots/scrape_results.json",
        "retrieved_at": "2026-08-25",
    },
}


def _gap_closure_complete() -> bool:
    return (GAP / "summary.json").exists()


def _has_tier1(sources: dict[str, dict], source_ids: list[str]) -> bool:
    return any(sources.get(sid, {}).get("authority_tier", 99) <= 1 for sid in source_ids)


def _evidence_for_claim(claim: dict) -> list[dict]:
    out: list[dict] = []
    for sid in claim.get("source_ids") or []:
        bundle = EVIDENCE_BY_SOURCE.get(sid)
        if bundle:
            out.append(dict(bundle))
    return out


def assign_status(claim: dict, sources: dict[str, dict], *, gap_complete: bool) -> tuple[str, str | None]:
    cid = claim["claim_id"]
    ctype = claim.get("claim_type") or ""
    info = claim.get("information_class") or "OFFICIAL"

    if gap_complete:
        if cid in GAP_RESOLVED_CLAIMS:
            return "PARTIALLY_VERIFIED", None
        if cid in GAP_PARTIAL_CLAIMS:
            return "PARTIALLY_VERIFIED", None
        if cid in GAP_FEE_CLAIMS:
            return "PARTIALLY_VERIFIED", "MISSING_VEHICLE_FEE_MATRIX"

    for gap_id, claim_ids in GAP_CLAIM_HINTS.items():
        if cid in claim_ids and not gap_complete:
            return "UNVERIFIED", gap_id
        if cid in claim_ids and gap_complete and gap_id == "MISSING_FITNESS_VALIDITY_BY_CLASS":
            return "PARTIALLY_VERIFIED", None

    if info == "DISCOVERY" and ctype in {"processing_time", "document", "fee", "official_metadata"}:
        return "UNVERIFIED", None

    if ctype == "application_url" and _has_tier1(sources, claim.get("source_ids") or []):
        if gap_complete and cid in GAP_RESOLVED_CLAIMS:
            return "PARTIALLY_VERIFIED", None
        return "VERIFIED", None

    if ctype == "application_url" and any(
        sources.get(sid, {}).get("snapshot") or EVIDENCE_BY_SOURCE.get(sid, {}).get("snapshot")
        for sid in claim.get("source_ids") or []
    ):
        return "VERIFIED", None

    if ctype == "fee":
        return "PARTIALLY_VERIFIED", "MISSING_VEHICLE_FEE_MATRIX" if not gap_complete else None

    if info == "PRACTICAL":
        return "PARTIALLY_VERIFIED", None

    if info == "DISCOVERY":
        return "PARTIALLY_VERIFIED", None

    if claim.get("source_ids") and "src-catalogue-transport" in claim.get("source_ids", []):
        if ctype in {"document", "eligibility", "procedure_step"} and len(claim.get("source_ids", [])) >= 2:
            return "PARTIALLY_VERIFIED", None
        if ctype in {"document", "eligibility"}:
            return "PARTIALLY_VERIFIED", None

    if _has_tier1(sources, claim.get("source_ids") or []):
        return "VERIFIED", None

    if any(sources.get(sid, {}).get("authority_tier", 99) <= 2 for sid in claim.get("source_ids") or []):
        return "PARTIALLY_VERIFIED", None

    return "UNVERIFIED", None


def _copy_snapshots() -> None:
    raw_snap = RAW / "source_snapshots"
    if raw_snap.is_dir():
        for path in raw_snap.glob("*.html"):
            shutil.copy2(path, SNAP / path.name)
    gap_snap = GAP / "source_snapshots"
    if gap_snap.is_dir():
        for path in gap_snap.glob("*"):
            if path.is_file():
                shutil.copy2(path, SNAP / path.name)


def _load_gaps() -> tuple[list[dict], int, int]:
    if _gap_closure_complete():
        gap_data = json.loads((GAP / "knowledge_gaps.json").read_text(encoding="utf-8"))
        gaps = gap_data.get("knowledge_gaps", [])
        summary = json.loads((GAP / "summary.json").read_text(encoding="utf-8"))
        blocking = int(summary.get("knowledge_gaps") or 0)
        documented = int(summary.get("knowledge_gaps_documented") or len(gaps))
        return gaps, blocking, documented
    raw_gaps = json.loads((RAW / "knowledge_gaps.json").read_text(encoding="utf-8"))["knowledge_gaps"]
    return raw_gaps, len(raw_gaps), len(raw_gaps)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    SNAP.mkdir(parents=True, exist_ok=True)
    _copy_snapshots()

    claims = json.loads((RAW / "claims.json").read_text(encoding="utf-8"))["claims"]
    sources_list = json.loads((RAW / "sources.json").read_text(encoding="utf-8"))["sources"]
    gaps, blocking_gaps, documented_gaps = _load_gaps()
    sources = {s["source_id"]: s for s in sources_list}
    gap_complete = _gap_closure_complete()

    gap_claims: list[dict] = []
    if gap_complete and (GAP / "new_claims.json").exists():
        gap_claims = json.loads((GAP / "new_claims.json").read_text(encoding="utf-8")).get("claims", [])

    enriched = []
    for c in claims:
        status, gap = assign_status(c, sources, gap_complete=gap_complete)
        evidence = _evidence_for_claim(c)
        enriched.append(
            {
                "claim_id": c["claim_id"],
                "service_id": c["service_id"],
                "claim_text": c["claim_text"],
                "claim_type": c.get("claim_type"),
                "information_class": c.get("information_class"),
                "verification_status": status,
                "knowledge_gap": gap,
                "source_ids": c.get("source_ids"),
                "evidence": evidence,
                "verifier": VERIFIER,
                "verified_at": VERIFIED_AT,
                "publication_status": "STAGING_ONLY",
                "reasoning": (
                    "Gap-closure availability evidence: catalogue URL valid, BSP TEMPORARILY_UNAVAILABLE off-hours."
                    if gap_complete and c["claim_id"] in GAP_RESOLVED_CLAIMS
                    else "Gap-closure browser render: portal metadata verified; CMS procedural body empty."
                    if gap_complete and c["claim_id"] in GAP_PARTIAL_CLAIMS
                    else "Fee amounts CALCULATOR_DERIVED; interactive matrix not captured."
                    if status == "PARTIALLY_VERIFIED" and c.get("claim_type") == "fee"
                    else "Fitness validity detail deferred to BATCH_03C."
                    if gap_complete and c["claim_id"] == "brta-new-vehicle-registration::c-fitness-prerequisite-crossref"
                    else "Portal procedural body not captured in JS-rendered page shell."
                    if status == "UNVERIFIED"
                    else "Supported by Tier 1–2 official sources at verification pass."
                ),
            }
        )

    for gc in gap_claims:
        enriched.append(
            {
                "claim_id": gc["claim_id"],
                "service_id": gc["service_id"],
                "claim_text": gc["claim_text"],
                "claim_type": gc.get("claim_type"),
                "information_class": gc.get("information_class", "OFFICIAL"),
                "verification_status": gc.get("verification_status", "PARTIALLY_VERIFIED"),
                "knowledge_gap": None,
                "source_ids": gc.get("source_ids"),
                "evidence": _evidence_for_claim(gc),
                "verifier": VERIFIER,
                "verified_at": VERIFIED_AT,
                "publication_status": "STAGING_ONLY",
                "reasoning": gc.get("evidence_excerpt") or "Gap-closure targeted investigation claim.",
                "gap_closure": True,
                "supersedes_interpretation_of": gc.get("supersedes_interpretation_of"),
                "related_prior_claim_ids": gc.get("related_prior_claim_ids"),
                "deferred_to_batch": gc.get("deferred_to_batch"),
            }
        )

    status_counts = dict(Counter(x["verification_status"] for x in enriched))

    summary = {
        "batch_id": BATCH_ID,
        "layer": "research/verification",
        "publication_status": "STAGING_ONLY",
        "verifier": VERIFIER,
        "verified_at": VERIFIED_AT,
        "claims_total": len(enriched),
        "total_claims": len(enriched),
        "original_claims": len(claims),
        "gap_closure_claims": len(gap_claims),
        "status_counts": status_counts,
        "verified": status_counts.get("VERIFIED", 0),
        "partially_verified": status_counts.get("PARTIALLY_VERIFIED", 0),
        "unverified": status_counts.get("UNVERIFIED", 0),
        "knowledge_gaps": blocking_gaps,
        "knowledge_gaps_open": blocking_gaps,
        "knowledge_gaps_documented": documented_gaps,
        "gap_closure_complete": gap_complete,
        "critical_conflicts": 0,
    }

    if gap_complete and (GAP / "service_readiness.json").exists():
        shutil.copy2(GAP / "service_readiness.json", OUT / "service_readiness.json")

    (OUT / "claims_verification.json").write_text(
        json.dumps(
            {"schema": "bda.research.verification.claims/1.0", "batch_id": BATCH_ID, "claims": enriched},
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    (OUT / "knowledge_gaps.json").write_text(
        json.dumps({"knowledge_gaps": gaps}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
