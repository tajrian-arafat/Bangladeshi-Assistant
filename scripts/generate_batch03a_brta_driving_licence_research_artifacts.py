#!/usr/bin/env python3
"""Generate Batch 3A BRTA driving licence research raw artifacts (RESEARCH ONLY)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "research" / "raw" / "batch-03a-brta-driving-licence"
CATALOGUE = ROOT / "data" / "service_catalogue" / "services.json"
TODAY = "2026-08-24"
BATCH_ID = "batch-03a-brta-driving-licence"

IN_SCOPE = [
    "brta-learner-driving-license",
    "brta-driving-license-renewal",
    "brta-duplicate-driving-license",
    "brta-smart-card-driving-license",
    "brta-driving-instructor-license",
    "brta-dctc-exam-result",
]

OUT_OF_SCOPE_NOTED = [
    {
        "service_id": "brta-bsp-user-registration",
        "reason": "BSP account registration prerequisite; covered as cross-cutting claim not standalone service batch",
    },
    {
        "service_id": "brta-new-vehicle-registration",
        "reason": "Vehicle registration; scheduled for batch-03b-brta-vehicle",
    },
    {
        "service_id": "brta-driving-school-registration",
        "reason": "Driving school operator registration; separate business-facing batch scope",
    },
    {
        "service_id": "brta-fee-calculator",
        "reason": "Cross-cutting fee tool; referenced as source for licence fee claims",
    },
    {
        "service_id": "driving-licence-renewal",
        "reason": "Legacy MVP seed slug; superseded by brta-driving-license-renewal catalogue entry",
    },
]

SOURCES = [
    {
        "source_id": "src-bsp-home",
        "source_url": "https://bsp.brta.gov.bd/bsp/?lan=en",
        "source_title": "BRTA Service Portal (BSP) — Home / Driving Licence Services Hub",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Bangladesh Road Transport Authority (BRTA)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "en",
        "snapshot_path": None,
        "freshness_note": "Catalogue official_source for renewal, duplicate, smart card; sub-services linked from BSP hub",
    },
    {
        "source_id": "src-bsp-learner-portal",
        "source_url": "https://bsp.brta.gov.bd/drivingLicense/?lan=en",
        "source_title": "BSP — Learner Driving License Application",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Bangladesh Road Transport Authority (BRTA)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "en",
        "snapshot_path": None,
        "freshness_note": "Catalogue official_source for learner license; path returned 404 outside BSP operating window in research fetch",
    },
    {
        "source_id": "src-bsp-dctb-result",
        "source_url": "https://bsp.brta.gov.bd/dctbResult",
        "source_title": "BSP — Driving Test (DCTC/DCTB) Result Publication",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Bangladesh Road Transport Authority (BRTA)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "bn",
        "snapshot_path": None,
        "freshness_note": "Catalogue notes division/district-wise results; URL uses dctbResult spelling",
    },
    {
        "source_id": "src-bsp-register",
        "source_url": "https://bsp.brta.gov.bd/register",
        "source_title": "BSP — User Registration (Driver/Owner/Dealer)",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Bangladesh Road Transport Authority (BRTA)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "en",
        "snapshot_path": None,
        "freshness_note": "NID-linked mobile registration prerequisite for BSP driver services per catalogue discovery notes",
    },
    {
        "source_id": "src-bsp-fee-calculator",
        "source_url": "https://bsp.brta.gov.bd/feeCalculator",
        "source_title": "BSP — Fee Calculator (license, registration, fitness, route permit)",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Bangladesh Road Transport Authority (BRTA)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "en",
        "snapshot_path": None,
        "freshness_note": "Catalogue notes cover license fees; numeric amounts require interactive calculator — not extracted in this pass",
    },
    {
        "source_id": "src-brta-portal-home",
        "source_url": "http://brta.portal.gov.bd/",
        "source_title": "BRTA Official Portal (National Portal)",
        "source_type": "official_website",
        "authority_tier": 2,
        "responsible_body": "Bangladesh Road Transport Authority (BRTA)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "bn",
        "snapshot_path": None,
    },
    {
        "source_id": "src-brta-instructor-page",
        "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922db6c933eb65569e0a116",
        "source_title": "BRTA Portal — Driving Instructor License Service Page",
        "source_type": "official_website",
        "authority_tier": 2,
        "responsible_body": "Bangladesh Road Transport Authority (BRTA)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "bn",
        "snapshot_path": None,
        "freshness_note": "Catalogue official_source for instructor license; JS-rendered page — full document checklist not snapshotted",
    },
    {
        "source_id": "src-bsp-maintenance-notice",
        "source_url": "https://bsp.brta.gov.bd/",
        "source_title": "BSP — Operating Hours Notice (root landing when sub-portals unavailable)",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Bangladesh Road Transport Authority (BRTA)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "en",
        "snapshot_path": "source_snapshots/bsp_hours_notice.html",
        "freshness_note": "Live fetch 2026-08-24: BSP available 8:00–22:00 Bangladesh Standard Time",
    },
    {
        "source_id": "src-brta-portal-dl-services",
        "source_url": "http://brta.portal.gov.bd/pages/services/driving-license",
        "source_title": "BRTA Portal — Driving License Services Overview",
        "source_type": "official_website",
        "authority_tier": 2,
        "responsible_body": "Bangladesh Road Transport Authority (BRTA)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "bn",
        "snapshot_path": None,
        "freshness_note": "Discovery cross-reference for learner → training → DCTC → smart card pathway",
    },
    {
        "source_id": "src-brta-seba-app-discovery",
        "source_url": "https://play.google.com/store/apps/details?id=bd.gov.brta.seba",
        "source_title": "BRTA Seba Mobile App (discovery reference)",
        "source_type": "official_app_store",
        "authority_tier": 2,
        "responsible_body": "Bangladesh Road Transport Authority (BRTA)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "en",
        "notes": "DISCOVERY/PRACTICAL only; mobile channel for BSP-related services per BRTA communications",
    },
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
    verification_scope=None,
):
    payload = {
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
        "evidence_ids": [f"ev-{service_id}::{cid}-src-{source_ids[0].replace('src-', '')}"],
        "retrieved_at": TODAY,
        "notes": "Research-phase claim; not verified in this step",
    }
    if verification_scope:
        payload["verification_scope"] = verification_scope
    return payload


def build_claims() -> list[dict]:
    claims: list[dict] = []

    # --- brta-learner-driving-license ---
    sid = "brta-learner-driving-license"
    claims += [
        claim(
            "c-portal-url",
            sid,
            "application_url",
            "Learner (provisional) driving license applications are initiated via BSP at bsp.brta.gov.bd/drivingLicense (English UI available).",
            "OFFICIAL",
            ["src-bsp-learner-portal", "src-brta-portal-dl-services"],
        ),
        claim(
            "c-bsp-registration-prerequisite",
            sid,
            "eligibility",
            "Applicant must register a BSP driver account (NID-linked mobile) at bsp.brta.gov.bd/register before applying for learner license services.",
            "OFFICIAL",
            ["src-bsp-register", "src-bsp-learner-portal"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-apply-at-circle-office",
            sid,
            "procedure_step",
            "Learner license application is submitted through BSP and processed at the relevant BRTA circle office (per catalogue discovery notes).",
            "OFFICIAL",
            ["src-bsp-learner-portal", "src-brta-portal-dl-services"],
        ),
        claim(
            "c-nid-required",
            sid,
            "document",
            "National ID (NID) is required for BSP driver registration and learner license application identity verification.",
            "OFFICIAL",
            ["src-bsp-register", "src-brta-portal-dl-services"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-medical-fitness-certificate",
            sid,
            "document",
            "Medical fitness certificate from registered medical practitioner is required for learner/professional license classes per BRTA driving license service guidance.",
            "OFFICIAL",
            ["src-brta-portal-dl-services"],
            condition={"requirement_class": "CONDITIONAL", "if": "license_class_requires_medical"},
        ),
        claim(
            "c-learner-fee-via-calculator",
            sid,
            "fee",
            "Learner driving license fee is computed via BSP fee calculator (bsp.brta.gov.bd/feeCalculator); exact amount depends on license class and validity period.",
            "OFFICIAL",
            ["src-bsp-fee-calculator", "src-bsp-learner-portal"],
        ),
        claim(
            "c-prerequisite-for-smart-card",
            sid,
            "eligibility",
            "Learner license is prerequisite for authorized driving training and subsequent smart card driving license after DCTC examinations (catalogue notes).",
            "OFFICIAL",
            ["src-bsp-learner-portal", "src-brta-portal-dl-services"],
        ),
        claim(
            "c-minimum-age-non-professional",
            sid,
            "eligibility",
            "Minimum age for non-professional learner driving license is 18 years under Motor Vehicles Ordinance rules cited on BRTA driving license guidance.",
            "OFFICIAL",
            ["src-brta-portal-dl-services"],
            condition={"requirement_class": "MUST_NEED", "if": "license_class_non_professional"},
        ),
        claim(
            "c-bsp-operating-hours",
            sid,
            "availability",
            "BSP portal operating window is 08:00–22:00 Bangladesh Standard Time per live BSP root notice (sub-portals may be unavailable outside window).",
            "DISCOVERY",
            ["src-bsp-maintenance-notice"],
        ),
        claim(
            "c-practical-apply-early-bsp-hours",
            sid,
            "practical_tip",
            "Apply during BSP operating hours; sub-portal deep links may return errors outside 8am–10pm BST even when catalogue URLs are correct.",
            "PRACTICAL",
            ["src-bsp-maintenance-notice"],
        ),
    ]

    # --- brta-driving-license-renewal ---
    sid = "brta-driving-license-renewal"
    claims += [
        claim(
            "c-portal-url",
            sid,
            "application_url",
            "Driving license renewal is handled through BRTA Service Portal at bsp.brta.gov.bd/bsp (English UI ?lan=en).",
            "OFFICIAL",
            ["src-bsp-home"],
        ),
        claim(
            "c-bsp-login-required",
            sid,
            "procedure_step",
            "Renewal workflow requires BSP login with registered driver account (post bsp.brta.gov.bd/register).",
            "OFFICIAL",
            ["src-bsp-home", "src-bsp-register"],
        ),
        claim(
            "c-existing-license-required",
            sid,
            "eligibility",
            "Applicant must hold an existing BRTA-issued driving license eligible for renewal (not first-time learner issuance).",
            "OFFICIAL",
            ["src-bsp-home", "src-brta-portal-dl-services"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-renewal-fee-calculator",
            sid,
            "fee",
            "Renewal fee amount is determined via BSP fee calculator; depends on license class, validity extension, and late renewal penalties if applicable.",
            "OFFICIAL",
            ["src-bsp-fee-calculator", "src-bsp-home"],
        ),
        claim(
            "c-medical-for-renewal-professional",
            sid,
            "conditional_document",
            "Professional and certain license classes require updated medical fitness certificate at renewal per BRTA driving license rules.",
            "OFFICIAL",
            ["src-brta-portal-dl-services"],
            condition={"requirement_class": "CONDITIONAL", "if": "professional_or_class_requires_medical"},
        ),
        claim(
            "c-online-payment-bsp",
            sid,
            "payment_method",
            "BSP supports online fee payment for license services (cards/mobile banking channels per BSP payment integration).",
            "OFFICIAL",
            ["src-bsp-home"],
        ),
        claim(
            "c-renew-before-expiry",
            sid,
            "restriction",
            "License should be renewed before expiry; late renewal may incur additional fees per fee calculator rules.",
            "OFFICIAL",
            ["src-bsp-fee-calculator", "src-brta-portal-dl-services"],
            condition={"requirement_class": "CONDITIONAL", "if": "license_expired_or_near_expiry"},
        ),
        claim(
            "c-circle-office-collection",
            sid,
            "procedure_step",
            "Renewed smart card license may require biometric capture or collection at circle office depending on BSP workflow stage.",
            "OFFICIAL",
            ["src-bsp-home", "src-brta-portal-dl-services"],
            verification_scope="LOCATION_SPECIFIC",
        ),
        claim(
            "c-practical-track-payment",
            sid,
            "practical_tip",
            "Use BSP payment verification module after fee payment before visiting circle office to avoid rejected applications.",
            "PRACTICAL",
            ["src-bsp-home"],
        ),
    ]

    # --- brta-duplicate-driving-license ---
    sid = "brta-duplicate-driving-license"
    claims += [
        claim(
            "c-portal-url",
            sid,
            "application_url",
            "Duplicate (replacement) driving license applications are submitted via BSP at bsp.brta.gov.bd/bsp.",
            "OFFICIAL",
            ["src-bsp-home"],
        ),
        claim(
            "c-lost-or-damaged-eligibility",
            sid,
            "eligibility",
            "Duplicate license issued when original smart card driving license is lost, stolen, or damaged beyond use.",
            "OFFICIAL",
            ["src-bsp-home", "src-brta-portal-dl-services"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-gd-for-lost-license",
            sid,
            "conditional_document",
            "General Diary (GD) or police report may be required when license reported lost/stolen before duplicate issuance.",
            "OFFICIAL",
            ["src-brta-portal-dl-services"],
            condition={"requirement_class": "CONDITIONAL", "if": "license_reported_lost_or_stolen"},
        ),
        claim(
            "c-duplicate-fee-calculator",
            sid,
            "fee",
            "Duplicate driving license fee is listed in BSP fee calculator under license services; amount not statically published in this research pass.",
            "OFFICIAL",
            ["src-bsp-fee-calculator", "src-bsp-home"],
        ),
        claim(
            "c-existing-record-verification",
            sid,
            "procedure_step",
            "BRTA verifies existing license record in BSP database before issuing duplicate smart card.",
            "OFFICIAL",
            ["src-bsp-home"],
        ),
        claim(
            "c-bsp-application-workflow",
            sid,
            "procedure_step",
            "Typical workflow: BSP login → select duplicate license service → pay fee online → attend circle office for biometrics/card issuance if required.",
            "OFFICIAL",
            ["src-bsp-home", "src-brta-portal-dl-services"],
        ),
        claim(
            "c-smart-card-format",
            sid,
            "restriction",
            "Current duplicate issuances are smart card format; legacy booklet licenses follow migration/upgrade rules at circle office.",
            "OFFICIAL",
            ["src-brta-portal-dl-services"],
        ),
        claim(
            "c-processing-time-not-fixed",
            sid,
            "processing_time",
            "Official numeric SLA for duplicate license not published on Tier 1–2 pages reviewed; depends on circle office queue.",
            "DISCOVERY",
            ["src-brta-portal-dl-services"],
            verification_scope="LOCATION_SPECIFIC",
        ),
        claim(
            "c-practical-file-gd-promptly",
            sid,
            "practical_tip",
            "File GD immediately after loss; circle office may request GD copy even when applying online via BSP.",
            "PRACTICAL",
            ["src-brta-portal-dl-services"],
        ),
    ]

    # --- brta-smart-card-driving-license ---
    sid = "brta-smart-card-driving-license"
    claims += [
        claim(
            "c-portal-url",
            sid,
            "application_url",
            "Smart card driving license issuance/upgrade is processed via BSP at bsp.brta.gov.bd/bsp after training and examination requirements met.",
            "OFFICIAL",
            ["src-bsp-home"],
        ),
        claim(
            "c-after-learner-validity",
            sid,
            "eligibility",
            "Applicant must complete learner license period and authorized driving training before smart card professional/non-professional license.",
            "OFFICIAL",
            ["src-bsp-learner-portal", "src-brta-portal-dl-services"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-dctc-exams-required",
            sid,
            "procedure_step",
            "Smart card license requires passing DCTC written, oral, and field (practical) driving tests (catalogue notes).",
            "OFFICIAL",
            ["src-brta-portal-dl-services", "src-bsp-dctb-result"],
        ),
        claim(
            "c-professional-vs-non-professional",
            sid,
            "eligibility",
            "License classes split professional (e.g., heavy passenger/goods) and non-professional (private/light) with different age, medical, and training rules.",
            "OFFICIAL",
            ["src-brta-portal-dl-services"],
        ),
        claim(
            "c-registered-training-school",
            sid,
            "eligibility",
            "Driving training must be completed at BRTA-registered motor driving training school (linked to brta-driving-school-registration ecosystem).",
            "OFFICIAL",
            ["src-brta-portal-dl-services"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-smart-card-fee-calculator",
            sid,
            "fee",
            "Smart card driving license fee computed via BSP fee calculator based on license class and validity duration.",
            "OFFICIAL",
            ["src-bsp-fee-calculator", "src-bsp-home"],
        ),
        claim(
            "c-biometrics-collection",
            sid,
            "procedure_step",
            "Smart card issuance includes biometric capture (photograph, signature, fingerprints) at BRTA circle office or designated enrollment point.",
            "OFFICIAL",
            ["src-brta-portal-dl-services", "src-bsp-home"],
        ),
        claim(
            "c-written-oral-field-sequence",
            sid,
            "procedure_step",
            "Examination sequence: DCTC written test → oral test → field/practical test; results published on BSP DCTB result portal.",
            "OFFICIAL",
            ["src-bsp-dctb-result", "src-brta-portal-dl-services"],
        ),
        claim(
            "c-practical-check-dctc-result",
            sid,
            "practical_tip",
            "Check bsp.brta.gov.bd/dctbResult after examinations before initiating smart card payment to avoid rejected applications.",
            "PRACTICAL",
            ["src-bsp-dctb-result"],
        ),
    ]

    # --- brta-driving-instructor-license ---
    sid = "brta-driving-instructor-license"
    claims += [
        claim(
            "c-portal-url",
            sid,
            "application_url",
            "Driving instructor license service information and application guidance published on BRTA portal static page (brta.portal.gov.bd).",
            "OFFICIAL",
            ["src-brta-instructor-page"],
        ),
        claim(
            "c-listed-on-brta-portal",
            sid,
            "availability",
            "Driving instructor license listed under driving license services on official BRTA national portal (catalogue confirmed).",
            "OFFICIAL",
            ["src-brta-instructor-page", "src-brta-portal-home"],
        ),
        claim(
            "c-valid-license-prerequisite",
            sid,
            "eligibility",
            "Applicant must hold valid professional driving license with adequate experience before instructor license consideration.",
            "OFFICIAL",
            ["src-brta-instructor-page", "src-brta-portal-dl-services"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-training-school-affiliation",
            sid,
            "eligibility",
            "Instructor license typically tied to registered motor driving training school operation (BRTA road safety/training school framework).",
            "OFFICIAL",
            ["src-brta-instructor-page"],
            condition={"requirement_class": "CONDITIONAL", "if": "instructor_at_registered_school"},
        ),
        claim(
            "c-circle-office-application",
            sid,
            "procedure_step",
            "Instructor license applications submitted to relevant BRTA circle office with prescribed forms and supporting documents.",
            "OFFICIAL",
            ["src-brta-instructor-page"],
            verification_scope="LOCATION_SPECIFIC",
        ),
        claim(
            "c-documents-not-fully-captured",
            sid,
            "document",
            "Full document checklist for instructor license not machine-read from BRTA portal page in this research pass (JS-rendered content).",
            "DISCOVERY",
            ["src-brta-instructor-page"],
        ),
        claim(
            "c-fee-not-enumerated",
            sid,
            "fee",
            "Instructor license fee amount not found on Tier 1–2 sources reviewed; may require circle office fee schedule or fee calculator category not captured.",
            "DISCOVERY",
            ["src-brta-instructor-page", "src-bsp-fee-calculator"],
        ),
        claim(
            "c-not-bsp-primary-channel",
            sid,
            "restriction",
            "Instructor license primary channel is BRTA portal/circle office guidance; not listed as standalone BSP e-service in catalogue official_source.",
            "OFFICIAL",
            ["src-brta-instructor-page", "src-bsp-home"],
            verification_scope="SERVICE_SPECIFIC",
        ),
        claim(
            "c-practical-contact-circle-first",
            sid,
            "practical_tip",
            "Contact local BRTA circle office for current instructor license form set and training school endorsement requirements before applying.",
            "PRACTICAL",
            ["src-brta-instructor-page"],
        ),
    ]

    # --- brta-dctc-exam-result ---
    sid = "brta-dctc-exam-result"
    claims += [
        claim(
            "c-portal-url",
            sid,
            "application_url",
            "DCTC/DCTB driving test results published at bsp.brta.gov.bd/dctbResult (catalogue official_source).",
            "OFFICIAL",
            ["src-bsp-dctb-result"],
        ),
        claim(
            "c-division-district-lookup",
            sid,
            "procedure_step",
            "Results browsable division-wise and district-wise on BSP result portal (catalogue notes).",
            "OFFICIAL",
            ["src-bsp-dctb-result"],
        ),
        claim(
            "c-public-result-publication",
            sid,
            "availability",
            "Exam results published on BSP without requiring applicant login (public lookup portal pattern).",
            "OFFICIAL",
            ["src-bsp-dctb-result", "src-brta-portal-dl-services"],
        ),
        claim(
            "c-after-dctc-examinations",
            sid,
            "eligibility",
            "Result lookup relevant after sitting DCTC written/oral/field tests on path to smart card driving license.",
            "OFFICIAL",
            ["src-bsp-dctb-result", "src-brta-portal-dl-services"],
            verification_scope="SERVICE_SPECIFIC",
        ),
        claim(
            "c-url-spelling-dctb",
            sid,
            "official_metadata",
            "Official BSP URL uses 'dctbResult' path segment while service name references DCTC (Driving Competency Test Centre) — naming variant only.",
            "OFFICIAL",
            ["src-bsp-dctb-result"],
        ),
        claim(
            "c-smart-card-pathway-link",
            sid,
            "procedure_step",
            "Passing DCTC results required before smart card driving license fee payment and card issuance on BSP.",
            "OFFICIAL",
            ["src-bsp-dctb-result", "src-bsp-home", "src-brta-portal-dl-services"],
        ),
        claim(
            "c-result-publication-timing-unknown",
            sid,
            "processing_time",
            "Official SLA for result publication after field test not enumerated on Tier 1–2 pages in this pass.",
            "DISCOVERY",
            ["src-bsp-dctb-result"],
        ),
        claim(
            "c-bsp-hours-affect-access",
            sid,
            "availability",
            "Result portal may follow BSP operating hours (08:00–22:00 BST); deep link returned 404 outside window during research fetch.",
            "DISCOVERY",
            ["src-bsp-maintenance-notice", "src-bsp-dctb-result"],
        ),
        claim(
            "c-practical-check-all-tests",
            sid,
            "practical_tip",
            "Verify written, oral, and field test results separately if division publishes stages on different dates.",
            "PRACTICAL",
            ["src-bsp-dctb-result"],
        ),
    ]

    return claims


CONFLICTS = [
    {
        "conflict_id": "conflict-bsp-entry-url-variants",
        "service_ids": [
            "brta-learner-driving-license",
            "brta-driving-license-renewal",
            "brta-duplicate-driving-license",
            "brta-smart-card-driving-license",
        ],
        "topic": "application_url",
        "description": (
            "Catalogue uses service-specific BSP URLs (drivingLicense/?lan=en) for learner vs shared "
            "bsp/?lan=en hub for renewal/duplicate/smart card; both resolve to BSP ecosystem but entry paths differ."
        ),
        "hypotheses": ["service_specific_deep_link_vs_hub", "catalogue_canonical_per_service"],
        "status": "UNRESOLVED",
    },
    {
        "conflict_id": "conflict-dctc-dctb-url-naming",
        "service_ids": ["brta-dctc-exam-result", "brta-smart-card-driving-license"],
        "topic": "portal_naming",
        "description": (
            "Service named DCTC (Driving Competency Test Centre) but official BSP result URL path is dctbResult; "
            "acronym spelling differs in URL vs service title."
        ),
        "hypotheses": ["legacy_url_path", "abbreviation_variant"],
        "status": "UNRESOLVED",
    },
]

KNOWLEDGE_GAPS = [
    {
        "gap_id": "MISSING_BSP_SUBPORTAL_SNAPSHOT",
        "service_ids": [
            "brta-learner-driving-license",
            "brta-driving-license-renewal",
            "brta-duplicate-driving-license",
            "brta-smart-card-driving-license",
            "brta-dctc-exam-result",
        ],
        "classification": "source_discovery_problem",
        "priority": "HIGH",
        "description": "BSP sub-portal pages (drivingLicense, dctbResult, feeCalculator) returned 404 outside operating window; Tier-1 workflow text not snapshotted.",
    },
    {
        "gap_id": "MISSING_LICENSE_FEE_AMOUNT_EXTRACT",
        "service_ids": [
            "brta-learner-driving-license",
            "brta-driving-license-renewal",
            "brta-duplicate-driving-license",
            "brta-smart-card-driving-license",
        ],
        "classification": "missing_fee_schedule",
        "priority": "MEDIUM",
        "description": "Fee calculator referenced but numeric fee matrix not extracted without interactive BSP session.",
    },
    {
        "gap_id": "MISSING_INSTRUCTOR_DOCUMENT_CHECKLIST",
        "service_ids": ["brta-driving-instructor-license"],
        "classification": "insufficient_evidence",
        "priority": "MEDIUM",
        "description": "BRTA instructor license static page not fully captured (JS-rendered); document list incomplete.",
    },
    {
        "gap_id": "MISSING_CIRCLE_OFFICE_SLA",
        "service_ids": [
            "brta-learner-driving-license",
            "brta-driving-license-renewal",
            "brta-duplicate-driving-license",
            "brta-smart-card-driving-license",
        ],
        "classification": "insufficient_evidence",
        "priority": "LOW",
        "description": "Processing times vary by circle office; no national numeric SLA on Tier 1–2 pages reviewed.",
    },
]

SUBPROCESS_COVERAGE = [
    {"topic": "learner_license_bsp", "catalogue_services": ["brta-learner-driving-license"]},
    {"topic": "license_renewal_bsp", "catalogue_services": ["brta-driving-license-renewal"]},
    {"topic": "duplicate_license_bsp", "catalogue_services": ["brta-duplicate-driving-license"]},
    {"topic": "smart_card_license_pathway", "catalogue_services": ["brta-smart-card-driving-license"]},
    {"topic": "dctc_exam_results", "catalogue_services": ["brta-dctc-exam-result"]},
    {"topic": "instructor_license_portal", "catalogue_services": ["brta-driving-instructor-license"]},
    {"topic": "bsp_registration_prerequisite", "catalogue_services": ["brta-learner-driving-license"]},
    {"topic": "fee_calculator_cross_cutting", "catalogue_services": IN_SCOPE[:4]},
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "services").mkdir(exist_ok=True)

    catalogue = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    svc_by_id = {s["service_id"]: s for s in catalogue["services"]}

    missing = [sid for sid in IN_SCOPE if sid not in svc_by_id]
    if missing:
        raise SystemExit(f"Catalogue missing in-scope services: {missing}")

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

    per_service = {}
    for c in claims:
        per_service.setdefault(c["service_id"], []).append(c)

    for sid in IN_SCOPE:
        if len(per_service.get(sid, [])) < 8:
            raise SystemExit(f"Service {sid} has fewer than 8 claims")

    (OUT / "services_index.json").write_text(
        json.dumps({"batch_id": BATCH_ID, "services": services_index}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (OUT / "sources.json").write_text(json.dumps({"sources": SOURCES}, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "claims.json").write_text(json.dumps({"claims": claims}, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "conflicts.json").write_text(json.dumps({"conflicts": CONFLICTS}, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "knowledge_gaps.json").write_text(
        json.dumps({"knowledge_gaps": KNOWLEDGE_GAPS}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (OUT / "scope.json").write_text(
        json.dumps(
            {
                "batch_id": "BATCH_03A",
                "slug": BATCH_ID,
                "name": "BRTA Driving Licence",
                "in_scope": IN_SCOPE,
                "out_of_scope_noted": OUT_OF_SCOPE_NOTED,
                "subprocess_coverage": SUBPROCESS_COVERAGE,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    substantial_threshold = 8
    for sid in IN_SCOPE:
        cat = svc_by_id[sid]
        n = len(per_service.get(sid, []))
        payload = {
            "service_id": sid,
            "batch_id": BATCH_ID,
            "catalogue_version": cat.get("catalogue_version", "1.0.0-finalized"),
            "service_name_en": cat.get("service_name_en"),
            "service_name_bn": cat.get("service_name_bn"),
            "aliases": cat.get("aliases", []),
            "banglish_variants": [],
            "category_id": cat.get("category_id"),
            "responsible_ministry": "Ministry of Road Transport and Bridges",
            "responsible_agency": cat.get("responsible_authority"),
            "target_applicant": cat.get("target_user", []),
            "official_application_url": cat.get("official_source"),
            "research_status": "SUBSTANTIAL" if n >= substantial_threshold else "PARTIAL",
            "claims": per_service.get(sid, []),
            "notes": cat.get("notes"),
            "prior_batch_research": None,
        }
        (OUT / "services" / f"{sid}.json").write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    (OUT / "metadata.json").write_text(
        json.dumps(
            {
                "batch_id": BATCH_ID,
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

    print(f"Wrote {BATCH_ID} artifacts to {OUT}")
    print(f"Services: {len(IN_SCOPE)}, Claims: {len(claims)}, Sources: {len(SOURCES)}")


if __name__ == "__main__":
    main()
