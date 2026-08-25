#!/usr/bin/env python3
"""Batch 2A targeted gap closure artifact generator (STAGING ONLY — does not publish)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "data/research/verification/batch-02a-passport-gap-closure"
SNAP = OUT / "source_snapshots"
DOCS = REPO / "docs/research/batch-02a-passport-gap-closure.md"
PRIOR_READINESS = (
    REPO / "data/research/verification/batch-02a-passport/service_readiness.json"
)

CLOSED_AT = datetime.now(timezone.utc).isoformat()
AGENT = "cursor-cloud-agent"

# --- New sources discovered during gap closure ---
NEW_SOURCES = [
    {
        "source_id": "src-gap-epassport-fees-browser",
        "source_url": "https://www.epassport.gov.bd/instructions/passport-fees",
        "source_title": "e-Passport Fees and Payment Options (browser-rendered)",
        "authority_tier": 1,
        "retrieval_method": "puppeteer_headless_chrome",
        "retrieved_at": "2026-08-24",
        "source_last_updated": "2026-07-12",
        "snapshot": "data/research/verification/batch-02a-passport-gap-closure/source_snapshots/epassport_fees.txt",
        "evidence_limitation": None,
    },
    {
        "source_id": "src-gap-epassport-fees-api",
        "source_url": "https://www.epassport.gov.bd/api/v1/landing/instruction/passportFees",
        "source_title": "e-Passport fee instruction API (observed during browser session)",
        "authority_tier": 1,
        "retrieval_method": "browser_network_intercept",
        "retrieved_at": "2026-08-24",
        "snapshot": "data/research/verification/batch-02a-passport-gap-closure/source_snapshots/scrape_results.json",
        "evidence_limitation": "Direct curl to API returns 403; JSON captured from SPA network call during puppeteer session",
    },
    {
        "source_id": "src-gap-epassport-instructions-browser",
        "source_url": "https://www.epassport.gov.bd/instructions/instructions",
        "source_title": "e-Passport form instructions (browser-rendered)",
        "authority_tier": 1,
        "retrieval_method": "puppeteer_headless_chrome",
        "retrieved_at": "2026-08-24",
        "source_last_updated": "2026-08-03",
        "snapshot": "data/research/verification/batch-02a-passport-gap-closure/source_snapshots/epassport_instructions.txt",
    },
    {
        "source_id": "src-gap-epassport-urgent-browser",
        "source_url": "https://epassport.gov.bd/instructions/urgent-applications",
        "source_title": "Urgent / Super Express applications (browser-rendered)",
        "authority_tier": 1,
        "retrieval_method": "puppeteer_headless_chrome",
        "retrieved_at": "2026-08-24",
        "source_last_updated": "2026-06-03",
        "snapshot": "data/research/verification/batch-02a-passport-gap-closure/source_snapshots/https_epassport_gov_bd_instructions_urgent_applications.txt",
    },
    {
        "source_id": "src-gap-epassport-faq-api",
        "source_url": "https://www.epassport.gov.bd/api/v1/landing/faq?lang=eng",
        "source_title": "e-Passport portal FAQ API (status check fields)",
        "authority_tier": 1,
        "retrieval_method": "browser_network_intercept",
        "retrieved_at": "2026-08-24",
        "source_last_updated": "2020-08-28",
        "snapshot": "data/research/verification/batch-02a-passport-gap-closure/source_snapshots/scrape_results.json",
        "evidence_limitation": "FAQ status-check entry last modified 2020-08-28; dedicated status route returned 404/403 in probes",
    },
    {
        "source_id": "src-gap-dip-mrp-fee-page",
        "source_url": "http://dip.gov.bd/site/page/389cbca1-6356-4fb7-b1a1-8f1d67e85463/-",
        "source_title": "DIP MRP fee (Bangladesh) page",
        "authority_tier": 1,
        "retrieval_method": "puppeteer_headless_chrome",
        "retrieved_at": "2026-08-24",
        "source_last_updated": "2017-02-15",
        "snapshot": "data/research/verification/batch-02a-passport-gap-closure/source_snapshots/http_dip_gov_bd_site_page_389cbca1_6356_4fb7_b1a1_8f1d67e854.txt",
        "evidence_limitation": "Page title present but fee table body not rendered in captured text",
    },
    {
        "source_id": "src-gap-abudhabi-epassport-static",
        "source_url": "https://abudhabi.mofa.gov.bd/pages/static-pages/6952667d35ce18e1c05a9876",
        "source_title": "Abu Dhabi Embassy E-Passport Issue/Reissue (static CMS page)",
        "authority_tier": 2,
        "retrieval_method": "puppeteer_headless_chrome",
        "retrieved_at": "2026-08-24",
        "source_last_updated": "2024-10-15",
        "snapshot": "data/research/verification/batch-02a-passport-gap-closure/source_snapshots/abudhabi_epassport_static.txt",
        "evidence_limitation": "CMS shell loads; instructional body text empty ('Content: Pages' only). Legacy /en/site/page/ URLs return 404.",
    },
    {
        "source_id": "src-gap-epassport-onboarding-browser",
        "source_url": "https://www.epassport.gov.bd/onboarding",
        "source_title": "e-Passport onboarding Step 1 (browser-rendered)",
        "authority_tier": 1,
        "retrieval_method": "puppeteer_headless_chrome",
        "retrieved_at": "2026-08-24",
        "snapshot": "data/research/verification/batch-02a-passport-gap-closure/source_snapshots/epassport_onboarding.txt",
    },
]

FEE_TIERS_DOMESTIC = [
    ("48p_5y", 4025, 6325, 8625),
    ("48p_10y", 5750, 8050, 10350),
    ("64p_5y", 6325, 8625, 12075),
    ("64p_10y", 8050, 10350, 13800),
]

NEW_CLAIMS = [
    {
        "claim_id": "gap-closure::c-epassport-fee-page-current-date",
        "service_id": "epassport-fee-payment",
        "claim_type": "official_metadata",
        "claim_text": "Official e-Passport fee page displays Last updated: 12 July 2026 as of gap-closure retrieval.",
        "verification_status": "VERIFIED",
        "applicability": "domestic_and_mission_fee_page",
        "source_ids": ["src-gap-epassport-fees-browser"],
        "evidence_excerpt": "Last updated: 12 July 2026 on https://www.epassport.gov.bd/instructions/passport-fees (browser-rendered).",
        "supersedes_interpretation_of": "conflict-fee-freshness (March 2023 index metadata only)",
        "related_prior_claim_ids": [
            "epassport-fee-payment::c-fee-48p-5y-regular",
            "epassport-fee-payment::c-fee-48p-10y-regular",
            "epassport-fee-payment::c-fee-64p-5y-regular",
            "epassport-fee-payment::c-fee-64p-10y-regular",
        ],
    },
    {
        "claim_id": "gap-closure::c-payment-gateways-achallan-dgepay-shurjopay",
        "service_id": "epassport-fee-payment",
        "claim_type": "payment_method",
        "claim_text": "Official fee page (July 2026) lists online payment via A-Challan, DGePay, and ShurjoPay; offline via A-Challan at banks.",
        "verification_status": "VERIFIED",
        "applicability": "epassport_fee_payment",
        "source_ids": ["src-gap-epassport-fees-browser"],
        "evidence_excerpt": "Online: Through \"A-Challan\", \"DGePay\" and \"ShurjoPay\" ... Offline: ... through A-Challan",
        "conflicts_with_prior_claim_ids": ["epassport-fee-payment::c-payment-ekpay-official"],
    },
]

for variant, regular, express, super_express in FEE_TIERS_DOMESTIC:
    pages, years = variant.split("_")
    page_n = pages.replace("p", "")
    year_n = years.replace("y", "")
    NEW_CLAIMS.append(
        {
            "claim_id": f"gap-closure::c-fee-domestic-{variant}-regular-current",
            "service_id": "epassport-fee-payment",
            "claim_type": "fee",
            "claim_text": f"Inside Bangladesh: {page_n}-page / {year_n}-year e-Passport regular delivery fee BDT {regular:,} (incl. 15% VAT) per official fee page updated 12 July 2026.",
            "verification_status": "VERIFIED",
            "applicability": "domestic_inside_bangladesh",
            "fee_metadata": {
                "pages": int(page_n),
                "validity_years": int(year_n),
                "delivery": "regular",
                "amount_bdt": regular,
                "vat_included": True,
                "effective_evidence_date": "2026-07-12",
            },
            "source_ids": ["src-gap-epassport-fees-browser"],
            "evidence_excerpt": f"Regular delivery: TK {regular:,}",
            "related_prior_claim_ids": [f"epassport-fee-payment::c-fee-{page_n}p-{year_n}y-regular"],
            "prior_claim_status_implication": "Prior OUTDATED status superseded by current Tier-1 browser snapshot; prior claim record not edited.",
        }
    )
    for delivery, amount in [("express", express), ("super_express", super_express)]:
        NEW_CLAIMS.append(
            {
                "claim_id": f"gap-closure::c-fee-domestic-{variant}-{delivery}-current",
                "service_id": "epassport-fee-payment",
                "claim_type": "fee",
                "claim_text": f"Inside Bangladesh: {page_n}-page / {year_n}-year e-Passport {delivery.replace('_', ' ')} delivery fee BDT {amount:,} (incl. 15% VAT) per official fee page updated 12 July 2026.",
                "verification_status": "VERIFIED",
                "applicability": "domestic_inside_bangladesh",
                "fee_metadata": {
                    "pages": int(page_n),
                    "validity_years": int(year_n),
                    "delivery": delivery,
                    "amount_bdt": amount,
                    "vat_included": True,
                    "effective_evidence_date": "2026-07-12",
                },
                "source_ids": ["src-gap-epassport-fees-browser"],
                "evidence_excerpt": f"{delivery.replace('_', ' ').title()} delivery: TK {amount:,}",
            }
        )

NEW_CLAIMS.extend(
    [
        {
            "claim_id": "gap-closure::c-pv-requirement-classification",
            "service_id": "police-passport-police-verification",
            "claim_type": "eligibility_rule",
            "claim_text": "Police verification requirement for e-Passport is CONDITIONAL: Dubai mission (Tier 2) states PV is mandatory for first-time Bangladeshi passport/e-Passport applications and may not be required when no PV is needed and there is no NID/BRC data mismatch on reissue.",
            "verification_status": "PARTIALLY_VERIFIED",
            "applicability": "conditional_by_applicant_path",
            "classification": "CONDITIONAL",
            "source_ids": ["src-mofa-dubai-epassport"],
            "evidence_excerpt": "For first-time ... police verification is mandatory ... If no police verification is required ... expected within 15 days (domestic) / 4-6 weeks (mission).",
            "evidence_limitation": "No Tier-1 DIP circular explicitly stating universal vs conditional rule captured; classification based on Tier-2 mission guidance plus onboarding police-station routing.",
        },
        {
            "claim_id": "gap-closure::c-onboarding-police-station-verified",
            "service_id": "police-passport-police-verification",
            "claim_type": "procedure",
            "claim_text": "e-Passport onboarding Step 1 requires selecting the police station nearest to present address (domestic applicants).",
            "verification_status": "VERIFIED",
            "applicability": "domestic_onboarding",
            "source_ids": ["src-gap-epassport-onboarding-browser"],
            "evidence_excerpt": "Select the police station nearest to your present address",
            "related_prior_claim_ids": [
                "epassport-new-application::c-police-station-select",
                "police-passport-police-verification::c-pv-station-onboarding",
            ],
        },
        {
            "claim_id": "gap-closure::c-epassport-status-check-fields",
            "service_id": "epassport-application-status",
            "claim_type": "portal_function",
            "claim_text": "e-Passport portal FAQ instructs applicants to use Status Check on the home page with Application ID or Online Registration ID plus applicant date of birth.",
            "verification_status": "PARTIALLY_VERIFIED",
            "applicability": "epassport_status_check",
            "source_ids": ["src-gap-epassport-faq-api"],
            "evidence_excerpt": "Go to the Status Check on the ePassport portal home page. Enter your Application ID or Online Registration ID and date of birth",
            "evidence_limitation": "Dedicated /application-status route returned 404/403 in probes; FAQ last modified 2020-08-28; live status UI not independently rendered.",
        },
        {
            "claim_id": "gap-closure::c-mrp-status-portal-fields",
            "service_id": "passport-application-status",
            "claim_type": "portal_function",
            "claim_text": "MRP online status portal at passport.gov.bd/OnlineStatus.aspx requires Enrolment ID and Date of Birth plus captcha.",
            "verification_status": "VERIFIED",
            "applicability": "mrp_application_status",
            "source_ids": ["src-mrp-status"],
            "evidence_excerpt": "Enrolment ID: * Date of Birth: * Enter above Captcha code",
            "snapshot": "data/research/verification/batch-02a-passport-gap-closure/source_snapshots/mrp_status.txt",
        },
        {
            "claim_id": "gap-closure::c-lost-passport-gd-instructions-2026",
            "service_id": "epassport-reissue",
            "claim_type": "procedure",
            "claim_text": "Official e-Passport instructions (updated 3 August 2026) require filing GD at nearest police station for lost/stolen passport and submitting GD copy with re-application.",
            "verification_status": "VERIFIED",
            "applicability": "lost_passport_reissue",
            "source_ids": ["src-gap-epassport-instructions-browser"],
            "evidence_excerpt": "পাসপোর্ট হারিয়ে গেলে ... নিকটস্থ থানায় জিডি ... জিডি কপিসহ আবেদনপত্র দাখিল",
        },
        {
            "claim_id": "gap-closure::c-damaged-passport-not-distinct",
            "service_id": "epassport-reissue",
            "claim_type": "procedure_gap",
            "claim_text": "Official e-Passport instructions (Aug 2026) enumerate lost/stolen passport GD rules but do not separately enumerate damaged-passport documentary rules.",
            "verification_status": "VERIFIED",
            "applicability": "damaged_passport_subprocess",
            "source_ids": ["src-gap-epassport-instructions-browser"],
            "evidence_excerpt": "Lost/stolen GD rule present at item 20; no distinct damaged-passport section in rendered instructions.",
            "knowledge_gap_status": "OPEN",
        },
        {
            "claim_id": "gap-closure::c-abudhabi-epassport-page-empty-cms",
            "service_id": "epassport-fee-payment",
            "claim_type": "mission_evidence",
            "claim_text": "Abu Dhabi mission static page for E-Passport Issue/Reissue exists (last content update 15 Oct 2024) but rendered instructional body is empty in gap-closure browser capture.",
            "verification_status": "UNVERIFIED",
            "applicability": "mission_abu_dhabi",
            "source_ids": ["src-gap-abudhabi-epassport-static"],
            "evidence_excerpt": "Title 'E-Passport Issue/ Reissue:' with 'Content: Pages' only; no fee/WEF surcharge text in live render.",
            "evidence_limitation": "Prior WEFF surcharge claim remains UNVERIFIED; search-index excerpts not used as verification.",
        },
        {
            "claim_id": "gap-closure::c-mrp-fee-page-historical-empty",
            "service_id": "passport-mrp-initial",
            "claim_type": "fee",
            "claim_text": "DIP official MRP fee (Bangladesh) page last content-updated 15 February 2017; captured page contains title only with no machine-readable fee table in browser render.",
            "verification_status": "OUTDATED",
            "applicability": "mrp_domestic_fee_schedule",
            "source_ids": ["src-gap-dip-mrp-fee-page"],
            "evidence_excerpt": "মেশিন রিডেবল পাসপোর্ট (MRP) ফি (বাংলাদেশ) — content last updated Feb 2017; no fee amounts in visible text.",
        },
        {
            "claim_id": "gap-closure::c-super-express-updated-june-2026",
            "service_id": "epassport-urgent-super-express",
            "claim_type": "official_metadata",
            "claim_text": "Urgent/Super Express instruction page last updated 3 June 2026; states any citizen may apply for Super Express domestically; pickup only at Agargaon.",
            "verification_status": "VERIFIED",
            "applicability": "domestic_super_express",
            "source_ids": ["src-gap-epassport-urgent-browser"],
            "evidence_excerpt": "Last updated: 3 June 2026 ... Any citizen of Bangladesh can apply for Super Express delivery ... not available outside Bangladesh",
            "note": "Differs from Oct 2022 indexed NOTE about MRP-only restriction; creates versioning conflict — see conflicts_resolution.json",
        },
    ]
)

GAP_INVESTIGATIONS = [
    {
        "gap_id": "MISSING_CURRENT_EPASSPORT_FEE_TIER1_SNAPSHOT",
        "priority": "CRITICAL",
        "status": "RESOLVED",
        "resolution": "Browser-rendered official fee page captured with Last updated 12 July 2026; domestic BDT tiers verified at listed amounts.",
        "new_claim_ids": [c["claim_id"] for c in NEW_CLAIMS if "fee" in c["claim_id"] or "fee-page-current" in c["claim_id"]],
    },
    {
        "gap_id": "MISSING_TIER1_PV_REQUIREMENT_RULE_2025",
        "priority": "HIGH",
        "status": "PARTIALLY_RESOLVED",
        "resolution": "Classification CONDITIONAL supported by Tier-2 Dubai mission text; Tier-1 universal rule not found.",
        "new_claim_ids": ["gap-closure::c-pv-requirement-classification", "gap-closure::c-onboarding-police-station-verified"],
    },
    {
        "gap_id": "MISSING_ABUDHABI_MISSION_EPASSPORT_PAGE",
        "priority": "HIGH",
        "status": "PARTIALLY_RESOLVED",
        "resolution": "Located static CMS URL; live instructional body empty. Legacy slug URLs 404.",
        "new_claim_ids": ["gap-closure::c-abudhabi-epassport-page-empty-cms"],
    },
    {
        "gap_id": "MISSING_MRP_FEE_SCHEDULE_MACHINE_READABLE",
        "priority": "HIGH",
        "status": "UNRESOLVED",
        "resolution": "DIP MRP fee page dated Feb 2017; no fee table in render. MRP portal references bank deposit without structured schedule.",
        "new_claim_ids": ["gap-closure::c-mrp-fee-page-historical-empty"],
    },
    {
        "gap_id": "MISSING_EPASSPORT_STATUS_PORTAL_FIELDS",
        "priority": "HIGH",
        "status": "PARTIALLY_RESOLVED",
        "resolution": "FAQ API documents Application ID / Online Registration ID + DOB; dedicated status route not accessible.",
        "new_claim_ids": [
            "gap-closure::c-epassport-status-check-fields",
            "gap-closure::c-mrp-status-portal-fields",
        ],
    },
    {
        "gap_id": "MISSING_PAYMENT_GATEWAY_OFFICIAL_ENUM",
        "priority": "MEDIUM",
        "status": "RESOLVED",
        "resolution": "Official July 2026 fee page lists A-Challan, DGePay, ShurjoPay (supersedes prior ekpay indexing).",
        "new_claim_ids": ["gap-closure::c-payment-gateways-achallan-dgepay-shurjopay"],
    },
    {
        "gap_id": "MISSING_DAMAGED_PASSPORT_DISTINCT_RULES",
        "priority": "MEDIUM",
        "status": "PARTIALLY_RESOLVED",
        "resolution": "Lost passport GD rules verified Aug 2026; damaged passport not separately enumerated.",
        "new_claim_ids": [
            "gap-closure::c-lost-passport-gd-instructions-2026",
            "gap-closure::c-damaged-passport-not-distinct",
        ],
    },
    {
        "gap_id": "MISSING_EXPATRIATE_UNIFIED_NATIONAL_PROCEDURE",
        "priority": "HIGH",
        "status": "UNRESOLVED",
        "resolution": "Mission pages remain variant-specific; no DIP consolidation page captured.",
        "new_claim_ids": [],
    },
    {
        "gap_id": "MISSING_POLICE_PV_DEDICATED_OFFICIAL_URL",
        "priority": "MEDIUM",
        "status": "UNRESOLVED",
        "resolution": "No standalone SB passport PV procedure URL found; citizen charter + onboarding routing only.",
        "new_claim_ids": [],
    },
    {
        "gap_id": "MISSING_PASSPORT_CANCELLATION_SERVICE",
        "priority": "LOW",
        "status": "UNRESOLVED",
        "resolution": "No dedicated cancellation service found in targeted pass; likely embedded in reissue/lost flows.",
        "new_claim_ids": [],
    },
    {
        "gap_id": "SINGAPORE_MISSION_EPASSPORT_URL_BROKEN",
        "priority": "LOW",
        "status": "CONFIRMED_OPEN",
        "resolution": "singapore.mofa.gov.bd/en/site/page/E-passport-application-rules returns 404; alternate paths 404 in gap closure.",
        "new_claim_ids": [],
    },
]

CONFLICTS = [
    {
        "conflict_id": "gap-conflict-fee-freshness-resolved",
        "resolution_status": "RESOLVED",
        "classification": "stale_index_metadata_vs_current_browser_page",
        "old_claim_summary": "Step 11 marked domestic fees OUTDATED based on March 2023 search-index last-updated metadata.",
        "new_claim_summary": "Browser-rendered fee page shows Last updated 12 July 2026 with same BDT amounts.",
        "outcome": "Prior OUTDATED verdict on amounts superseded by gap-closure claim series gap-closure::c-fee-domestic-*-current; original claim records unchanged.",
        "blocks_official_publication": False,
    },
    {
        "conflict_id": "gap-conflict-payment-gateway-ekpay-vs-current",
        "resolution_status": "RESOLVED",
        "classification": "official_page_updated_payment_providers",
        "old_claim_summary": "epassport-fee-payment::c-payment-ekpay-official referenced ekpay + A-Challan from index excerpt.",
        "new_claim_summary": "July 2026 fee page lists A-Challan, DGePay, ShurjoPay (no ekpay mention).",
        "outcome": "Represent payment methods from gap-closure::c-payment-gateways-achallan-dgepay-shurjopay; prior ekpay claim should not be published without re-verification.",
        "blocks_official_publication": False,
    },
    {
        "conflict_id": "gap-conflict-super-express-eligibility-june-2026",
        "resolution_status": "UNRESOLVED",
        "classification": "instruction_page_version_drift",
        "old_claim_summary": "Oct 2022 urgent page NOTE restricted Super Express to existing MRP without address change.",
        "new_claim_summary": "June 2026 browser-rendered urgent page states any citizen may apply for Super Express domestically.",
        "outcome": "Treat as time-sensitive rule; prefer June 2026 Tier-1 browser snapshot for eligibility headline; operational NOTE may have changed — manual DIP confirmation recommended before publication.",
        "blocks_official_publication": True,
    },
]

KNOWLEDGE_GAPS_OPEN = [
    g for g in GAP_INVESTIGATIONS if g["status"] in ("UNRESOLVED", "PARTIALLY_RESOLVED", "CONFIRMED_OPEN")
]


def updated_service_readiness() -> dict:
    prior = json.loads(PRIOR_READINESS.read_text())
    services = prior["services"]

    # Fee payment: fees now Tier-1 verified via browser — upgrade from RED to YELLOW
    services["epassport-fee-payment"] = {
        **services["epassport-fee-payment"],
        "readiness": "YELLOW",
        "reason": "Domestic fee tiers verified via browser-rendered Tier-1 page (July 2026). Payment gateway list updated (A-Challan/DGePay/ShurjoPay). Super Express eligibility page drift unresolved.",
        "gap_closure_delta": "RED→YELLOW",
    }
    services["epassport-urgent-super-express"] = {
        **services["epassport-urgent-super-express"],
        "readiness": "YELLOW",
        "reason": "June 2026 urgent page captured; conflicts with Oct 2022 NOTE on MRP-only restriction — unresolved.",
        "gap_closure_delta": "unchanged YELLOW, new conflict",
    }
    services["police-passport-police-verification"] = {
        **services["police-passport-police-verification"],
        "readiness": "YELLOW",
        "reason": "PV classified CONDITIONAL (Tier-2); onboarding police-station step verified; no Tier-1 universal rule.",
        "gap_closure_delta": "unchanged YELLOW, classification added",
    }
    services["epassport-application-status"] = {
        **services["epassport-application-status"],
        "readiness": "YELLOW",
        "reason": "Status check fields partially verified via FAQ API; live status UI route not rendered.",
        "gap_closure_delta": "unchanged YELLOW",
    }
    services["passport-mrp-initial"] = {
        **services["passport-mrp-initial"],
        "readiness": "YELLOW",
        "reason": "MRP fee schedule still missing; DIP fee page Feb 2017 empty shell.",
        "gap_closure_delta": "unchanged YELLOW",
    }

    green = sum(1 for s in services.values() if s["readiness"] == "GREEN")
    yellow = sum(1 for s in services.values() if s["readiness"] == "YELLOW")
    red = sum(1 for s in services.values() if s["readiness"] == "RED")
    return {
        "services": services,
        "summary": {"green": green, "yellow": yellow, "red": red},
        "prior_readiness_source": str(PRIOR_READINESS.relative_to(REPO)),
        "updated_at": CLOSED_AT,
    }


def build_summary() -> dict:
    status_counts = {}
    for c in NEW_CLAIMS:
        status_counts[c["verification_status"]] = status_counts.get(c["verification_status"], 0) + 1
    readiness = updated_service_readiness()
    resolved = sum(1 for g in GAP_INVESTIGATIONS if g["status"] == "RESOLVED")
    partial = sum(1 for g in GAP_INVESTIGATIONS if g["status"] == "PARTIALLY_RESOLVED")
    open_g = sum(1 for g in GAP_INVESTIGATIONS if g["status"] in ("UNRESOLVED", "CONFIRMED_OPEN"))
    return {
        "batch_id": "batch-02a-passport",
        "phase": "gap-closure",
        "layer": "research/verification/batch-02a-passport-gap-closure",
        "publication_status": "STAGING_ONLY",
        "published": False,
        "agent": AGENT,
        "closed_at": CLOSED_AT,
        "gaps_investigated": len(GAP_INVESTIGATIONS),
        "gaps_resolved": resolved,
        "gaps_partially_resolved": partial,
        "gaps_unresolved": open_g,
        "new_sources": len(NEW_SOURCES),
        "new_claims": len(NEW_CLAIMS),
        "new_claim_status_counts": status_counts,
        "conflicts_new_or_updated": len(CONFLICTS),
        "service_readiness": readiness["summary"],
        "critical_findings": [
            "e-Passport fee page browser-rendered with Last updated 12 July 2026 — domestic BDT amounts verified",
            "Payment gateways: A-Challan, DGePay, ShurjoPay (ekpay not on current page)",
            "Police verification: CONDITIONAL (first-time mandatory per Dubai Tier-2; not universal Tier-1 rule)",
            "Abu Dhabi mission e-passport CMS page shell empty; WEFF surcharge still unverified",
            "MRP DIP fee page Feb 2017 with no fee table",
            "Super Express eligibility text changed between Oct 2022 NOTE and June 2026 page",
        ],
        "evidence_limitations": [
            "epassport.gov.bd API endpoints return 403 to curl; browser render required",
            "Status check dedicated route 404/403; FAQ API dated 2020 for field names",
            "Abu Dhabi/Singapore mission CMS pages incomplete or 404",
            "Bright Data MCP unavailable (401)",
        ],
    }


def write_markdown(summary: dict, readiness: dict) -> None:
    lines = [
        "# Batch 2A — Targeted Passport Gap Closure",
        "",
        f"**Date:** {CLOSED_AT[:10]}  ",
        f"**Agent:** `{AGENT}`  ",
        "**Layer:** `data/research/verification/batch-02a-passport-gap-closure` (STAGING ONLY)  ",
        "**Published to runtime:** No",
        "",
        "## Scope",
        "",
        "Targeted investigation of highest-priority unresolved gaps from Step 11 verification. "
        "Did not re-verify all 55 original claims. Created **versioned new claims**; original claim records unchanged.",
        "",
        "## Gap investigation summary",
        "",
        f"- Gaps investigated: **{summary['gaps_investigated']}**",
        f"- Resolved: **{summary['gaps_resolved']}**",
        f"- Partially resolved: **{summary['gaps_partially_resolved']}**",
        f"- Unresolved / open: **{summary['gaps_unresolved']}**",
        f"- New sources: **{summary['new_sources']}**",
        f"- New claims: **{summary['new_claims']}**",
        "",
        "## Priority 1 — Current e-Passport fee (CRITICAL)",
        "",
        "**RESOLVED** via `puppeteer_headless_chrome` render of "
        "[https://www.epassport.gov.bd/instructions/passport-fees](https://www.epassport.gov.bd/instructions/passport-fees).",
        "",
        "- **Last updated:** 12 July 2026 (not March 2023 index metadata)",
        "- Domestic BDT tiers verified at official listed amounts (48p/64p × 5y/10y × regular/express/super express)",
        "- Mission USD tiers captured in browser snapshot",
        "- Prior Step 11 OUTDATED fee claims superseded by new `gap-closure::c-fee-domestic-*-current` claims",
        "",
        "## Priority 2 — Police verification (HIGH)",
        "",
        "**PARTIALLY RESOLVED — classification: CONDITIONAL**",
        "",
        "- Tier-2 Dubai: first-time passport/e-Passport → PV mandatory in Bangladesh",
        "- Tier-2 Dubai: reissue with no mismatch → PV may not be required",
        "- Tier-1 onboarding: police station selection verified (browser render)",
        "- No Tier-1 DIP circular stating universal vs abolished PV captured",
        "",
        "## Priority 2 — Abu Dhabi mission (HIGH)",
        "",
        "**PARTIALLY RESOLVED**",
        "",
        "- Static CMS URL located: `abudhabi.mofa.gov.bd/pages/static-pages/6952667d35ce18e1c05a9876`",
        "- Page title present; **instructional body empty** in browser capture",
        "- Legacy `/en/site/page/E-Passport-Issue--Reissue:` → 404",
        "- WEFF 10% surcharge claim remains **UNVERIFIED**",
        "",
        "## Priority 3 — MRP fees, status portal, payment gateway",
        "",
        "| Topic | Outcome |",
        "|-------|---------|",
        "| MRP fee schedule | **UNRESOLVED** — DIP page Feb 2017, no fee table in render |",
        "| e-Passport status | **PARTIAL** — FAQ: Application ID or Online Registration ID + DOB; status route not accessible |",
        "| MRP status | **VERIFIED** — Enrolment ID + DOB + captcha at passport.gov.bd/OnlineStatus.aspx |",
        "| Payment gateway | **RESOLVED** — A-Challan, DGePay, ShurjoPay (July 2026 fee page) |",
        "",
        "## Priority 4 — Lower gaps",
        "",
        "- **Lost passport:** GD rules verified in Aug 2026 instructions",
        "- **Damaged passport:** No distinct rules found — gap remains open",
        "- **Singapore mission e-passport URL:** Confirmed 404",
        "- **Cancellation service / unified expatriate procedure / PV dedicated URL:** Not resolved",
        "",
        "## New conflicts",
        "",
        "1. **Fee freshness** — RESOLVED (July 2026 browser page vs March 2023 index)",
        "2. **Payment gateway** — RESOLVED (ekpay → A-Challan/DGePay/ShurjoPay on current page)",
        "3. **Super Express eligibility** — UNRESOLVED (June 2026 'any citizen' vs Oct 2022 MRP-only NOTE)",
        "",
        "## Updated service readiness",
        "",
        f"- GREEN: **{readiness['summary']['green']}**",
        f"- YELLOW: **{readiness['summary']['yellow']}**",
        f"- RED: **{readiness['summary']['red']}** (`epassport-fee-payment` upgraded RED→YELLOW)",
        "",
        "## Evidence limitations",
        "",
    ]
    for item in summary["evidence_limitations"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Explicit non-actions",
            "",
            "- Did not publish claims",
            "- Did not run `publish_verified_knowledge.py`",
            "- Did not start Batch 2B",
            "- Did not deploy or modify frontend",
            "",
            "## Machine-readable outputs",
            "",
            "- `data/research/verification/batch-02a-passport-gap-closure/gap_investigations.json`",
            "- `data/research/verification/batch-02a-passport-gap-closure/new_claims.json`",
            "- `data/research/verification/batch-02a-passport-gap-closure/new_sources.json`",
            "- `data/research/verification/batch-02a-passport-gap-closure/conflicts_resolution.json`",
            "- `data/research/verification/batch-02a-passport-gap-closure/knowledge_gaps.json`",
            "- `data/research/verification/batch-02a-passport-gap-closure/service_readiness.json`",
            "- `data/research/verification/batch-02a-passport-gap-closure/summary.json`",
            "- `data/research/verification/batch-02a-passport-gap-closure/source_snapshots/`",
        ]
    )
    DOCS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    SNAP.mkdir(parents=True, exist_ok=True)

    readiness = updated_service_readiness()
    summary = build_summary()

    (OUT / "new_sources.json").write_text(json.dumps({"sources": NEW_SOURCES}, indent=2), encoding="utf-8")
    (OUT / "new_claims.json").write_text(
        json.dumps(
            {
                "schema": "bda.research.gap_closure.claims/1.0",
                "batch_id": "batch-02a-passport",
                "created_at": CLOSED_AT,
                "claims": NEW_CLAIMS,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (OUT / "gap_investigations.json").write_text(
        json.dumps({"investigations": GAP_INVESTIGATIONS, "closed_at": CLOSED_AT}, indent=2),
        encoding="utf-8",
    )
    (OUT / "conflicts_resolution.json").write_text(
        json.dumps({"conflicts": CONFLICTS, "closed_at": CLOSED_AT}, indent=2),
        encoding="utf-8",
    )
    (OUT / "knowledge_gaps.json").write_text(
        json.dumps({"knowledge_gaps": KNOWLEDGE_GAPS_OPEN, "closed_at": CLOSED_AT}, indent=2),
        encoding="utf-8",
    )
    (OUT / "service_readiness.json").write_text(json.dumps(readiness, indent=2), encoding="utf-8")
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (OUT / "README.md").write_text(
        "# Batch 2A Passport Gap Closure (STAGING ONLY)\n\n"
        "Targeted gap investigation after Step 11 verification. **Not published.**\n",
        encoding="utf-8",
    )

    write_markdown(summary, readiness)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
