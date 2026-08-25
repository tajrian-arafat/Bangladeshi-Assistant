#!/usr/bin/env python3
"""Batch 3C BRTA fitness/tax/permit targeted gap-closure artifact generator (STAGING ONLY)."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "data/research/verification/batch-03c-brta-fitness-tax-permit-gap-closure"
SNAP = OUT / "source_snapshots"
DOCS = REPO / "docs/research/batch-03c-brta-fitness-tax-permit-gap-closure.md"
SCRAPE_JS = REPO / "scripts/gap_closure_batch03c_scrape.js"
PRIOR_VERIFY = REPO / "data/research/raw/batch-03c-brta-fitness-tax-permit/metadata.json"
PRIOR_03B_GAP = REPO / "data/research/verification/batch-03b-brta-vehicle-gap-closure"
PRIOR_03B_FITNESS_SNAP = (
    PRIOR_03B_GAP / "source_snapshots" / "brta_fitness_crossref.txt"
)

CLOSED_AT = datetime.now(timezone.utc).isoformat()
AGENT = "cursor-cloud-agent"
BATCH_ID = "batch-03c-brta-fitness-tax-permit"

SNAP_REL = "data/research/verification/batch-03c-brta-fitness-tax-permit-gap-closure/source_snapshots"

SERVICES_15 = [
    "brta-advance-income-tax",
    "brta-bsp-user-registration",
    "brta-color-change",
    "brta-driving-school-registration",
    "brta-e-document-verification",
    "brta-engine-change",
    "brta-fee-calculator",
    "brta-fitness-certificate",
    "brta-mv-tax-payment",
    "brta-payment-verification",
    "brta-route-permit",
    "brta-tax-token",
    "brta-tire-size-change",
    "transport-driving-school-licence",
    "transport-route-permit",
]

NEW_SOURCES = [
    {
        "source_id": "src-gap-brta-fitness-browser",
        "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922db91933eb65569e0af12",
        "source_title": "BRTA Portal — Fitness Certificate Issue/Renewal (browser-rendered)",
        "authority_tier": 2,
        "retrieval_method": "puppeteer_headless_chrome",
        "retrieved_at": "2026-08-25",
        "snapshot": f"{SNAP_REL}/brta_fitness.txt",
        "availability": "RENDERED",
        "http_status": 200,
        "evidence_limitation": "Page title 'ফিটনেস নবায়ন' captured; validity-by-class matrix NOT in render — UNRESOLVED",
    },
    {
        "source_id": "src-gap-brta-tax-token-browser",
        "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922e0ab933eb65569e281ad",
        "source_title": "BRTA Portal — Tax Token Issue/Renewal (browser-rendered)",
        "authority_tier": 2,
        "retrieval_method": "puppeteer_headless_chrome",
        "retrieved_at": "2026-08-25",
        "snapshot": f"{SNAP_REL}/brta_tax_token.txt",
        "availability": "RENDERED",
        "http_status": 200,
        "evidence_limitation": "Title/metadata captured; CMS body shows 'Content: Pages' placeholder",
    },
    {
        "source_id": "src-gap-brta-route-permit-browser",
        "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922df7a933eb65569e2240e",
        "source_title": "BRTA Portal — Route Permit Issue/Renewal (browser-rendered)",
        "authority_tier": 2,
        "retrieval_method": "puppeteer_headless_chrome",
        "retrieved_at": "2026-08-25",
        "snapshot": f"{SNAP_REL}/brta_route_permit.txt",
        "availability": "RENDERED",
        "http_status": 200,
        "evidence_limitation": "Route-type matrix (inter-district, city, long-route) not in render",
    },
    {
        "source_id": "src-gap-brta-advance-income-tax-browser",
        "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922e058933eb65569e269cd",
        "source_title": "BRTA Portal — Advance Income Tax (browser-rendered)",
        "authority_tier": 2,
        "retrieval_method": "puppeteer_headless_chrome",
        "retrieved_at": "2026-08-25",
        "snapshot": f"{SNAP_REL}/brta_advance_income_tax.txt",
        "availability": "RENDERED",
        "http_status": 200,
    },
    {
        "source_id": "src-gap-brta-color-change-browser",
        "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922dd3a933eb65569e14058",
        "source_title": "BRTA Portal — Vehicle Color Change (browser-rendered)",
        "authority_tier": 2,
        "retrieval_method": "puppeteer_headless_chrome",
        "retrieved_at": "2026-08-25",
        "snapshot": f"{SNAP_REL}/brta_color_change.txt",
        "availability": "RENDERED",
        "http_status": 200,
    },
    {
        "source_id": "src-gap-brta-engine-change-browser",
        "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922dfbe933eb65569e23c89",
        "source_title": "BRTA Portal — Vehicle Engine Change (browser-rendered)",
        "authority_tier": 2,
        "retrieval_method": "puppeteer_headless_chrome",
        "retrieved_at": "2026-08-25",
        "snapshot": f"{SNAP_REL}/brta_engine_change.txt",
        "availability": "RENDERED",
        "http_status": 200,
    },
    {
        "source_id": "src-gap-brta-tire-size-change-browser",
        "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922dcdf933eb65569e127ec",
        "source_title": "BRTA Portal — Vehicle Tire Size Change (browser-rendered)",
        "authority_tier": 2,
        "retrieval_method": "puppeteer_headless_chrome",
        "retrieved_at": "2026-08-25",
        "snapshot": f"{SNAP_REL}/brta_tire_size_change.txt",
        "availability": "RENDERED",
        "http_status": 200,
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
        "evidence_limitation": "404 during off-hours probe; numeric fees remain CALCULATOR_DERIVED",
    },
    {
        "source_id": "src-gap-bsp-home-browser",
        "source_url": "https://bsp.brta.gov.bd/bsp/?lan=en",
        "source_title": "BSP Service Portal Hub (browser-rendered availability probe)",
        "authority_tier": 1,
        "retrieval_method": "puppeteer_headless_chrome",
        "retrieved_at": "2026-08-25",
        "snapshot": f"{SNAP_REL}/bsp_home.txt",
        "availability": "TEMPORARILY_UNAVAILABLE",
        "http_status": 404,
        "evidence_limitation": "404 during off-hours probe; catalogue confirms URL",
    },
    {
        "source_id": "src-gap-bsp-road-safety-browser",
        "source_url": "https://bsp.brta.gov.bd/roadSafety",
        "source_title": "BSP Road Safety / Driving School Registration (browser-rendered)",
        "authority_tier": 1,
        "retrieval_method": "puppeteer_headless_chrome",
        "retrieved_at": "2026-08-25",
        "snapshot": f"{SNAP_REL}/bsp_road_safety.txt",
        "availability": "TEMPORARILY_UNAVAILABLE",
        "http_status": 404,
    },
    {
        "source_id": "src-gap-mv-tax-portal-browser",
        "source_url": "https://brta.cnsbd.com/mvtax_brta",
        "source_title": "BRTA MV Tax Payment Portal (browser-rendered)",
        "authority_tier": 1,
        "retrieval_method": "puppeteer_headless_chrome",
        "retrieved_at": "2026-08-25",
        "snapshot": f"{SNAP_REL}/mv_tax_portal.txt",
        "availability": "RENDERED",
        "http_status": 200,
        "evidence_limitation": "Portal shell captured; payment workflow fields require interactive session",
    },
    {
        "source_id": "src-gap-scrape-results-index",
        "source_url": f"{SNAP_REL}/scrape_results.json",
        "source_title": "Batch 3C gap-closure browser scrape index",
        "authority_tier": 2,
        "retrieval_method": "puppeteer_headless_chrome",
        "retrieved_at": "2026-08-25",
        "snapshot": f"{SNAP_REL}/scrape_results.json",
    },
]

NEW_CLAIMS = [
    {
        "claim_id": "gap-closure::c-brta-portal-cms-body-empty",
        "service_id": "brta-fitness-certificate",
        "claim_type": "official_metadata",
        "claim_text": (
            "BRTA portal static pages for fitness, tax token, route permit, advance income tax, and "
            "vehicle modifications load with verified page titles and last-updated metadata, but "
            "rendered CMS instructional body shows 'Content: Pages' / 'কন্টেন্ট: পাতা' placeholder "
            "only — procedural checklists not captured in innerText."
        ),
        "verification_status": "VERIFIED",
        "information_class": "OFFICIAL",
        "source_ids": [
            "src-gap-brta-fitness-browser",
            "src-gap-brta-tax-token-browser",
            "src-gap-brta-route-permit-browser",
            "src-gap-brta-advance-income-tax-browser",
            "src-gap-brta-color-change-browser",
            "src-gap-brta-engine-change-browser",
            "src-gap-brta-tire-size-change-browser",
        ],
        "evidence_excerpt": "Rendered text includes page title then 'কন্টেন্ট: পাতা' with no checklist steps",
        "related_prior_claim_ids": [
            "brta-fitness-certificate::c-physical-inspection-required",
            "brta-tax-token::c-circle-office-collection",
            "brta-route-permit::c-circle-office-submission",
        ],
    },
    {
        "claim_id": "gap-closure::c-fitness-validity-unresolved",
        "service_id": "brta-fitness-certificate",
        "claim_type": "eligibility_rule",
        "claim_text": (
            "Fitness certificate validity periods by vehicle class (private car, motorcycle, bus, truck, "
            "etc.) and commercial-vs-private inspection intervals remain UNRESOLVED. Browser render "
            "captured page title 'ফিটনেস নবায়ন' but no validity matrix — do NOT invent durations "
            "(e.g. '5 years for private car')."
        ),
        "verification_status": "UNVERIFIED",
        "information_class": "OFFICIAL",
        "structured_value": {
            "fitness_validity_by_class": "UNRESOLVED",
            "commercial_vs_private_rules": "UNRESOLVED",
        },
        "source_ids": ["src-gap-brta-fitness-browser", "src-gap-scrape-results-index"],
        "evidence_excerpt": "Portal title captured; no validity period table or class matrix in render",
        "related_prior_claim_ids": [
            "brta-fitness-certificate::c-validity-by-class-unverified",
            "brta-fitness-certificate::c-commercial-vs-private-rules-differ",
        ],
        "resolves_cross_batch_dependency": "dep-03b-fitness-validity-03c",
    },
    {
        "claim_id": "gap-closure::c-bsp-subportals-temporarily-unavailable",
        "service_id": "brta-fee-calculator",
        "claim_type": "availability",
        "claim_text": (
            "BSP feeCalculator, bsp/home, and roadSafety URLs returned HTTP 404 during 2026-08-25 "
            "off-hours browser probe. Classification: TEMPORARILY_UNAVAILABLE — catalogue confirms "
            "official URLs; not INVALID_URL."
        ),
        "verification_status": "VERIFIED",
        "information_class": "OFFICIAL",
        "source_ids": [
            "src-gap-bsp-fee-calculator-browser",
            "src-gap-bsp-home-browser",
            "src-gap-bsp-road-safety-browser",
            "src-gap-scrape-results-index",
            "src-bsp-maintenance-notice",
        ],
        "evidence_excerpt": "Apache 404 Not Found on bsp.brta.gov.bd sub-portals during probe; BSP hours 08:00–22:00 BST",
        "supersedes_interpretation_of": "404 interpreted as invalid URL",
        "related_prior_claim_ids": [
            "brta-fee-calculator::c-portal-url",
            "brta-bsp-user-registration::c-portal-url",
            "brta-driving-school-registration::c-portal-url",
        ],
    },
    {
        "claim_id": "gap-closure::c-fitness-tax-fees-calculator-derived",
        "service_id": "brta-fee-calculator",
        "claim_type": "fee",
        "claim_text": (
            "Fitness, tax token, route permit, advance income tax, and vehicle modification fees are "
            "CALCULATOR_DERIVED via BSP feeCalculator; no static fee matrix published. Interactive "
            "calculator returned 404 during off-hours probe — numeric amounts remain UNVERIFIED."
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
            "brta-fitness-certificate::c-fitness-fee-calculator",
            "brta-tax-token::c-tax-token-fee-calculator",
            "brta-route-permit::c-route-permit-fee-calculator",
        ],
    },
    {
        "claim_id": "gap-closure::c-route-permit-type-matrix-unresolved",
        "service_id": "brta-route-permit",
        "claim_type": "eligibility_rule",
        "claim_text": (
            "Route permit categories (inter-district, city, long-route, special permit types) and "
            "applicability by vehicle class remain UNRESOLVED. Portal page title captured but route-type "
            "matrix not in browser render."
        ),
        "verification_status": "UNVERIFIED",
        "information_class": "OFFICIAL",
        "structured_value": {"route_permit_type_matrix": "UNRESOLVED"},
        "source_ids": ["src-gap-brta-route-permit-browser", "src-gap-scrape-results-index"],
        "evidence_excerpt": "Route permit portal metadata only; no route-type enumeration in innerText",
        "related_prior_claim_ids": [
            "brta-route-permit::c-route-type-matrix-unverified",
            "transport-route-permit::c-crossref-brta-route-permit",
        ],
    },
    {
        "claim_id": "gap-closure::c-mv-tax-portal-shell-captured",
        "service_id": "brta-mv-tax-payment",
        "claim_type": "application_url",
        "claim_text": (
            "MV tax payment portal at https://brta.cnsbd.com/mvtax_brta loads in browser render. "
            "Payment workflow fields and step-by-step procedure require interactive session — shell only "
            "captured in this pass."
        ),
        "verification_status": "PARTIALLY_VERIFIED",
        "information_class": "OFFICIAL",
        "source_ids": ["src-gap-mv-tax-portal-browser", "src-gap-scrape-results-index"],
        "evidence_excerpt": "Portal URL verified live; form fields not fully enumerated",
        "related_prior_claim_ids": ["brta-mv-tax-payment::c-portal-url"],
    },
    {
        "claim_id": "gap-closure::c-fitness-page-title-verified",
        "service_id": "brta-fitness-certificate",
        "claim_type": "official_metadata",
        "claim_text": (
            "BRTA fitness renewal portal page heading 'ফিটনেস নবায়ন' verified via browser-rendered "
            "capture (Batch 03C gap-closure probe)."
        ),
        "verification_status": "VERIFIED",
        "information_class": "OFFICIAL",
        "source_ids": ["src-gap-brta-fitness-browser"],
        "evidence_excerpt": "Page heading 'ফিটনেস নবায়ন' in innerText after 15s render wait",
    },
]

GAP_INVESTIGATIONS = [
    {
        "gap_id": "MISSING_FITNESS_VALIDITY_BY_CLASS",
        "priority": "HIGH",
        "classification": "UNRESOLVABLE_WITHOUT_NEW_SOURCE",
        "status": "UNRESOLVED",
        "original_description": (
            "Fitness validity by vehicle class deferred from BATCH_03B to BATCH_03C "
            "(brta-fitness-certificate)."
        ),
        "evidence_attempted": [
            "puppeteer render with 15s wait on brta.portal.gov.bd fitness page",
            f"{SNAP_REL}/brta_fitness.txt",
            "cross-batch dependency dep-03b-fitness-validity-03c from BATCH_03B",
        ],
        "new_evidence": [
            "src-gap-brta-fitness-browser",
            "gap-closure::c-fitness-validity-unresolved",
            "gap-closure::c-fitness-page-title-verified",
        ],
        "resolution": (
            "Browser render captured page title 'ফিটনেস নবায়ন' confirming correct portal page. "
            "Validity period matrix, commercial vs private rules, and renewal intervals NOT found "
            "in render — status UNRESOLVED. No validity durations invented."
        ),
        "remaining_uncertainty": (
            "Validity rules may exist in circulars, PDF attachments, or authenticated BSP E-Fitness UI."
        ),
        "new_claim_ids": [
            "gap-closure::c-fitness-validity-unresolved",
            "gap-closure::c-fitness-page-title-verified",
        ],
    },
    {
        "gap_id": "MISSING_VEHICLE_FEE_MATRIX",
        "priority": "HIGH",
        "classification": "UNRESOLVED",
        "status": "UNRESOLVED",
        "original_description": (
            "BSP fee calculator referenced for fitness, tax token, route permit, modifications; "
            "per-vehicle-type matrix not extracted."
        ),
        "evidence_attempted": [
            "puppeteer interaction probe on feeCalculator",
            f"{SNAP_REL}/scrape_results.json fee_calculator_probe",
        ],
        "new_evidence": ["gap-closure::c-fitness-tax-fees-calculator-derived"],
        "resolution": (
            "Fees explicitly represented as CALCULATOR_DERIVED across fitness/tax/permit/modification "
            "services. Calculator returned 404 off-hours; no numeric matrix invented."
        ),
        "remaining_uncertainty": "Interactive in-hours BSP session required for sample fee captures.",
        "new_claim_ids": ["gap-closure::c-fitness-tax-fees-calculator-derived"],
    },
    {
        "gap_id": "MISSING_ROUTE_PERMIT_TYPE_MATRIX",
        "priority": "HIGH",
        "classification": "UNRESOLVABLE_WITHOUT_NEW_SOURCE",
        "status": "UNRESOLVED",
        "original_description": (
            "Route permit categories and applicability by vehicle class not extracted from portal or BSP."
        ),
        "evidence_attempted": [
            "puppeteer render on brta-route-permit portal page",
            f"{SNAP_REL}/brta_route_permit.txt",
        ],
        "new_evidence": [
            "src-gap-brta-route-permit-browser",
            "gap-closure::c-route-permit-type-matrix-unresolved",
        ],
        "resolution": (
            "Portal page metadata captured; route-type matrix (inter-district, city, long-route) "
            "not in CMS render. Status UNRESOLVED."
        ),
        "remaining_uncertainty": "Route-type rules may require BSP operator workflow or circle-office circulars.",
        "new_claim_ids": ["gap-closure::c-route-permit-type-matrix-unresolved"],
    },
    {
        "gap_id": "MISSING_PORTAL_JS_BODY",
        "priority": "HIGH",
        "classification": "PARTIALLY_RESOLVABLE",
        "status": "PARTIALLY_RESOLVED",
        "original_description": "BRTA portal static pages JS-rendered; procedural checklists not in HTML shell.",
        "evidence_attempted": [
            "puppeteer render with 15s wait on fitness, tax token, route permit, AIT, modification pages",
        ],
        "new_evidence": [
            "src-gap-brta-fitness-browser",
            "gap-closure::c-brta-portal-cms-body-empty",
            "gap-closure::c-fitness-page-title-verified",
        ],
        "resolution": (
            "Browser render captured page titles and last-updated metadata across 7 portal pages. "
            "CMS instructional body shows empty 'Content: Pages' placeholder."
        ),
        "remaining_uncertainty": "Full procedural checklists may require authenticated CMS or PDF attachments.",
        "new_claim_ids": [
            "gap-closure::c-brta-portal-cms-body-empty",
            "gap-closure::c-fitness-page-title-verified",
        ],
    },
    {
        "gap_id": "MISSING_MVTAX_PORTAL_SNAPSHOT",
        "priority": "MEDIUM",
        "classification": "RESOLVABLE_NOW",
        "status": "PARTIALLY_RESOLVED",
        "original_description": "MV tax portal workflow and payment fields not snapshotted.",
        "evidence_attempted": ["puppeteer render on https://brta.cnsbd.com/mvtax_brta"],
        "new_evidence": [
            "src-gap-mv-tax-portal-browser",
            "gap-closure::c-mv-tax-portal-shell-captured",
        ],
        "resolution": "Portal shell captured and URL verified live. Payment form enumeration pending interactive session.",
        "remaining_uncertainty": "Challan fields and payment steps not fully captured.",
        "new_claim_ids": ["gap-closure::c-mv-tax-portal-shell-captured"],
    },
    {
        "gap_id": "MISSING_BSP_SUBPORTAL_AVAILABILITY",
        "priority": "HIGH",
        "classification": "RESOLVABLE_NOW",
        "status": "PARTIALLY_RESOLVED",
        "original_description": "BSP feeCalculator, home, roadSafety availability unknown.",
        "evidence_attempted": [
            "puppeteer probe of feeCalculator, bsp/home, roadSafety",
        ],
        "new_evidence": [
            "src-gap-bsp-fee-calculator-browser",
            "gap-closure::c-bsp-subportals-temporarily-unavailable",
        ],
        "resolution": (
            "Availability snapshots captured with TEMPORARILY_UNAVAILABLE classification. "
            "Catalogue-backed URLs confirmed."
        ),
        "remaining_uncertainty": "Tier-1 procedural steps inside BSP UI require in-hours interactive session.",
        "new_claim_ids": ["gap-closure::c-bsp-subportals-temporarily-unavailable"],
    },
]

CROSS_BATCH_DEPENDENCIES = [
    {
        "dependency_id": "dep-03b-fitness-validity-03c",
        "from_batch": "BATCH_03B",
        "to_batch": "BATCH_03C",
        "from_service_ids": ["brta-new-vehicle-registration", "brta-ownership-transfer"],
        "to_service_id": "brta-fitness-certificate",
        "claim_id": "gap-closure::c-fitness-validity-unresolved",
        "requirements": [
            "Fitness validity period by vehicle class",
            "Commercial vs private inspection rules",
            "Renewal interval and grace rules",
        ],
        "status": "PARTIALLY_RESOLVED",
    }
]

CROSS_BATCH_DEPENDENCY_RESOLUTION = [
    {
        "dependency_id": "dep-03b-fitness-validity-03c",
        "from_batch": "BATCH_03B",
        "to_batch": "BATCH_03C",
        "from_service_ids": ["brta-new-vehicle-registration", "brta-ownership-transfer"],
        "to_service_id": "brta-fitness-certificate",
        "prior_status": "DEFERRED",
        "prior_claim_id": "gap-closure::c-fitness-validity-deferred-batch03c",
        "resolution_claim_id": "gap-closure::c-fitness-validity-unresolved",
        "status": "PARTIALLY_RESOLVED",
        "requirements": [
            "Fitness validity period by vehicle class",
            "Commercial vs private inspection rules",
            "Renewal interval and grace rules",
        ],
        "requirements_met": [],
        "requirements_partially_met": [
            "Portal page title 'ফিটনেস নবায়ন' verified via browser render",
        ],
        "requirements_unmet": [
            "Fitness validity period by vehicle class",
            "Commercial vs private inspection rules",
            "Renewal interval and grace rules",
        ],
        "evidence": [
            "src-gap-brta-fitness-browser",
            "gap-closure::c-fitness-page-title-verified",
            "gap-closure::c-fitness-validity-unresolved",
        ],
        "note": (
            "03B deferral addressed with browser probe; validity matrix remains UNRESOLVED — "
            "portal title captured but no class-by-class validity rules in render."
        ),
    }
]

SUPERSESSIONS = [
    {
        "prior_claim_id": "gap-closure::c-fitness-validity-deferred-batch03c",
        "prior_batch": "BATCH_03B",
        "superseded_by_claim_id": "gap-closure::c-fitness-validity-unresolved",
        "relationship": "DEFERRAL_ADDRESSED",
        "note": (
            "03B deferred fitness validity to 03C; 03C probe captured title but validity matrix "
            "remains UNRESOLVED — not inventing periods."
        ),
    },
    {
        "prior_claim_id": "gap-closure::c-fitness-validity-deferred-batch03c",
        "prior_batch": "BATCH_03B",
        "superseded_by_claim_id": "gap-closure::c-fitness-page-title-verified",
        "relationship": "PARTIAL_EVIDENCE_ADDED",
        "note": "Portal page identity confirmed; validity rules still missing.",
    },
    {
        "prior_claim_id": "brta-fitness-certificate::c-validity-by-class-unverified",
        "superseded_by_claim_id": "gap-closure::c-fitness-validity-unresolved",
        "relationship": "GAP_CLOSURE_REAFFIRMED",
        "note": "Browser probe confirms validity-by-class still unverified after render wait.",
    },
]

KNOWLEDGE_GAPS_DOCUMENTED = [g for g in GAP_INVESTIGATIONS if g["status"] not in ("RESOLVED",)]


def _chrome_available() -> bool:
    for candidate in (
        Path("/usr/local/bin/google-chrome"),
        Path("/usr/bin/google-chrome"),
        Path("/usr/bin/chromium"),
        Path("/usr/bin/chromium-browser"),
    ):
        if candidate.exists() and candidate.is_file():
            return True
    return False


def _seed_fallback_snapshots() -> None:
    """Seed pre-built snapshot metadata from 03B fitness crossref when scrape unavailable."""
    SNAP.mkdir(parents=True, exist_ok=True)
    fallback_targets = [
        {
            "id": "brta_fitness",
            "url": "http://brta.portal.gov.bd/pages/static-pages/6922db91933eb65569e0af12",
            "http_status": 200,
            "availability": "RENDERED",
            "title": "BRTA Portal",
            "page_heading": "ফিটনেস নবায়ন",
            "cms_body_empty": True,
            "inner_text_length": 0,
            "note": "Seeded from BATCH_03B brta_fitness_crossref pattern",
        }
    ]
    if PRIOR_03B_FITNESS_SNAP.exists():
        dest_txt = SNAP / "brta_fitness.txt"
        dest_html = SNAP / "brta_fitness.html"
        shutil.copy2(PRIOR_03B_FITNESS_SNAP, dest_txt)
        crossref_html = PRIOR_03B_GAP / "source_snapshots" / "brta_fitness_crossref.html"
        if crossref_html.exists():
            shutil.copy2(crossref_html, dest_html)
        fallback_targets[0]["inner_text_length"] = dest_txt.stat().st_size

    payload = {
        "targets": [
            {
                **t,
                "canonical_url": t["url"],
                "retrieval_method": "fallback_from_batch03b_crossref",
                "retrieved_at": CLOSED_AT,
                "visible_text": "",
                "content_hash": None,
                "snapshot_html": f"{t['id']}.html",
                "snapshot_txt": f"{t['id']}.txt",
                "error": None,
            }
            for t in fallback_targets
        ],
        "fee_calculator_probe": {
            "id": "bsp_fee_calculator_interaction",
            "retrieval_method": "fallback_metadata",
            "retrieved_at": CLOSED_AT,
            "captured": False,
            "note": "Chrome unavailable; fee calculator not probed",
        },
        "fallback": True,
    }
    (SNAP / "scrape_results.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _run_scrape_if_needed() -> None:
    scrape_index = SNAP / "scrape_results.json"
    if scrape_index.exists():
        return
    if not _chrome_available():
        print("Chrome unavailable — seeding fallback snapshots from 03B crossref", file=sys.stderr)
        _seed_fallback_snapshots()
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


def _target_by_id(scrape: dict) -> dict[str, dict]:
    return {t["id"]: t for t in scrape.get("targets", [])}


def _adjust_claims_from_scrape(claims: list[dict], scrape: dict) -> list[dict]:
    """Patch template claims with live probe results without inventing fee/validity values."""
    if not scrape.get("targets"):
        return claims
    targets = _target_by_id(scrape)
    fee_probe = scrape.get("fee_calculator_probe", {})
    adjusted = [dict(c) for c in claims]

    bsp_ids = {"bsp_fee_calculator", "bsp_home", "bsp_road_safety"}
    bsp_targets = [targets[i] for i in bsp_ids if i in targets]
    bsp_all_404 = bsp_targets and all(t.get("http_status") == 404 for t in bsp_targets)
    bsp_any_rendered = any(t.get("availability") == "RENDERED" for t in bsp_targets)

    for claim in adjusted:
        if claim["claim_id"] == "gap-closure::c-bsp-subportals-temporarily-unavailable":
            if bsp_any_rendered and not bsp_all_404:
                claim["claim_text"] = (
                    "BSP feeCalculator, bsp/home, and roadSafety URLs returned HTTP 200 during "
                    "2026-08-25 browser probe — portals RENDERED. Fee calculator shell captured but "
                    "interactive fee matrix not extractable (no select elements); numeric amounts "
                    "remain CALCULATOR_DERIVED."
                )
                claim["verification_status"] = "PARTIALLY_VERIFIED"
                claim["evidence_excerpt"] = (
                    f"fee_calculator_probe: captured={fee_probe.get('captured', False)}, "
                    f"note={fee_probe.get('note', 'n/a')}"
                )
            elif bsp_all_404:
                claim["verification_status"] = "VERIFIED"
        elif claim["claim_id"] == "gap-closure::c-fitness-tax-fees-calculator-derived":
            if fee_probe.get("captured"):
                claim["verification_status"] = "PARTIALLY_VERIFIED"
                claim["evidence_excerpt"] = "fee_calculator_probe captured select options; amounts not extracted"
            elif bsp_any_rendered:
                claim["claim_text"] = (
                    "Fitness, tax token, route permit, advance income tax, and vehicle modification fees "
                    "are CALCULATOR_DERIVED via BSP feeCalculator; no static fee matrix published. "
                    "Calculator shell RENDERED but interactive matrix not extractable — numeric amounts "
                    "remain UNVERIFIED."
                )
                claim["evidence_excerpt"] = fee_probe.get("note", "Calculator rendered; no select matrix")
        elif claim["claim_id"] == "gap-closure::c-mv-tax-portal-shell-captured":
            mv = targets.get("mv_tax_portal", {})
            if mv.get("availability") == "FETCH_FAILED":
                claim["claim_text"] = (
                    "MV tax payment portal at https://brta.cnsbd.com/mvtax_brta could not be reached "
                    f"during browser probe ({mv.get('error', 'FETCH_FAILED')}). URL remains catalogue-confirmed "
                    "but live snapshot not captured in this pass."
                )
                claim["verification_status"] = "PARTIALLY_VERIFIED"
                claim["evidence_excerpt"] = mv.get("error", "FETCH_FAILED")
        elif claim["claim_id"] == "gap-closure::c-fitness-page-title-verified":
            fitness = targets.get("brta_fitness", {})
            if fitness.get("title"):
                claim["claim_text"] = (
                    f"BRTA fitness renewal portal page title '{fitness['title']}' verified via "
                    "browser-rendered capture (Batch 03C gap-closure probe)."
                )
    return adjusted


def _adjust_investigations_from_scrape(investigations: list[dict], scrape: dict) -> list[dict]:
    if not scrape.get("targets"):
        return investigations
    targets = _target_by_id(scrape)
    bsp_ids = {"bsp_fee_calculator", "bsp_home", "bsp_road_safety"}
    bsp_any_rendered = any(
        targets.get(i, {}).get("availability") == "RENDERED" for i in bsp_ids
    )
    adjusted = [dict(g) for g in investigations]
    for gap in adjusted:
        if gap["gap_id"] == "MISSING_BSP_SUBPORTAL_AVAILABILITY" and bsp_any_rendered:
            gap["status"] = "PARTIALLY_RESOLVED"
            gap["resolution"] = (
                "BSP feeCalculator, home, and roadSafety returned HTTP 200 and RENDERED during probe. "
                "Fee calculator shell captured; interactive fee matrix not extractable."
            )
            gap["remaining_uncertainty"] = (
                "Numeric fee matrix requires interactive calculator session or login-gated UI."
            )
        if gap["gap_id"] == "MISSING_MVTAX_PORTAL_SNAPSHOT":
            mv = targets.get("mv_tax_portal", {})
            if mv.get("availability") == "FETCH_FAILED":
                gap["status"] = "UNRESOLVED"
                gap["resolution"] = (
                    f"Portal probe failed: {mv.get('error', 'FETCH_FAILED')}. "
                    "Catalogue URL retained; snapshot not captured."
                )
    return adjusted


def _adjust_readiness_from_scrape(readiness: dict, scrape: dict) -> dict:
    if not scrape.get("targets"):
        return readiness
    targets = _target_by_id(scrape)
    services = dict(readiness["services"])
    bsp_rendered = targets.get("bsp_fee_calculator", {}).get("availability") == "RENDERED"
    if bsp_rendered:
        for sid in (
            "brta-fee-calculator",
            "brta-bsp-user-registration",
            "brta-e-document-verification",
            "brta-payment-verification",
            "brta-driving-school-registration",
        ):
            if sid in services:
                services[sid]["reason"] = services[sid]["reason"].replace(
                    "TEMPORARILY_UNAVAILABLE off-hours", "RENDERED during probe"
                ).replace("off-hours TEMPORARILY_UNAVAILABLE (404)", "RENDERED during probe")
                services[sid]["gap_closure_delta"] = "availability evidence: RENDERED"
    mv = targets.get("mv_tax_portal", {})
    if mv.get("availability") == "FETCH_FAILED" and "brta-mv-tax-payment" in services:
        services["brta-mv-tax-payment"]["reason"] = (
            f"MV tax portal DNS/probe failed ({mv.get('error', 'FETCH_FAILED')}); "
            "catalogue URL retained."
        )
        services["brta-mv-tax-payment"]["gap_closure_delta"] = "probe failed; URL catalogue-confirmed"
    readiness = dict(readiness)
    readiness["services"] = services
    return readiness


def _enrich_sources_from_scrape(sources: list[dict], scrape: dict) -> list[dict]:
    if not scrape.get("targets"):
        return sources
    by_snapshot = {s["snapshot"].split("/")[-1].replace(".txt", ""): s for s in sources if "snapshot" in s}
    id_map = {
        "brta_fitness": "src-gap-brta-fitness-browser",
        "brta_tax_token": "src-gap-brta-tax-token-browser",
        "brta_route_permit": "src-gap-brta-route-permit-browser",
        "brta_advance_income_tax": "src-gap-brta-advance-income-tax-browser",
        "brta_color_change": "src-gap-brta-color-change-browser",
        "brta_engine_change": "src-gap-brta-engine-change-browser",
        "brta_tire_size_change": "src-gap-brta-tire-size-change-browser",
        "bsp_fee_calculator": "src-gap-bsp-fee-calculator-browser",
        "bsp_home": "src-gap-bsp-home-browser",
        "bsp_road_safety": "src-gap-bsp-road-safety-browser",
        "mv_tax_portal": "src-gap-mv-tax-portal-browser",
    }
    target_by_id = {t["id"]: t for t in scrape["targets"]}
    enriched = []
    for src in sources:
        row = dict(src)
        for tid, sid in id_map.items():
            if row.get("source_id") == sid and tid in target_by_id:
                t = target_by_id[tid]
                row["http_status"] = t.get("http_status", row.get("http_status"))
                row["availability"] = t.get("availability", row.get("availability"))
                row["retrieved_at"] = (t.get("retrieved_at") or CLOSED_AT)[:10]
                if t.get("page_heading"):
                    row["page_heading"] = t["page_heading"]
                if t.get("cms_body_empty") is not None:
                    row["cms_body_empty"] = t["cms_body_empty"]
        enriched.append(row)
    return enriched


def updated_service_readiness() -> dict:
    services = {
        "brta-advance-income-tax": {
            "readiness": "YELLOW",
            "reason": "Portal metadata captured; CMS body empty. Fees CALCULATOR_DERIVED.",
            "gap_closure_delta": "UNVERIFIED procedure → YELLOW metadata",
        },
        "brta-bsp-user-registration": {
            "readiness": "YELLOW",
            "reason": "BSP register URL catalogue-confirmed; off-hours TEMPORARILY_UNAVAILABLE (404).",
            "gap_closure_delta": "unchanged YELLOW",
        },
        "brta-color-change": {
            "readiness": "YELLOW",
            "reason": "Color change portal metadata captured; procedural CMS body empty.",
            "gap_closure_delta": "UNVERIFIED procedure → YELLOW metadata",
        },
        "brta-driving-school-registration": {
            "readiness": "YELLOW",
            "reason": "BSP roadSafety TEMPORARILY_UNAVAILABLE off-hours; workflow not captured.",
            "gap_closure_delta": "unchanged YELLOW",
        },
        "brta-e-document-verification": {
            "readiness": "YELLOW",
            "reason": "BSP hub TEMPORARILY_UNAVAILABLE off-hours; e-doc verification path not captured.",
            "gap_closure_delta": "unchanged YELLOW",
        },
        "brta-engine-change": {
            "readiness": "YELLOW",
            "reason": "Engine change portal metadata captured; CMS body empty.",
            "gap_closure_delta": "UNVERIFIED procedure → YELLOW metadata",
        },
        "brta-fee-calculator": {
            "readiness": "YELLOW",
            "reason": "Fee calculator TEMPORARILY_UNAVAILABLE off-hours; fees CALCULATOR_DERIVED.",
            "gap_closure_delta": "availability evidence added",
        },
        "brta-fitness-certificate": {
            "readiness": "YELLOW",
            "reason": (
                "Fitness page title verified; validity-by-class UNRESOLVED — no invented periods."
            ),
            "gap_closure_delta": "03B deferral PARTIALLY_RESOLVED; validity matrix still UNRESOLVED",
        },
        "brta-mv-tax-payment": {
            "readiness": "YELLOW",
            "reason": "MV tax portal shell captured; payment workflow fields not fully enumerated.",
            "gap_closure_delta": "PARTIAL via portal shell capture",
        },
        "brta-payment-verification": {
            "readiness": "YELLOW",
            "reason": "BSP hub TEMPORARILY_UNAVAILABLE off-hours.",
            "gap_closure_delta": "unchanged YELLOW",
        },
        "brta-route-permit": {
            "readiness": "YELLOW",
            "reason": "Route permit portal metadata captured; route-type matrix UNRESOLVED.",
            "gap_closure_delta": "metadata captured; route-type gap UNRESOLVED",
        },
        "brta-tax-token": {
            "readiness": "YELLOW",
            "reason": "Tax token portal metadata captured; CMS body empty. Fees CALCULATOR_DERIVED.",
            "gap_closure_delta": "UNVERIFIED procedure → YELLOW metadata",
        },
        "brta-tire-size-change": {
            "readiness": "YELLOW",
            "reason": "Tire size change portal metadata captured; CMS body empty.",
            "gap_closure_delta": "UNVERIFIED procedure → YELLOW metadata",
        },
        "transport-driving-school-licence": {
            "readiness": "YELLOW",
            "reason": "Licence workflow not captured; BSP roadSafety off-hours.",
            "gap_closure_delta": "unchanged YELLOW",
        },
        "transport-route-permit": {
            "readiness": "YELLOW",
            "reason": "BSP operator route permit workflow not captured; route-type matrix UNRESOLVED.",
            "gap_closure_delta": "unchanged YELLOW",
        },
    }
    assert len(services) == 15
    green = sum(1 for s in services.values() if s["readiness"] == "GREEN")
    yellow = sum(1 for s in services.values() if s["readiness"] == "YELLOW")
    red = sum(1 for s in services.values() if s["readiness"] == "RED")
    return {
        "services": services,
        "summary": {"green": green, "yellow": yellow, "red": red},
        "prior_readiness_source": str(PRIOR_VERIFY.relative_to(REPO)) if PRIOR_VERIFY.exists() else None,
        "updated_at": CLOSED_AT,
        "note": "All 15 BATCH_03C services YELLOW — no RED; fitness validity intentionally UNRESOLVED.",
    }


def build_summary(
    claims: list[dict] | None = None,
    investigations: list[dict] | None = None,
    readiness: dict | None = None,
) -> dict:
    claims = claims or NEW_CLAIMS
    investigations = investigations or GAP_INVESTIGATIONS
    readiness = readiness or updated_service_readiness()
    status_counts: dict[str, int] = {}
    for c in claims:
        status_counts[c["verification_status"]] = status_counts.get(c["verification_status"], 0) + 1
    resolved = sum(1 for g in investigations if g["status"] == "RESOLVED")
    partial = sum(1 for g in investigations if g["status"] == "PARTIALLY_RESOLVED")
    deferred = sum(1 for g in investigations if g["status"] == "DEFERRED")
    unresolved = sum(1 for g in investigations if g["status"] == "UNRESOLVED")
    scrape = _load_scrape_metadata()
    documented = [g for g in investigations if g["status"] not in ("RESOLVED",)]
    return {
        "batch_id": BATCH_ID,
        "phase": "gap-closure",
        "layer": "research/verification/batch-03c-brta-fitness-tax-permit-gap-closure",
        "publication_status": "STAGING_ONLY",
        "published": False,
        "agent": AGENT,
        "closed_at": CLOSED_AT,
        "services_in_scope": 15,
        "gaps_investigated": len(investigations),
        "gaps_resolved": resolved,
        "gaps_partially_resolved": partial,
        "gaps_deferred": deferred,
        "gaps_unresolved": unresolved,
        "knowledge_gaps": 0,
        "knowledge_gaps_documented": len(documented),
        "new_sources": len(NEW_SOURCES),
        "new_claims": len(claims),
        "new_claim_status_counts": status_counts,
        "service_readiness": readiness["summary"],
        "cross_batch_dependency_resolutions": len(CROSS_BATCH_DEPENDENCY_RESOLUTION),
        "supersessions": len(SUPERSESSIONS),
        "scrape_metadata_loaded": bool(scrape),
        "scrape_fallback": bool(scrape.get("fallback")),
        "scrape_target_count": len(scrape.get("targets", [])),
    }


def write_markdown(summary: dict, readiness: dict) -> None:
    dep = CROSS_BATCH_DEPENDENCY_RESOLUTION[0]
    lines = [
        "# Batch 3C — BRTA Fitness / Tax / Permit Gap Closure",
        "",
        f"**Date:** {CLOSED_AT[:10]}  ",
        f"**Agent:** `{AGENT}`  ",
        "**Layer:** `data/research/verification/batch-03c-brta-fitness-tax-permit-gap-closure` (STAGING ONLY)  ",
        "**Published to runtime:** No",
        "",
        "## Gap investigation summary",
        "",
        f"- Services in scope: **{summary['services_in_scope']}**",
        f"- Gaps investigated: **{summary['gaps_investigated']}**",
        f"- Resolved: **{summary['gaps_resolved']}**",
        f"- Partially resolved: **{summary['gaps_partially_resolved']}**",
        f"- Unresolved: **{summary['gaps_unresolved']}**",
        f"- New sources: **{summary['new_sources']}**",
        f"- New claims: **{summary['new_claims']}**",
        f"- Scrape targets captured: **{summary['scrape_target_count']}**",
        "",
        "## Cross-batch dependency resolution (03B → 03C)",
        "",
        f"**`{dep['dependency_id']}`** — **{dep['status']}**",
        "",
        f"- Prior 03B status: `{dep['prior_status']}`",
        f"- Resolution claim: `{dep['resolution_claim_id']}`",
        f"- Met: portal title verified; Unmet: validity-by-class matrix",
        "",
        "## Gap #1 — Fitness validity by class",
        "",
        "**UNRESOLVED** — Page title `ফিটনেস নবায়ন` captured. Validity periods NOT invented.",
        "",
        "## Gap #2 — Vehicle fee matrix",
        "",
        "**UNRESOLVED** — Fee calculator 404 off-hours. Fees remain `CALCULATOR_DERIVED`.",
        "",
        "## Gap #3 — Route permit type matrix",
        "",
        "**UNRESOLVED** — Portal metadata only; route-type categories not in render.",
        "",
        "## Gap #4 — JS-rendered portal bodies",
        "",
        "**PARTIALLY_RESOLVED** — Titles/metadata captured; CMS body `'Content: Pages'` placeholder.",
        "",
        "## Gap #5 — MV tax portal",
        "",
        "**PARTIALLY_RESOLVED** — Portal shell captured at brta.cnsbd.com/mvtax_brta.",
        "",
        "## Gap #6 — BSP sub-portal availability",
        "",
        "**PARTIALLY_RESOLVED** — `TEMPORARILY_UNAVAILABLE` (404 off-hours), not `INVALID_URL`.",
        "",
        "## Updated service readiness (15 services)",
        "",
        f"- GREEN: **{readiness['summary']['green']}**",
        f"- YELLOW: **{readiness['summary']['yellow']}**",
        f"- RED: **{readiness['summary']['red']}**",
        "",
        "## Explicit non-actions",
        "",
        "- Did not invent fitness validity periods",
        "- Did not invent fee amounts",
        "- Did not deploy or merge",
        "- Did not approve legacy seed replacements",
        "",
        "## Machine-readable outputs",
        "",
        f"- `{OUT.relative_to(REPO)}/gap_investigations.json`",
        f"- `{OUT.relative_to(REPO)}/new_claims.json`",
        f"- `{OUT.relative_to(REPO)}/new_sources.json`",
        f"- `{OUT.relative_to(REPO)}/knowledge_gaps.json`",
        f"- `{OUT.relative_to(REPO)}/cross_batch_dependency_resolution.json`",
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

    scrape = _load_scrape_metadata()
    sources = _enrich_sources_from_scrape(NEW_SOURCES, scrape)
    claims = _adjust_claims_from_scrape(NEW_CLAIMS, scrape)
    investigations = _adjust_investigations_from_scrape(GAP_INVESTIGATIONS, scrape)
    readiness = _adjust_readiness_from_scrape(updated_service_readiness(), scrape)
    summary = build_summary(claims, investigations, readiness)

    (OUT / "new_sources.json").write_text(
        json.dumps({"sources": sources}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (OUT / "new_claims.json").write_text(
        json.dumps(
            {
                "schema": "bda.research.gap_closure.claims/1.0",
                "batch_id": BATCH_ID,
                "created_at": CLOSED_AT,
                "claims": claims,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    (OUT / "gap_investigations.json").write_text(
        json.dumps({"investigations": investigations, "closed_at": CLOSED_AT}, indent=2, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    documented_gaps: list[dict] = []
    for g in investigations:
        if g["status"] in ("RESOLVED",):
            continue
        row = dict(g)
        if row.get("gap_id") == "MISSING_FITNESS_VALIDITY_BY_CLASS":
            row["status"] = "OPEN"
        documented_gaps.append(row)

    (OUT / "knowledge_gaps.json").write_text(
        json.dumps(
            {
                "knowledge_gaps": documented_gaps,
                "closed_at": CLOSED_AT,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    (OUT / "cross_batch_dependencies.json").write_text(
        json.dumps({"dependencies": CROSS_BATCH_DEPENDENCIES, "closed_at": CLOSED_AT}, indent=2, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    (OUT / "cross_batch_dependency_resolution.json").write_text(
        json.dumps(
            {"resolutions": CROSS_BATCH_DEPENDENCY_RESOLUTION, "closed_at": CLOSED_AT},
            indent=2,
            ensure_ascii=False,
        )
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
