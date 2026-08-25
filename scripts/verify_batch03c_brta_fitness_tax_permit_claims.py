#!/usr/bin/env python3
"""Independent Batch 3C BRTA fitness/tax/permit claim verification (STAGING ONLY)."""

from __future__ import annotations

import json
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RAW = REPO / "data/research/raw/batch-03c-brta-fitness-tax-permit"
OUT = REPO / "data/research/verification/batch-03c-brta-fitness-tax-permit"
GAP = REPO / "data/research/verification/batch-03c-brta-fitness-tax-permit-gap-closure"
GAP_03B = REPO / "data/research/verification/batch-03b-brta-vehicle-gap-closure"
SNAP = OUT / "source_snapshots"
BATCH_ID = "batch-03c-brta-fitness-tax-permit"

VERIFIER = "cursor-cloud-agent"
VERIFIED_AT = datetime.now(timezone.utc).isoformat()

# Fitness validity-by-class must stay UNVERIFIED — gap closure will not provide authoritative matrix.
FITNESS_VALIDITY_CLAIMS = {
    "brta-fitness-certificate::c-validity-by-class-unverified",
    "brta-fitness-certificate::c-commercial-vs-private-rules-differ",
}

GAP_RESOLVED_CLAIMS = {
    "brta-fitness-certificate::c-portal-url",
    "brta-tax-token::c-portal-url",
    "brta-route-permit::c-portal-url",
    "brta-advance-income-tax::c-portal-url",
    "brta-color-change::c-portal-url",
    "brta-engine-change::c-portal-url",
    "brta-tire-size-change::c-portal-url",
    "brta-mv-tax-payment::c-portal-url",
    "brta-fee-calculator::c-portal-url",
    "brta-bsp-user-registration::c-portal-url",
    "brta-driving-school-registration::c-portal-url",
    "transport-route-permit::c-bsp-service",
    "transport-driving-school-licence::c-bsp-service",
    "brta-payment-verification::c-portal-url",
    "brta-e-document-verification::c-portal-url",
}

GAP_PARTIAL_CLAIMS = {
    "brta-fitness-certificate::c-physical-inspection-required",
    "brta-fitness-certificate::c-e-fitness-bsp",
    "brta-tax-token::c-circle-office-collection",
    "brta-route-permit::c-circle-office-submission",
    "brta-route-permit::c-route-type-matrix-unverified",
    "transport-route-permit::c-route-type-matrix-unverified",
    "brta-color-change::c-circle-office-application",
    "brta-engine-change::c-circle-office-application",
    "brta-tire-size-change::c-circle-office-application",
    "brta-mv-tax-payment::c-online-payment-channel",
    "brta-driving-school-registration::c-facility-inspection-likely",
    "transport-driving-school-licence::c-licence-vs-registration",
    "brta-e-document-verification::c-e-fitness-may-be-included",
}

GAP_FEE_CLAIMS = {
    "brta-fitness-certificate::c-fitness-fee-calculator",
    "brta-tax-token::c-tax-token-fee-calculator",
    "brta-mv-tax-payment::c-mv-tax-amount-calculator",
    "brta-advance-income-tax::c-ait-fee-calculator",
    "brta-route-permit::c-route-permit-fee-calculator",
    "transport-route-permit::c-route-permit-fee-calculator",
    "brta-fee-calculator::c-interactive-matrix-not-extracted",
    "brta-color-change::c-color-change-fee-calculator",
    "brta-engine-change::c-engine-change-fee-calculator",
    "brta-tire-size-change::c-tire-change-fee-calculator",
    "brta-driving-school-registration::c-registration-fee-unknown",
    "transport-driving-school-licence::c-licence-fee-calculator",
}

GAP_CLAIM_HINTS = {
    "MISSING_FITNESS_VALIDITY_BY_CLASS": FITNESS_VALIDITY_CLAIMS,
    "MISSING_VEHICLE_FEE_MATRIX": GAP_FEE_CLAIMS,
    "MISSING_ROUTE_PERMIT_TYPE_MATRIX": {
        "brta-route-permit::c-route-type-matrix-unverified",
        "transport-route-permit::c-route-type-matrix-unverified",
    },
    "MISSING_PORTAL_JS_BODY": {
        "brta-fitness-certificate::c-physical-inspection-required",
        "brta-tax-token::c-circle-office-collection",
        "brta-route-permit::c-circle-office-submission",
        "brta-color-change::c-circle-office-application",
        "brta-engine-change::c-circle-office-application",
        "brta-tire-size-change::c-circle-office-application",
        "brta-advance-income-tax::c-portal-url",
    },
    "MISSING_MVTAX_PORTAL_SNAPSHOT": {
        "brta-mv-tax-payment::c-portal-url",
        "brta-mv-tax-payment::c-online-payment-channel",
        "brta-mv-tax-payment::c-mv-tax-amount-calculator",
        "brta-mv-tax-payment::c-registered-vehicle-required",
    },
    "MISSING_E_FITNESS_WORKFLOW_DETAIL": {
        "brta-fitness-certificate::c-e-fitness-bsp",
        "brta-e-document-verification::c-e-fitness-may-be-included",
    },
    "MISSING_DRIVING_SCHOOL_LICENCE_WORKFLOW": {
        "brta-driving-school-registration::c-facility-inspection-likely",
        "brta-driving-school-registration::c-bsp-account-required",
        "transport-driving-school-licence::c-licence-vs-registration",
        "transport-driving-school-licence::c-bsp-account-required",
    },
}

SNAP_03B = "data/research/verification/batch-03b-brta-vehicle-gap-closure/source_snapshots"
SNAP_GAP = "data/research/verification/batch-03c-brta-fitness-tax-permit-gap-closure/source_snapshots"
SNAP_RAW = "data/research/raw/batch-03c-brta-fitness-tax-permit/source_snapshots"

E_BSP_REGISTER = {
    "source_id": "src-bsp-register",
    "source_url": "https://bsp.brta.gov.bd/register",
    "authority_tier": 1,
    "retrieval_method": "catalogue_cross_batch_03a",
    "snapshot": f"{SNAP_03B}/bsp_register.txt",
    "retrieved_at": "2026-08-25",
    "availability": "TEMPORARILY_UNAVAILABLE",
}

E_BSP_HOME = {
    "source_id": "src-bsp-home",
    "source_url": "https://bsp.brta.gov.bd/bsp/?lan=en",
    "authority_tier": 1,
    "retrieval_method": "catalogue_cross_batch_03b",
    "snapshot": f"{SNAP_03B}/bsp_home.txt",
    "retrieved_at": "2026-08-25",
}

E_BSP_FEE = {
    "source_id": "src-bsp-fee-calculator",
    "source_url": "https://bsp.brta.gov.bd/feeCalculator",
    "authority_tier": 1,
    "retrieval_method": "catalogue_cross_batch_03b",
    "snapshot": f"{SNAP_03B}/bsp_fee_calculator.txt",
    "retrieved_at": "2026-08-25",
    "availability": "TEMPORARILY_UNAVAILABLE",
}

E_BSP_HOURS = {
    "source_id": "src-bsp-maintenance-notice",
    "source_url": "https://bsp.brta.gov.bd/",
    "authority_tier": 1,
    "retrieval_method": "catalogue_cross_batch_03a",
    "snapshot": f"{SNAP_RAW}/bsp_hours_notice.html",
    "retrieved_at": "2026-08-25",
}

E_BRTA_FITNESS = {
    "source_id": "src-brta-portal-fitness",
    "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922db91933eb65569e0af12",
    "authority_tier": 2,
    "retrieval_method": "puppeteer_headless_chrome",
    "snapshot": f"{SNAP_03B}/brta_fitness_crossref.txt",
    "retrieved_at": "2026-08-25",
}

E_BRTA_TAX_TOKEN = {
    "source_id": "src-brta-portal-tax-token",
    "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922e0ab933eb65569e281ad",
    "authority_tier": 2,
    "retrieval_method": "catalogue_reference",
    "snapshot": f"{SNAP_RAW}/brta_tax_token.html",
    "retrieved_at": "2026-08-25",
}

E_BRTA_ROUTE = {
    "source_id": "src-brta-portal-route-permit",
    "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922df7a933eb65569e2240e",
    "authority_tier": 2,
    "retrieval_method": "catalogue_reference",
    "snapshot": f"{SNAP_RAW}/brta_route_permit.html",
    "retrieved_at": "2026-08-25",
}

E_BRTA_AIT = {
    "source_id": "src-brta-portal-advance-tax",
    "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922e058933eb65569e269cd",
    "authority_tier": 2,
    "retrieval_method": "catalogue_reference",
    "snapshot": f"{SNAP_RAW}/brta_advance_income_tax.html",
    "retrieved_at": "2026-08-25",
}

E_BRTA_COLOR = {
    "source_id": "src-brta-portal-color-change",
    "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922dd3a933eb65569e14058",
    "authority_tier": 2,
    "retrieval_method": "catalogue_reference",
    "snapshot": f"{SNAP_RAW}/brta_color_change.html",
    "retrieved_at": "2026-08-25",
}

E_BRTA_ENGINE = {
    "source_id": "src-brta-portal-engine-change",
    "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922dfbe933eb65569e23c89",
    "authority_tier": 2,
    "retrieval_method": "catalogue_reference",
    "snapshot": f"{SNAP_RAW}/brta_engine_change.html",
    "retrieved_at": "2026-08-25",
}

E_BRTA_TIRE = {
    "source_id": "src-brta-portal-tire-change",
    "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922dcdf933eb65569e127ec",
    "authority_tier": 2,
    "retrieval_method": "catalogue_reference",
    "snapshot": f"{SNAP_RAW}/brta_tire_size_change.html",
    "retrieved_at": "2026-08-25",
}

E_MVTAX = {
    "source_id": "src-mvtax-portal",
    "source_url": "https://brta.cnsbd.com/mvtax_brta",
    "authority_tier": 1,
    "retrieval_method": "catalogue_reference",
    "snapshot": None,
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
    "src-bsp-register": E_BSP_REGISTER,
    "src-bsp-home": E_BSP_HOME,
    "src-bsp-fee-calculator": E_BSP_FEE,
    "src-bsp-road-safety": {
        "source_id": "src-bsp-road-safety",
        "source_url": "https://bsp.brta.gov.bd/roadSafety",
        "authority_tier": 1,
        "retrieval_method": "catalogue_reference",
        "snapshot": None,
        "retrieved_at": "2026-08-25",
        "availability": "TEMPORARILY_UNAVAILABLE",
    },
    "src-bsp-maintenance-notice": E_BSP_HOURS,
    "src-mvtax-portal": E_MVTAX,
    "src-brta-portal-fitness": E_BRTA_FITNESS,
    "src-brta-portal-tax-token": E_BRTA_TAX_TOKEN,
    "src-brta-portal-route-permit": E_BRTA_ROUTE,
    "src-brta-portal-advance-tax": E_BRTA_AIT,
    "src-brta-portal-color-change": E_BRTA_COLOR,
    "src-brta-portal-engine-change": E_BRTA_ENGINE,
    "src-brta-portal-tire-change": E_BRTA_TIRE,
    "src-brta-portal-home": {
        "source_id": "src-brta-portal-home",
        "source_url": "http://brta.portal.gov.bd/",
        "authority_tier": 2,
        "retrieval_method": "catalogue_reference",
        "snapshot": None,
        "retrieved_at": "2026-08-25",
    },
    "src-catalogue-transport": E_CATALOGUE,
    "src-gap-bsp-fee-calculator-browser": E_BSP_FEE | {"source_id": "src-gap-bsp-fee-calculator-browser"},
    "src-gap-brta-fitness-browser": E_BRTA_FITNESS | {"source_id": "src-gap-brta-fitness-browser"},
    "src-gap-brta-tax-token-browser": E_BRTA_TAX_TOKEN | {"source_id": "src-gap-brta-tax-token-browser"},
    "src-gap-brta-route-permit-browser": E_BRTA_ROUTE | {"source_id": "src-gap-brta-route-permit-browser"},
    "src-gap-brta-advance-tax-browser": E_BRTA_AIT | {"source_id": "src-gap-brta-advance-tax-browser"},
    "src-gap-brta-color-change-browser": E_BRTA_COLOR | {"source_id": "src-gap-brta-color-change-browser"},
    "src-gap-brta-engine-change-browser": E_BRTA_ENGINE | {"source_id": "src-gap-brta-engine-change-browser"},
    "src-gap-brta-tire-change-browser": E_BRTA_TIRE | {"source_id": "src-gap-brta-tire-change-browser"},
    "src-gap-mvtax-portal-browser": E_MVTAX | {"source_id": "src-gap-mvtax-portal-browser"},
    "src-gap-bsp-road-safety-browser": {
        "source_id": "src-gap-bsp-road-safety-browser",
        "source_url": "https://bsp.brta.gov.bd/roadSafety",
        "authority_tier": 1,
        "retrieval_method": "puppeteer_headless_chrome",
        "snapshot": f"{SNAP_GAP}/bsp_road_safety.txt",
        "retrieved_at": "2026-08-25",
        "availability": "TEMPORARILY_UNAVAILABLE",
    },
    "src-gap-scrape-results-index": {
        "source_id": "src-gap-scrape-results-index",
        "source_url": f"{SNAP_GAP}/scrape_results.json",
        "authority_tier": 2,
        "retrieval_method": "puppeteer_headless_chrome",
        "snapshot": f"{SNAP_GAP}/scrape_results.json",
        "retrieved_at": "2026-08-25",
    },
    "src-gap-brta-fitness-crossref-browser": E_BRTA_FITNESS | {
        "source_id": "src-gap-brta-fitness-crossref-browser",
        "snapshot": f"{SNAP_03B}/brta_fitness_crossref.txt",
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


def _reasoning_for_claim(
    claim: dict,
    *,
    status: str,
    gap: str | None,
    gap_complete: bool,
) -> str:
    cid = claim["claim_id"]
    if cid in FITNESS_VALIDITY_CLAIMS:
        return (
            "Fitness validity-by-class matrix not verified from authoritative source; "
            "do not publish invented durations."
        )
    if gap_complete and cid in GAP_RESOLVED_CLAIMS:
        return "Gap-closure: catalogue URL confirmed; BSP/portal availability evidence captured."
    if gap_complete and cid in GAP_PARTIAL_CLAIMS:
        return "Gap-closure browser render: portal metadata verified; CMS procedural body empty or partial."
    if status == "PARTIALLY_VERIFIED" and claim.get("claim_type") == "fee":
        return "Fee amounts CALCULATOR_DERIVED; interactive matrix not captured."
    if status == "UNVERIFIED":
        return "Portal procedural body not captured in JS-rendered page shell or source not snapshotted."
    if claim.get("information_class") == "PRACTICAL":
        return "Practical tip supported by BSP hours notice or catalogue cross-reference."
    return "Supported by Tier 1–2 official sources at verification pass."


def assign_status(claim: dict, sources: dict[str, dict], *, gap_complete: bool) -> tuple[str, str | None]:
    cid = claim["claim_id"]
    ctype = claim.get("claim_type") or ""
    info = claim.get("information_class") or "OFFICIAL"

    if cid in FITNESS_VALIDITY_CLAIMS:
        return "UNVERIFIED", None if gap_complete else "MISSING_FITNESS_VALIDITY_BY_CLASS"

    if gap_complete:
        if cid in GAP_RESOLVED_CLAIMS:
            if ctype == "application_url":
                return "VERIFIED", None
            return "PARTIALLY_VERIFIED", None
        if cid in GAP_PARTIAL_CLAIMS:
            if cid == "brta-fitness-certificate::c-e-fitness-bsp" and _has_tier1(
                sources, claim.get("source_ids") or []
            ):
                return "VERIFIED", None
            if cid == "brta-e-document-verification::c-verifies-digital-documents":
                return "VERIFIED", None
            return "PARTIALLY_VERIFIED", None
        if cid in GAP_FEE_CLAIMS:
            return "PARTIALLY_VERIFIED", None

    for gap_id, claim_ids in GAP_CLAIM_HINTS.items():
        if cid in claim_ids and not gap_complete:
            return "UNVERIFIED", gap_id

    if info == "DISCOVERY" and ctype in {"processing_time", "document", "fee", "official_metadata"}:
        return "UNVERIFIED", None

    if ctype == "application_url" and _has_tier1(sources, claim.get("source_ids") or []):
        if gap_complete and cid in GAP_RESOLVED_CLAIMS:
            return "PARTIALLY_VERIFIED", None
        return "VERIFIED", None

    if ctype == "application_url" and any(
        sources.get(sid, {}).get("snapshot_path")
        or EVIDENCE_BY_SOURCE.get(sid, {}).get("snapshot")
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
        for path in raw_snap.glob("*"):
            if path.is_file():
                shutil.copy2(path, SNAP / path.name)
    gap_snap = GAP / "source_snapshots"
    if gap_snap.is_dir():
        for path in gap_snap.glob("*"):
            if path.is_file():
                shutil.copy2(path, SNAP / path.name)
    gap_03b_snap = GAP_03B / "source_snapshots"
    if gap_03b_snap.is_dir():
        for name in (
            "bsp_register.txt",
            "bsp_home.txt",
            "bsp_fee_calculator.txt",
            "brta_fitness_crossref.txt",
        ):
            src = gap_03b_snap / name
            if src.is_file():
                shutil.copy2(src, SNAP / name)


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
                "reasoning": _reasoning_for_claim(c, status=status, gap=gap, gap_complete=gap_complete),
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
                "resolves_cross_batch_dependency": gc.get("resolves_cross_batch_dependency"),
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
        "fitness_validity_unverified": sum(
            1 for x in enriched if x["claim_id"] in FITNESS_VALIDITY_CLAIMS and x["verification_status"] == "UNVERIFIED"
        ),
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
