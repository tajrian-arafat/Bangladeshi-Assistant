#!/usr/bin/env python3
"""Generate Batch 3C BRTA fitness/tax token/route permit research raw artifacts (RESEARCH ONLY)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "research" / "raw" / "batch-03c-brta-fitness-tax-permit"
CATALOGUE = ROOT / "data" / "service_catalogue" / "services.json"
TODAY = "2026-08-25"
BATCH_ID = "batch-03c-brta-fitness-tax-permit"

IN_SCOPE = [
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

OUT_OF_SCOPE_NOTED = [
    {
        "service_id": "brta-new-vehicle-registration",
        "reason": "Vehicle registration bundle; assigned to BATCH_03B. Fitness/tax may be bundled at first registration.",
    },
    {
        "service_id": "brta-ownership-transfer",
        "reason": "Ownership transfer; BATCH_03B. May require current tax/fitness as prerequisites only.",
    },
    {
        "service_id": "brta-vehicle-info-correction",
        "reason": "RC data correction; BATCH_03B. Distinct from vehicle modification services in this batch.",
    },
    {
        "subprocedure": "vehicle_modification_vs_fitness_tax",
        "reason": "Engine/color/tyre modification services researched in 03C but are separate procedures from fitness renewal, tax token, and route permit.",
    },
]

FITNESS_TAX_VARIANT_MODEL = {
    "dimensions": [
        {
            "id": "vehicle_type",
            "values": [
                "motorcycle",
                "private_car",
                "jeep_microbus",
                "bus",
                "truck",
                "auto_rickshaw",
                "trailer",
                "other_commercial",
            ],
            "notes": "Fee, fitness inspection, route permit, and tax rules vary by vehicle class.",
        },
        {
            "id": "usage_class",
            "values": ["private", "commercial"],
            "notes": "Commercial vehicles typically require fitness, route permit, and periodic tax; private rules differ by class.",
        },
        {
            "id": "procedure_action",
            "values": [
                "fitness_issue",
                "fitness_renewal",
                "tax_token_issue",
                "tax_token_renewal",
                "mv_tax_payment",
                "advance_income_tax",
                "route_permit_issue",
                "route_permit_renewal",
                "vehicle_modification",
            ],
        },
        {
            "id": "route_permit_type",
            "values": ["UNKNOWN"],
            "notes": "Route-type matrix (inter-district, city, long-route, etc.) not extracted in this research pass.",
        },
        {
            "id": "fitness_validity_period",
            "values": ["UNVERIFIED"],
            "notes": "Validity periods by vehicle class are NOT verified in this batch — do not publish invented durations.",
        },
    ],
    "do_not_flatten": [
        "brta-route-permit (portal static page) vs transport-route-permit (BSP operator service)",
        "brta-driving-school-registration vs transport-driving-school-licence",
        "fitness/tax renewal vs engine/color/tyre modification",
        "MV tax payment portal vs tax token issue/renewal",
        "private car fitness rules vs commercial bus/truck fitness rules",
    ],
}

SOURCES = [
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
        "freshness_note": "Owner/dealer account prerequisite for BSP fitness, tax, and route permit workflows",
    },
    {
        "source_id": "src-bsp-home",
        "source_url": "https://bsp.brta.gov.bd/bsp/?lan=en",
        "source_title": "BSP — Service Portal Hub",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Bangladesh Road Transport Authority (BRTA)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "en",
        "snapshot_path": None,
        "freshness_note": "Hub for payment verification, e-document verification, and operator services",
    },
    {
        "source_id": "src-bsp-fee-calculator",
        "source_url": "https://bsp.brta.gov.bd/feeCalculator",
        "source_title": "BSP — Fee Calculator (registration, fitness, route permit, tax)",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Bangladesh Road Transport Authority (BRTA)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "en",
        "snapshot_path": None,
        "freshness_note": "Vehicle-type and action-dependent fees; numeric matrix requires interactive session",
    },
    {
        "source_id": "src-bsp-road-safety",
        "source_url": "https://bsp.brta.gov.bd/roadSafety",
        "source_title": "BSP — Road Safety / Driving Training School Registration",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Bangladesh Road Transport Authority (BRTA)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "en",
        "snapshot_path": None,
        "freshness_note": "Catalogue official_source for brta-driving-school-registration",
    },
    {
        "source_id": "src-bsp-maintenance-notice",
        "source_url": "https://bsp.brta.gov.bd/",
        "source_title": "BSP — Operating Hours Notice",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Bangladesh Road Transport Authority (BRTA)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "en",
        "snapshot_path": "source_snapshots/bsp_hours_notice.html",
        "freshness_note": "Cross-batch reference: BSP available 08:00–22:00 BST",
    },
    {
        "source_id": "src-mvtax-portal",
        "source_url": "https://brta.cnsbd.com/mvtax_brta",
        "source_title": "BRTA MV Tax Payment Portal",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Bangladesh Road Transport Authority (BRTA)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "en",
        "snapshot_path": None,
        "freshness_note": "Catalogue official_source for brta-mv-tax-payment; linked from BRTA portal e-services",
    },
    {
        "source_id": "src-brta-portal-fitness",
        "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922db91933eb65569e0af12",
        "source_title": "BRTA Portal — Fitness Certificate Issue/Renewal",
        "source_type": "official_website",
        "authority_tier": 2,
        "responsible_body": "Bangladesh Road Transport Authority (BRTA)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "bn",
        "snapshot_path": "source_snapshots/brta_fitness_certificate.html",
        "freshness_note": "Page title confirms fitness issue/renewal; E-Fitness results on BSP per catalogue notes",
    },
    {
        "source_id": "src-brta-portal-tax-token",
        "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922e0ab933eb65569e281ad",
        "source_title": "BRTA Portal — Tax Token Issue/Renewal",
        "source_type": "official_website",
        "authority_tier": 2,
        "responsible_body": "Bangladesh Road Transport Authority (BRTA)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "bn",
        "snapshot_path": "source_snapshots/brta_tax_token.html",
        "freshness_note": "Catalogue official_source for brta-tax-token",
    },
    {
        "source_id": "src-brta-portal-route-permit",
        "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922df7a933eb65569e2240e",
        "source_title": "BRTA Portal — Route Permit Issue/Renewal",
        "source_type": "official_website",
        "authority_tier": 2,
        "responsible_body": "Bangladesh Road Transport Authority (BRTA)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "bn",
        "snapshot_path": "source_snapshots/brta_route_permit.html",
        "freshness_note": "Portal static page for brta-route-permit; distinct from BSP transport-route-permit workflow",
    },
    {
        "source_id": "src-brta-portal-advance-tax",
        "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922e058933eb65569e269cd",
        "source_title": "BRTA Portal — Advance Income Tax Payment (Motor Vehicle)",
        "source_type": "official_website",
        "authority_tier": 2,
        "responsible_body": "Bangladesh Road Transport Authority (BRTA)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "bn",
        "snapshot_path": "source_snapshots/brta_advance_income_tax.html",
        "freshness_note": "Catalogue notes AIT available via BSP and BRTA Seba mobile app",
    },
    {
        "source_id": "src-brta-portal-color-change",
        "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922dd3a933eb65569e14058",
        "source_title": "BRTA Portal — Vehicle Color Change",
        "source_type": "official_website",
        "authority_tier": 2,
        "responsible_body": "Bangladesh Road Transport Authority (BRTA)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "bn",
        "snapshot_path": "source_snapshots/brta_color_change.html",
        "freshness_note": "Vehicle modification; separate from fitness/tax procedures",
    },
    {
        "source_id": "src-brta-portal-engine-change",
        "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922dfbe933eb65569e23c89",
        "source_title": "BRTA Portal — Vehicle Engine Change",
        "source_type": "official_website",
        "authority_tier": 2,
        "responsible_body": "Bangladesh Road Transport Authority (BRTA)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "bn",
        "snapshot_path": "source_snapshots/brta_engine_change.html",
        "freshness_note": "Vehicle modification; separate from fitness/tax procedures",
    },
    {
        "source_id": "src-brta-portal-tire-change",
        "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922dcdf933eb65569e127ec",
        "source_title": "BRTA Portal — Vehicle Tire Size Change",
        "source_type": "official_website",
        "authority_tier": 2,
        "responsible_body": "Bangladesh Road Transport Authority (BRTA)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "bn",
        "snapshot_path": "source_snapshots/brta_tire_size_change.html",
        "freshness_note": "Vehicle modification; separate from fitness/tax procedures",
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
        "source_id": "src-catalogue-transport",
        "source_url": "data/service_catalogue/by_category/transport.json",
        "source_title": "Canonical Service Catalogue — Transport/BRTA entries",
        "source_type": "internal_catalogue",
        "authority_tier": 2,
        "responsible_body": "Bangladesh Road Transport Authority (BRTA)",
        "published_date": "2026-08-24",
        "retrieved_at": TODAY,
        "language": "en",
        "freshness_note": "464-service finalized catalogue; scope discovery authority",
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

    # --- brta-fitness-certificate ---
    sid = "brta-fitness-certificate"
    claims += [
        claim(
            "c-portal-url",
            sid,
            "application_url",
            "Vehicle fitness certificate issue and renewal guidance published on BRTA portal static page.",
            "OFFICIAL",
            ["src-brta-portal-fitness", "src-catalogue-transport"],
        ),
        claim(
            "c-e-fitness-bsp",
            sid,
            "procedure_step",
            "E-Fitness inspection results are viewable on BSP per catalogue discovery notes — digital fitness workflow complements circle office inspection.",
            "OFFICIAL",
            ["src-catalogue-transport", "src-bsp-home"],
        ),
        claim(
            "c-physical-inspection-required",
            sid,
            "procedure_step",
            "Fitness issuance/renewal requires vehicle inspection at authorized inspection centre or circle office — not fully online-only.",
            "OFFICIAL",
            ["src-brta-portal-fitness", "src-catalogue-transport"],
            condition={"requirement_class": "MUST_NEED"},
            verification_scope="LOCATION_SPECIFIC",
        ),
        claim(
            "c-validity-by-class-unverified",
            sid,
            "restriction",
            "Fitness certificate validity period by vehicle class (e.g., private car vs commercial bus) is NOT verified in this research pass — do not publish specific year durations.",
            "DISCOVERY",
            ["src-brta-portal-fitness", "src-catalogue-transport"],
            verification_scope="UNVERIFIED",
        ),
        claim(
            "c-commercial-vs-private-rules-differ",
            sid,
            "eligibility",
            "Fitness requirements and inspection frequency differ between private and commercial vehicle classes; rules must not be generalized from one class to another.",
            "OFFICIAL",
            ["src-brta-portal-fitness", "src-catalogue-transport"],
            condition={"requirement_class": "CONDITIONAL", "if": "vehicle_class_and_usage"},
            verification_scope="UNVERIFIED",
        ),
        claim(
            "c-fitness-fee-calculator",
            sid,
            "fee",
            "Fitness certificate fees depend on vehicle type and issue vs renewal action; amounts computed via BSP fee calculator.",
            "OFFICIAL",
            ["src-bsp-fee-calculator", "src-brta-portal-fitness"],
            structured={
                "service": sid,
                "vehicle_type": "VARIES",
                "action": "fitness_issue_or_renewal",
                "condition": "vehicle_class_selected_in_calculator",
                "amount": "CALCULATOR_DERIVED",
                "source": "src-bsp-fee-calculator",
                "verification": "PENDING_INTERACTIVE_EXTRACT",
            },
        ),
        claim(
            "c-bsp-account-prerequisite",
            sid,
            "eligibility",
            "BSP owner account registration may be required to view E-Fitness results and pay fitness-related fees online.",
            "OFFICIAL",
            ["src-bsp-register", "src-bsp-home", "src-catalogue-transport"],
            condition={"requirement_class": "CONDITIONAL", "if": "online_e_fitness_or_payment"},
        ),
        claim(
            "c-distinct-from-modification",
            sid,
            "restriction",
            "Fitness renewal is distinct from vehicle modification services (engine/color/tyre change) in this batch — modifications may trigger re-inspection separately.",
            "OFFICIAL",
            ["src-brta-portal-fitness", "src-brta-portal-engine-change"],
            condition={"requirement_class": "NOT_APPLICABLE", "if": "procedure_is_modification_only"},
        ),
        claim(
            "c-practical-bsp-hours",
            sid,
            "practical_tip",
            "Check E-Fitness results and pay fees during BSP operating hours (08:00–22:00 BST); sub-portals may be unavailable outside window.",
            "PRACTICAL",
            ["src-bsp-maintenance-notice"],
        ),
    ]

    # --- brta-tax-token ---
    sid = "brta-tax-token"
    claims += [
        claim(
            "c-portal-url",
            sid,
            "application_url",
            "Motor vehicle tax token issue and renewal process published on BRTA portal static page.",
            "OFFICIAL",
            ["src-brta-portal-tax-token", "src-catalogue-transport"],
        ),
        claim(
            "c-registered-vehicle-required",
            sid,
            "eligibility",
            "Tax token issued for vehicles already registered with BRTA; requires valid registration record.",
            "OFFICIAL",
            ["src-brta-portal-tax-token", "src-catalogue-transport"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-tax-token-fee-calculator",
            sid,
            "fee",
            "Tax token issue/renewal fees vary by vehicle type and engine capacity; amounts via BSP fee calculator.",
            "OFFICIAL",
            ["src-bsp-fee-calculator", "src-brta-portal-tax-token"],
            structured={
                "service": sid,
                "vehicle_type": "VARIES",
                "action": "tax_token_issue_or_renewal",
                "condition": "vehicle_class_and_tax_year",
                "amount": "CALCULATOR_DERIVED",
                "source": "src-bsp-fee-calculator",
                "verification": "PENDING_INTERACTIVE_EXTRACT",
            },
        ),
        claim(
            "c-distinct-from-mv-tax",
            sid,
            "restriction",
            "Tax token issue/renewal is distinct from MV tax payment (brta-mv-tax-payment at brta.cnsbd.com/mvtax_brta) — related but separate procedures.",
            "OFFICIAL",
            ["src-brta-portal-tax-token", "src-mvtax-portal", "src-catalogue-transport"],
        ),
        claim(
            "c-circle-office-collection",
            sid,
            "procedure_step",
            "Physical tax token sticker or e-tax token collection may require circle office visit after fee payment.",
            "OFFICIAL",
            ["src-brta-portal-tax-token"],
            verification_scope="LOCATION_SPECIFIC",
        ),
        claim(
            "c-fitness-may-be-prerequisite",
            sid,
            "conditional_document",
            "Valid fitness certificate may be required before tax token renewal for applicable vehicle classes.",
            "OFFICIAL",
            ["src-brta-portal-tax-token", "src-brta-portal-fitness"],
            condition={"requirement_class": "CONDITIONAL", "if": "vehicle_class_requires_fitness"},
        ),
        claim(
            "c-e-tax-token-verifiable",
            sid,
            "procedure_step",
            "E-tax token can be verified via BSP e-document verification service (brta-e-document-verification).",
            "OFFICIAL",
            ["src-bsp-home", "src-catalogue-transport"],
            condition={"requirement_class": "RECOMMENDED"},
        ),
        claim(
            "c-practical-verify-payment-first",
            sid,
            "practical_tip",
            "Use BSP payment verification before visiting circle office for tax token collection to confirm fee settlement.",
            "PRACTICAL",
            ["src-bsp-home", "src-bsp-fee-calculator"],
        ),
    ]

    # --- brta-mv-tax-payment ---
    sid = "brta-mv-tax-payment"
    claims += [
        claim(
            "c-portal-url",
            sid,
            "application_url",
            "Motor vehicle tax (MV tax) payment available at brta.cnsbd.com/mvtax_brta per catalogue official_source.",
            "OFFICIAL",
            ["src-mvtax-portal", "src-catalogue-transport"],
        ),
        claim(
            "c-linked-from-brta-portal",
            sid,
            "application_url",
            "MV tax portal linked from BRTA portal internal e-services section per catalogue discovery notes.",
            "OFFICIAL",
            ["src-mvtax-portal", "src-brta-portal-home"],
        ),
        claim(
            "c-distinct-from-tax-token",
            sid,
            "restriction",
            "MV tax payment portal is separate from tax token issue/renewal (brta-tax-token) — both relate to vehicle taxation but use different workflows.",
            "OFFICIAL",
            ["src-mvtax-portal", "src-brta-portal-tax-token"],
        ),
        claim(
            "c-registered-vehicle-required",
            sid,
            "eligibility",
            "MV tax payment requires registered vehicle identification (registration number/chassis) on payment portal.",
            "OFFICIAL",
            ["src-mvtax-portal", "src-catalogue-transport"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-mv-tax-amount-calculator",
            sid,
            "fee",
            "MV tax amounts depend on vehicle class, engine capacity, and tax year; may align with BSP fee calculator categories but portal computes at payment time.",
            "OFFICIAL",
            ["src-mvtax-portal", "src-bsp-fee-calculator"],
            structured={
                "service": sid,
                "vehicle_type": "VARIES",
                "action": "mv_tax_payment",
                "condition": "vehicle_class_and_tax_year",
                "amount": "CALCULATOR_DERIVED",
                "source": "src-mvtax-portal",
                "verification": "PENDING_INTERACTIVE_EXTRACT",
            },
        ),
        claim(
            "c-online-payment-channel",
            sid,
            "procedure_step",
            "MV tax payable online via dedicated portal — reduces need for in-person payment for eligible cases.",
            "OFFICIAL",
            ["src-mvtax-portal"],
        ),
        claim(
            "c-advance-tax-related",
            sid,
            "conditional_document",
            "Advance income tax (brta-advance-income-tax) may interact with overall vehicle tax settlement — exact sequencing not fully captured.",
            "DISCOVERY",
            ["src-mvtax-portal", "src-brta-portal-advance-tax"],
            condition={"requirement_class": "CONDITIONAL", "if": "ait_applicable_to_vehicle_class"},
        ),
        claim(
            "c-practical-keep-receipt",
            sid,
            "practical_tip",
            "Save MV tax payment receipt/transaction ID for tax token renewal and circle office visits.",
            "PRACTICAL",
            ["src-mvtax-portal"],
        ),
    ]

    # --- brta-advance-income-tax ---
    sid = "brta-advance-income-tax"
    claims += [
        claim(
            "c-portal-url",
            sid,
            "application_url",
            "Advance income tax (AIT) payment for motor vehicles published on BRTA portal static page.",
            "OFFICIAL",
            ["src-brta-portal-advance-tax", "src-catalogue-transport"],
        ),
        claim(
            "c-bsp-and-mobile-app",
            sid,
            "application_url",
            "AIT payment available via BSP and BRTA Seba mobile app per catalogue discovery notes.",
            "OFFICIAL",
            ["src-brta-portal-advance-tax", "src-bsp-home", "src-catalogue-transport"],
        ),
        claim(
            "c-vehicle-owner-target",
            sid,
            "eligibility",
            "Advance income tax applies to registered motor vehicle owners per catalogue target_user.",
            "OFFICIAL",
            ["src-catalogue-transport", "src-brta-portal-advance-tax"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-ait-fee-calculator",
            sid,
            "fee",
            "AIT amounts depend on vehicle class and assessed value; fee calculator may include AIT-related categories.",
            "OFFICIAL",
            ["src-bsp-fee-calculator", "src-brta-portal-advance-tax"],
            structured={
                "service": sid,
                "vehicle_type": "VARIES",
                "action": "advance_income_tax",
                "condition": "vehicle_class_and_assessed_value",
                "amount": "CALCULATOR_DERIVED",
                "source": "src-bsp-fee-calculator",
                "verification": "PENDING_INTERACTIVE_EXTRACT",
            },
        ),
        claim(
            "c-distinct-from-mv-tax",
            sid,
            "restriction",
            "Advance income tax is distinct from MV tax payment (brta-mv-tax-payment) and tax token (brta-tax-token) — separate tax categories.",
            "OFFICIAL",
            ["src-brta-portal-advance-tax", "src-mvtax-portal", "src-brta-portal-tax-token"],
        ),
        claim(
            "c-registration-prerequisite",
            sid,
            "eligibility",
            "Vehicle must be registered with BRTA for AIT assessment tied to motor vehicle ownership.",
            "OFFICIAL",
            ["src-brta-portal-advance-tax", "src-catalogue-transport"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-payment-verification",
            sid,
            "procedure_step",
            "AIT payment status verifiable via BSP payment verification after online payment.",
            "OFFICIAL",
            ["src-bsp-home", "src-brta-portal-advance-tax"],
            condition={"requirement_class": "RECOMMENDED"},
        ),
        claim(
            "c-practical-bsp-hours",
            sid,
            "practical_tip",
            "Pay AIT via BSP during operating hours (08:00–22:00 BST) when using online channels.",
            "PRACTICAL",
            ["src-bsp-maintenance-notice"],
        ),
    ]

    # --- brta-route-permit ---
    sid = "brta-route-permit"
    claims += [
        claim(
            "c-portal-url",
            sid,
            "application_url",
            "Route permit issue and renewal process published on BRTA portal static page for brta-route-permit.",
            "OFFICIAL",
            ["src-brta-portal-route-permit", "src-catalogue-transport"],
        ),
        claim(
            "c-commercial-operator-target",
            sid,
            "eligibility",
            "Route permits target commercial transport operators and businesses per catalogue target_user.",
            "OFFICIAL",
            ["src-catalogue-transport", "src-brta-portal-route-permit"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-not-applicable-private-car",
            sid,
            "restriction",
            "Route permit not applicable to standard private passenger vehicles — commercial/public transport service authorization.",
            "OFFICIAL",
            ["src-brta-portal-route-permit", "src-catalogue-transport"],
            condition={"requirement_class": "NOT_APPLICABLE", "if": "usage_class_private_passenger"},
        ),
        claim(
            "c-route-permit-fee-calculator",
            sid,
            "fee",
            "Route permit fees depend on vehicle type and permit category; amounts via BSP fee calculator.",
            "OFFICIAL",
            ["src-bsp-fee-calculator", "src-brta-portal-route-permit"],
            structured={
                "service": sid,
                "vehicle_type": "VARIES",
                "action": "route_permit_issue_or_renewal",
                "condition": "route_type_and_vehicle_class",
                "amount": "CALCULATOR_DERIVED",
                "source": "src-bsp-fee-calculator",
                "verification": "PENDING_INTERACTIVE_EXTRACT",
            },
        ),
        claim(
            "c-fitness-prerequisite",
            sid,
            "conditional_document",
            "Valid fitness certificate typically required before route permit issue/renewal for commercial vehicles.",
            "OFFICIAL",
            ["src-brta-portal-route-permit", "src-brta-portal-fitness"],
            condition={"requirement_class": "CONDITIONAL", "if": "commercial_vehicle"},
        ),
        claim(
            "c-crossref-transport-route-permit",
            sid,
            "restriction",
            "brta-route-permit (portal static page) differs from transport-route-permit (BSP operator service) — related but separate catalogue entries; do not merge workflows.",
            "OFFICIAL",
            ["src-brta-portal-route-permit", "src-bsp-home", "src-catalogue-transport"],
        ),
        claim(
            "c-route-type-matrix-unverified",
            sid,
            "restriction",
            "Route permit categories (inter-district, city, long-route, etc.) and applicability matrix not extracted from portal in this pass.",
            "DISCOVERY",
            ["src-brta-portal-route-permit"],
            verification_scope="UNVERIFIED",
        ),
        claim(
            "c-circle-office-submission",
            sid,
            "procedure_step",
            "Route permit applications submitted to relevant BRTA circle office with supporting documents.",
            "OFFICIAL",
            ["src-brta-portal-route-permit"],
            verification_scope="LOCATION_SPECIFIC",
        ),
    ]

    # --- transport-route-permit ---
    sid = "transport-route-permit"
    claims += [
        claim(
            "c-bsp-service",
            sid,
            "application_url",
            "Route permit (BRTA) is a BSP operator licensing service per catalogue finalization_notes; official_source is bsp.brta.gov.bd.",
            "OFFICIAL",
            ["src-bsp-home", "src-catalogue-transport"],
        ),
        claim(
            "c-crossref-brta-route-permit",
            sid,
            "restriction",
            "transport-route-permit (BSP workflow) is related to but distinct from brta-route-permit (portal static page) — cross-reference both, do not flatten.",
            "OFFICIAL",
            ["src-bsp-home", "src-brta-portal-route-permit", "src-catalogue-transport"],
        ),
        claim(
            "c-operator-business-target",
            sid,
            "eligibility",
            "Route permit service targets business operators per catalogue target_user (business, operator).",
            "OFFICIAL",
            ["src-catalogue-transport"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-route-permit-fee-calculator",
            sid,
            "fee",
            "Route permit fees on BSP computed via fee calculator by vehicle type and route category.",
            "OFFICIAL",
            ["src-bsp-fee-calculator", "src-bsp-home"],
            structured={
                "service": sid,
                "vehicle_type": "VARIES",
                "action": "route_permit_issue_or_renewal",
                "condition": "route_type_and_vehicle_class",
                "amount": "CALCULATOR_DERIVED",
                "source": "src-bsp-fee-calculator",
                "verification": "PENDING_INTERACTIVE_EXTRACT",
            },
        ),
        claim(
            "c-bsp-account-required",
            sid,
            "eligibility",
            "BSP operator/business account likely required for route permit application on BSP.",
            "DISCOVERY",
            ["src-bsp-register", "src-bsp-home"],
            condition={"requirement_class": "CONDITIONAL", "if": "online_bsp_application"},
        ),
        claim(
            "c-route-type-matrix-unverified",
            sid,
            "restriction",
            "Route-type applicability matrix (inter-city, intra-district, etc.) not extracted from BSP in this research pass.",
            "DISCOVERY",
            ["src-bsp-home", "src-brta-portal-route-permit"],
            verification_scope="UNVERIFIED",
        ),
        claim(
            "c-fitness-tax-prerequisites",
            sid,
            "conditional_document",
            "Valid fitness and current tax token may be prerequisites for route permit renewal.",
            "OFFICIAL",
            ["src-brta-portal-route-permit", "src-brta-portal-fitness", "src-brta-portal-tax-token"],
            condition={"requirement_class": "CONDITIONAL", "if": "commercial_vehicle_renewal"},
        ),
        claim(
            "c-practical-bsp-hours",
            sid,
            "practical_tip",
            "Access BSP route permit services during 08:00–22:00 BST operating window.",
            "PRACTICAL",
            ["src-bsp-maintenance-notice"],
        ),
    ]

    # --- brta-fee-calculator ---
    sid = "brta-fee-calculator"
    claims += [
        claim(
            "c-portal-url",
            sid,
            "application_url",
            "BRTA fee calculator available at bsp.brta.gov.bd/feeCalculator per catalogue official_source.",
            "OFFICIAL",
            ["src-bsp-fee-calculator", "src-catalogue-transport"],
        ),
        claim(
            "c-covers-fitness-route-tax",
            sid,
            "procedure_step",
            "Fee calculator covers fitness, route permit, registration, and license fees per catalogue notes.",
            "OFFICIAL",
            ["src-bsp-fee-calculator", "src-catalogue-transport"],
        ),
        claim(
            "c-vehicle-type-dependent",
            sid,
            "restriction",
            "All fee outputs depend on selected vehicle type/class — no single flat fee for any service category.",
            "OFFICIAL",
            ["src-bsp-fee-calculator"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-interactive-matrix-not-extracted",
            sid,
            "fee",
            "Per-vehicle-type numeric fee matrix not statically published; requires interactive calculator session.",
            "DISCOVERY",
            ["src-bsp-fee-calculator"],
            structured={
                "service": sid,
                "vehicle_type": "VARIES",
                "action": "fee_lookup",
                "condition": "service_and_vehicle_class_selected",
                "amount": "CALCULATOR_DERIVED",
                "source": "src-bsp-fee-calculator",
                "verification": "PENDING_INTERACTIVE_EXTRACT",
            },
        ),
        claim(
            "c-cross-cutting-tool",
            sid,
            "restriction",
            "Fee calculator is cross-cutting — referenced by fitness, tax token, route permit, and modification services in this batch.",
            "OFFICIAL",
            ["src-bsp-fee-calculator", "src-catalogue-transport"],
        ),
        claim(
            "c-may-differ-from-static-pages",
            sid,
            "restriction",
            "Calculator-derived fees may differ from outdated static fee tables on portal pages — calculator treated as authoritative when available.",
            "DISCOVERY",
            ["src-bsp-fee-calculator", "src-brta-portal-home"],
        ),
        claim(
            "c-no-login-required-likely",
            sid,
            "eligibility",
            "Fee calculator likely accessible without BSP login for fee estimation (workflow not fully snapshotted).",
            "DISCOVERY",
            ["src-bsp-fee-calculator"],
            condition={"requirement_class": "RECOMMENDED"},
        ),
        claim(
            "c-practical-use-before-visit",
            sid,
            "practical_tip",
            "Use fee calculator before circle office visits for fitness, tax token, or route permit to prepare exact payment amounts.",
            "PRACTICAL",
            ["src-bsp-fee-calculator"],
        ),
    ]

    # --- brta-payment-verification ---
    sid = "brta-payment-verification"
    claims += [
        claim(
            "c-portal-url",
            sid,
            "application_url",
            "BRTA payment verification available via BSP hub at bsp.brta.gov.bd per catalogue official_source.",
            "OFFICIAL",
            ["src-bsp-home", "src-catalogue-transport"],
        ),
        claim(
            "c-cross-cutting-verification",
            sid,
            "procedure_step",
            "Payment verification applies across BSP services including fitness, tax, route permit, and registration fees.",
            "OFFICIAL",
            ["src-bsp-home", "src-bsp-fee-calculator"],
        ),
        claim(
            "c-transaction-id-required",
            sid,
            "document",
            "Payment verification requires transaction reference or payment receipt details from BSP payment.",
            "DISCOVERY",
            ["src-bsp-home"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-pre-circle-office-check",
            sid,
            "procedure_step",
            "Verify payment status online before visiting circle office for document collection (tax token, fitness certificate).",
            "OFFICIAL",
            ["src-bsp-home", "src-brta-portal-tax-token"],
            condition={"requirement_class": "RECOMMENDED"},
        ),
        claim(
            "c-bsp-account-may-be-required",
            sid,
            "eligibility",
            "Payment verification may require BSP account login linked to the payment transaction.",
            "DISCOVERY",
            ["src-bsp-home", "src-bsp-register"],
            condition={"requirement_class": "CONDITIONAL", "if": "payment_linked_to_bsp_account"},
        ),
        claim(
            "c-not-a-payment-gateway",
            sid,
            "restriction",
            "Payment verification confirms prior payment — it does not initiate new payments.",
            "OFFICIAL",
            ["src-bsp-home"],
        ),
        claim(
            "c-practical-bsp-hours",
            sid,
            "practical_tip",
            "Payment verification portal subject to BSP operating hours (08:00–22:00 BST).",
            "PRACTICAL",
            ["src-bsp-maintenance-notice"],
        ),
        claim(
            "c-distinct-from-e-document",
            sid,
            "restriction",
            "Payment verification is distinct from e-document verification (brta-e-document-verification) — confirms payment, not document authenticity.",
            "OFFICIAL",
            ["src-bsp-home", "src-catalogue-transport"],
        ),
    ]

    # --- brta-e-document-verification ---
    sid = "brta-e-document-verification"
    claims += [
        claim(
            "c-portal-url",
            sid,
            "application_url",
            "E-tax token and e-license verification available via BSP hub per catalogue official_source and service name.",
            "OFFICIAL",
            ["src-bsp-home", "src-catalogue-transport"],
        ),
        claim(
            "c-verifies-digital-documents",
            sid,
            "procedure_step",
            "Service verifies authenticity of e-tax tokens and e-licenses for citizens and law enforcement.",
            "OFFICIAL",
            ["src-catalogue-transport", "src-bsp-home"],
        ),
        claim(
            "c-not-payment-verification",
            sid,
            "restriction",
            "E-document verification confirms document validity — distinct from payment verification (brta-payment-verification).",
            "OFFICIAL",
            ["src-bsp-home", "src-catalogue-transport"],
        ),
        claim(
            "c-e-fitness-may-be-included",
            sid,
            "procedure_step",
            "E-Fitness results from brta-fitness-certificate may be viewable/verifiable on BSP per catalogue cross-notes.",
            "OFFICIAL",
            ["src-catalogue-transport", "src-brta-portal-fitness"],
            condition={"requirement_class": "CONDITIONAL", "if": "e_fitness_enabled_for_vehicle"},
        ),
        claim(
            "c-public-verification-tool",
            sid,
            "eligibility",
            "Verification tool usable by citizens and law enforcement per catalogue target_user.",
            "OFFICIAL",
            ["src-catalogue-transport"],
        ),
        claim(
            "c-document-id-required",
            sid,
            "document",
            "Verification requires document identifier (token number, license number, or QR code) from issued e-document.",
            "DISCOVERY",
            ["src-bsp-home"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-no-fee-for-verification-likely",
            sid,
            "fee",
            "Document verification likely free — no fee schedule captured for verification lookups in this pass.",
            "DISCOVERY",
            ["src-bsp-home"],
            condition={"requirement_class": "NOT_APPLICABLE", "if": "verification_lookup_only"},
        ),
        claim(
            "c-practical-law-enforcement-use",
            sid,
            "practical_tip",
            "Law enforcement can use e-document verification roadside to confirm valid e-tax token or e-license without physical sticker.",
            "PRACTICAL",
            ["src-catalogue-transport"],
        ),
    ]

    # --- brta-bsp-user-registration ---
    sid = "brta-bsp-user-registration"
    claims += [
        claim(
            "c-portal-url",
            sid,
            "application_url",
            "BSP user registration at bsp.brta.gov.bd/register for driver, owner, or dealer accounts.",
            "OFFICIAL",
            ["src-bsp-register", "src-catalogue-transport"],
        ),
        claim(
            "c-nid-linked-mobile",
            sid,
            "document",
            "Registration requires NID-linked mobile number per catalogue discovery notes.",
            "OFFICIAL",
            ["src-bsp-register", "src-catalogue-transport"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-user-types",
            sid,
            "eligibility",
            "Register as driver, vehicle owner, or vehicle dealer — account type determines accessible BSP services.",
            "OFFICIAL",
            ["src-catalogue-transport", "src-bsp-register"],
        ),
        claim(
            "c-prerequisite-for-batch-services",
            sid,
            "eligibility",
            "BSP account prerequisite for online fitness (E-Fitness), tax payment, route permit, and payment verification in this batch.",
            "OFFICIAL",
            ["src-bsp-register", "src-bsp-home", "src-catalogue-transport"],
            condition={"requirement_class": "CONDITIONAL", "if": "online_bsp_workflow"},
        ),
        claim(
            "c-not-applicable-verification-only",
            sid,
            "restriction",
            "BSP registration not required for read-only e-document verification lookups that accept public document IDs.",
            "DISCOVERY",
            ["src-bsp-home", "src-catalogue-transport"],
            condition={"requirement_class": "NOT_APPLICABLE", "if": "public_verification_lookup_only"},
        ),
        claim(
            "c-dealer-for-school-registration",
            sid,
            "eligibility",
            "Business/dealer account type may be required for driving school registration workflows.",
            "OFFICIAL",
            ["src-bsp-register", "src-bsp-road-safety"],
            condition={"requirement_class": "CONDITIONAL", "if": "applicant_is_driving_school_operator"},
        ),
        claim(
            "c-no-registration-fee-known",
            sid,
            "fee",
            "BSP account registration fee (if any) not published on sources reviewed in this pass.",
            "DISCOVERY",
            ["src-bsp-register"],
        ),
        claim(
            "c-practical-complete-before-fitness-tax",
            sid,
            "practical_tip",
            "Complete BSP registration before attempting E-Fitness, MV tax, or route permit online workflows.",
            "PRACTICAL",
            ["src-bsp-register", "src-bsp-maintenance-notice"],
        ),
    ]

    # --- brta-color-change ---
    sid = "brta-color-change"
    claims += [
        claim(
            "c-portal-url",
            sid,
            "application_url",
            "Vehicle color change approval process published on BRTA portal static page.",
            "OFFICIAL",
            ["src-brta-portal-color-change", "src-catalogue-transport"],
        ),
        claim(
            "c-modification-not-fitness",
            sid,
            "restriction",
            "Color change is a vehicle modification procedure — distinct from fitness certificate renewal or tax token services.",
            "OFFICIAL",
            ["src-brta-portal-color-change", "src-brta-portal-fitness"],
            condition={"requirement_class": "NOT_APPLICABLE", "if": "procedure_is_fitness_or_tax_only"},
        ),
        claim(
            "c-registered-vehicle-required",
            sid,
            "eligibility",
            "Vehicle must be registered with BRTA before color change approval.",
            "OFFICIAL",
            ["src-brta-portal-color-change"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-original-rc-required",
            sid,
            "document",
            "Original registration certificate required for color change application.",
            "OFFICIAL",
            ["src-brta-portal-color-change"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-color-change-fee-calculator",
            sid,
            "fee",
            "Color change fees vehicle-type dependent via BSP fee calculator.",
            "OFFICIAL",
            ["src-bsp-fee-calculator", "src-brta-portal-color-change"],
            structured={
                "service": sid,
                "vehicle_type": "VARIES",
                "action": "vehicle_modification_color",
                "condition": "vehicle_class",
                "amount": "CALCULATOR_DERIVED",
                "source": "src-bsp-fee-calculator",
                "verification": "PENDING_INTERACTIVE_EXTRACT",
            },
        ),
        claim(
            "c-reinspection-may-be-required",
            sid,
            "conditional_document",
            "Fitness re-inspection may be required after color change before updated RC reflects modification.",
            "DISCOVERY",
            ["src-brta-portal-color-change", "src-brta-portal-fitness"],
            condition={"requirement_class": "CONDITIONAL", "if": "post_modification_inspection_required"},
        ),
        claim(
            "c-circle-office-application",
            sid,
            "procedure_step",
            "Color change application submitted to relevant BRTA circle office with prescribed forms.",
            "OFFICIAL",
            ["src-brta-portal-color-change"],
            verification_scope="LOCATION_SPECIFIC",
        ),
        claim(
            "c-practical-separate-from-info-correction",
            sid,
            "practical_tip",
            "Color change is a modification service (03C), not registration info correction (03B brta-vehicle-info-correction).",
            "PRACTICAL",
            ["src-brta-portal-color-change", "src-catalogue-transport"],
        ),
    ]

    # --- brta-engine-change ---
    sid = "brta-engine-change"
    claims += [
        claim(
            "c-portal-url",
            sid,
            "application_url",
            "Vehicle engine change approval process published on BRTA portal static page.",
            "OFFICIAL",
            ["src-brta-portal-engine-change", "src-catalogue-transport"],
        ),
        claim(
            "c-modification-not-fitness",
            sid,
            "restriction",
            "Engine change is a vehicle modification — distinct from fitness renewal, tax token, and route permit procedures.",
            "OFFICIAL",
            ["src-brta-portal-engine-change", "src-brta-portal-fitness"],
            condition={"requirement_class": "NOT_APPLICABLE", "if": "procedure_is_fitness_or_tax_only"},
        ),
        claim(
            "c-registered-vehicle-required",
            sid,
            "eligibility",
            "Vehicle must be registered before engine change approval.",
            "OFFICIAL",
            ["src-brta-portal-engine-change"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-engine-proof-required",
            sid,
            "conditional_document",
            "Supporting documents for new engine (invoice, customs release if imported engine) required per modification type.",
            "OFFICIAL",
            ["src-brta-portal-engine-change"],
            condition={"requirement_class": "CONDITIONAL", "if": "engine_origin_and_type"},
        ),
        claim(
            "c-engine-change-fee-calculator",
            sid,
            "fee",
            "Engine change fees vehicle-type dependent via BSP fee calculator.",
            "OFFICIAL",
            ["src-bsp-fee-calculator", "src-brta-portal-engine-change"],
            structured={
                "service": sid,
                "vehicle_type": "VARIES",
                "action": "vehicle_modification_engine",
                "condition": "vehicle_class",
                "amount": "CALCULATOR_DERIVED",
                "source": "src-bsp-fee-calculator",
                "verification": "PENDING_INTERACTIVE_EXTRACT",
            },
        ),
        claim(
            "c-fitness-reinspection-likely",
            sid,
            "conditional_document",
            "Fitness re-inspection likely required after engine change due to altered vehicle specifications.",
            "DISCOVERY",
            ["src-brta-portal-engine-change", "src-brta-portal-fitness"],
            condition={"requirement_class": "CONDITIONAL", "if": "post_engine_change"},
        ),
        claim(
            "c-circle-office-application",
            sid,
            "procedure_step",
            "Engine change application submitted to BRTA circle office with technical inspection.",
            "OFFICIAL",
            ["src-brta-portal-engine-change"],
            verification_scope="LOCATION_SPECIFIC",
        ),
        claim(
            "c-practical-update-rc-after-approval",
            sid,
            "practical_tip",
            "Ensure RC/engine number updated on registration record after approved engine change.",
            "PRACTICAL",
            ["src-brta-portal-engine-change"],
        ),
    ]

    # --- brta-tire-size-change ---
    sid = "brta-tire-size-change"
    claims += [
        claim(
            "c-portal-url",
            sid,
            "application_url",
            "Vehicle tire size (width) change approval process published on BRTA portal static page.",
            "OFFICIAL",
            ["src-brta-portal-tire-change", "src-catalogue-transport"],
        ),
        claim(
            "c-modification-not-fitness",
            sid,
            "restriction",
            "Tire size change is a vehicle modification — separate from fitness certificate and tax token services.",
            "OFFICIAL",
            ["src-brta-portal-tire-change", "src-brta-portal-fitness"],
            condition={"requirement_class": "NOT_APPLICABLE", "if": "procedure_is_fitness_or_tax_only"},
        ),
        claim(
            "c-registered-vehicle-required",
            sid,
            "eligibility",
            "Vehicle must be registered before tire size change approval.",
            "OFFICIAL",
            ["src-brta-portal-tire-change"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-technical-compliance",
            sid,
            "restriction",
            "Proposed tire size must comply with vehicle manufacturer specifications and road safety standards.",
            "OFFICIAL",
            ["src-brta-portal-tire-change"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-tire-change-fee-calculator",
            sid,
            "fee",
            "Tire size change fees vehicle-type dependent via BSP fee calculator.",
            "OFFICIAL",
            ["src-bsp-fee-calculator", "src-brta-portal-tire-change"],
            structured={
                "service": sid,
                "vehicle_type": "VARIES",
                "action": "vehicle_modification_tire",
                "condition": "vehicle_class",
                "amount": "CALCULATOR_DERIVED",
                "source": "src-bsp-fee-calculator",
                "verification": "PENDING_INTERACTIVE_EXTRACT",
            },
        ),
        claim(
            "c-fitness-reinspection-possible",
            sid,
            "conditional_document",
            "Fitness re-inspection may be required if tire modification affects vehicle roadworthiness assessment.",
            "DISCOVERY",
            ["src-brta-portal-tire-change", "src-brta-portal-fitness"],
            condition={"requirement_class": "CONDITIONAL", "if": "modification_affects_roadworthiness"},
        ),
        claim(
            "c-circle-office-application",
            sid,
            "procedure_step",
            "Tire size change application submitted to BRTA circle office.",
            "OFFICIAL",
            ["src-brta-portal-tire-change"],
            verification_scope="LOCATION_SPECIFIC",
        ),
        claim(
            "c-practical-document-new-specs",
            sid,
            "practical_tip",
            "Bring tire specification documentation and invoice when applying for tire width change approval.",
            "PRACTICAL",
            ["src-brta-portal-tire-change"],
        ),
    ]

    # --- brta-driving-school-registration ---
    sid = "brta-driving-school-registration"
    claims += [
        claim(
            "c-portal-url",
            sid,
            "application_url",
            "Motor driving training school registration available via BSP roadSafety portal per catalogue official_source.",
            "OFFICIAL",
            ["src-bsp-road-safety", "src-catalogue-transport"],
        ),
        claim(
            "c-business-operator-target",
            sid,
            "eligibility",
            "Driving school registration targets business operators per catalogue target_user.",
            "OFFICIAL",
            ["src-catalogue-transport", "src-bsp-road-safety"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-brta-mandated-registration",
            sid,
            "restriction",
            "BRTA mandates registration of motor driving training schools per catalogue notes.",
            "OFFICIAL",
            ["src-catalogue-transport", "src-bsp-road-safety"],
        ),
        claim(
            "c-crossref-transport-licence",
            sid,
            "restriction",
            "brta-driving-school-registration (BSP roadSafety) related to but distinct from transport-driving-school-licence (BSP licensing service).",
            "OFFICIAL",
            ["src-bsp-road-safety", "src-bsp-home", "src-catalogue-transport"],
        ),
        claim(
            "c-bsp-account-required",
            sid,
            "eligibility",
            "BSP business/dealer account likely required for driving school registration application.",
            "DISCOVERY",
            ["src-bsp-register", "src-bsp-road-safety"],
            condition={"requirement_class": "CONDITIONAL", "if": "online_application"},
        ),
        claim(
            "c-registration-fee-unknown",
            sid,
            "fee",
            "Driving school registration fee not statically published; may appear in fee calculator under road safety category.",
            "DISCOVERY",
            ["src-bsp-fee-calculator", "src-bsp-road-safety"],
            structured={
                "service": sid,
                "vehicle_type": "NOT_APPLICABLE",
                "action": "driving_school_registration",
                "condition": "school_category",
                "amount": "CALCULATOR_DERIVED",
                "source": "src-bsp-fee-calculator",
                "verification": "PENDING_INTERACTIVE_EXTRACT",
            },
        ),
        claim(
            "c-facility-inspection-likely",
            sid,
            "procedure_step",
            "Driving school registration likely requires facility and instructor inspection by BRTA.",
            "DISCOVERY",
            ["src-bsp-road-safety", "src-brta-portal-home"],
            verification_scope="LOCATION_SPECIFIC",
        ),
        claim(
            "c-practical-bsp-hours",
            sid,
            "practical_tip",
            "Access roadSafety registration portal during BSP operating hours (08:00–22:00 BST).",
            "PRACTICAL",
            ["src-bsp-maintenance-notice"],
        ),
    ]

    # --- transport-driving-school-licence ---
    sid = "transport-driving-school-licence"
    claims += [
        claim(
            "c-bsp-service",
            sid,
            "application_url",
            "Driving school/training centre licence is a BSP licensing service per catalogue finalization_notes.",
            "OFFICIAL",
            ["src-bsp-home", "src-catalogue-transport"],
        ),
        claim(
            "c-crossref-brta-registration",
            sid,
            "restriction",
            "transport-driving-school-licence (BSP licence) distinct from brta-driving-school-registration (roadSafety registration) — related operator services.",
            "OFFICIAL",
            ["src-bsp-home", "src-bsp-road-safety", "src-catalogue-transport"],
        ),
        claim(
            "c-business-target",
            sid,
            "eligibility",
            "Licence service targets business operators running driving training centres.",
            "OFFICIAL",
            ["src-catalogue-transport"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-licence-vs-registration",
            sid,
            "restriction",
            "Licence issuance is authorization to operate; registration is initial enrolment — may be sequential requirements.",
            "DISCOVERY",
            ["src-bsp-home", "src-bsp-road-safety"],
        ),
        claim(
            "c-licence-fee-calculator",
            sid,
            "fee",
            "Driving school licence fees may be listed in BSP fee calculator under licensing categories.",
            "DISCOVERY",
            ["src-bsp-fee-calculator", "src-bsp-home"],
            structured={
                "service": sid,
                "vehicle_type": "NOT_APPLICABLE",
                "action": "driving_school_licence",
                "condition": "licence_type",
                "amount": "CALCULATOR_DERIVED",
                "source": "src-bsp-fee-calculator",
                "verification": "PENDING_INTERACTIVE_EXTRACT",
            },
        ),
        claim(
            "c-bsp-account-required",
            sid,
            "eligibility",
            "BSP business account required for licence application workflow.",
            "DISCOVERY",
            ["src-bsp-register", "src-bsp-home"],
            condition={"requirement_class": "CONDITIONAL", "if": "online_bsp_application"},
        ),
        claim(
            "c-not-applicable-vehicle-owner",
            sid,
            "restriction",
            "Driving school licence not applicable to individual vehicle owners — business/operator service only.",
            "OFFICIAL",
            ["src-catalogue-transport"],
            condition={"requirement_class": "NOT_APPLICABLE", "if": "applicant_is_individual_vehicle_owner"},
        ),
        claim(
            "c-practical-bsp-hours",
            sid,
            "practical_tip",
            "Apply for driving school licence via BSP during 08:00–22:00 BST operating window.",
            "PRACTICAL",
            ["src-bsp-maintenance-notice"],
        ),
    ]

    return claims


CONFLICTS = [
    {
        "conflict_id": "conflict-portal-cms-empty-vs-procedure",
        "service_ids": [
            "brta-fitness-certificate",
            "brta-tax-token",
            "brta-route-permit",
            "brta-advance-income-tax",
            "brta-color-change",
            "brta-engine-change",
            "brta-tire-size-change",
        ],
        "topic": "portal_content",
        "description": (
            "BRTA portal static pages for fitness, tax token, route permit, AIT, and modification services "
            "have JS-rendered procedural bodies; HTML shell snapshots may show empty CMS content vs expected procedures."
        ),
        "hypotheses": ["js_rendered_content", "catalogue_url_correct"],
        "status": "UNRESOLVED",
    },
    {
        "conflict_id": "conflict-calculator-vs-static-fees",
        "service_ids": [
            "brta-fee-calculator",
            "brta-fitness-certificate",
            "brta-tax-token",
            "brta-route-permit",
            "transport-route-permit",
        ],
        "topic": "fee_authority",
        "description": (
            "BSP fee calculator provides CALCULATOR_DERIVED amounts but portal static pages may list outdated "
            "fee tables; authority between calculator and portal static fees not reconciled in this pass."
        ),
        "hypotheses": ["calculator_authoritative", "portal_fees_stale"],
        "status": "UNRESOLVED",
    },
    {
        "conflict_id": "conflict-route-permit-dual-catalogue",
        "service_ids": ["brta-route-permit", "transport-route-permit"],
        "topic": "service_deduplication",
        "description": (
            "Two catalogue entries for route permit: brta-route-permit (portal static page) vs "
            "transport-route-permit (BSP operator service). Workflows may overlap or represent portal guide vs live BSP application."
        ),
        "hypotheses": ["portal_guide_bsp_application", "duplicate_discovery"],
        "status": "UNRESOLVED",
    },
    {
        "conflict_id": "conflict-driving-school-dual-catalogue",
        "service_ids": ["brta-driving-school-registration", "transport-driving-school-licence"],
        "topic": "service_deduplication",
        "description": (
            "Two catalogue entries: brta-driving-school-registration (roadSafety BSP) vs "
            "transport-driving-school-licence (BSP licensing). Registration vs licence may be sequential or overlapping."
        ),
        "hypotheses": ["registration_then_licence", "duplicate_discovery"],
        "status": "UNRESOLVED",
    },
    {
        "conflict_id": "conflict-mv-tax-vs-tax-token",
        "service_ids": ["brta-mv-tax-payment", "brta-tax-token"],
        "topic": "tax_workflow",
        "description": (
            "MV tax payment portal (brta.cnsbd.com/mvtax_brta) vs tax token issue/renewal (portal page) — "
            "relationship and sequencing between payment and token issuance not fully documented."
        ),
        "hypotheses": ["payment_then_token", "parallel_tax_channels"],
        "status": "UNRESOLVED",
    },
]

KNOWLEDGE_GAPS = [
    {
        "gap_id": "MISSING_FITNESS_VALIDITY_BY_CLASS",
        "service_ids": ["brta-fitness-certificate"],
        "classification": "insufficient_evidence",
        "priority": "HIGH",
        "description": (
            "Fitness certificate validity periods by vehicle class (private car, motorcycle, bus, truck, etc.) "
            "not verified from official sources. Do NOT invent durations such as '5 years for private car'."
        ),
    },
    {
        "gap_id": "MISSING_VEHICLE_FEE_MATRIX",
        "service_ids": [
            "brta-fee-calculator",
            "brta-fitness-certificate",
            "brta-tax-token",
            "brta-route-permit",
            "brta-advance-income-tax",
            "brta-color-change",
            "brta-engine-change",
            "brta-tire-size-change",
            "transport-route-permit",
        ],
        "classification": "missing_fee_schedule",
        "priority": "HIGH",
        "description": "BSP fee calculator referenced but per-vehicle-type numeric matrix not extracted without interactive session.",
    },
    {
        "gap_id": "MISSING_ROUTE_PERMIT_TYPE_MATRIX",
        "service_ids": ["brta-route-permit", "transport-route-permit"],
        "classification": "insufficient_evidence",
        "priority": "HIGH",
        "description": (
            "Route permit categories (inter-district, city, long-route, special permit types) and "
            "applicability by vehicle class not extracted from portal or BSP."
        ),
    },
    {
        "gap_id": "MISSING_PORTAL_JS_BODY",
        "service_ids": [
            "brta-fitness-certificate",
            "brta-tax-token",
            "brta-route-permit",
            "brta-advance-income-tax",
            "brta-color-change",
            "brta-engine-change",
            "brta-tire-size-change",
        ],
        "classification": "insufficient_evidence",
        "priority": "HIGH",
        "description": "BRTA portal static pages are JS-rendered; procedural checklists in page body not captured in HTML shell snapshots.",
    },
    {
        "gap_id": "MISSING_MVTAX_PORTAL_SNAPSHOT",
        "service_ids": ["brta-mv-tax-payment"],
        "classification": "source_discovery_problem",
        "priority": "MEDIUM",
        "description": "MV tax portal (brta.cnsbd.com/mvtax_brta) workflow and payment fields not snapshotted in this pass.",
    },
    {
        "gap_id": "MISSING_E_FITNESS_WORKFLOW_DETAIL",
        "service_ids": ["brta-fitness-certificate", "brta-e-document-verification"],
        "classification": "insufficient_evidence",
        "priority": "MEDIUM",
        "description": "E-Fitness on BSP noted in catalogue but step-by-step digital inspection workflow not captured.",
    },
    {
        "gap_id": "MISSING_DRIVING_SCHOOL_LICENCE_WORKFLOW",
        "service_ids": ["brta-driving-school-registration", "transport-driving-school-licence"],
        "classification": "insufficient_evidence",
        "priority": "MEDIUM",
        "description": "Registration vs licence sequencing and facility requirements not fully documented from BSP roadSafety portal.",
    },
]

SUBPROCESS_COVERAGE = [
    {"topic": "fitness_certificate_issue_renewal", "catalogue_services": ["brta-fitness-certificate"]},
    {"topic": "tax_token_issue_renewal", "catalogue_services": ["brta-tax-token"]},
    {"topic": "mv_tax_online_payment", "catalogue_services": ["brta-mv-tax-payment"]},
    {"topic": "advance_income_tax", "catalogue_services": ["brta-advance-income-tax"]},
    {"topic": "route_permit_portal", "catalogue_services": ["brta-route-permit"]},
    {"topic": "route_permit_bsp", "catalogue_services": ["transport-route-permit"]},
    {"topic": "vehicle_modification_color_engine_tire", "catalogue_services": [
        "brta-color-change", "brta-engine-change", "brta-tire-size-change",
    ]},
    {"topic": "driving_school_registration", "catalogue_services": ["brta-driving-school-registration"]},
    {"topic": "driving_school_licence", "catalogue_services": ["transport-driving-school-licence"]},
    {"topic": "bsp_cross_cutting_tools", "catalogue_services": [
        "brta-fee-calculator", "brta-payment-verification", "brta-e-document-verification", "brta-bsp-user-registration",
    ]},
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

    per_service: dict[str, list[dict]] = {}
    for c in claims:
        per_service.setdefault(c["service_id"], []).append(c)

    for sid in IN_SCOPE:
        if len(per_service.get(sid, [])) < 7:
            raise SystemExit(f"Service {sid} has fewer than 7 claims")

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
                "batch_id": "BATCH_03C",
                "slug": BATCH_ID,
                "name": "BRTA Fitness / Tax Token / Route Permit",
                "in_scope": IN_SCOPE,
                "out_of_scope_noted": OUT_OF_SCOPE_NOTED,
                "fitness_tax_variant_model": FITNESS_TAX_VARIANT_MODEL,
                "subprocess_coverage": SUBPROCESS_COVERAGE,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    substantial_threshold = 7
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
            "prior_batch_research": "batch-03a-brta-driving-licence (BSP registration, fee calculator); batch-03b-brta-vehicle (fitness/tax cross-refs)",
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
