#!/usr/bin/env python3
"""Generate Batch 2B police + immigration research raw artifacts (RESEARCH ONLY)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "research" / "raw" / "batch-02b-police-immigration"
TODAY = "2026-08-24"

# Confirmed catalogue services — police, clearance, GD, verification, immigration (visa)
IN_SCOPE = [
    "police-clearance-certificate",
    "police-cyber-support-women",
    "police-employment-verification",
    "police-general-diary",
    "police-general-diary-online",
    "police-nid-address-verification",
    "police-passport-police-verification",
    "police-passport-verification",
    "migration-visa-application-dip",
    "police-expatriate-services",
    "police-firearms-license",
]

OUT_OF_SCOPE_NOTED = [
    {"service_id": "epassport-new-application", "reason": "Passport issuance; covered in batch-02a"},
    {"service_id": "epassport-reissue", "reason": "Passport reissue; covered in batch-02a"},
    {"service_id": "passport-mrp-initial", "reason": "MRP passport; covered in batch-02a"},
    {"service_id": "migration-e-apostille", "reason": "MOFA e-apostille; separate MOFA batch"},
    {"service_id": "mofa-document-attestation", "reason": "MOFA consular attestation; separate batch"},
    {"service_id": "bida-work-permit-security-clearance", "reason": "BIDA expatriate work-permit clearance; not Bangladesh Police citizen service"},
    {"service_id": "expatriate-emigration-clearance", "reason": "BMET emigration clearance; separate expatriate/labour batch"},
]

SOURCES = [
    {
        "source_id": "src-pcc-portal",
        "source_url": "https://pcc.police.gov.bd/ords/r/pcc/pcc/9",
        "source_title": "Bangladesh Police — Online Police Clearance Certificate Portal",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Bangladesh Police (Special Branch / PCC system)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "en",
        "snapshot_path": "source_snapshots/pcc_portal_home.html",
        "freshness_note": "Live portal captured 2026-08-24; fee/terms on portal home page",
    },
    {
        "source_id": "src-police-pcc-offline-page",
        "source_url": "https://www.police.gov.bd/en/police_clearance_certificate",
        "source_title": "Bangladesh Police — Police Clearance Certificate (offline procedure page)",
        "source_type": "official_website",
        "authority_tier": 2,
        "responsible_body": "Bangladesh Police",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "en",
        "snapshot_path": "source_snapshots/police_pcc_page.html",
        "freshness_note": "Describes legacy paper/chalan procedure; may predate online 1500 BDT fee",
    },
    {
        "source_id": "src-gd-portal",
        "source_url": "https://gd.police.gov.bd/",
        "source_title": "Bangladesh Police — Online GD Portal",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Bangladesh Police",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "bn",
        "snapshot_path": None,
        "freshness_note": "SSL fetch failed in research environment; portal URL confirmed in catalogue",
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
        "language": "bn",
        "snapshot_path": "source_snapshots/police_charter.html",
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
        "snapshot_path": "source_snapshots/police_sb.html",
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
        "snapshot_path": "source_snapshots/dip_home.html",
    },
    {
        "source_id": "src-dip-visa-online",
        "source_url": "https://dip.gov.bd/site/page/29bf208d-7729-4149-b17b-2a76efea59c9/",
        "source_title": "DIP — Apply Visa Online",
        "source_type": "official_website",
        "authority_tier": 1,
        "responsible_body": "Department of Immigration and Passports (DIP)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "en",
        "last_updated_on_page": "2026-08-03",
        "snapshot_path": "source_snapshots/dip_visa_online.html",
    },
    {
        "source_id": "src-visa-gov-bd",
        "source_url": "https://www.visa.gov.bd/",
        "source_title": "Bangladesh Online MRV Visa Application Portal",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Department of Immigration and Passports (DIP)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "en",
        "snapshot_path": None,
        "freshness_note": "Referenced from DIP Apply Visa Online page; direct snapshot fetch failed",
    },
    {
        "source_id": "src-dip-visa-types",
        "source_url": "https://dip.gov.bd/site/page/d34b2e25-44dc-4cc0-b9e1-89bd1a124bc1/Types-and-Essential-Documents-of-Visa/-",
        "source_title": "DIP — Types and Essential Documents of Visa",
        "source_type": "official_website",
        "authority_tier": 1,
        "responsible_body": "Department of Immigration and Passports (DIP)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "en",
        "last_updated_on_page": "2022-03-29",
        "snapshot_path": "source_snapshots/dip_visa_types.html",
        "freshness_note": "Page last updated March 2022; visa document matrix may be stale",
    },
    {
        "source_id": "src-dip-mrv-fees",
        "source_url": "https://dip.gov.bd/site/page/4b2827cf-d95a-48fb-b3c4-794fa0dfd933/-",
        "source_title": "DIP — Machine Readable Visa (MRV) Fees",
        "source_type": "official_website",
        "authority_tier": 1,
        "responsible_body": "Department of Immigration and Passports (DIP)",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "bn",
        "snapshot_path": "source_snapshots/dip_mrv_fees.html",
    },
    {
        "source_id": "src-bss-online-gd-rollout",
        "source_url": "https://www.bssnews.net/news/315020",
        "source_title": "BSS — Online GD services nationwide rollout (Sep 2025)",
        "source_type": "news_agency",
        "authority_tier": 5,
        "responsible_body": "Bangladesh Sangbad Sangstha / Police HQ statement",
        "published_date": "2025-09-24",
        "retrieved_at": TODAY,
        "language": "en",
        "notes": "DISCOVERY/PRACTICAL only; confirms policy expansion timing",
    },
    {
        "source_id": "src-tbs-online-gd-expansion",
        "source_url": "https://www.tbsnews.net/bangladesh/online-gd-service-be-launched-dhaka-mymensingh-tomorrow-1177476",
        "source_title": "The Business Standard — Online GD all-types expansion (Jul 2025)",
        "source_type": "news_media",
        "authority_tier": 5,
        "responsible_body": "Police Headquarters press release (via TBS)",
        "published_date": "2025-06-30",
        "retrieved_at": TODAY,
        "language": "en",
        "notes": "DISCOVERY only; prior lost-and-found-only limitation vs all GD types",
    },
    {
        "source_id": "src-unb-pcc-guide",
        "source_url": "https://unb.com.bd/category/Bangladesh/how-to-apply-online-for-police-clearance-certificate-in-bangladesh/113080",
        "source_title": "UNB — How to apply online for PCC (secondary guide)",
        "source_type": "news_media",
        "authority_tier": 5,
        "responsible_body": "United News of Bangladesh",
        "published_date": None,
        "retrieved_at": TODAY,
        "language": "en",
        "notes": "PRACTICAL cross-check only; cites older Tk 500 fee",
    },
    {
        "source_id": "src-batch-02a-passport-research",
        "source_url": "data/research/raw/batch-02a-passport/",
        "source_title": "Batch 2A passport research artifacts (cross-reference)",
        "source_type": "internal_research",
        "authority_tier": 2,
        "responsible_body": "BDA research pipeline",
        "published_date": "2026-08-24",
        "retrieved_at": TODAY,
        "language": "en",
        "notes": "Prior partial research for passport-pathway police verification",
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


def build_claims():
    claims = []

    # --- police-clearance-certificate ---
    sid = "police-clearance-certificate"
    claims += [
        claim(
            "c-online-portal-url",
            sid,
            "application_url",
            "Online Police Clearance Certificate applications are submitted at pcc.police.gov.bd (Oracle APEX portal).",
            "OFFICIAL",
            ["src-pcc-portal"],
        ),
        claim(
            "c-online-fee-1500",
            sid,
            "fee",
            "Online PCC application fee is BDT 1,500 payable via treasury challan code 1-7301-0001-2681 (Sonali Bank/Bangladesh Bank) or online card payment with service charges.",
            "OFFICIAL",
            ["src-pcc-portal"],
            structured={"amount": 1500, "currency": "BDT", "treasury_code": "1-7301-0001-2681"},
        ),
        claim(
            "c-online-passport-validity",
            sid,
            "eligibility",
            "Online PCC applicant must hold a passport valid for at least 3 months.",
            "OFFICIAL",
            ["src-pcc-portal"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-online-jurisdiction-address",
            sid,
            "eligibility",
            "Applicant present address must fall under same metropolitan/district police jurisdiction as permanent or emergency contact address on passport (foreign passport holders: present address = Bangladesh stay address).",
            "OFFICIAL",
            ["src-pcc-portal"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-online-no-address-nid-birth-ward",
            sid,
            "conditional_document",
            "If passport has no address, present address must be supported by NID, Birth ID, or ward councillor certificate attested by class-one gazetted officer.",
            "OFFICIAL",
            ["src-pcc-portal", "src-police-pcc-offline-page"],
            condition={"requirement_class": "CONDITIONAL", "if": "passport_lacks_address"},
        ),
        claim(
            "c-online-eligible-populations",
            sid,
            "eligibility",
            "Online system issues PCC to Bangladeshi nationals going/residing abroad and foreign nationals who departed Bangladesh after their stay.",
            "OFFICIAL",
            ["src-pcc-portal"],
        ),
        claim(
            "c-online-not-for-domestic-employment",
            sid,
            "restriction",
            "PCC for employment or other work within Bangladesh is not handled through online portal; applicant must contact district DSB or metropolitan City Special Branch per portal terms.",
            "OFFICIAL",
            ["src-pcc-portal"],
            condition={"requirement_class": "CONDITIONAL", "if": "purpose_domestic_employment"},
        ),
        claim(
            "c-online-abroad-attestation-bd-national",
            sid,
            "conditional_document",
            "Bangladeshi nationals applying from abroad must upload passport bio/address pages attested by Bangladesh High Commission of present country of residence.",
            "OFFICIAL",
            ["src-pcc-portal"],
            condition={"requirement_class": "CONDITIONAL", "if": "applicant_abroad", "applicant_type": "bangladeshi_national"},
        ),
        claim(
            "c-online-abroad-attestation-foreigner",
            sid,
            "conditional_document",
            "Foreign passport holders applying from abroad must upload passport pages attested by Justice of the Peace in country of present residence.",
            "OFFICIAL",
            ["src-pcc-portal"],
            condition={"requirement_class": "CONDITIONAL", "if": "applicant_abroad", "applicant_type": "foreign_passport"},
        ),
        claim(
            "c-online-expatriate-auth-letter",
            sid,
            "conditional_document",
            "Expatriate applicants must upload authorization letter naming collector and collector NID; local applicants must send same permission letter to collector at certificate acceptance.",
            "OFFICIAL",
            ["src-pcc-portal"],
            condition={"requirement_class": "CONDITIONAL", "if": "representative_collection"},
        ),
        claim(
            "c-online-arrival-stamp",
            sid,
            "conditional_document",
            "Bangladeshi citizens/expatriates who issued/reissued passport outside Bangladesh must upload latest arrival stamp page when seeking PCC after arriving in Bangladesh.",
            "OFFICIAL",
            ["src-pcc-portal"],
            condition={"requirement_class": "CONDITIONAL", "if": "passport_issued_abroad_and_applicant_in_bangladesh"},
        ),
        claim(
            "c-online-apply-steps",
            sid,
            "procedure_step",
            "Online PCC workflow: register → login → Apply → personal/address pages → upload documents → review/submit (no edit after final submit) → pay fee.",
            "OFFICIAL",
            ["src-pcc-portal"],
        ),
        claim(
            "c-online-status-sms",
            sid,
            "procedure_step",
            "Application status check: SMS 'PCC S' + application reference number to 26969.",
            "OFFICIAL",
            ["src-pcc-portal"],
        ),
        claim(
            "c-online-helpdesk",
            sid,
            "office",
            "PCC portal helpdesk Sun–Thu 9:00–16:00 (excl. public holidays): 01320001824, 01320001825; email ssaphq@gmail.com.",
            "OFFICIAL",
            ["src-pcc-portal"],
        ),
        claim(
            "c-charter-online-fee-sla",
            sid,
            "processing_time",
            "Citizen charter lists online police clearance fee BDT 1,500 to government and service time 3–7 days.",
            "OFFICIAL",
            ["src-police-charter"],
            structured={"official_sla_days_min": 3, "official_sla_days_max": 7, "fee_bdt": 1500},
        ),
        claim(
            "c-offline-sp-application",
            sid,
            "procedure_step",
            "Offline PCC: written application addressed to Superintendent of Police or Police Commissioner (metropolitan) on white paper.",
            "OFFICIAL",
            ["src-police-pcc-offline-page"],
        ),
        claim(
            "c-offline-fee-500-chalan",
            sid,
            "fee",
            "Offline PCC page cites treasury chalan Tk 500 to code 1-2201-0001-2681 (Bangladesh Bank/Sonali Bank).",
            "OFFICIAL",
            ["src-police-pcc-offline-page"],
            structured={"amount": 500, "currency": "BDT", "treasury_code": "1-2201-0001-2681", "channel": "offline_paper"},
        ),
        claim(
            "c-offline-passport-attested-copy",
            sid,
            "document",
            "Offline PCC requires passport photocopy attested by first-class gazetted officer; renewed pages must be included; expired passport not accepted.",
            "OFFICIAL",
            ["src-police-pcc-offline-page"],
        ),
        claim(
            "c-offline-relative-abroad",
            sid,
            "conditional_document",
            "Persons staying abroad may apply through relative with embassy/high commission attested passport copy.",
            "OFFICIAL",
            ["src-police-pcc-offline-page"],
            condition={"requirement_class": "CONDITIONAL", "if": "applicant_abroad"},
        ),
        claim(
            "c-destination-spain-extra",
            sid,
            "conditional_document",
            "PCC for Spain requires three passport-size photos submitted to Home Ministry immigration section-3 addressing the Secretary (per offline police page).",
            "OFFICIAL",
            ["src-police-pcc-offline-page"],
            condition={"requirement_class": "CONDITIONAL", "if": "destination_country", "value": "Spain"},
        ),
        claim(
            "c-dmp-token-collection",
            sid,
            "procedure_step",
            "DMP provides token with serial number and collection date for PCC pickup (metropolitan-specific).",
            "OFFICIAL",
            ["src-police-pcc-offline-page"],
            condition={"requirement_class": "LOCATION_SPECIFIC", "if": "jurisdiction", "value": "DMP"},
        ),
        claim(
            "c-certificate-language-attestation",
            sid,
            "procedure_step",
            "PCC issued in English; applications may be Bangla or English; certificates attested by officials concerned in foreign ministry.",
            "OFFICIAL",
            ["src-police-pcc-offline-page"],
        ),
        claim(
            "c-practical-fee-confusion",
            sid,
            "practical_tip",
            "Secondary media guides still reference Tk 500 PCC fee; treat as potentially stale vs current online portal 1500 BDT until independently verified.",
            "PRACTICAL",
            ["src-unb-pcc-guide"],
        ),
    ]

    # --- police-general-diary & police-general-diary-online (shared portal) ---
    for sid in ("police-general-diary", "police-general-diary-online"):
        claims += [
            claim(
                "c-gd-portal-url",
                sid,
                "application_url",
                "Online General Diary is filed via gd.police.gov.bd and/or Online GD mobile app (per catalogue and police communications).",
                "OFFICIAL",
                ["src-gd-portal", "src-police-charter"],
            ),
            claim(
                "c-charter-gd-fee-free",
                sid,
                "fee",
                "Citizen charter lists GD service fee as free (বিনামূল্যে).",
                "OFFICIAL",
                ["src-police-charter"],
                structured={"amount": 0, "currency": "BDT"},
            ),
            claim(
                "c-charter-gd-sla",
                sid,
                "processing_time",
                "Citizen charter official SLA for GD: 1–7 days.",
                "OFFICIAL",
                ["src-police-charter"],
                structured={"official_sla_days_min": 1, "official_sla_days_max": 7},
            ),
            claim(
                "c-charter-gd-channels",
                sid,
                "procedure_step",
                "Citizen charter states GD available directly at police station and online.",
                "OFFICIAL",
                ["src-police-charter"],
            ),
            claim(
                "c-charter-gd-office",
                sid,
                "office",
                "GD handled at relevant police station / unit (থানা).",
                "OFFICIAL",
                ["src-police-charter"],
            ),
        ]

    claims += [
        claim(
            "c-gd-online-registration-nid",
            "police-general-diary-online",
            "eligibility",
            "Online GD registration requires valid NID, active mobile number, and live photo during registration (per police rollout communications).",
            "DISCOVERY",
            ["src-bss-online-gd-rollout", "src-tbs-online-gd-expansion"],
            condition={"requirement_class": "MUST_NEED"},
        ),
        claim(
            "c-gd-online-hotline",
            "police-general-diary-online",
            "office",
            "Online GD support hotline 01320001428 operates 24/7 per Police HQ statements.",
            "DISCOVERY",
            ["src-bss-online-gd-rollout"],
        ),
        claim(
            "c-gd-all-types-expansion",
            "police-general-diary-online",
            "availability",
            "Police HQ announced expansion from lost-and-found-only online GD to all GD types, with nationwide availability claimed from Sep 2025.",
            "DISCOVERY",
            ["src-bss-online-gd-rollout", "src-tbs-online-gd-expansion"],
        ),
        claim(
            "c-gd-digital-copy-no-seal",
            "police-general-diary-online",
            "procedure_step",
            "Digital GD copy may be downloaded/printed; rollout reporting states seal/signature not required on online GD copy.",
            "DISCOVERY",
            ["src-tbs-online-gd-expansion"],
        ),
        claim(
            "c-gd-not-all-types-historically",
            "police-general-diary",
            "restriction",
            "Prior to 2025 expansion communications, online GD was limited to lost-and-found categories; do not assume all complaint types were always online.",
            "DISCOVERY",
            ["src-tbs-online-gd-expansion"],
        ),
        claim(
            "c-gd-cognizable-offence-thana",
            "police-general-diary-online",
            "procedure_step",
            "If online complaint concerns cognizable offence (case), applicant may need to attend thana with print copy or complaint code (per GD portal guidance cited in rollout reporting).",
            "DISCOVERY",
            ["src-bss-online-gd-rollout"],
            condition={"requirement_class": "CONDITIONAL", "if": "complaint_type_cognizable_offence"},
        ),
    ]

    # --- police-cyber-support-women ---
    sid = "police-cyber-support-women"
    claims += [
        claim(
            "c-pcsw-channels",
            sid,
            "availability",
            "Police Cyber Support for Women (PCSW) available online and offline per citizen charter.",
            "OFFICIAL",
            ["src-police-charter"],
        ),
        claim(
            "c-pcsw-free",
            sid,
            "fee",
            "PCSW service is free (বিনামূল্যে) per citizen charter.",
            "OFFICIAL",
            ["src-police-charter"],
            structured={"amount": 0, "currency": "BDT"},
        ),
        claim(
            "c-pcsw-sla-fastest",
            sid,
            "processing_time",
            "Citizen charter commits PCSW service at fastest possible time (দ্রুততম সময়ে সেবা প্রদান).",
            "OFFICIAL",
            ["src-police-charter"],
        ),
        claim(
            "c-pcsw-hotline",
            sid,
            "office",
            "PCSW hotline 01320-000888; email cybersupport.women@police.gov.bd; responsible AIG (LIC), Police HQ Dhaka.",
            "OFFICIAL",
            ["src-police-charter"],
        ),
        claim(
            "c-pcsw-facebook-page",
            sid,
            "application_url",
            "Citizen charter references PCSW Facebook page m.facebook.com/PCSw.PHQ/ as contact channel.",
            "OFFICIAL",
            ["src-police-charter"],
        ),
    ]

    # --- police-employment-verification ---
    sid = "police-employment-verification"
    claims += [
        claim(
            "c-ev-charter-pathway",
            sid,
            "procedure_step",
            "Employment verification processed on application at District Special Branch / Metropolitan Special Branch / SB.",
            "OFFICIAL",
            ["src-police-charter"],
            verification_scope="SERVICE_SPECIFIC",
        ),
        claim(
            "c-ev-charter-fee",
            sid,
            "fee",
            "Employment verification requires government-prescribed fee (সরকার কর্তৃক নির্ধারিত ফি) per citizen charter; amount not enumerated on charter page.",
            "OFFICIAL",
            ["src-police-charter"],
        ),
        claim(
            "c-ev-charter-sla",
            sid,
            "processing_time",
            "Citizen charter lists employment verification service time as 'timely' (যথাসময়ে) without numeric SLA.",
            "OFFICIAL",
            ["src-police-charter"],
        ),
        claim(
            "c-ev-responsible-officer",
            sid,
            "office",
            "Responsible officers: SP (DSB) / DC Metropolitan Police / Special Superintendent (City SB).",
            "OFFICIAL",
            ["src-police-charter"],
        ),
        claim(
            "c-ev-no-universal-rule",
            sid,
            "eligibility",
            "Employment verification requirements are employer/request-driven; no universal document list found on Tier 1–2 sources in this pass.",
            "DISCOVERY",
            ["src-police-charter"],
            verification_scope="UNKNOWN",
        ),
    ]

    # --- police-nid-address-verification ---
    sid = "police-nid-address-verification"
    claims += [
        claim(
            "c-nid-verify-when-no-passport-address",
            sid,
            "conditional_document",
            "When passport lacks address, NID/birth certificate/ward councillor certificate may establish present address for police verification/PCC (attested).",
            "OFFICIAL",
            ["src-police-pcc-offline-page", "src-pcc-portal"],
            condition={"requirement_class": "CONDITIONAL", "if": "passport_lacks_address"},
            verification_scope="CONDITIONAL",
        ),
        claim(
            "c-nid-address-match",
            sid,
            "eligibility",
            "Present address on NID/birth/ward councillor certificate must match applicant present address for verification purposes.",
            "OFFICIAL",
            ["src-police-pcc-offline-page"],
            condition={"requirement_class": "MUST_NEED", "if": "passport_lacks_address"},
        ),
        claim(
            "c-nid-not-standalone-service-url",
            sid,
            "application_url",
            "No dedicated standalone portal URL for address/NID verification; service routed through local police unit / PCC / verification request context.",
            "DISCOVERY",
            ["src-police-charter", "src-police-pcc-offline-page"],
            verification_scope="LOCATION_SPECIFIC",
        ),
    ]

    # --- police-passport-police-verification (extended; cross-ref batch-02a) ---
    sid = "police-passport-police-verification"
    claims += [
        claim(
            "c-pv-e-passport-pathway-sb",
            sid,
            "availability",
            "Passport police verification for e-Passport processing routes through Special Branch per DIP/police pathway.",
            "OFFICIAL",
            ["src-police-sb", "src-dip-home", "src-batch-02a-passport-research"],
            verification_scope="SERVICE_SPECIFIC",
        ),
        claim(
            "c-pv-onboarding-station-select",
            sid,
            "procedure_step",
            "e-Passport onboarding requires applicant to select nearest police station for verification routing (Batch 2A cross-reference).",
            "OFFICIAL",
            ["src-batch-02a-passport-research"],
            verification_scope="SERVICE_SPECIFIC",
        ),
        claim(
            "c-pv-not-universal-all-police-services",
            sid,
            "restriction",
            "Passport onboarding police-station selection rule applies to e-Passport pathway only; must not be generalized to employment PCC or GD services.",
            "OFFICIAL",
            ["src-pcc-portal", "src-batch-02a-passport-research"],
            verification_scope="SERVICE_SPECIFIC",
        ),
        claim(
            "c-pv-online-pcc-domestic-employment-elsewhere",
            sid,
            "procedure_step",
            "Domestic employment police clearance uses district DSB/metro CSB, not e-Passport onboarding station selection.",
            "OFFICIAL",
            ["src-pcc-portal"],
            condition={"requirement_class": "CONDITIONAL", "if": "purpose_domestic_employment"},
        ),
    ]

    # --- police-passport-verification ---
    sid = "police-passport-verification"
    claims += [
        claim(
            "c-pv-charter-sla-normal",
            sid,
            "processing_time",
            "Citizen charter official SLA: normal passport verification 15–21 days.",
            "OFFICIAL",
            ["src-police-charter"],
            structured={"official_sla_days_min": 15, "official_sla_days_max": 21, "tier": "normal"},
        ),
        claim(
            "c-pv-charter-sla-urgent",
            sid,
            "processing_time",
            "Citizen charter official SLA: urgent passport verification 7 days.",
            "OFFICIAL",
            ["src-police-charter"],
            structured={"official_sla_days": 7, "tier": "urgent"},
            condition={"requirement_class": "CONDITIONAL", "if": "urgent_request"},
        ),
        claim(
            "c-pv-charter-fee",
            sid,
            "fee",
            "Passport verification requires government-prescribed fee per citizen charter; amount not listed on charter page.",
            "OFFICIAL",
            ["src-police-charter"],
        ),
        claim(
            "c-pv-district-sb-office",
            sid,
            "office",
            "District-level passport verification handled by District Special Branch / Metropolitan Special Branch.",
            "OFFICIAL",
            ["src-police-charter"],
            verification_scope="LOCATION_SPECIFIC",
        ),
        claim(
            "c-pv-distinct-from-online-pcc",
            sid,
            "restriction",
            "Charter 'passport verification' is distinct from online PCC portal service; purposes and channels differ.",
            "OFFICIAL",
            ["src-police-charter", "src-pcc-portal"],
            verification_scope="SERVICE_SPECIFIC",
        ),
    ]

    # --- migration-visa-application-dip ---
    sid = "migration-visa-application-dip"
    claims += [
        claim(
            "c-visa-online-portal",
            sid,
            "application_url",
            "Bangladesh visa (MRV) online applications are submitted at visa.gov.bd per DIP Apply Visa Online page.",
            "OFFICIAL",
            ["src-dip-visa-online", "src-visa-gov-bd", "src-dip-home"],
        ),
        claim(
            "c-visa-dip-responsible",
            sid,
            "eligibility",
            "Department of Immigration and Passports (Ministry of Home Affairs) is responsible authority for Bangladesh visa issuance to foreigners.",
            "OFFICIAL",
            ["src-dip-home", "src-dip-visa-online"],
        ),
        claim(
            "c-visa-types-page",
            sid,
            "document",
            "DIP publishes visa types and essential documents matrix (Types and Essential Documents of Visa page).",
            "OFFICIAL",
            ["src-dip-visa-types"],
        ),
        claim(
            "c-visa-types-freshness-2022",
            sid,
            "restriction",
            "Visa types/documents page last updated March 2022; treat document requirements as requiring freshness verification before publication.",
            "OFFICIAL",
            ["src-dip-visa-types"],
        ),
        claim(
            "c-visa-mrv-fees-page",
            sid,
            "fee",
            "DIP publishes Machine Readable Visa (MRV) fee schedule on dedicated fee page; structured fee table not extracted in this research pass.",
            "DISCOVERY",
            ["src-dip-mrv-fees"],
        ),
        claim(
            "c-visa-foreign-embassy-not-in-scope",
            sid,
            "restriction",
            "Foreign embassy visa rules for Bangladesh citizens traveling abroad are out of scope; this service covers Bangladesh-government visa issuance only.",
            "OFFICIAL",
            ["src-dip-visa-online"],
        ),
        claim(
            "c-visa-dip-eservice-link",
            sid,
            "application_url",
            "DIP home page e-services section links 'Online MRV Application' to visa.gov.bd.",
            "OFFICIAL",
            ["src-dip-home"],
        ),
    ]

    # --- police-expatriate-services ---
    sid = "police-expatriate-services"
    claims += [
        claim(
            "c-expat-charter-services",
            sid,
            "availability",
            "Expatriate Cell services include passport verification, legal action on admitted offences, family security, and investment protection per citizen charter item 23.",
            "OFFICIAL",
            ["src-police-charter"],
        ),
        claim(
            "c-expat-charter-free",
            sid,
            "fee",
            "Expatriate services listed as free (বিনামূল্যে) in citizen charter.",
            "OFFICIAL",
            ["src-police-charter"],
            structured={"amount": 0, "currency": "BDT"},
        ),
        claim(
            "c-expat-charter-sla",
            sid,
            "processing_time",
            "Citizen charter commits expatriate services at fastest possible time (দ্রুততম সময়).",
            "OFFICIAL",
            ["src-police-charter"],
        ),
        claim(
            "c-expat-responsible-aig",
            sid,
            "office",
            "Expatriate Cell led by AIG (Expatriate Cell), Police HQ Dhaka; mobile 55101678 per charter.",
            "OFFICIAL",
            ["src-police-charter"],
        ),
        claim(
            "c-expat-pcc-auth-letter-link",
            sid,
            "conditional_document",
            "Online PCC rules require expatriate authorization letter for representative collection — related but distinct from Expatriate Cell charter entry.",
            "OFFICIAL",
            ["src-pcc-portal"],
            condition={"requirement_class": "CONDITIONAL", "if": "pcc_via_representative"},
        ),
    ]

    # --- police-firearms-license ---
    sid = "police-firearms-license"
    claims += [
        claim(
            "c-firearms-charter-pathway",
            sid,
            "procedure_step",
            "Firearms license applications processed on application at District Special Branch per citizen charter.",
            "OFFICIAL",
            ["src-police-charter"],
        ),
        claim(
            "c-firearms-charter-fee-na",
            sid,
            "fee",
            "Citizen charter lists firearms license service fee as not applicable (প্রযোজ্য নহে) on charter table.",
            "OFFICIAL",
            ["src-police-charter"],
        ),
        claim(
            "c-firearms-charter-sla",
            sid,
            "processing_time",
            "Citizen charter official SLA for firearms license: 21–30 days.",
            "OFFICIAL",
            ["src-police-charter"],
            structured={"official_sla_days_min": 21, "official_sla_days_max": 30},
        ),
        claim(
            "c-firearms-responsible-officer",
            sid,
            "office",
            "Responsible: SP (DSB) / metropolitan unit officer / Special Superintendent (City SB).",
            "OFFICIAL",
            ["src-police-charter"],
        ),
    ]

    return claims


CONFLICTS = [
    {
        "conflict_id": "conflict-pcc-fee-online-vs-offline",
        "service_ids": ["police-clearance-certificate"],
        "topic": "pcc_fee_amount",
        "claim_ids": [
            "police-clearance-certificate::c-online-fee-1500",
            "police-clearance-certificate::c-offline-fee-500-chalan",
        ],
        "description": "Online PCC portal requires BDT 1,500 (code 1-7301-0001-2681) while police.gov.bd offline instruction page still cites Tk 500 (code 1-2201-0001-2681).",
        "hypotheses": ["channel_specific_fee", "fee_revision_not_reflected_on_static_page", "offline_procedure_deprecated"],
        "status": "UNRESOLVED",
    },
    {
        "conflict_id": "conflict-pcc-treasury-code",
        "service_ids": ["police-clearance-certificate"],
        "topic": "treasury_challan_code",
        "description": "Online portal uses treasury code 1-7301-0001-2681; offline page uses 1-2201-0001-2681.",
        "status": "UNRESOLVED",
    },
    {
        "conflict_id": "conflict-gd-online-scope-timeline",
        "service_ids": ["police-general-diary", "police-general-diary-online"],
        "topic": "online_gd_complaint_types",
        "description": "2025 Police HQ communications claim all GD types online nationwide; older reporting and partial rollout referenced lost-and-found-only online GD.",
        "hypotheses": ["policy_expansion_2025", "regional_rollout_lag"],
        "status": "UNRESOLVED",
    },
    {
        "conflict_id": "conflict-passport-verification-vs-pcc",
        "service_ids": ["police-passport-verification", "police-clearance-certificate"],
        "topic": "verification_service_boundaries",
        "description": "Citizen charter 'passport verification' (15–21 days) differs from online PCC (3–7 days charter SLA); purposes and channels overlap in public language but are distinct services.",
        "status": "UNRESOLVED",
    },
    {
        "conflict_id": "conflict-pcc-portal-url-variants",
        "service_ids": ["police-clearance-certificate"],
        "topic": "application_url",
        "description": "Catalogue and portal use pcc.police.gov.bd/ords/r/pcc/pcc/9; police.gov.bd menu links alternate APEX paths (e.g. f?p=500:1).",
        "status": "UNRESOLVED",
    },
]

KNOWLEDGE_GAPS = [
    {
        "gap_id": "MISSING_GD_PORTAL_SNAPSHOT",
        "service_ids": ["police-general-diary", "police-general-diary-online"],
        "classification": "source_discovery_problem",
        "priority": "HIGH",
        "description": "gd.police.gov.bd SSL fetch failed; Tier-1 portal text not independently snapshotted in this pass.",
    },
    {
        "gap_id": "MISSING_VISA_GOV_BD_SNAPSHOT",
        "service_ids": ["migration-visa-application-dip"],
        "classification": "source_discovery_problem",
        "priority": "HIGH",
        "description": "visa.gov.bd application workflow, fees, and document upload rules not captured from live portal.",
    },
    {
        "gap_id": "MISSING_MRV_FEE_TABLE_EXTRACT",
        "service_ids": ["migration-visa-application-dip"],
        "classification": "missing_fee_schedule",
        "priority": "HIGH",
        "description": "DIP MRV fee page fetched but structured fee matrix not extracted (likely embedded PDF/image).",
    },
    {
        "gap_id": "MISSING_VISA_TYPES_MATRIX",
        "service_ids": ["migration-visa-application-dip"],
        "classification": "insufficient_evidence",
        "priority": "HIGH",
        "description": "Visa types/documents page last updated 2022; per-visa-type document list not machine-read in this pass.",
    },
    {
        "gap_id": "MISSING_EMPLOYMENT_VERIFICATION_FEE_AMOUNT",
        "service_ids": ["police-employment-verification"],
        "classification": "missing_fee_schedule",
        "priority": "MEDIUM",
        "description": "Charter cites government fee but no numeric amount on Tier 1–2 pages reviewed.",
    },
    {
        "gap_id": "MISSING_PASSPORT_VERIFICATION_FEE_AMOUNT",
        "service_ids": ["police-passport-verification"],
        "classification": "missing_fee_schedule",
        "priority": "MEDIUM",
        "description": "Charter cites government fee but no numeric amount on Tier 1–2 pages reviewed.",
    },
    {
        "gap_id": "MISSING_PCC_COLLECTION_DELIVERY_OFFICIAL",
        "service_ids": ["police-clearance-certificate"],
        "classification": "insufficient_evidence",
        "priority": "MEDIUM",
        "description": "Courier/mail delivery options referenced in third-party guides; not confirmed on Tier 1 portal pages captured.",
    },
    {
        "gap_id": "MISSING_FIREARMS_DOCUMENT_CHECKLIST",
        "service_ids": ["police-firearms-license"],
        "classification": "insufficient_evidence",
        "priority": "MEDIUM",
        "description": "No dedicated firearms license document checklist found on Tier 1–2 sources in this pass.",
    },
    {
        "gap_id": "MISSING_GD_DUPLICATE_CANONICAL_RESOLUTION",
        "service_ids": ["police-general-diary", "police-general-diary-online"],
        "classification": "service_identification_problem",
        "priority": "LOW",
        "description": "Two catalogue entries share gd.police.gov.bd; relationship (alias vs subprocess) not resolved in research phase.",
    },
    {
        "gap_id": "MISSING_PCC_REISSUE_CORRECTION_PROCESS",
        "service_ids": ["police-clearance-certificate"],
        "classification": "insufficient_evidence",
        "priority": "MEDIUM",
        "description": "Correction/reissue workflow for issued PCC not found on official pages reviewed.",
    },
]

SUBPROCESS_COVERAGE = [
    {"topic": "police_clearance_online", "catalogue_services": ["police-clearance-certificate"]},
    {"topic": "police_clearance_offline", "catalogue_services": ["police-clearance-certificate"]},
    {"topic": "general_diary_online", "catalogue_services": ["police-general-diary", "police-general-diary-online"]},
    {"topic": "general_diary_offline", "catalogue_services": ["police-general-diary"]},
    {"topic": "employment_verification", "catalogue_services": ["police-employment-verification"]},
    {"topic": "address_nid_verification", "catalogue_services": ["police-nid-address-verification"]},
    {"topic": "passport_pathway_police_verification", "catalogue_services": ["police-passport-police-verification"]},
    {"topic": "district_passport_verification", "catalogue_services": ["police-passport-verification"]},
    {"topic": "visa_application_mrv", "catalogue_services": ["migration-visa-application-dip"]},
    {"topic": "expatriate_police_support", "catalogue_services": ["police-expatriate-services"]},
    {"topic": "firearms_licensing", "catalogue_services": ["police-firearms-license"]},
    {"topic": "cyber_support_women", "catalogue_services": ["police-cyber-support-women"]},
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

    (OUT / "services_index.json").write_text(
        json.dumps({"batch_id": "batch-02b-police-immigration", "services": services_index}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (OUT / "sources.json").write_text(json.dumps({"sources": SOURCES}, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "claims.json").write_text(json.dumps({"claims": claims}, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "conflicts.json").write_text(json.dumps({"conflicts": CONFLICTS}, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "knowledge_gaps.json").write_text(
        json.dumps({"knowledge_gaps": KNOWLEDGE_GAPS}, indent=2, ensure_ascii=False), encoding="utf-8"
    )
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

    claims_by_service: dict[str, list] = {}
    for c in claims:
        claims_by_service.setdefault(c["service_id"], []).append(c)

    substantial_threshold = 8
    for sid in IN_SCOPE:
        cat = svc_by_id[sid]
        n = len(claims_by_service.get(sid, []))
        payload = {
            "service_id": sid,
            "batch_id": "batch-02b-police-immigration",
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
            "research_status": "SUBSTANTIAL" if n >= substantial_threshold else "PARTIAL",
            "claims": claims_by_service.get(sid, []),
            "notes": cat.get("notes"),
            "prior_batch_research": (
                "batch-02a-passport partial claims exist for police-passport-* services"
                if sid.startswith("police-passport")
                else None
            ),
        }
        (OUT / "services" / f"{sid}.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    (OUT / "metadata.json").write_text(
        json.dumps(
            {
                "batch_id": "batch-02b-police-immigration",
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

    print(f"Wrote batch-02b artifacts to {OUT}")
    print(f"Services: {len(IN_SCOPE)}, Claims: {len(claims)}, Sources: {len(SOURCES)}")


if __name__ == "__main__":
    main()
