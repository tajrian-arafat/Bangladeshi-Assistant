#!/usr/bin/env python3
"""Generate Batch 3B BRTA vehicle registration/ownership research raw artifacts (RESEARCH ONLY)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "research" / "raw" / "batch-03b-brta-vehicle"
CATALOGUE = ROOT / "data" / "service_catalogue" / "services.json"
TODAY = "2026-08-25"
BATCH_ID = "batch-03b-brta-vehicle"

IN_SCOPE = [
    "brta-digital-registration-certificate",
    "brta-new-vehicle-registration",
    "brta-ownership-transfer",
    "brta-retro-reflective-number-plate",
    "brta-trustee-board-certificate",
    "brta-vehicle-info-correction",
]

OUT_OF_SCOPE_NOTED = [
    {
        "service_id": "brta-fitness-certificate",
        "reason": "CONFIRMED catalogue service; assigned to BATCH_03C. Cross-referenced as prerequisite for registration/transfer, not researched as standalone service in 3B.",
    },
    {
        "service_id": "brta-fee-calculator",
        "reason": "Cross-cutting fee tool; referenced as authoritative fee lookup for vehicle-type-dependent amounts.",
    },
    {
        "service_id": "brta-bsp-user-registration",
        "reason": "BSP account prerequisite; covered as cross-cutting owner/dealer registration claim.",
    },
    {
        "service_id": "brta-mv-tax-payment",
        "reason": "MV tax payment; assigned to BATCH_03C. Referenced as registration/transfer prerequisite only.",
    },
    {
        "service_id": "brta-tax-token",
        "reason": "Tax token issue/renewal; assigned to BATCH_03C. Referenced as new-registration bundle component.",
    },
    {
        "service_id": "brta-route-permit",
        "reason": "Commercial route permit; BATCH_03C. Not flattened into private vehicle registration.",
    },
    {
        "service_id": "brta-engine-change",
        "reason": "Vehicle modification; BATCH_03C grouping (brta-other). Separate procedure from info correction.",
    },
    {
        "service_id": "brta-color-change",
        "reason": "Vehicle modification; BATCH_03C. Separate procedure from registration correction.",
    },
    {
        "subprocedure": "lost_or_damaged_registration_certificate",
        "reason": "No separate CONFIRMED catalogue service ID. Treated as replacement/DRC reissue sub-procedure under brta-digital-registration-certificate and brta-vehicle-info-correction workflows; GD/affidavit rules vary by case.",
    },
]

VEHICLE_VARIANT_MODEL = {
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
            "notes": "Fee and inspection rules vary by vehicle class on BSP fee calculator.",
        },
        {
            "id": "usage_class",
            "values": ["private", "commercial"],
            "notes": "Commercial vehicles may require fitness, route permit, and additional inspection (BATCH_03C).",
        },
        {
            "id": "origin",
            "values": ["local_assembled", "imported", "reconditioned"],
            "notes": "Imported vehicles may require customs/VAT/release documents before registration.",
        },
        {
            "id": "procedure_action",
            "values": [
                "new_registration",
                "ownership_transfer",
                "drc_biometric_issue",
                "registration_info_correction",
                "retro_reflective_plate",
                "trustee_board_certificate_download",
            ],
        },
        {
            "id": "certificate_state",
            "values": ["valid", "lost", "damaged", "outdated_booklet"],
            "notes": "Lost/damaged RC handled via replacement/DRC reissue — no standalone catalogue service.",
        },
    ],
    "do_not_flatten": [
        "private_car new registration vs commercial bus registration",
        "ownership transfer vs registration data correction",
        "DRC biometric collection vs retro-reflective plate upgrade",
        "fitness renewal (03C) vs new registration bundled fitness (03B prerequisite reference)",
    ],
}

SOURCES = [
    {
        "source_id": "src-bsp-vehicle-registration",
        "source_url": "https://bsp.brta.gov.bd/vehicleRegistration/?lan=en",
        "source_title": "BSP — New Motor Vehicle Registration",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Bangladesh Road Transport Authority (BRTA)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "en",
        "snapshot_path": None,
        "freshness_note": "Catalogue official_source; returned 404 outside BSP operating window during research fetch",
    },
    {
        "source_id": "src-bsp-register-owner",
        "source_url": "https://bsp.brta.gov.bd/register",
        "source_title": "BSP — User Registration (Driver/Owner/Dealer)",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Bangladesh Road Transport Authority (BRTA)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "en",
        "snapshot_path": None,
        "freshness_note": "Owner/dealer account prerequisite for vehicle registration BSP workflows",
    },
    {
        "source_id": "src-bsp-fee-calculator",
        "source_url": "https://bsp.brta.gov.bd/feeCalculator",
        "source_title": "BSP — Fee Calculator (registration, fitness, route permit)",
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
        "source_id": "src-bsp-tbc",
        "source_url": "https://bsp.brta.gov.bd/tbc/",
        "source_title": "BSP — Trustee Board Certificate Download",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Bangladesh Road Transport Authority (BRTA)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "bn",
        "snapshot_path": None,
        "freshness_note": "Catalogue official_source; 404 outside BSP hours during fetch",
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
        "freshness_note": "Cross-batch reference from Batch 3A: BSP available 08:00–22:00 BST",
    },
    {
        "source_id": "src-brta-portal-ownership-transfer",
        "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922dc6b933eb65569e10468",
        "source_title": "BRTA Portal — Motor Vehicle Ownership Transfer (মালিকানা বদলী)",
        "source_type": "official_website",
        "authority_tier": 2,
        "responsible_body": "Bangladesh Road Transport Authority (BRTA)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "bn",
        "snapshot_path": "source_snapshots/brta_ownership_transfer.html",
        "freshness_note": "Page shell fetched 2026-08-25; main procedural body JS-rendered",
    },
    {
        "source_id": "src-brta-portal-drc",
        "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922dba6933eb65569e0b8fe",
        "source_title": "BRTA Portal — DRC Biometric Provision and Collection",
        "source_type": "official_website",
        "authority_tier": 2,
        "responsible_body": "Bangladesh Road Transport Authority (BRTA)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "bn",
        "snapshot_path": "source_snapshots/brta_drc_biometric.html",
        "freshness_note": "Catalogue notes biometrics required; page title confirms biometric provision/collection process",
    },
    {
        "source_id": "src-brta-portal-retro-plate",
        "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922db7a933eb65569e0a505",
        "source_title": "BRTA Portal — Retro-Reflective Number Plate and RFID Tag",
        "source_type": "official_website",
        "authority_tier": 2,
        "responsible_body": "Bangladesh Road Transport Authority (BRTA)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "bn",
        "snapshot_path": "source_snapshots/brta_retro_plate.html",
        "freshness_note": "Page title: retro-reflective number plate and RFID tag installation process; last updated Nov 2023 in page metadata",
    },
    {
        "source_id": "src-brta-portal-info-correction",
        "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922dc03933eb65569e0df09",
        "source_title": "BRTA Portal — Registration Certificate Information Correction",
        "source_type": "official_website",
        "authority_tier": 2,
        "responsible_body": "Bangladesh Road Transport Authority (BRTA)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "bn",
        "snapshot_path": "source_snapshots/brta_vehicle_info_correction.html",
        "freshness_note": "Page title confirms RC data correction/change approval process",
    },
    {
        "source_id": "src-brta-portal-fitness-crossref",
        "source_url": "http://brta.portal.gov.bd/pages/static-pages/6922db91933eb65569e0af12",
        "source_title": "BRTA Portal — Fitness Certificate Issue/Renewal (cross-reference only)",
        "source_type": "official_website",
        "authority_tier": 2,
        "responsible_body": "Bangladesh Road Transport Authority (BRTA)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "bn",
        "snapshot_path": "source_snapshots/brta_fitness_crossref.html",
        "freshness_note": "BATCH_03C service brta-fitness-certificate; referenced for registration prerequisites only",
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

    # --- brta-new-vehicle-registration ---
    sid = "brta-new-vehicle-registration"
    claims += [
        claim(
            "c-portal-url",
            sid,
            "application_url",
            "New motor vehicle registration applications are initiated via BSP at bsp.brta.gov.bd/vehicleRegistration (English UI ?lan=en).",
            "OFFICIAL",
            ["src-bsp-vehicle-registration", "src-catalogue-transport"],
        ),
        claim(
            "c-bsp-owner-registration-prerequisite",
            sid,
            "eligibility",
            "Applicant must register a BSP owner or dealer account (NID-linked mobile) at bsp.brta.gov.bd/register before vehicle registration services.",
            "OFFICIAL",
            ["src-bsp-register-owner", "src-bsp-vehicle-registration"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-bundle-includes-fitness-tax-drc",
            sid,
            "procedure_step",
            "New registration bundle includes vehicle inspection, fitness certificate, tax token, and DRC biometric steps per catalogue discovery notes.",
            "OFFICIAL",
            ["src-catalogue-transport", "src-brta-portal-drc"],
        ),
        claim(
            "c-vehicle-type-fee-variation",
            sid,
            "fee",
            "Registration fees depend on vehicle type and class; amounts are computed via BSP fee calculator — not a single flat registration fee.",
            "OFFICIAL",
            ["src-bsp-fee-calculator", "src-bsp-vehicle-registration"],
            structured={
                "service": sid,
                "vehicle_type": "VARIES",
                "action": "new_registration",
                "condition": "vehicle_class_selected_in_calculator",
                "amount": "CALCULATOR_DERIVED",
                "source": "src-bsp-fee-calculator",
                "verification": "PENDING_INTERACTIVE_EXTRACT",
            },
        ),
        claim(
            "c-imported-vehicle-documents",
            sid,
            "conditional_document",
            "Imported or customs-cleared vehicles require customs/VAT/release-related documents in addition to standard ownership proof before BRTA registration.",
            "OFFICIAL",
            ["src-catalogue-transport", "src-brta-portal-home"],
            condition={"requirement_class": "CONDITIONAL", "if": "vehicle_origin_imported_or_customs_cleared"},
        ),
        claim(
            "c-nid-identity-required",
            sid,
            "document",
            "Owner NID (or authorized representative identity proof) required for BSP registration identity verification.",
            "OFFICIAL",
            ["src-bsp-register-owner", "src-bsp-vehicle-registration"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-dealer-eligible",
            sid,
            "eligibility",
            "Vehicle dealers listed as target users in catalogue may initiate registration on behalf of buyers via BSP dealer account.",
            "OFFICIAL",
            ["src-catalogue-transport", "src-bsp-register-owner"],
            condition={"requirement_class": "CONDITIONAL", "if": "applicant_is_registered_dealer"},
        ),
        claim(
            "c-circle-office-inspection",
            sid,
            "procedure_step",
            "Physical vehicle inspection and circle office processing required as part of new registration workflow (not fully online-only).",
            "OFFICIAL",
            ["src-catalogue-transport", "src-brta-portal-home"],
            verification_scope="LOCATION_SPECIFIC",
        ),
        claim(
            "c-fitness-prerequisite-crossref",
            sid,
            "eligibility",
            "Valid fitness certificate is part of new registration bundle; standalone fitness renewal is brta-fitness-certificate (BATCH_03C).",
            "OFFICIAL",
            ["src-catalogue-transport", "src-brta-portal-fitness-crossref"],
            condition={"requirement_class": "MUST_NEED", "if": "vehicle_requires_fitness_by_class"},
        ),
        claim(
            "c-practical-bsp-hours",
            sid,
            "practical_tip",
            "Apply during BSP operating hours (08:00–22:00 BST); vehicleRegistration deep link may 404 outside window even when URL is correct.",
            "PRACTICAL",
            ["src-bsp-maintenance-notice"],
        ),
    ]

    # --- brta-ownership-transfer ---
    sid = "brta-ownership-transfer"
    claims += [
        claim(
            "c-portal-url",
            sid,
            "application_url",
            "Motor vehicle ownership transfer guidance is published on BRTA portal static page for মালিকানা বদল/হস্তান্তর.",
            "OFFICIAL",
            ["src-brta-portal-ownership-transfer", "src-catalogue-transport"],
        ),
        claim(
            "c-to-tto-forms-required",
            sid,
            "document",
            "Transfer of ownership requires prescribed TO/TTO forms (Transfer Order / Transfer Take Over) per catalogue notes.",
            "OFFICIAL",
            ["src-catalogue-transport", "src-brta-portal-ownership-transfer"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-original-rc-required",
            sid,
            "document",
            "Original registration certificate (RC/DRC) must be submitted for ownership transfer.",
            "OFFICIAL",
            ["src-catalogue-transport", "src-brta-portal-ownership-transfer"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-buyer-tin-required",
            sid,
            "document",
            "Buyer TIN certificate required for ownership transfer per catalogue discovery notes.",
            "OFFICIAL",
            ["src-catalogue-transport", "src-brta-portal-ownership-transfer"],
            condition={"requirement_class": "MUST_NEED", "if": "buyer_is_individual_or_entity_requiring_tin"},
        ),
        claim(
            "c-affidavits-required",
            sid,
            "document",
            "Seller and/or buyer affidavits required supporting ownership transfer application per catalogue notes.",
            "OFFICIAL",
            ["src-catalogue-transport", "src-brta-portal-ownership-transfer"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-seller-buyer-both-parties",
            sid,
            "eligibility",
            "Both seller (current registered owner) and buyer must participate in ownership transfer with identity and ownership proof.",
            "OFFICIAL",
            ["src-brta-portal-ownership-transfer", "src-catalogue-transport"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-transfer-fee-calculator",
            sid,
            "fee",
            "Ownership transfer fees differ from new registration fees; amounts are vehicle-type dependent via BSP fee calculator.",
            "OFFICIAL",
            ["src-bsp-fee-calculator", "src-brta-portal-ownership-transfer"],
            structured={
                "service": sid,
                "vehicle_type": "VARIES",
                "action": "ownership_transfer",
                "condition": "vehicle_class_and_transfer_type",
                "amount": "CALCULATOR_DERIVED",
                "source": "src-bsp-fee-calculator",
                "verification": "PENDING_INTERACTIVE_EXTRACT",
            },
        ),
        claim(
            "c-tax-fitness-current",
            sid,
            "conditional_document",
            "Current tax token and valid fitness (where applicable by vehicle class) may be required before transfer is processed.",
            "OFFICIAL",
            ["src-brta-portal-ownership-transfer", "src-brta-portal-fitness-crossref"],
            condition={"requirement_class": "CONDITIONAL", "if": "vehicle_class_requires_tax_and_fitness"},
        ),
        claim(
            "c-circle-office-submission",
            sid,
            "procedure_step",
            "Ownership transfer application submitted to relevant BRTA circle office with completed forms and supporting documents.",
            "OFFICIAL",
            ["src-brta-portal-ownership-transfer"],
            verification_scope="LOCATION_SPECIFIC",
        ),
        claim(
            "c-lost-rc-gd-conditional",
            sid,
            "conditional_document",
            "If original RC is lost, General Diary (GD) and replacement/DRC reissue steps may be required before transfer — not a separate catalogue service.",
            "OFFICIAL",
            ["src-brta-portal-ownership-transfer", "src-brta-portal-drc"],
            condition={"requirement_class": "CONDITIONAL", "if": "registration_certificate_lost"},
        ),
        claim(
            "c-practical-verify-fees-before-visit",
            sid,
            "practical_tip",
            "Use BSP fee calculator and payment verification before visiting circle office for ownership transfer to avoid rejected applications.",
            "PRACTICAL",
            ["src-bsp-fee-calculator"],
        ),
    ]

    # --- brta-digital-registration-certificate ---
    sid = "brta-digital-registration-certificate"
    claims += [
        claim(
            "c-portal-url",
            sid,
            "application_url",
            "Digital Registration Certificate (DRC) biometric provision and collection process documented on BRTA portal static page.",
            "OFFICIAL",
            ["src-brta-portal-drc", "src-catalogue-transport"],
        ),
        claim(
            "c-biometrics-required",
            sid,
            "procedure_step",
            "DRC issuance requires biometric capture: photograph, signature, and fingerprints per catalogue and portal page title.",
            "OFFICIAL",
            ["src-brta-portal-drc", "src-catalogue-transport"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-smart-card-format",
            sid,
            "restriction",
            "DRC is smart-card format digital registration certificate replacing legacy booklet RC for enrolled vehicles.",
            "OFFICIAL",
            ["src-brta-portal-drc", "src-catalogue-transport"],
        ),
        claim(
            "c-part-of-new-registration",
            sid,
            "procedure_step",
            "DRC biometrics collected as part of new vehicle registration workflow after inspection/fitness steps.",
            "OFFICIAL",
            ["src-catalogue-transport", "src-bsp-vehicle-registration", "src-brta-portal-drc"],
            condition={"requirement_class": "CONDITIONAL", "if": "procedure_action_new_registration"},
        ),
        claim(
            "c-after-ownership-transfer",
            sid,
            "procedure_step",
            "After ownership transfer, buyer may require DRC update/reissuance with new owner biometrics at circle office.",
            "OFFICIAL",
            ["src-brta-portal-drc", "src-brta-portal-ownership-transfer"],
            condition={"requirement_class": "CONDITIONAL", "if": "procedure_action_ownership_transfer"},
        ),
        claim(
            "c-drc-fee-calculator",
            sid,
            "fee",
            "DRC-related fees listed under DNP/DRC fee section on BRTA portal menu; numeric amounts via BSP fee calculator.",
            "OFFICIAL",
            ["src-bsp-fee-calculator", "src-brta-portal-drc"],
            structured={
                "service": sid,
                "vehicle_type": "VARIES",
                "action": "drc_biometric_issue",
                "condition": "first_issue_vs_reissue",
                "amount": "CALCULATOR_DERIVED",
                "source": "src-bsp-fee-calculator",
                "verification": "PENDING_INTERACTIVE_EXTRACT",
            },
        ),
        claim(
            "c-collection-at-circle",
            sid,
            "procedure_step",
            "DRC smart card collected at BRTA circle office after biometric enrollment and fee payment.",
            "OFFICIAL",
            ["src-brta-portal-drc"],
            verification_scope="LOCATION_SPECIFIC",
        ),
        claim(
            "c-lost-damaged-replacement",
            sid,
            "eligibility",
            "Lost or damaged DRC replacement handled via DRC reissue/replacement procedure (GD may be required if lost) — no separate catalogue service ID.",
            "OFFICIAL",
            ["src-brta-portal-drc", "src-catalogue-transport"],
            condition={"requirement_class": "CONDITIONAL", "if": "certificate_state_lost_or_damaged"},
        ),
        claim(
            "c-practical-bring-original-if-available",
            sid,
            "practical_tip",
            "Bring damaged RC booklet/card to circle office when applying for DRC replacement to speed record matching.",
            "PRACTICAL",
            ["src-brta-portal-drc"],
        ),
    ]

    # --- brta-vehicle-info-correction ---
    sid = "brta-vehicle-info-correction"
    claims += [
        claim(
            "c-portal-url",
            sid,
            "application_url",
            "Registration certificate information correction/change approval process published on BRTA portal static page.",
            "OFFICIAL",
            ["src-brta-portal-info-correction", "src-catalogue-transport"],
        ),
        claim(
            "c-not-ownership-transfer",
            sid,
            "restriction",
            "Registration data correction is distinct from ownership transfer (brta-ownership-transfer); owner identity unchanged.",
            "OFFICIAL",
            ["src-brta-portal-info-correction", "src-brta-portal-ownership-transfer"],
            condition={"requirement_class": "NOT_APPLICABLE", "if": "change_of_registered_owner"},
        ),
        claim(
            "c-original-rc-required",
            sid,
            "document",
            "Original registration certificate required for information correction application.",
            "OFFICIAL",
            ["src-brta-portal-info-correction"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-supporting-proof-required",
            sid,
            "conditional_document",
            "Supporting documents proving correct information (e.g., factory invoice, customs papers, court order) required depending on field being corrected.",
            "OFFICIAL",
            ["src-brta-portal-info-correction"],
            condition={"requirement_class": "CONDITIONAL", "if": "field_being_corrected"},
        ),
        claim(
            "c-circle-office-application",
            sid,
            "procedure_step",
            "Information correction applications submitted to relevant BRTA circle office with prescribed forms.",
            "OFFICIAL",
            ["src-brta-portal-info-correction"],
            verification_scope="LOCATION_SPECIFIC",
        ),
        claim(
            "c-correction-fee-calculator",
            sid,
            "fee",
            "Registration information correction fees are vehicle-type dependent via BSP fee calculator.",
            "OFFICIAL",
            ["src-bsp-fee-calculator", "src-brta-portal-info-correction"],
            structured={
                "service": sid,
                "vehicle_type": "VARIES",
                "action": "registration_info_correction",
                "condition": "correction_type",
                "amount": "CALCULATOR_DERIVED",
                "source": "src-bsp-fee-calculator",
                "verification": "PENDING_INTERACTIVE_EXTRACT",
            },
        ),
        claim(
            "c-fields-not-fully-enumerated",
            sid,
            "document",
            "Full list of correctable RC fields not machine-read from portal page in this research pass (JS-rendered content).",
            "DISCOVERY",
            ["src-brta-portal-info-correction"],
        ),
        claim(
            "c-practical-separate-from-modifications",
            sid,
            "practical_tip",
            "Engine/color/tyre changes are separate BRTA modification services (BATCH_03C), not generic info correction.",
            "PRACTICAL",
            ["src-brta-portal-info-correction", "src-catalogue-transport"],
        ),
    ]

    # --- brta-retro-reflective-number-plate ---
    sid = "brta-retro-reflective-number-plate"
    claims += [
        claim(
            "c-portal-url",
            sid,
            "application_url",
            "Retro-reflective number plate and RFID tag installation process published on BRTA portal static page.",
            "OFFICIAL",
            ["src-brta-portal-retro-plate", "src-catalogue-transport"],
        ),
        claim(
            "c-rfid-tag-component",
            sid,
            "procedure_step",
            "Process covers both retro-reflective number plate and RFID tag installation per official page title.",
            "OFFICIAL",
            ["src-brta-portal-retro-plate"],
        ),
        claim(
            "c-registered-vehicle-required",
            sid,
            "eligibility",
            "Vehicle must already be registered with BRTA before retro-reflective plate upgrade.",
            "OFFICIAL",
            ["src-brta-portal-retro-plate", "src-catalogue-transport"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-plate-fee-not-static",
            sid,
            "fee",
            "Number plate upgrade fees not statically published on Tier 1–2 pages reviewed; likely via fee calculator or circle office schedule.",
            "DISCOVERY",
            ["src-bsp-fee-calculator", "src-brta-portal-retro-plate"],
            structured={
                "service": sid,
                "vehicle_type": "VARIES",
                "action": "retro_reflective_plate",
                "condition": "plate_type",
                "amount": "UNKNOWN",
                "source": "src-bsp-fee-calculator",
                "verification": "PENDING",
            },
        ),
        claim(
            "c-circle-office-or-approved-vendor",
            sid,
            "procedure_step",
            "Plate installation typically completed at BRTA circle office or authorized plate vendor per national retrofit program.",
            "OFFICIAL",
            ["src-brta-portal-retro-plate"],
            verification_scope="LOCATION_SPECIFIC",
        ),
        claim(
            "c-private-vs-commercial-plate-rules",
            sid,
            "restriction",
            "Plate format and color rules differ between private and commercial vehicles; do not generalize private-car plate rules to all classes.",
            "OFFICIAL",
            ["src-brta-portal-retro-plate", "src-catalogue-transport"],
        ),
        claim(
            "c-page-last-updated-2023",
            sid,
            "official_metadata",
            "Portal page metadata indicates content last updated November 2023 — verify against current circulars for mandate deadlines.",
            "DISCOVERY",
            ["src-brta-portal-retro-plate"],
        ),
        claim(
            "c-practical-check-rfid-after-install",
            sid,
            "practical_tip",
            "Confirm RFID tag registration appears on BSP/e-document verification after plate installation before leaving vendor.",
            "PRACTICAL",
            ["src-brta-portal-retro-plate"],
        ),
    ]

    # --- brta-trustee-board-certificate ---
    sid = "brta-trustee-board-certificate"
    claims += [
        claim(
            "c-portal-url",
            sid,
            "application_url",
            "Trustee Board Certificate download available via BSP at bsp.brta.gov.bd/tbc/ per catalogue official_source.",
            "OFFICIAL",
            ["src-bsp-tbc", "src-catalogue-transport"],
        ),
        claim(
            "c-grant-certificate-purpose",
            sid,
            "eligibility",
            "Certificate relates to Trustee Board grant/disbursement for registered vehicles under BRTA Trustee Board scheme.",
            "OFFICIAL",
            ["src-bsp-tbc", "src-brta-portal-home"],
        ),
        claim(
            "c-download-not-registration",
            sid,
            "restriction",
            "TBC download is certificate retrieval for trustee-board-eligible vehicles — not a substitute for vehicle registration or transfer.",
            "OFFICIAL",
            ["src-bsp-tbc", "src-catalogue-transport"],
        ),
        claim(
            "c-bsp-login-may-be-required",
            sid,
            "procedure_step",
            "Download may require BSP account login linked to vehicle/owner record (portal workflow not snapshotted in this pass).",
            "DISCOVERY",
            ["src-bsp-tbc", "src-bsp-register-owner"],
        ),
        claim(
            "c-eligibility-not-fully-captured",
            sid,
            "eligibility",
            "Trustee Board eligibility criteria and required vehicle grant status not extracted from Tier 1–2 pages in this pass.",
            "DISCOVERY",
            ["src-bsp-tbc"],
        ),
        claim(
            "c-fee-if-any-unknown",
            sid,
            "fee",
            "Certificate download fee (if any) not published on sources reviewed in this research pass.",
            "DISCOVERY",
            ["src-bsp-tbc", "src-bsp-fee-calculator"],
        ),
        claim(
            "c-practical-trustee-board-forms",
            sid,
            "practical_tip",
            "Trustee Board grant applications may require separate paper forms on BRTA portal forms section before certificate download.",
            "PRACTICAL",
            ["src-brta-portal-home"],
        ),
    ]

    return claims


CONFLICTS = [
    {
        "conflict_id": "conflict-fitness-batch-assignment",
        "service_ids": ["brta-new-vehicle-registration", "brta-ownership-transfer"],
        "topic": "cross_batch_prerequisite",
        "description": (
            "Fitness certificate is prerequisite for registration/transfer workflows but brta-fitness-certificate "
            "is assigned to BATCH_03C, not BATCH_03B. Cross-reference claims must not duplicate 03C research."
        ),
        "hypotheses": ["batch_split_by_subcategory", "intentional_prerequisite_reference"],
        "status": "UNRESOLVED",
    },
    {
        "conflict_id": "conflict-bsp-subportal-404-vs-catalogue-url",
        "service_ids": [
            "brta-new-vehicle-registration",
            "brta-trustee-board-certificate",
        ],
        "topic": "application_url",
        "description": (
            "Catalogue lists BSP deep links (vehicleRegistration, tbc) as official_source but live fetch returned 404 "
            "outside BSP operating hours; URLs treated as valid per catalogue with availability caveat."
        ),
        "hypotheses": ["operating_hours_gate", "catalogue_url_correct"],
        "status": "UNRESOLVED",
    },
    {
        "conflict_id": "conflict-retro-plate-page-age",
        "service_ids": ["brta-retro-reflective-number-plate"],
        "topic": "freshness",
        "description": (
            "Retro-reflective plate portal page metadata shows last update November 2023 while ownership transfer page "
            "shows June 2026 — potential policy/fee drift on plate mandate not cross-verified."
        ),
        "hypotheses": ["stale_page_metadata", "stable_policy"],
        "status": "UNRESOLVED",
    },
]

KNOWLEDGE_GAPS = [
    {
        "gap_id": "MISSING_BSP_VEHICLE_SUBPORTAL_SNAPSHOT",
        "service_ids": ["brta-new-vehicle-registration", "brta-trustee-board-certificate"],
        "classification": "source_discovery_problem",
        "priority": "HIGH",
        "description": "BSP vehicleRegistration and tbc URLs returned 404 outside operating window; Tier-1 workflow text not snapshotted.",
    },
    {
        "gap_id": "MISSING_PORTAL_JS_BODY",
        "service_ids": [
            "brta-ownership-transfer",
            "brta-digital-registration-certificate",
            "brta-vehicle-info-correction",
            "brta-retro-reflective-number-plate",
        ],
        "classification": "insufficient_evidence",
        "priority": "HIGH",
        "description": "BRTA portal static pages are JS-rendered; procedural checklists in page body not captured in HTML shell snapshots.",
    },
    {
        "gap_id": "MISSING_VEHICLE_FEE_MATRIX",
        "service_ids": [
            "brta-new-vehicle-registration",
            "brta-ownership-transfer",
            "brta-digital-registration-certificate",
            "brta-vehicle-info-correction",
        ],
        "classification": "missing_fee_schedule",
        "priority": "MEDIUM",
        "description": "Fee calculator referenced but per-vehicle-type numeric matrix not extracted without interactive BSP session.",
    },
    {
        "gap_id": "MISSING_FITNESS_VALIDITY_BY_CLASS",
        "service_ids": ["brta-new-vehicle-registration"],
        "classification": "cross_batch_dependency",
        "priority": "MEDIUM",
        "description": "Fitness validity periods and commercial-vs-private inspection rules belong to brta-fitness-certificate (BATCH_03C).",
    },
    {
        "gap_id": "MISSING_LOST_RC_PROCEDURE_DETAIL",
        "service_ids": ["brta-digital-registration-certificate", "brta-ownership-transfer"],
        "classification": "insufficient_evidence",
        "priority": "MEDIUM",
        "description": "No standalone lost/damaged RC catalogue service; replacement/GD procedure details not fully captured.",
    },
]

SUBPROCESS_COVERAGE = [
    {"topic": "new_vehicle_registration_bsp", "catalogue_services": ["brta-new-vehicle-registration"]},
    {"topic": "ownership_transfer_portal", "catalogue_services": ["brta-ownership-transfer"]},
    {"topic": "drc_biometric_smart_card", "catalogue_services": ["brta-digital-registration-certificate"]},
    {"topic": "registration_info_correction", "catalogue_services": ["brta-vehicle-info-correction"]},
    {"topic": "retro_reflective_plate_rfid", "catalogue_services": ["brta-retro-reflective-number-plate"]},
    {"topic": "trustee_board_certificate", "catalogue_services": ["brta-trustee-board-certificate"]},
    {"topic": "bsp_owner_registration_prerequisite", "catalogue_services": ["brta-new-vehicle-registration"]},
    {"topic": "fee_calculator_cross_cutting", "catalogue_services": IN_SCOPE[:4]},
    {"topic": "fitness_cross_reference_only", "catalogue_services": ["brta-new-vehicle-registration"], "batch": "BATCH_03C"},
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
                "batch_id": "BATCH_03B",
                "slug": BATCH_ID,
                "name": "BRTA Vehicle Registration / Ownership / Fitness",
                "in_scope": IN_SCOPE,
                "out_of_scope_noted": OUT_OF_SCOPE_NOTED,
                "vehicle_variant_model": VEHICLE_VARIANT_MODEL,
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
            "prior_batch_research": "batch-03a-brta-driving-licence (BSP registration, fee calculator, hours)",
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
