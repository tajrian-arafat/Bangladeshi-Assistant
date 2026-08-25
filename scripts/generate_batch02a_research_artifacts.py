#!/usr/bin/env python3
"""Generate Batch 2A passport research raw artifacts (DISCOVERY + RESEARCH only)."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "research" / "raw" / "batch-02a-passport"
TODAY = "2026-08-24"

# Confirmed passport services from canonical catalogue (464), passport batch scope
IN_SCOPE = [
    "epassport-new-application",
    "epassport-reissue",
    "epassport-fee-payment",
    "epassport-enrollment-appointment",
    "epassport-application-status",
    "epassport-urgent-super-express",
    "epassport-rpo-secretariat",
    "passport-mrp-initial",
    "passport-mrp-reissue",
    "passport-application-status",
    "police-passport-police-verification",
    "police-passport-verification",
]

OUT_OF_SCOPE_NOTED = [
    {
        "service_id": "local-passport-attestation",
        "reason": "Union-level attestation; not DIP passport issuance",
    },
    {
        "service_id": "migration-visa-application-dip",
        "reason": "Visa service; excluded from passport-only batch",
    },
    {
        "service_id": "migration-e-apostille",
        "reason": "MOFA document authentication; not passport issuance",
    },
    {
        "service_id": "mofa-document-attestation",
        "reason": "MOFA consular attestation; separate batch",
    },
    {
        "service_id": "mofa-csat",
        "reason": "MOFA appointment portal; not passport issuance",
    },
    {
        "service_id": "mofa-education-attestation-chain",
        "reason": "Education attestation chain; not passport issuance",
    },
    {
        "service_id": "mofa-nv-loi-application",
        "reason": "Note Verbale/LOI; not passport issuance",
    },
]

SOURCES = [
    {
        "source_id": "src-epassport-fees",
        "source_url": "https://epassport.gov.bd/instructions/passport-fees",
        "source_title": "e-Passport Fees and Payment Options",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Department of Immigration and Passports (DIP)",
        "published_date": "2023-03-08",
        "retrieved_at": TODAY,
        "language": "en",
        "last_updated_on_page": "8 March 2023",
    },
    {
        "source_id": "src-epassport-instructions",
        "source_url": "https://epassport.gov.bd/instructions/instructions",
        "source_title": "e-Passport Application Instructions",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Department of Immigration and Passports (DIP)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "bn",
    },
    {
        "source_id": "src-epassport-urgent",
        "source_url": "https://epassport.gov.bd/instructions/urgent-applications",
        "source_title": "Urgent / Super Express e-Passport Applications",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Department of Immigration and Passports (DIP)",
        "published_date": "2022-10-22",
        "retrieved_at": TODAY,
        "language": "en",
        "last_updated_on_page": "22 October 2022",
    },
    {
        "source_id": "src-epassport-enrollment-docs",
        "source_url": "https://www.epassport.gov.bd/landing/notices/34",
        "source_title": "Documents need to be carried while enrolment at Passport offices",
        "source_type": "official_notice",
        "authority_tier": 1,
        "responsible_body": "Department of Immigration and Passports (DIP)",
        "published_date": "2025-05-07",
        "retrieved_at": TODAY,
        "language": "bn",
        "last_updated_on_page": "7 May 2025",
    },
    {
        "source_id": "src-epassport-onboarding",
        "source_url": "https://www.epassport.gov.bd/onboarding",
        "source_title": "e-Passport Online Onboarding (Step 1 region/police station)",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Department of Immigration and Passports (DIP)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "en",
    },
    {
        "source_id": "src-epassport-status",
        "source_url": "https://www.epassport.gov.bd/authorization/application-status",
        "source_title": "e-Passport Application Status Check",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Department of Immigration and Passports (DIP)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "en",
    },
    {
        "source_id": "src-epassport-landing",
        "source_url": "https://epassport.gov.bd/landing",
        "source_title": "e-Passport Landing Portal",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Department of Immigration and Passports (DIP)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "en",
    },
    {
        "source_id": "src-epassport-app-form",
        "source_url": "https://epassport.gov.bd/instructions/application-form",
        "source_title": "e-Passport Application Form Instructions (RPO Secretariat)",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Department of Immigration and Passports (DIP)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "bn",
    },
    {
        "source_id": "src-mrp-home",
        "source_url": "http://passport.gov.bd/",
        "source_title": "Bangladesh MRP Online Application (DIP Form 1)",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Department of Immigration and Passports (DIP)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "en",
    },
    {
        "source_id": "src-mrp-reissue",
        "source_url": "http://passport.gov.bd/UserHome.aspx",
        "source_title": "Bangladesh MRP Reissue/Correction (DIP Form 2)",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Department of Immigration and Passports (DIP)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "en",
    },
    {
        "source_id": "src-mrp-status",
        "source_url": "http://passport.gov.bd/OnlineStatus.aspx",
        "source_title": "MRP Application Status Check",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Department of Immigration and Passports (DIP)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "en",
    },
    {
        "source_id": "src-dip-home",
        "source_url": "https://www.dip.gov.bd/",
        "source_title": "Department of Immigration and Passports — Official Website",
        "source_type": "official_website",
        "authority_tier": 1,
        "responsible_body": "Department of Immigration and Passports (DIP)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "bn",
    },
    {
        "source_id": "src-mofa-dubai-epassport",
        "source_url": "https://bcgdubai.gov.bd/e-passport/",
        "source_title": "Bangladesh Consulate Dubai — e-Passport page",
        "source_type": "official_mission",
        "authority_tier": 2,
        "responsible_body": "Ministry of Foreign Affairs / DIP (mission guidance)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "en",
    },
    {
        "source_id": "src-mofa-singapore-epassport",
        "source_url": "https://singapore.mofa.gov.bd/en/site/page/E-passport-application-rules",
        "source_title": "Bangladesh High Commission Singapore — e-Passport application rules",
        "source_type": "official_mission",
        "authority_tier": 2,
        "responsible_body": "Ministry of Foreign Affairs / DIP (mission guidance)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "en",
    },
    {
        "source_id": "src-police-charter",
        "source_url": "https://www.police.gov.bd/index.php/en/citizen_charter",
        "source_title": "Bangladesh Police Citizen Charter",
        "source_type": "official_website",
        "authority_tier": 2,
        "responsible_body": "Bangladesh Police",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "en",
    },
    {
        "source_id": "src-police-sb",
        "source_url": "https://www.police.gov.bd/en/special_branch",
        "source_title": "Bangladesh Police — Special Branch",
        "source_type": "official_website",
        "authority_tier": 2,
        "responsible_body": "Bangladesh Police (Special Branch)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "en",
    },
    {
        "source_id": "src-practical-qna-fees",
        "source_url": "https://en.qnabangla.com/passport-fee-bangladesh/",
        "source_title": "QnA Bangla — Passport fee summary (secondary)",
        "source_type": "guide_blog",
        "authority_tier": 6,
        "responsible_body": "Third-party guide",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "en",
        "notes": "PRACTICAL only; cross-check against official fee page before verification",
    },
    {
        "source_id": "src-epassport-five-steps",
        "source_url": "https://epassport.gov.bd/instructions/five-step-to-your-epassport",
        "source_title": "5 Steps to Your e-Passport",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Department of Immigration and Passports (DIP)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "en",
    },
    {
        "source_id": "src-mofa-abudhabi-epassport",
        "source_url": "https://abudhabi.mofa.gov.bd/en/site/page/E-Passport-Issue--Reissue:",
        "source_title": "Bangladesh Embassy Abu Dhabi — e-Passport Issue/Reissue",
        "source_type": "official_mission",
        "authority_tier": 2,
        "responsible_body": "Ministry of Foreign Affairs / DIP (mission guidance)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "en",
    },
    {
        "source_id": "src-mrp-form-pdf",
        "source_url": "http://passport.gov.bd/Reports/MRP_Application_Form[Hard%20Copy].pdf",
        "source_title": "MRP Application Form (Hard Copy PDF)",
        "source_type": "official_form",
        "authority_tier": 1,
        "responsible_body": "Department of Immigration and Passports (DIP)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "bn",
    },
]

# Shared fee tiers (inside Bangladesh, incl 15% VAT) — from official fee page snippets
FEE_TIERS_DOMESTIC = [
    {"pages": 48, "validity_years": 5, "regular_bdt": 4025, "express_bdt": 6325, "super_express_bdt": 8625},
    {"pages": 48, "validity_years": 10, "regular_bdt": 5750, "express_bdt": 8050, "super_express_bdt": 10350},
    {"pages": 64, "validity_years": 5, "regular_bdt": 6325, "express_bdt": 8625, "super_express_bdt": 12075},
    {"pages": 64, "validity_years": 10, "regular_bdt": 8050, "express_bdt": 10350, "super_express_bdt": 13800},
]


def claim(
    cid: str,
    service_id: str,
    claim_type: str,
    text: str,
    info_class: str,
    source_ids: list[str],
    *,
    structured=None,
    condition=None,
):
    return {
        "claim_id": f"{service_id}::{cid}",
        "legacy_claim_id": cid,
        "service_id": service_id,
        "claim_type": claim_type,
        "claim_text": text,
        "information_class": info_class,
        "pipeline_status": "DISCOVERED",
        "verification_status": "PENDING_INDEPENDENT_VERIFICATION",
        "confidence": None,
        "structured_value": structured,
        "condition": condition,
        "source_ids": source_ids,
        "evidence_ids": [f"ev-{service_id}::{cid}-src-{source_ids[0].replace('src-','')}"],
        "retrieved_at": TODAY,
        "notes": "Research-phase claim; not verified in this step",
    }


def build_claims():
    claims = []

    # --- epassport-new-application ---
    sid = "epassport-new-application"
    claims += [
        claim("c-apply-online", sid, "application_url", "New e-Passport applications are submitted online at www.epassport.gov.bd/onboarding.", "OFFICIAL", ["src-epassport-onboarding"]),
        claim("c-no-attestation-online", sid, "procedure_step", "Online e-Passport application does not require attested documents or photo upload at application stage.", "OFFICIAL", ["src-epassport-instructions"]),
        claim("c-id-nid-or-brc", sid, "document", "Applicant must use NID or 17-digit online-verifiable Birth Registration Certificate (English) matching portal rules.", "OFFICIAL", ["src-epassport-instructions", "src-epassport-enrollment-docs"]),
        claim("c-minor-parent-nid", sid, "conditional_document", "Applicants under 18 without own NID must provide father or mother NID number in application.", "OFFICIAL", ["src-epassport-instructions"], condition={"field": "age", "op": "lt", "value": 18}),
        claim("c-minor-3r-photo", sid, "conditional_document", "Applicants under 6 years must submit 3R size lab-print photo at enrollment.", "OFFICIAL", ["src-epassport-instructions"], condition={"field": "age", "op": "lt", "value": 6}),
        claim("c-police-station-select", sid, "procedure_step", "Applicant selects nearest police station to present address during online onboarding.", "OFFICIAL", ["src-epassport-onboarding"]),
        claim("c-govt-noc", sid, "conditional_document", "Government employees must provide GO/NOC at enrollment when applicable.", "OFFICIAL", ["src-epassport-enrollment-docs"], condition={"field": "employment_type", "op": "eq", "value": "government"}),
        claim("c-enrollment-docs-list", sid, "document", "Enrollment requires printed application summary with appointment, original NID/BRC, printed application form, previous passport if any.", "OFFICIAL", ["src-epassport-enrollment-docs"]),
        claim("c-five-step-workflow", sid, "procedure_step", "Official portal documents a five-step e-Passport application workflow from online apply through enrollment to collection.", "OFFICIAL", ["src-epassport-five-steps", "src-epassport-landing"]),
        claim("c-expatriate-onboarding-no", sid, "procedure_step", "Expatriate applicants select 'No' for applying from Bangladesh and choose mission/country during onboarding Step 1.", "OFFICIAL", ["src-epassport-onboarding", "src-mofa-abudhabi-epassport"]),
        claim("c-brc-everify", sid, "conditional_document", "Mission guidance requires 17-digit online-verifiable Birth Registration Certificate (English) verifiable at everify.bdris.gov.bd when BRC used instead of NID.", "OFFICIAL", ["src-mofa-dubai-epassport", "src-mofa-abudhabi-epassport"], condition={"field": "id_document_type", "op": "eq", "value": "brc"}),
    ]

    # --- epassport-reissue (renewal, lost, damaged, correction workflows) ---
    sid = "epassport-reissue"
    claims += [
        claim("c-reissue-portal", sid, "application_url", "e-Passport re-issue applications are made via epassport.gov.bd landing Apply Online for e-Passport / Re-Issue.", "OFFICIAL", ["src-epassport-landing"]),
        claim("c-show-previous-passport", sid, "conditional_document", "For re-issue, original previous passport must be presented at enrollment.", "OFFICIAL", ["src-epassport-instructions"], condition={"field": "application_type", "op": "in", "value": ["reissue", "renewal"]}),
        claim("c-lost-gd-copy", sid, "conditional_document", "For lost passport re-issue, GD copy must be presented/submitted at application.", "OFFICIAL", ["src-epassport-instructions"], condition={"field": "application_type", "op": "eq", "value": "lost"}),
        claim("c-lost-gd-immediate", sid, "practical_tip", "If passport is lost or damaged, citizen should file GD promptly at nearest police station before re-application.", "OFFICIAL", ["src-epassport-instructions"]),
        claim("c-correction-extra-docs", sid, "conditional_document", "Information correction may require additional supporting documents depending on correction type.", "OFFICIAL", ["src-epassport-enrollment-docs"], condition={"field": "application_type", "op": "eq", "value": "correction"}),
        claim("c-mission-lost-report", sid, "conditional_document", "Expatriate lost passport applicants at missions may need local police lost report (mission-specific).", "OFFICIAL", ["src-mofa-dubai-epassport"], condition={"field": "applicant_location", "op": "eq", "value": "foreign_mission"}),
        claim("c-dubai-mrp-validity-limit", sid, "eligibility", "Dubai consulate states e-Passport not accepted if existing MRP has more than one year validity remaining.", "OFFICIAL", ["src-mofa-dubai-epassport"], condition={"field": "applicant_location", "op": "eq", "value": "dubai_mission"}),
        claim("c-mission-biometric-presence", sid, "procedure_step", "Mission pages state physical presence mandatory for biometric enrollment (age thresholds vary by mission; Dubai cites under-5 exemption).", "OFFICIAL", ["src-mofa-dubai-epassport", "src-mofa-singapore-epassport"]),
    ]

    # --- epassport-fee-payment ---
    sid = "epassport-fee-payment"
    for tier in FEE_TIERS_DOMESTIC:
        key = f"c-fee-{tier['pages']}p-{tier['validity_years']}y-regular"
        claims.append(
            claim(
                key,
                sid,
                "fee",
                f"Inside Bangladesh: {tier['pages']}-page / {tier['validity_years']}-year e-Passport regular delivery fee BDT {tier['regular_bdt']} (incl. 15% VAT).",
                "OFFICIAL",
                ["src-epassport-fees"],
                structured={"amount": tier["regular_bdt"], "currency": "BDT", "delivery": "regular", **tier},
            )
        )
    claims += [
        claim("c-fee-vat-included", sid, "fee", "Published inside-Bangladesh e-Passport fees include 15% VAT.", "OFFICIAL", ["src-epassport-fees"]),
        claim("c-fee-mission-general-usd", sid, "fee", "Mission general applicant fees published in USD by page count, validity, and delivery tier on official fee page.", "OFFICIAL", ["src-epassport-fees"]),
        claim("c-fee-mission-labor-student-usd", sid, "fee", "Mission labor/student applicant fees published separately in USD on official fee page.", "OFFICIAL", ["src-epassport-fees"]),
        claim("c-payment-online-offline", sid, "payment_method", "Fees may be paid online (payment gateways) or offline via bank/A-Challan per official instructions.", "OFFICIAL", ["src-epassport-fees"]),
        claim("c-payment-slip-offline-only", sid, "conditional_document", "Payment slip required at enrollment for offline payment only.", "OFFICIAL", ["src-epassport-enrollment-docs"], condition={"field": "payment_method", "op": "eq", "value": "offline"}),
        claim("c-practical-ekpay-mention", sid, "practical_tip", "Community guides reference ekpay and e-Challan verification for online payments; confirm current gateway list on official portal.", "PRACTICAL", ["src-practical-qna-fees"]),
        claim("c-regular-delivery-sla", sid, "processing_time", "Regular delivery stated as within 15 working days / 21 days from biometric enrolment date on official fee page.", "OFFICIAL", ["src-epassport-fees"]),
        claim("c-payment-ekpay-official", sid, "payment_method", "Official fee page states fees can be paid online via ekpay platform or offline at participating banks using A-Challan.", "OFFICIAL", ["src-epassport-fees"]),
        claim("c-mission-weff-surcharge", sid, "fee", "Abu Dhabi mission page notes 10% surcharge on consular fees under Wage Earners' Welfare Board Act 2018 Section 14(e).", "OFFICIAL", ["src-mofa-abudhabi-epassport"], condition={"field": "applicant_location", "op": "eq", "value": "foreign_mission"}),
    ]

    # --- epassport-enrollment-appointment ---
    sid = "epassport-enrollment-appointment"
    claims += [
        claim("c-appointment-required", sid, "procedure_step", "Biometric enrollment at passport office requires printed application summary including appointment when scheduled.", "OFFICIAL", ["src-epassport-enrollment-docs", "src-epassport-instructions"]),
        claim("c-bring-original-id", sid, "document", "Original NID or Birth Certificate must be carried to enrollment.", "OFFICIAL", ["src-epassport-enrollment-docs"]),
    ]

    # --- epassport-application-status ---
    sid = "epassport-application-status"
    claims += [
        claim("c-status-portal", sid, "application_url", "e-Passport application status is checked at epassport.gov.bd authorization application-status.", "OFFICIAL", ["src-epassport-status"]),
        claim("c-status-oid-dob", sid, "eligibility", "Status check requires Application ID or Online Registration ID (OID) and date of birth.", "OFFICIAL", ["src-epassport-status"]),
    ]

    # --- epassport-urgent-super-express ---
    sid = "epassport-urgent-super-express"
    claims += [
        claim("c-super-express-2-days", sid, "processing_time", "Super Express (urgent) passport issued within 2 working days under stated conditions.", "OFFICIAL", ["src-epassport-urgent"]),
        claim("c-super-express-domestic-only", sid, "restriction", "Super Express service not available at Bangladesh Missions abroad.", "OFFICIAL", ["src-epassport-urgent"]),
        claim("c-super-express-pickup-agargaon", sid, "office", "Super Express passports picked up only at Divisional Passport and Visa Office, Agargaon, Dhaka.", "OFFICIAL", ["src-epassport-urgent"]),
        claim("c-super-express-mrp-no-address-change", sid, "eligibility", "Current note: Super Express available only for e-Passport issuance where applicant already holds MRP without changing permanent address.", "OFFICIAL", ["src-epassport-urgent"]),
        claim("c-super-express-fee-tier", sid, "fee", "Super Express delivery uses Super Express fee tier on official fee schedule.", "OFFICIAL", ["src-epassport-fees", "src-epassport-urgent"]),
    ]

    # --- epassport-rpo-secretariat ---
    sid = "epassport-rpo-secretariat"
    claims += [
        claim("c-rpo-secretariat-form", sid, "application_url", "RPO Bangladesh Secretariat application guidance published on epassport application-form instructions page.", "OFFICIAL", ["src-epassport-app-form"]),
    ]

    # --- passport-mrp-initial ---
    sid = "passport-mrp-initial"
    claims += [
        claim("c-mrp-form1", sid, "application_url", "Initial MRP applications use DIP Form 1 via passport.gov.bd online portal.", "OFFICIAL", ["src-mrp-home"]),
        claim("c-mrp-email-credentials", sid, "procedure_step", "MRP online application provides Application ID and Password by email after first page save.", "OFFICIAL", ["src-mrp-home"]),
        claim("c-mrp-biometric-visit", sid, "procedure_step", "After online submit, applicant must visit passport office with printed form for biometric enrollment.", "OFFICIAL", ["src-mrp-home"]),
        claim("c-mrp-govt-single-form", sid, "conditional_document", "Certain government/retired/surrendered categories submit one form copy; others submit two copies (per MRP portal notice).", "OFFICIAL", ["src-mrp-home"], condition={"field": "applicant_category", "op": "in", "value": ["government", "retired_government", "surrendered"]}),
        claim("c-mrp-attested-copies", sid, "document", "MRP pathway requires attested photocopies of NID/BRC and relevant certificates (contrasts with e-Passport no-attestation rule).", "OFFICIAL", ["src-mrp-home", "src-mrp-form-pdf"]),
        claim("c-mrp-appointment-validity", sid, "processing_time", "MRP online application appointment validity stated as 5 days from system generation (per MRP portal).", "OFFICIAL", ["src-mrp-reissue"]),
    ]

    # --- passport-mrp-reissue ---
    sid = "passport-mrp-reissue"
    claims += [
        claim("c-mrp-form2", sid, "application_url", "MRP reissue/correction/alternation uses DIP Form 2 via passport.gov.bd UserHome.", "OFFICIAL", ["src-mrp-reissue"]),
    ]

    # --- passport-application-status ---
    sid = "passport-application-status"
    claims += [
        claim("c-mrp-status-portal", sid, "application_url", "Legacy MRP application status checked at passport.gov.bd OnlineStatus.aspx.", "OFFICIAL", ["src-mrp-status"]),
    ]

    # --- police-passport-police-verification ---
    sid = "police-passport-police-verification"
    claims += [
        claim("c-pv-pathway-exists", sid, "availability", "Passport police verification is part of e-Passport processing pathway via Special Branch.", "OFFICIAL", ["src-dip-home", "src-police-sb"]),
        claim("c-pv-station-onboarding", sid, "procedure_step", "Applicant selects nearest police station during e-Passport onboarding for verification routing.", "OFFICIAL", ["src-epassport-onboarding"]),
        claim("c-pv-delay-note", sid, "practical_tip", "Mission pages note police verification timing can affect e-Passport processing duration.", "PRACTICAL", ["src-mofa-dubai-epassport"]),
    ]

    # --- police-passport-verification ---
    sid = "police-passport-verification"
    claims += [
        claim("c-pv-charter-sla", sid, "processing_time", "Citizen charter cites normal passport verification 15-21 days and urgent 7 days (requires live charter verification).", "DISCOVERY", ["src-police-charter"]),
        claim("c-pv-district-scope", sid, "office", "District-level passport verification service under Bangladesh Police citizen charter.", "DISCOVERY", ["src-police-charter"]),
    ]

    return claims


CONFLICTS = [
    {
        "conflict_id": "conflict-super-express-eligibility",
        "service_ids": ["epassport-urgent-super-express", "epassport-reissue"],
        "topic": "super_express_eligibility",
        "claim_ids": [
            "epassport-urgent-super-express::c-super-express-mrp-no-address-change",
            "epassport-urgent-super-express::c-super-express-2-days",
        ],
        "description": "Urgent page states any citizen may apply for Super Express, but NOTE restricts current availability to existing MRP holders without permanent address change.",
        "hypotheses": ["policy_change_over_time", "applicant_type_restriction"],
        "status": "UNRESOLVED",
    },
    {
        "conflict_id": "conflict-mrp-vs-epassport-primary",
        "service_ids": ["passport-mrp-initial", "epassport-new-application"],
        "topic": "primary_passport_channel",
        "description": "Both MRP (passport.gov.bd) and e-Passport (epassport.gov.bd) portals remain active; national primary channel for new applicants needs DIP circular confirmation.",
        "status": "UNRESOLVED",
    },
    {
        "conflict_id": "conflict-fee-freshness",
        "service_ids": ["epassport-fee-payment"],
        "topic": "fee_schedule_date",
        "description": "Official fee page last updated 8 March 2023; potential stale fees if revised by gazette/circular without page update.",
        "status": "UNRESOLVED",
    },
]

KNOWLEDGE_GAPS = [
    {
        "gap_id": "MISSING_MRP_FEE_SCHEDULE_MACHINE_READABLE",
        "service_ids": ["passport-mrp-initial", "passport-mrp-reissue"],
        "classification": "missing_fee_schedule",
        "priority": "HIGH",
        "description": "MRP portal references bank deposit fees but structured fee table not extracted from official live source in this research pass.",
    },
    {
        "gap_id": "MISSING_PASSPORT_CANCELLATION_SERVICE",
        "service_ids": [],
        "classification": "service_identification_problem",
        "priority": "MEDIUM",
        "description": "No dedicated canonical catalogue entry for passport cancellation; may be embedded in reissue/lost workflows.",
    },
    {
        "gap_id": "MISSING_EXPATRIATE_UNIFIED_NATIONAL_PROCEDURE",
        "service_ids": ["epassport-new-application", "epassport-reissue"],
        "classification": "geographic_local_variation",
        "priority": "HIGH",
        "description": "Mission-specific document lists (Dubai, Singapore, etc.) vary; no single DIP page consolidates all expatriate requirements.",
    },
    {
        "gap_id": "MISSING_POLICE_PV_DEDICATED_OFFICIAL_URL",
        "service_ids": ["police-passport-police-verification"],
        "classification": "source_discovery_problem",
        "priority": "MEDIUM",
        "description": "Catalogue points to dip.gov.bd for passport police verification; no standalone SB passport PV procedure page captured.",
    },
    {
        "gap_id": "MISSING_PAYMENT_GATEWAY_OFFICIAL_ENUM",
        "service_ids": ["epassport-fee-payment"],
        "classification": "insufficient_evidence",
        "priority": "MEDIUM",
        "description": "Current official list of online payment gateways (ekpay vs A-Challan vs others) not fully captured from live JS portal in this pass.",
    },
    {
        "gap_id": "MISSING_DAMAGED_PASSPORT_DISTINCT_RULES",
        "service_ids": ["epassport-reissue"],
        "classification": "insufficient_evidence",
        "priority": "MEDIUM",
        "description": "Lost passport GD rules found; damaged passport distinct documentary rules not separately enumerated on Tier-1 pages reviewed.",
    },
]

SUBPROCESS_COVERAGE = [
    {"topic": "first_time_application", "catalogue_services": ["epassport-new-application", "passport-mrp-initial"]},
    {"topic": "renewal_reissue", "catalogue_services": ["epassport-reissue", "passport-mrp-reissue"]},
    {"topic": "information_correction", "catalogue_services": ["epassport-reissue", "passport-mrp-reissue"]},
    {"topic": "lost_passport", "catalogue_services": ["epassport-reissue"]},
    {"topic": "damaged_passport", "catalogue_services": ["epassport-reissue"]},
    {"topic": "minor_applicants", "catalogue_services": ["epassport-new-application", "epassport-reissue"]},
    {"topic": "expatriate_applicants", "catalogue_services": ["epassport-new-application", "epassport-reissue", "epassport-fee-payment"]},
    {"topic": "biometric_enrollment", "catalogue_services": ["epassport-enrollment-appointment"]},
    {"topic": "fee_payment", "catalogue_services": ["epassport-fee-payment"]},
    {"topic": "status_checking", "catalogue_services": ["epassport-application-status", "passport-application-status"]},
    {"topic": "urgent_processing", "catalogue_services": ["epassport-urgent-super-express"]},
    {"topic": "police_verification", "catalogue_services": ["police-passport-police-verification", "police-passport-verification"]},
    {"topic": "passport_cancellation", "catalogue_services": [], "notes": "No canonical entry identified"},
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "services").mkdir(exist_ok=True)

    catalogue = json.loads((ROOT / "data/service_catalogue/final/services.json").read_text())
    svc_by_id = {s["service_id"]: s for s in catalogue["services"]}

    services_index = []
    for sid in IN_SCOPE:
        cat = svc_by_id[sid]
        services_index.append(
            {
                "service_id": sid,
                "service_name_en": cat.get("service_name_en"),
                "service_name_bn": cat.get("service_name_bn"),
                "category_id": cat.get("category_id"),
                "subcategory": cat.get("subcategory"),
                "official_source": cat.get("official_source"),
                "status": cat.get("status"),
            }
        )

    claims = build_claims()
    tier12 = [s for s in SOURCES if s["authority_tier"] <= 2]

    (OUT / "services_index.json").write_text(json.dumps({"batch_id": "batch-02a-passport", "services": services_index}, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "sources.json").write_text(json.dumps({"sources": SOURCES}, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "claims.json").write_text(json.dumps({"claims": claims}, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "conflicts.json").write_text(json.dumps({"conflicts": CONFLICTS}, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "knowledge_gaps.json").write_text(json.dumps({"knowledge_gaps": KNOWLEDGE_GAPS}, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "scope.json").write_text(
        json.dumps(
            {
                "in_scope": IN_SCOPE,
                "out_of_scope_noted": OUT_OF_SCOPE_NOTED,
                "subprocess_coverage": SUBPROCESS_COVERAGE,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (OUT / "metadata.json").write_text(
        json.dumps(
            {
                "batch_id": "batch-02a-passport",
                "phase": "RESEARCH_ONLY",
                "researched_at": TODAY,
                "catalogue_version": "1.0.0-finalized",
                "services_in_scope": len(IN_SCOPE),
                "services_researched": len(IN_SCOPE),
                "source_count": len(SOURCES),
                "official_source_count_tier1_2": len(tier12),
                "claims_total": len(claims),
                "claims_official": sum(1 for c in claims if c["information_class"] == "OFFICIAL"),
                "claims_practical": sum(1 for c in claims if c["information_class"] == "PRACTICAL"),
                "claims_discovery": sum(1 for c in claims if c["information_class"] == "DISCOVERY"),
                "conflicts": len(CONFLICTS),
                "knowledge_gaps": len(KNOWLEDGE_GAPS),
                "verification_status": "NOT_STARTED",
                "publication_status": "NOT_STARTED",
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # Per-service stub files for downstream staging
    claims_by_service: dict[str, list] = {}
    for c in claims:
        claims_by_service.setdefault(c["service_id"], []).append(c)

    for sid in IN_SCOPE:
        cat = svc_by_id[sid]
        payload = {
            "service_id": sid,
            "batch_id": "batch-02a-passport",
            "catalogue_version": "1.0.0-finalized",
            "service_name_en": cat.get("service_name_en"),
            "service_name_bn": cat.get("service_name_bn"),
            "aliases": cat.get("aliases", []),
            "banglish_variants": [],
            "category_id": cat.get("category_id"),
            "responsible_ministry": "Ministry of Home Affairs",
            "responsible_agency": cat.get("responsible_authority"),
            "target_applicant": cat.get("target_user", []),
            "official_application_url": cat.get("official_source"),
            "research_status": "SUBSTANTIAL" if len(claims_by_service.get(sid, [])) >= 5 else "PARTIAL",
            "claims": claims_by_service.get(sid, []),
            "notes": cat.get("notes"),
        }
        (OUT / "services" / f"{sid}.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Wrote batch-02a artifacts to {OUT}")
    print(f"Services: {len(IN_SCOPE)}, Claims: {len(claims)}, Sources: {len(SOURCES)}")


if __name__ == "__main__":
    main()
