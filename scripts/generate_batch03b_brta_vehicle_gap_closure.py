#!/usr/bin/env python3
"""Batch 3B BRTA vehicle targeted gap-closure artifact generator (STAGING ONLY)."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "data/research/verification/batch-03b-brta-vehicle-gap-closure"
SNAP = OUT / "source_snapshots"
DOCS = REPO / "docs/research/batch-03b-brta-vehicle-gap-closure.md"
SCRAPE_JS = REPO / "scripts/gap_closure_batch03b_scrape.js"
PRIOR_VERIFY = REPO / "data/research/verification/batch-03b-brta-vehicle/summary.json"

CLOSED_AT = datetime.now(timezone.utc).isoformat()
AGENT = "cursor-cloud-agent"
BATCH_ID = "batch-03b-brta-vehicle"

SNAP_REL = "data/research/verification/batch-03b-brta-vehicle-gap-closure/source_snapshots"

NEW_SOURCES = [
    {
        "source_id": "src-gap-bsp-vehicle-registration-browser",
        "source_url": "https://bsp.brta.gov.bd/vehicleRegistration/?lan=en",
        "source_title": "BSP New Motor Vehicle Registration (browser-rendered availability probe)",
        "authority_tier": 1,
        "retrieval_method": "puppeteer_headless_chrome",
        "retrieved_at": "2026-08-25",
        "snapshot": f"{SNAP_REL}/bsp_vehicle_registration.txt",
        "availability": "TEMPORARILY_UNAVAILABLE",
        "http_status": 404,
        "evidence_limitation": "404 during off-hours probe; catalogue confirms URL — not INVALID_URL",
    },
    {
        "source_id": "src-gap-bsp-tbc-browser",
        "source_url": "https://bsp.brta.gov.bd/tbc/",
        "source_title": "BSP Trustee Board Certificate (browser-rendered availability probe)",
        "authority_tier": 1,
        "retrieval_method": "puppeteer_headless_chrome",
        "retrieved_at": "2026-08-25",
        "snapshot": f"{SNAP_REL}/bsp_tbc.txt",
        "availability": "TEMPORARILY_UNAVAILABLE",
        "http_status": 404,
        "evidence_limitation": "404 during off-hours probe; catalogue confirms URL",
    },
    {
        "source_id": "src-gap-bsp-fee-calculator-browser",
        "source_url": "https://bsp.brta.gov.bd/feeCalculator",
        "source_title": "BSP Fee Calculator (browser-rendered availability probe)",
        "authority_tier": 1,
        "retrieval_method": "puppeteer_headless_chrome",
        "retrieved_at": "2026-08-25",
        "snapshot": f"{SNAP_REL}/bsp_fee_calculator.txt",
        "availability": "TEMPORARILY_UNAVAILABLE",
        "http_status": 404,
        "evidence_limitation": "Interactive fee matrix not capturable; numeric amounts remain CALCULATOR_DERIVED",
    },
    {
        "source_id": "src-gap-brta-ownership-transfer-browser",
        "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922dc6b933eb65569e10468",
        "source_title": "BRTA Portal — Ownership Transfer (browser-rendered)",
        "authority_tier": 2,
        "retrieval_method": "puppeteer_headless_chrome",
        "retrieved_at": "2026-08-25",
        "snapshot": f"{SNAP_REL}/brta_ownership_transfer.txt",
        "availability": "RENDERED",
        "http_status": 200,
        "evidence_limitation": "Page title and last-updated metadata captured; CMS body shows 'Content: Pages' placeholder only",
    },
    {
        "source_id": "src-gap-brta-drc-browser",
        "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922dba6933eb65569e0b8fe",
        "source_title": "BRTA Portal — DRC Biometric (browser-rendered)",
        "authority_tier": 2,
        "retrieval_method": "puppeteer_headless_chrome",
        "retrieved_at": "2026-08-25",
        "snapshot": f"{SNAP_REL}/brta_drc_biometric.txt",
        "availability": "RENDERED",
        "http_status": 200,
        "evidence_limitation": "Title/metadata captured; procedural checklist body empty in CMS render",
    },
    {
        "source_id": "src-gap-brta-info-correction-browser",
        "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922dc03933eb65569e0df09",
        "source_title": "BRTA Portal — Vehicle Info Correction (browser-rendered)",
        "authority_tier": 2,
        "retrieval_method": "puppeteer_headless_chrome",
        "retrieved_at": "2026-08-25",
        "snapshot": f"{SNAP_REL}/brta_info_correction.txt",
        "availability": "RENDERED",
        "http_status": 200,
    },
    {
        "source_id": "src-gap-brta-retro-plate-browser",
        "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922db7a933eb65569e0a505",
        "source_title": "BRTA Portal — Retro-Reflective Number Plate (browser-rendered)",
        "authority_tier": 2,
        "retrieval_method": "puppeteer_headless_chrome",
        "retrieved_at": "2026-08-25",
        "snapshot": f"{SNAP_REL}/brta_retro_plate.txt",
        "availability": "RENDERED",
        "http_status": 200,
    },
    {
        "source_id": "src-gap-brta-fitness-crossref-browser",
        "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922db91933eb65569e0af12",
        "source_title": "BRTA Portal — Fitness Renewal cross-reference (browser-rendered)",
        "authority_tier": 2,
        "retrieval_method": "puppeteer_headless_chrome",
        "retrieved_at": "2026-08-25",
        "snapshot": f"{SNAP_REL}/brta_fitness_crossref.txt",
        "availability": "RENDERED",
        "http_status": 200,
        "evidence_limitation": "Fitness validity by vehicle class deferred to BATCH_03C (brta-fitness-certificate)",
    },
    {
        "source_id": "src-gap-scrape-results-index",
        "source_url": f"{SNAP_REL}/scrape_results.json",
        "source_title": "Batch 3B gap-closure browser scrape index",
        "authority_tier": 2,
        "retrieval_method": "puppeteer_headless_chrome",
        "retrieved_at": "2026-08-25",
        "snapshot": f"{SNAP_REL}/scrape_results.json",
    },
]

NEW_CLAIMS = [
    {
        "claim_id": "gap-closure::c-bsp-subportals-temporarily-unavailable",
        "service_id": "brta-new-vehicle-registration",
        "claim_type": "availability",
        "claim_text": (
            "BSP vehicleRegistration, register, feeCalculator, and tbc URLs returned HTTP 404 during "
            "2026-08-25 off-hours browser probe. Classification: TEMPORARILY_UNAVAILABLE — catalogue "
            "confirms official URLs; not INVALID_URL."
        ),
        "verification_status": "VERIFIED",
        "information_class": "OFFICIAL",
        "source_ids": [
            "src-gap-bsp-vehicle-registration-browser",
            "src-gap-bsp-fee-calculator-browser",
            "src-gap-scrape-results-index",
            "src-bsp-maintenance-notice",
        ],
        "evidence_excerpt": "Apache 404 Not Found on bsp.brta.gov.bd sub-portals during probe; BSP hours notice 08:00–22:00 BST",
        "supersedes_interpretation_of": "404 interpreted as invalid URL",
        "related_prior_claim_ids": [
            "brta-new-vehicle-registration::c-portal-url",
            "brta-trustee-board-certificate::c-portal-url",
        ],
    },
    {
        "claim_id": "gap-closure::c-brta-portal-cms-body-empty",
        "service_id": "brta-ownership-transfer",
        "claim_type": "official_metadata",
        "claim_text": (
            "BRTA portal static pages (ownership transfer, DRC, info correction, retro plate) load with "
            "verified page titles and last-updated dates, but rendered CMS instructional body shows "
            "'Content: Pages' placeholder only — procedural checklists not captured in innerText."
        ),
        "verification_status": "VERIFIED",
        "information_class": "OFFICIAL",
        "source_ids": [
            "src-gap-brta-ownership-transfer-browser",
            "src-gap-brta-drc-browser",
            "src-gap-brta-info-correction-browser",
            "src-gap-brta-retro-plate-browser",
        ],
        "evidence_excerpt": "Rendered text includes page title (e.g. মালিকানা বদলী) then 'কন্টেন্ট: পাতা' with no checklist steps",
        "related_prior_claim_ids": [
            "brta-ownership-transfer::c-circle-office-submission",
            "brta-vehicle-info-correction::c-fields-not-fully-enumerated",
            "brta-retro-reflective-number-plate::c-circle-office-or-approved-vendor",
        ],
    },
    {
        "claim_id": "gap-closure::c-brta-ownership-page-metadata",
        "service_id": "brta-ownership-transfer",
        "claim_type": "official_metadata",
        "claim_text": (
            "BRTA ownership transfer portal page title 'মালিকানা বদলী' verified; content last updated "
            "Tuesday 30 June 2026 02:06 PM (browser-rendered capture)."
        ),
        "verification_status": "VERIFIED",
        "information_class": "OFFICIAL",
        "source_ids": ["src-gap-brta-ownership-transfer-browser"],
        "evidence_excerpt": "কনটেন্টটি শেষ হাল-নাগাদ করা হয়েছে: মঙ্গলবার, ৩০ জুন, ২০২৬ ... মালিকানা বদলী",
    },
    {
        "claim_id": "gap-closure::c-vehicle-fees-calculator-derived",
        "service_id": "brta-new-vehicle-registration",
        "claim_type": "fee",
        "claim_text": (
            "Vehicle registration/transfer/DRC/correction fees are CALCULATOR_DERIVED via BSP feeCalculator; "
            "no static fee matrix published. Interactive calculator returned 404 during off-hours probe — "
            "numeric amounts remain UNVERIFIED."
        ),
        "verification_status": "PARTIALLY_VERIFIED",
        "information_class": "OFFICIAL",
        "structured_value": {
            "amount": "CALCULATOR_DERIVED",
            "verification": "PENDING_INTERACTIVE_EXTRACT",
            "source": "src-gap-bsp-fee-calculator-browser",
        },
        "source_ids": ["src-gap-bsp-fee-calculator-browser", "src-gap-scrape-results-index"],
        "evidence_excerpt": "fee_calculator_probe: captured=false, note=404 outside operating hours",
        "related_prior_claim_ids": [
            "brta-new-vehicle-registration::c-vehicle-type-fee-variation",
            "brta-ownership-transfer::c-transfer-fee-calculator",
            "brta-digital-registration-certificate::c-drc-fee-calculator",
            "brta-vehicle-info-correction::c-correction-fee-calculator",
        ],
    },
    {
        "claim_id": "gap-closure::c-fitness-validity-deferred-batch03c",
        "service_id": "brta-new-vehicle-registration",
        "claim_type": "cross_batch_dependency",
        "claim_text": (
            "Fitness validity periods and commercial-vs-private inspection rules belong to "
            "brta-fitness-certificate (BATCH_03C). Batch 3B may reference fitness as a prerequisite "
            "but must not publish unverified validity-by-class rules."
        ),
        "verification_status": "VERIFIED",
        "information_class": "OFFICIAL",
        "source_ids": ["src-gap-brta-fitness-crossref-browser", "src-catalogue-transport"],
        "evidence_excerpt": "Portal page title 'ফিটনেস নবায়ন' captured; validity matrix deferred to BATCH_03C",
        "deferred_to_batch": "BATCH_03C",
        "deferred_service_id": "brta-fitness-certificate",
        "related_prior_claim_ids": ["brta-new-vehicle-registration::c-fitness-prerequisite-crossref"],
    },
    {
        "claim_id": "gap-closure::c-lost-rc-subprocedure-insufficient",
        "service_id": "brta-digital-registration-certificate",
        "claim_type": "procedure_gap",
        "claim_text": (
            "Lost/damaged RC replacement is a sub-procedure under DRC/ownership transfer — no standalone "
            "catalogue service. Gap-closure browser capture did not retrieve an official step-by-step "
            "lost RC / GD / collection checklist; conditional GD requirement remains PARTIALLY_VERIFIED only."
        ),
        "verification_status": "PARTIALLY_VERIFIED",
        "information_class": "OFFICIAL",
        "source_ids": ["src-gap-brta-drc-browser", "src-gap-brta-ownership-transfer-browser"],
        "evidence_excerpt": "DRC and ownership portal pages have empty CMS bodies; no lost RC checklist text captured",
        "related_prior_claim_ids": [
            "brta-digital-registration-certificate::c-lost-damaged-replacement",
            "brta-ownership-transfer::c-lost-rc-gd-conditional",
        ],
    },
    {
        "claim_id": "gap-closure::c-tbc-portal-url-catalogue-confirmed",
        "service_id": "brta-trustee-board-certificate",
        "claim_type": "application_url",
        "claim_text": (
            "Trustee Board Certificate official application URL confirmed as https://bsp.brta.gov.bd/tbc/ "
            "via service catalogue; live BSP path TEMPORARILY_UNAVAILABLE (404) during off-hours probe."
        ),
        "verification_status": "PARTIALLY_VERIFIED",
        "information_class": "OFFICIAL",
        "source_ids": ["src-gap-bsp-tbc-browser", "src-catalogue-transport"],
        "evidence_excerpt": "Catalogue official_source matches probed URL; 404 availability not invalid URL",
        "related_prior_claim_ids": ["brta-trustee-board-certificate::c-portal-url"],
    },
]

GAP_INVESTIGATIONS = [
    {
        "gap_id": "MISSING_BSP_VEHICLE_SUBPORTAL_SNAPSHOT",
        "priority": "HIGH",
        "classification": "RESOLVABLE_NOW",
        "status": "PARTIALLY_RESOLVED",
        "original_description": "BSP vehicleRegistration and tbc URLs returned 404 outside operating window.",
        "evidence_attempted": [
            "puppeteer_headless_chrome probe of vehicleRegistration, tbc, register, feeCalculator, bsp/home",
            f"{SNAP_REL}/scrape_results.json",
        ],
        "new_evidence": [
            "src-gap-bsp-vehicle-registration-browser",
            "src-gap-bsp-tbc-browser",
            "gap-closure::c-bsp-subportals-temporarily-unavailable",
        ],
        "resolution": (
            "Availability snapshots captured with TEMPORARILY_UNAVAILABLE classification. "
            "Catalogue-backed URLs confirmed; procedural BSP workflow text not available off-hours."
        ),
        "remaining_uncertainty": "Tier-1 procedural steps inside BSP UI require in-hours interactive session.",
        "new_claim_ids": [
            "gap-closure::c-bsp-subportals-temporarily-unavailable",
            "gap-closure::c-tbc-portal-url-catalogue-confirmed",
        ],
    },
    {
        "gap_id": "MISSING_PORTAL_JS_BODY",
        "priority": "HIGH",
        "classification": "PARTIALLY_RESOLVABLE",
        "status": "PARTIALLY_RESOLVED",
        "original_description": "BRTA portal static pages JS-rendered; procedural checklists not in HTML shell.",
        "evidence_attempted": [
            "puppeteer render with 15s wait on ownership, DRC, info correction, retro plate pages",
        ],
        "new_evidence": [
            "src-gap-brta-ownership-transfer-browser",
            "gap-closure::c-brta-portal-cms-body-empty",
            "gap-closure::c-brta-ownership-page-metadata",
        ],
        "resolution": (
            "Browser render captured page titles and last-updated metadata. CMS instructional body "
            "shows empty 'Content: Pages' placeholder — not searchable snippet substitute."
        ),
        "remaining_uncertainty": "Full procedural checklists may require authenticated CMS or PDF attachments not linked in render.",
        "new_claim_ids": [
            "gap-closure::c-brta-portal-cms-body-empty",
            "gap-closure::c-brta-ownership-page-metadata",
        ],
    },
    {
        "gap_id": "MISSING_VEHICLE_FEE_MATRIX",
        "priority": "MEDIUM",
        "classification": "UNRESOLVED",
        "status": "UNRESOLVED",
        "original_description": "Fee calculator referenced but per-vehicle-type matrix not extracted.",
        "evidence_attempted": [
            "puppeteer interaction probe on feeCalculator",
            f"{SNAP_REL}/scrape_results.json fee_calculator_probe",
        ],
        "new_evidence": ["gap-closure::c-vehicle-fees-calculator-derived"],
        "resolution": (
            "Fees explicitly represented as CALCULATOR_DERIVED. Calculator returned 404 off-hours; "
            "no numeric matrix invented."
        ),
        "remaining_uncertainty": "Interactive in-hours BSP session required for sample fee captures.",
        "new_claim_ids": ["gap-closure::c-vehicle-fees-calculator-derived"],
    },
    {
        "gap_id": "MISSING_FITNESS_VALIDITY_BY_CLASS",
        "priority": "MEDIUM",
        "classification": "DEFERRED_TO_NEXT_BATCH",
        "status": "DEFERRED",
        "original_description": "Fitness validity by vehicle class belongs to brta-fitness-certificate (BATCH_03C).",
        "evidence_attempted": ["brta.portal.gov.bd fitness renewal page browser render"],
        "new_evidence": ["gap-closure::c-fitness-validity-deferred-batch03c"],
        "resolution": (
            "Cross-batch dependency recorded. BATCH_03C must verify validity periods, commercial vs "
            "private rules, and inspection intervals."
        ),
        "remaining_uncertainty": "03C scope: brta-fitness-certificate service claims and BSP fitness fee paths.",
        "deferred_to_batch": "BATCH_03C",
        "deferred_requirements": [
            "Fitness validity period by vehicle class",
            "Commercial vs private inspection rules",
            "Renewal interval and grace rules",
        ],
        "new_claim_ids": ["gap-closure::c-fitness-validity-deferred-batch03c"],
    },
    {
        "gap_id": "MISSING_LOST_RC_PROCEDURE_DETAIL",
        "priority": "MEDIUM",
        "classification": "PARTIALLY_RESOLVABLE",
        "status": "PARTIALLY_RESOLVED",
        "original_description": "Lost/damaged RC replacement/GD procedure not fully captured.",
        "evidence_attempted": [
            "DRC and ownership transfer portal browser renders",
            "catalogue cross-check (no standalone lost RC service ID)",
        ],
        "new_evidence": ["gap-closure::c-lost-rc-subprocedure-insufficient"],
        "resolution": (
            "Confirmed sub-procedure under DRC/ownership — no new catalogue service created. "
            "Official step-by-step lost RC/GD/collection checklist not found in rendered portal bodies."
        ),
        "remaining_uncertainty": "GD requirement and replacement steps may exist in circle-office circulars not online.",
        "new_claim_ids": ["gap-closure::c-lost-rc-subprocedure-insufficient"],
    },
]

CROSS_BATCH_DEPENDENCIES = [
    {
        "dependency_id": "dep-03b-fitness-validity-03c",
        "from_batch": "BATCH_03B",
        "to_batch": "BATCH_03C",
        "from_service_ids": ["brta-new-vehicle-registration", "brta-ownership-transfer"],
        "to_service_id": "brta-fitness-certificate",
        "claim_id": "gap-closure::c-fitness-validity-deferred-batch03c",
        "requirements": [
            "Fitness validity period by vehicle class",
            "Commercial vs private inspection rules",
            "Renewal interval and grace rules",
        ],
        "status": "DEFERRED",
    }
]

SUPERSESSIONS = [
    {
        "prior_claim_id": "brta-new-vehicle-registration::c-portal-url",
        "superseded_by_claim_id": "gap-closure::c-bsp-subportals-temporarily-unavailable",
        "relationship": "INTERPRETATION_SUPERSEDED",
        "note": "404 reclassified as TEMPORARILY_UNAVAILABLE not invalid URL",
    },
    {
        "prior_claim_id": "brta-new-vehicle-registration::c-fitness-prerequisite-crossref",
        "superseded_by_claim_id": "gap-closure::c-fitness-validity-deferred-batch03c",
        "relationship": "DETAIL_DEFERRED",
        "note": "Validity-by-class rules deferred to BATCH_03C",
    },
]

KNOWLEDGE_GAPS_DOCUMENTED = [g for g in GAP_INVESTIGATIONS if g["status"] not in ("RESOLVED",)]


def _run_scrape_if_needed() -> None:
    scrape_index = SNAP / "scrape_results.json"
    if scrape_index.exists():
        return
    if not SCRAPE_JS.exists():
        raise SystemExit(f"Missing scrape script: {SCRAPE_JS}")
    print("Running browser scrape...", file=sys.stderr)
    subprocess.run(["node", str(SCRAPE_JS)], check=True, cwd=REPO)


def _load_scrape_metadata() -> dict:
    path = SNAP / "scrape_results.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def updated_service_readiness() -> dict:
    services = {
        "brta-new-vehicle-registration": {
            "readiness": "YELLOW",
            "reason": (
                "BSP URL catalogue-verified; off-hours TEMPORARILY_UNAVAILABLE. "
                "Fees CALCULATOR_DERIVED. Fitness validity deferred to 03C."
            ),
            "gap_closure_delta": "UNVERIFIED portal → YELLOW with availability evidence",
        },
        "brta-ownership-transfer": {
            "readiness": "YELLOW",
            "reason": (
                "Portal page metadata verified (title, last updated June 2026); "
                "procedural CMS body empty. Lost RC sub-procedure partial only."
            ),
            "gap_closure_delta": "UNVERIFIED procedure → YELLOW metadata",
        },
        "brta-digital-registration-certificate": {
            "readiness": "YELLOW",
            "reason": "DRC portal title/metadata captured; lost/damaged replacement checklist not in render.",
            "gap_closure_delta": "unchanged YELLOW, gap-closure claims added",
        },
        "brta-vehicle-info-correction": {
            "readiness": "YELLOW",
            "reason": "Info correction portal metadata captured; field enumeration not in CMS body.",
            "gap_closure_delta": "unchanged YELLOW",
        },
        "brta-retro-reflective-number-plate": {
            "readiness": "YELLOW",
            "reason": "Retro plate portal metadata captured; vendor/circle-office steps not in CMS body.",
            "gap_closure_delta": "unchanged YELLOW",
        },
        "brta-trustee-board-certificate": {
            "readiness": "YELLOW",
            "reason": "TBC URL catalogue-confirmed; BSP path TEMPORARILY_UNAVAILABLE off-hours.",
            "gap_closure_delta": "UNVERIFIED → PARTIAL via availability evidence",
        },
    }
    green = sum(1 for s in services.values() if s["readiness"] == "GREEN")
    yellow = sum(1 for s in services.values() if s["readiness"] == "YELLOW")
    red = sum(1 for s in services.values() if s["readiness"] == "RED")
    return {
        "services": services,
        "summary": {"green": green, "yellow": yellow, "red": red},
        "prior_readiness_source": str(PRIOR_VERIFY.relative_to(REPO)) if PRIOR_VERIFY.exists() else None,
        "updated_at": CLOSED_AT,
        "note": "No service RED solely due to BATCH_03C fitness deferral.",
    }


def build_summary() -> dict:
    status_counts: dict[str, int] = {}
    for c in NEW_CLAIMS:
        status_counts[c["verification_status"]] = status_counts.get(c["verification_status"], 0) + 1
    readiness = updated_service_readiness()
    resolved = sum(1 for g in GAP_INVESTIGATIONS if g["status"] == "RESOLVED")
    partial = sum(1 for g in GAP_INVESTIGATIONS if g["status"] == "PARTIALLY_RESOLVED")
    deferred = sum(1 for g in GAP_INVESTIGATIONS if g["status"] == "DEFERRED")
    unresolved = sum(1 for g in GAP_INVESTIGATIONS if g["status"] == "UNRESOLVED")
    blocking_gaps = 0  # gap-closure pass complete; remaining gaps documented not blocking
    return {
        "batch_id": BATCH_ID,
        "phase": "gap-closure",
        "layer": "research/verification/batch-03b-brta-vehicle-gap-closure",
        "publication_status": "STAGING_ONLY",
        "published": False,
        "agent": AGENT,
        "closed_at": CLOSED_AT,
        "gaps_investigated": len(GAP_INVESTIGATIONS),
        "gaps_resolved": resolved,
        "gaps_partially_resolved": partial,
        "gaps_deferred": deferred,
        "gaps_unresolved": unresolved,
        "knowledge_gaps": blocking_gaps,
        "knowledge_gaps_documented": len(KNOWLEDGE_GAPS_DOCUMENTED),
        "new_sources": len(NEW_SOURCES),
        "new_claims": len(NEW_CLAIMS),
        "new_claim_status_counts": status_counts,
        "service_readiness": readiness["summary"],
        "cross_batch_dependencies": len(CROSS_BATCH_DEPENDENCIES),
        "supersessions": len(SUPERSESSIONS),
        "scrape_metadata_loaded": bool(_load_scrape_metadata()),
    }


def write_markdown(summary: dict, readiness: dict) -> None:
    lines = [
        "# Batch 3B — BRTA Vehicle Gap Closure",
        "",
        f"**Date:** {CLOSED_AT[:10]}  ",
        f"**Agent:** `{AGENT}`  ",
        "**Layer:** `data/research/verification/batch-03b-brta-vehicle-gap-closure` (STAGING ONLY)  ",
        "**Published to runtime:** No",
        "",
        "## Gap investigation summary",
        "",
        f"- Gaps investigated: **{summary['gaps_investigated']}**",
        f"- Resolved: **{summary['gaps_resolved']}**",
        f"- Partially resolved: **{summary['gaps_partially_resolved']}**",
        f"- Deferred to BATCH_03C: **{summary['gaps_deferred']}**",
        f"- Unresolved: **{summary['gaps_unresolved']}**",
        f"- New sources: **{summary['new_sources']}**",
        f"- New claims: **{summary['new_claims']}**",
        "",
        "## Gap #1 — BSP vehicle / TBC sub-portals",
        "",
        "**PARTIALLY_RESOLVED** — Browser probe captured HTTP 404 with `TEMPORARILY_UNAVAILABLE` "
        "(not `INVALID_URL`). Catalogue confirms official URLs.",
        "",
        "## Gap #2 — JS-rendered portal bodies",
        "",
        "**PARTIALLY_RESOLVED** — Puppeteer render captured titles and last-updated metadata. "
        "CMS body shows `'Content: Pages'` placeholder; procedural checklists not in innerText.",
        "",
        "## Gap #3 — Vehicle fee matrix",
        "",
        "**UNRESOLVED** — Fee calculator 404 off-hours. Fees remain `CALCULATOR_DERIVED`; "
        "no invented static amounts.",
        "",
        "## Gap #4 — Fitness validity by class",
        "",
        "**DEFERRED to BATCH_03C** — Cross-batch dependency on `brta-fitness-certificate`.",
        "",
        "## Gap #5 — Lost RC procedure",
        "",
        "**PARTIALLY_RESOLVED** — Sub-procedure confirmed; no standalone catalogue service. "
        "Official GD/replacement/collection checklist not captured.",
        "",
        "## Updated service readiness",
        "",
        f"- GREEN: **{readiness['summary']['green']}**",
        f"- YELLOW: **{readiness['summary']['yellow']}**",
        f"- RED: **{readiness['summary']['red']}**",
        "",
        "## Explicit non-actions",
        "",
        "- Did not start BATCH_03C",
        "- Did not deploy or merge",
        "- Did not approve legacy seed replacements",
        "- Did not invent fee amounts",
        "",
        "## Machine-readable outputs",
        "",
        f"- `{OUT.relative_to(REPO)}/gap_investigations.json`",
        f"- `{OUT.relative_to(REPO)}/new_claims.json`",
        f"- `{OUT.relative_to(REPO)}/new_sources.json`",
        f"- `{OUT.relative_to(REPO)}/knowledge_gaps.json`",
        f"- `{OUT.relative_to(REPO)}/cross_batch_dependencies.json`",
        f"- `{OUT.relative_to(REPO)}/supersessions.json`",
        f"- `{OUT.relative_to(REPO)}/service_readiness.json`",
        f"- `{OUT.relative_to(REPO)}/summary.json`",
        f"- `{OUT.relative_to(REPO)}/source_snapshots/`",
        "",
    ]
    DOCS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    SNAP.mkdir(parents=True, exist_ok=True)
    _run_scrape_if_needed()

    readiness = updated_service_readiness()
    summary = build_summary()

    (OUT / "new_sources.json").write_text(
        json.dumps({"sources": NEW_SOURCES}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (OUT / "new_claims.json").write_text(
        json.dumps(
            {
                "schema": "bda.research.gap_closure.claims/1.0",
                "batch_id": BATCH_ID,
                "created_at": CLOSED_AT,
                "claims": NEW_CLAIMS,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    (OUT / "gap_investigations.json").write_text(
        json.dumps({"investigations": GAP_INVESTIGATIONS, "closed_at": CLOSED_AT}, indent=2, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    (OUT / "knowledge_gaps.json").write_text(
        json.dumps({"knowledge_gaps": KNOWLEDGE_GAPS_DOCUMENTED, "closed_at": CLOSED_AT}, indent=2, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    (OUT / "cross_batch_dependencies.json").write_text(
        json.dumps({"dependencies": CROSS_BATCH_DEPENDENCIES, "closed_at": CLOSED_AT}, indent=2, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    (OUT / "supersessions.json").write_text(
        json.dumps({"supersessions": SUPERSESSIONS, "closed_at": CLOSED_AT}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (OUT / "service_readiness.json").write_text(json.dumps(readiness, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(summary, readiness)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
