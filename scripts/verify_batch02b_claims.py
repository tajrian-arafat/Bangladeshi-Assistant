#!/usr/bin/env python3
"""Independent Batch 2B police + immigration claim verification (STAGING ONLY)."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RAW = REPO / "data/research/raw/batch-02b-police-immigration"
OUT = REPO / "data/research/verification/batch-02b-police-immigration"
DOCS = REPO / "docs/research/batch-02b-police-immigration-independent-verification.md"
SNAP = OUT / "source_snapshots"

VERIFIER = "cursor-cloud-agent"
VERIFIED_AT = datetime.now(timezone.utc).isoformat()

STATES = {
    "VERIFIED",
    "PARTIALLY_VERIFIED",
    "CONFLICTING",
    "OUTDATED",
    "UNVERIFIED",
    "REJECTED",
}

# --- Evidence bundles (live retrieval 2026-08-24 verification pass) ---
E_PCC_PORTAL = {
    "source_id": "src-pcc-portal",
    "source_url": "https://pcc.police.gov.bd/ords/r/pcc/pcc/9",
    "authority_tier": 1,
    "retrieval_method": "live_html",
    "live_http_status": 200,
    "snapshot": "data/research/verification/batch-02b-police-immigration/source_snapshots/pcc_portal_live.html",
    "retrieved_at": "2026-08-24",
    "evidence_locator": "Terms and conditions / Required Documents / How to Apply sections",
}

E_PCC_OFFLINE = {
    "source_id": "src-police-pcc-offline-page",
    "source_url": "https://www.police.gov.bd/en/police_clearance_certificate",
    "authority_tier": 2,
    "retrieval_method": "live_html",
    "live_http_status": 200,
    "snapshot": "data/research/verification/batch-02b-police-immigration/source_snapshots/police_pcc_offline_live.html",
    "retrieved_at": "2026-08-24",
}

E_POLICE_CHARTER = {
    "source_id": "src-police-charter",
    "source_url": "https://www.police.gov.bd/index.php/en/citizen_charter",
    "authority_tier": 2,
    "retrieval_method": "live_html",
    "live_http_status": 200,
    "snapshot": "data/research/verification/batch-02b-police-immigration/source_snapshots/police_charter_live.html",
    "retrieved_at": "2026-08-24",
    "evidence_locator": "Citizen services table rows 3 (GD), 5 (passport verification), 6 (employment), 7 (clearance), 8 (firearms), 23 (expatriate)",
}

E_DIP_HOME = {
    "source_id": "src-dip-home",
    "source_url": "https://www.dip.gov.bd/",
    "authority_tier": 1,
    "retrieval_method": "live_html",
    "live_http_status": 200,
    "snapshot": "data/research/verification/batch-02b-police-immigration/source_snapshots/dip_home_live.html",
    "retrieved_at": "2026-08-24",
}

E_DIP_VISA_ONLINE = {
    "source_id": "src-dip-visa-online",
    "source_url": "https://dip.gov.bd/site/page/29bf208d-7729-4149-b17b-2a76efea59c9/",
    "authority_tier": 1,
    "retrieval_method": "live_html",
    "live_http_status": 200,
    "snapshot": "data/research/verification/batch-02b-police-immigration/source_snapshots/dip_visa_online_live.html",
    "source_last_updated_on_page": "2026-08-03",
    "retrieved_at": "2026-08-24",
}

E_VISA_GOV = {
    "source_id": "src-visa-gov-bd",
    "source_url": "https://www.visa.gov.bd/",
    "authority_tier": 1,
    "retrieval_method": "fetch_failed_ssl",
    "live_http_status": None,
    "evidence_limitation": "Direct fetch failed (SSL/connection); corroborated via live DIP Apply Visa Online page link only",
    "retrieved_at": "2026-08-24",
}

E_DIP_VISA_TYPES_PAGE = {
    "source_id": "src-dip-visa-types",
    "source_url": "https://dip.gov.bd/site/page/d34b2e25-44dc-4cc0-b9e1-89bd1a124bc1/Types-and-Essential-Documents-of-Visa/-",
    "authority_tier": 1,
    "retrieval_method": "live_html_plus_official_pdf",
    "source_last_updated_on_page": "2022-03-29",
    "pdf_attachment": "office-dip/2024/12/8dcb018c8e5e45e080476b142b06bb50.pdf",
    "pdf_snapshot": "data/research/verification/batch-02b-police-immigration/source_snapshots/dip_visa_types_dec2024.pdf",
    "retrieved_at": "2026-08-24",
}

E_DIP_MRV_FEES_PAGE = {
    "source_id": "src-dip-mrv-fees",
    "source_url": "https://dip.gov.bd/site/page/4b2827cf-d95a-48fb-b3c4-794fa0dfd933/-",
    "authority_tier": 1,
    "retrieval_method": "live_html_plus_scanned_pdf",
    "source_last_updated_on_page": "2016-03-03",
    "pdf_attachment": "office-dip/2024/12/6865f2a2b73c4ac6a747007d7cc62a07.pdf",
    "pdf_snapshot": "data/research/verification/batch-02b-police-immigration/source_snapshots/dip_mrv_fees_dec2024.pdf",
    "evidence_limitation": "Fee PDF is image/scanned; pypdf text extraction garbled — fee matrix not machine-verified",
    "retrieved_at": "2026-08-24",
}

E_GD_PORTAL = {
    "source_id": "src-gd-portal",
    "source_url": "https://gd.police.gov.bd/",
    "authority_tier": 1,
    "retrieval_method": "fetch_failed",
    "live_http_status": 502,
    "evidence_limitation": "HTTPS returned 502; http://gd.police.gov.bd/ also failed in verifier environment",
    "retrieved_at": "2026-08-24",
}

E_BSS_GD = {
    "source_id": "src-bss-online-gd-rollout",
    "source_url": "https://www.bssnews.net/news/315020",
    "authority_tier": 5,
    "retrieval_method": "secondary_news",
    "published_date": "2025-09-24",
    "retrieved_at": "2026-08-24",
}

E_TBS_GD = {
    "source_id": "src-tbs-online-gd-expansion",
    "source_url": "https://www.tbsnews.net/bangladesh/online-gd-service-be-launched-dhaka-mymensingh-tomorrow-1177476",
    "authority_tier": 5,
    "retrieval_method": "secondary_news",
    "published_date": "2025-06-30",
    "retrieved_at": "2026-08-24",
}

E_UNB_PCC = {
    "source_id": "src-unb-pcc-guide",
    "source_url": "https://unb.com.bd/category/Bangladesh/how-to-apply-online-for-police-clearance-certificate-in-bangladesh/113080",
    "authority_tier": 5,
    "retrieval_method": "secondary_media",
    "retrieved_at": "2026-08-24",
}

E_BATCH_02A = {
    "source_id": "src-batch-02a-passport-research",
    "source_url": "data/research/verification/batch-02a-passport/",
    "authority_tier": 2,
    "retrieval_method": "prior_verification_artifacts",
    "retrieved_at": "2026-08-24",
}


def V(**kwargs):
    status = kwargs["verification_status"]
    assert status in STATES
    return {
        "verifier": VERIFIER,
        "verified_at": VERIFIED_AT,
        "publication_status": "STAGING_ONLY",
        "do_not_publish_yet": True,
        **kwargs,
    }


def build_results() -> dict[str, dict]:
    R: dict[str, dict] = {}

    def put(cid: str, **kw):
        R[cid] = V(claim_id=cid, **kw)

    # ===================== police-clearance-certificate =====================
    put(
        "police-clearance-certificate::c-online-portal-url",
        service_id="police-clearance-certificate",
        priority=1,
        claim_type="application_url",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_PCC_PORTAL],
        evidence_excerpt="Live portal HTML: Oracle APEX app at pcc.police.gov.bd/ords/r/pcc/pcc/9 with Registration/Login/Apply.",
        reasoning="Tier-1 live portal confirms official online PCC application system at stated URL.",
        applicability="online_pcc_channel",
    )
    put(
        "police-clearance-certificate::c-online-fee-1500",
        service_id="police-clearance-certificate",
        priority=1,
        claim_type="fee",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_PCC_PORTAL, E_POLICE_CHARTER],
        evidence_excerpt=(
            "Portal Required Documents: 'fee of 1500/- taka ... code (1-7301-0001-2681)'. "
            "Charter row 7 online clearance: '১৫০০ টাকা'."
        ),
        reasoning=(
            "Online PCC fee BDT 1,500 and treasury code 1-7301-0001-2681 explicitly stated on live Tier-1 portal "
            "and corroborated by citizen charter online clearance row. Applicable to online channel only."
        ),
        applicability="online_pcc_channel",
        fee_metadata={"amount_bdt": 1500, "treasury_code": "1-7301-0001-2681", "channel": "online"},
    )
    put(
        "police-clearance-certificate::c-online-passport-validity",
        service_id="police-clearance-certificate",
        priority=1,
        claim_type="eligibility",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_PCC_PORTAL],
        evidence_excerpt="Terms item 1: 'passport valid for minimum 3 months'.",
        reasoning="Exact eligibility rule on live Tier-1 portal.",
        applicability="online_pcc_channel",
    )
    put(
        "police-clearance-certificate::c-online-jurisdiction-address",
        service_id="police-clearance-certificate",
        priority=1,
        claim_type="eligibility",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_PCC_PORTAL],
        evidence_excerpt="Terms item 2: present address under same district/metro jurisdiction as passport addresses; foreign passport stay address rule.",
        reasoning="Live portal terms match claim text.",
        applicability="online_pcc_channel",
    )
    put(
        "police-clearance-certificate::c-online-no-address-nid-birth-ward",
        service_id="police-clearance-certificate",
        priority=1,
        claim_type="conditional_document",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_PCC_PORTAL, E_PCC_OFFLINE],
        evidence_excerpt="Portal terms item 3; offline page item 6/footnote 5: NID/birth/ward councillor when passport lacks address.",
        reasoning="Conditional document rule confirmed on live Tier-1 portal and Tier-2 offline page.",
        applicability="online_pcc_channel",
        condition={"requirement_class": "CONDITIONAL", "if": "passport_lacks_address"},
    )
    put(
        "police-clearance-certificate::c-online-eligible-populations",
        service_id="police-clearance-certificate",
        priority=1,
        claim_type="eligibility",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_PCC_PORTAL],
        evidence_excerpt="Terms item 5: issued to Bangladeshi nationals going/residing abroad and foreign nationals returned abroad after stay.",
        reasoning="Population restriction explicitly on live portal.",
        applicability="online_pcc_channel",
    )
    put(
        "police-clearance-certificate::c-online-not-for-domestic-employment",
        service_id="police-clearance-certificate",
        priority=1,
        claim_type="restriction",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_PCC_PORTAL],
        evidence_excerpt="Terms item 8: employment/work within Bangladesh — contact district DSB or metro City SB, not online system.",
        reasoning="Domestic employment exception explicitly stated on Tier-1 portal.",
        applicability="online_pcc_channel",
        condition={"requirement_class": "CONDITIONAL", "if": "purpose_domestic_employment"},
    )
    put(
        "police-clearance-certificate::c-online-abroad-attestation-bd-national",
        service_id="police-clearance-certificate",
        priority=1,
        claim_type="conditional_document",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_PCC_PORTAL],
        evidence_excerpt="Terms item 4 and Required Documents: Bangladesh High Commission attestation when applied from abroad.",
        reasoning="Live portal attestation rule for Bangladeshi nationals abroad.",
        applicability="online_pcc_channel",
        condition={"requirement_class": "CONDITIONAL", "if": "applicant_abroad", "applicant_type": "bangladeshi_national"},
    )
    put(
        "police-clearance-certificate::c-online-abroad-attestation-foreigner",
        service_id="police-clearance-certificate",
        priority=1,
        claim_type="conditional_document",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_PCC_PORTAL],
        evidence_excerpt="Required Documents: foreign passport pages attested by Justice of Peace of country of present residence.",
        reasoning="Live portal attestation rule for foreign passport holders abroad.",
        applicability="online_pcc_channel",
        condition={"requirement_class": "CONDITIONAL", "if": "applicant_abroad", "applicant_type": "foreign_passport"},
    )
    put(
        "police-clearance-certificate::c-online-expatriate-auth-letter",
        service_id="police-clearance-certificate",
        priority=1,
        claim_type="conditional_document",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_PCC_PORTAL],
        evidence_excerpt="Terms item 7: Authorization Letter with collector name and NID; local applicants send permission letter at acceptance.",
        reasoning="Representative collection rule on live Tier-1 portal.",
        applicability="online_pcc_channel",
        condition={"requirement_class": "CONDITIONAL", "if": "representative_collection"},
    )
    put(
        "police-clearance-certificate::c-online-arrival-stamp",
        service_id="police-clearance-certificate",
        priority=1,
        claim_type="conditional_document",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_PCC_PORTAL],
        evidence_excerpt="Terms item 6: upload latest arrival stamp if passport issued/reissued outside Bangladesh when seeking PCC after arrival.",
        reasoning="Conditional arrival-stamp upload rule on live portal.",
        applicability="online_pcc_channel",
        condition={"requirement_class": "CONDITIONAL", "if": "passport_issued_abroad_and_applicant_in_bangladesh"},
    )
    put(
        "police-clearance-certificate::c-online-apply-steps",
        service_id="police-clearance-certificate",
        priority=2,
        claim_type="procedure_step",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_PCC_PORTAL],
        evidence_excerpt="How to Apply Steps 1–6: register, login/apply, personal+address pages, upload docs, review/submit, pay fee.",
        reasoning="Six-step workflow present on live portal.",
        applicability="online_pcc_channel",
    )
    put(
        "police-clearance-certificate::c-online-status-sms",
        service_id="police-clearance-certificate",
        priority=2,
        claim_type="procedure_step",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_PCC_PORTAL],
        evidence_excerpt="Tips: SMS 'PCC S' + application reference number to 26969 for status.",
        reasoning="Status-check SMS instruction on live portal.",
        applicability="online_pcc_channel",
    )
    put(
        "police-clearance-certificate::c-online-helpdesk",
        service_id="police-clearance-certificate",
        priority=2,
        claim_type="office",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_PCC_PORTAL],
        evidence_excerpt="Helpdesk Sun–Thu 9:00–16:00: 01320001824, 01320001825; ssaphq@gmail.com.",
        reasoning="Contact details on live portal home page.",
        applicability="online_pcc_channel",
    )
    put(
        "police-clearance-certificate::c-charter-online-fee-sla",
        service_id="police-clearance-certificate",
        priority=1,
        claim_type="processing_time",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_POLICE_CHARTER],
        evidence_excerpt="Charter row 7 (পুলিশ ক্লিয়ারেন্স): online, BDT 1500, service time ৩-৭ দিন.",
        reasoning=(
            "Official SLA 3–7 days and fee 1500 verified on live citizen charter for online police clearance service. "
            "Distinct from passport verification row 5 (15–21 / 7 days)."
        ),
        applicability="online_pcc_service_charter",
        fee_metadata={"official_sla_days_min": 3, "official_sla_days_max": 7, "fee_bdt": 1500},
    )
    put(
        "police-clearance-certificate::c-offline-sp-application",
        service_id="police-clearance-certificate",
        priority=2,
        claim_type="procedure_step",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_PCC_OFFLINE],
        evidence_excerpt="Offline page: application addressing Superintendent of Police or Police Commissioner on white paper.",
        reasoning="Paper/offline application procedure still published on live Tier-2 police page.",
        applicability="offline_paper_pcc_channel",
    )
    put(
        "police-clearance-certificate::c-offline-fee-500-chalan",
        service_id="police-clearance-certificate",
        priority=1,
        claim_type="fee",
        information_class="OFFICIAL",
        verification_status="CONFLICTING",
        evidence=[E_PCC_OFFLINE, E_PCC_PORTAL, E_POLICE_CHARTER],
        evidence_excerpt=(
            "Offline page item 3: treasury chalan Tk 500 code 1-2201-0001-2681. "
            "Live online portal: BDT 1500 code 1-7301-0001-2681. Charter lists online clearance at 1500 only."
        ),
        reasoning=(
            "Offline page still live with Tk 500 / code 1-2201-0001-2681 for paper/chalan procedure, but Tier-1 online "
            "portal and charter online row specify BDT 1500 / 1-7301-0001-2681. No official notice captured reconciling "
            "whether offline paper path remains valid at 500 or is superseded. Per policy: do not publish as authoritative "
            "current universal fee; retain conflict."
        ),
        applicability="offline_paper_pcc_channel",
        conflict_id="conflict-pcc-fee-online-vs-offline",
        conflict_classification="channel_specific_unreconciled",
        fee_metadata={"amount_bdt": 500, "treasury_code": "1-2201-0001-2681", "channel": "offline_paper_page"},
        do_not_promote_to_must=True,
    )
    put(
        "police-clearance-certificate::c-offline-passport-attested-copy",
        service_id="police-clearance-certificate",
        priority=1,
        claim_type="document",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_PCC_OFFLINE],
        evidence_excerpt="Offline page items 2/footnotes: attested passport copy; include renewal pages; expired passport not allowed.",
        reasoning="Document requirements on live Tier-2 offline instruction page.",
        applicability="offline_paper_pcc_channel",
    )
    put(
        "police-clearance-certificate::c-offline-relative-abroad",
        service_id="police-clearance-certificate",
        priority=2,
        claim_type="conditional_document",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_PCC_OFFLINE],
        evidence_excerpt="Offline page item 5: those abroad may apply through relative with embassy attested passport copy.",
        reasoning="Offline expatriate-via-relative rule on live Tier-2 page.",
        applicability="offline_paper_pcc_channel",
        condition={"requirement_class": "CONDITIONAL", "if": "applicant_abroad"},
    )
    put(
        "police-clearance-certificate::c-destination-spain-extra",
        service_id="police-clearance-certificate",
        priority=2,
        claim_type="conditional_document",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_PCC_OFFLINE],
        evidence_excerpt="Offline page item 7: PCC for Spain requires three passport photos to Home Ministry immigration section-3.",
        reasoning="Destination-specific Spain requirement on live Tier-2 page.",
        applicability="offline_paper_pcc_channel",
        condition={"requirement_class": "CONDITIONAL", "if": "destination_country", "value": "Spain"},
    )
    put(
        "police-clearance-certificate::c-dmp-token-collection",
        service_id="police-clearance-certificate",
        priority=2,
        claim_type="procedure_step",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_PCC_OFFLINE],
        evidence_excerpt="Offline page item 8: DMP provides token with serial number and collection date.",
        reasoning="Metropolitan (DMP) token procedure on live Tier-2 page.",
        applicability="location_specific_dmp",
        condition={"requirement_class": "LOCATION_SPECIFIC", "if": "jurisdiction", "value": "DMP"},
    )
    put(
        "police-clearance-certificate::c-certificate-language-attestation",
        service_id="police-clearance-certificate",
        priority=2,
        claim_type="procedure_step",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_PCC_OFFLINE],
        evidence_excerpt="Offline page: applications Bangla or English; certificates in English attested by foreign ministry officials.",
        reasoning="Language/attestation rule on live Tier-2 page.",
        applicability="offline_paper_pcc_channel",
    )
    put(
        "police-clearance-certificate::c-practical-fee-confusion",
        service_id="police-clearance-certificate",
        priority=3,
        claim_type="practical_tip",
        information_class="PRACTICAL",
        verification_status="VERIFIED",
        evidence=[E_UNB_PCC, E_PCC_PORTAL],
        evidence_excerpt="UNB guide cites Tk 500; live portal shows 1500 — secondary source stale relative to Tier-1 portal.",
        reasoning="PRACTICAL observation confirmed: community/secondary media may cite outdated fee; not authoritative.",
        applicability="practical_only",
        do_not_promote_to_must=True,
    )

    # ===================== GD services =====================
    gd_charter_claims = [
        ("c-gd-portal-url", "application_url", "Charter row 3 GD: 'সরাসরি ও অনলাইনে'; catalogue official gd.police.gov.bd."),
        ("c-charter-gd-fee-free", "fee", "Charter row 3: GD fee 'বিনামূল্যে'."),
        ("c-charter-gd-sla", "processing_time", "Charter row 3: GD service time '১-৭ দিন'."),
        ("c-charter-gd-channels", "procedure_step", "Charter row 3: 'সরাসরি ও অনলাইনে'."),
        ("c-charter-gd-office", "office", "Charter row 3: receiving unit 'থানা'."),
    ]
    for sid in ("police-general-diary", "police-general-diary-online"):
        for cid_suffix, ctype, excerpt in gd_charter_claims:
            cid = f"{sid}::{cid_suffix}"
            is_portal_url = cid_suffix == "c-gd-portal-url"
            put(
                cid,
                service_id=sid,
                priority=1 if is_portal_url or "sla" in cid_suffix or "fee" in cid_suffix else 2,
                claim_type=ctype,
                information_class="OFFICIAL",
                verification_status="PARTIALLY_VERIFIED" if is_portal_url else "VERIFIED",
                evidence=[E_POLICE_CHARTER] if not is_portal_url else [E_POLICE_CHARTER, E_GD_PORTAL],
                evidence_excerpt=excerpt,
                reasoning=(
                    "Charter facts live-verified from Tier-2 HTML."
                    if not is_portal_url
                    else "Charter confirms online GD channel exists; gd.police.gov.bd returned 502 in verifier — portal URL not independently reachable."
                ),
                applicability="gd_service_charter" if not is_portal_url else "online_gd_portal",
                knowledge_gap="MISSING_GD_PORTAL_SNAPSHOT" if is_portal_url else None,
            )

    put(
        "police-general-diary-online::c-gd-online-registration-nid",
        service_id="police-general-diary-online",
        priority=1,
        claim_type="eligibility",
        information_class="DISCOVERY",
        verification_status="UNVERIFIED",
        evidence=[E_BSS_GD, E_TBS_GD],
        evidence_excerpt="Tier-5 press reports cite NID, mobile, live photo for Online GD app registration.",
        reasoning="No Tier 1–2 official page or reachable gd.police.gov.bd snapshot confirms NID registration requirement.",
        applicability="online_gd_channel",
        do_not_promote_to_must=True,
    )
    put(
        "police-general-diary-online::c-gd-online-hotline",
        service_id="police-general-diary-online",
        priority=2,
        claim_type="office",
        information_class="DISCOVERY",
        verification_status="UNVERIFIED",
        evidence=[E_BSS_GD],
        evidence_excerpt="BSS Sep 2025 Police HQ statement cites hotline 01320001428.",
        reasoning="Hotline only in Tier-5 news citing PHQ; not verified on live charter or reachable portal.",
        applicability="online_gd_support",
    )
    put(
        "police-general-diary-online::c-gd-all-types-expansion",
        service_id="police-general-diary-online",
        priority=1,
        claim_type="availability",
        information_class="DISCOVERY",
        verification_status="UNVERIFIED",
        evidence=[E_BSS_GD, E_TBS_GD],
        evidence_excerpt="Tier-5: expansion from lost-and-found-only to all GD types; nationwide from Sep 2025.",
        reasoning=(
            "Current online GD complaint-type scope cannot be established from Tier 1–2 evidence. "
            "Charter confirms online channel exists but not 'all types nationwide' scope."
        ),
        applicability="online_gd_scope",
        conflict_id="conflict-gd-online-scope-timeline",
        knowledge_gap="MISSING_GD_PORTAL_SNAPSHOT",
    )
    put(
        "police-general-diary-online::c-gd-digital-copy-no-seal",
        service_id="police-general-diary-online",
        priority=2,
        claim_type="procedure_step",
        information_class="DISCOVERY",
        verification_status="UNVERIFIED",
        evidence=[E_TBS_GD],
        evidence_excerpt="Tier-5 regional press conference quote: digital GD copy without seal/signature.",
        reasoning="Not confirmed on Tier 1–2 official documentation.",
        applicability="online_gd_output_format",
    )
    put(
        "police-general-diary::c-gd-not-all-types-historically",
        service_id="police-general-diary",
        priority=3,
        claim_type="restriction",
        information_class="DISCOVERY",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_TBS_GD],
        evidence_excerpt="TBS Jun 2025: online GD previously limited to loss/recovery; expanding to all types.",
        reasoning="Historical limitation supported by Tier-5 PHQ-attributed press; not an official rule document — contextual only.",
        applicability="historical_context_not_current_official_rule",
        do_not_promote_to_must=True,
    )
    put(
        "police-general-diary-online::c-gd-cognizable-offence-thana",
        service_id="police-general-diary-online",
        priority=2,
        claim_type="procedure_step",
        information_class="DISCOVERY",
        verification_status="UNVERIFIED",
        evidence=[E_BSS_GD],
        evidence_excerpt="Tier-5 reporting: cognizable offence may require thana attendance with print/code.",
        reasoning="Conditional thana attendance rule not verified on Tier 1–2 sources.",
        applicability="online_gd_cognizable_offence",
        condition={"requirement_class": "CONDITIONAL", "if": "complaint_type_cognizable_offence"},
    )

    # ===================== PCSW =====================
    put(
        "police-cyber-support-women::c-pcsw-channels",
        service_id="police-cyber-support-women",
        priority=2,
        claim_type="availability",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_POLICE_CHARTER],
        evidence_excerpt="Charter row 1 PCSW: 'অনলাইন এবং অফ লাইন'.",
        reasoning="Service channels on live charter.",
        applicability="pcsw_service",
    )
    put(
        "police-cyber-support-women::c-pcsw-free",
        service_id="police-cyber-support-women",
        priority=1,
        claim_type="fee",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_POLICE_CHARTER],
        evidence_excerpt="Charter row 1: 'বিনামূল্যে'.",
        reasoning="Free service on live charter.",
        applicability="pcsw_service",
    )
    put(
        "police-cyber-support-women::c-pcsw-sla-fastest",
        service_id="police-cyber-support-women",
        priority=1,
        claim_type="processing_time",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_POLICE_CHARTER],
        evidence_excerpt="Charter row 1: 'দ্রুততম সময়ে সেবা প্রদান' (no numeric SLA).",
        reasoning="Official qualitative SLA verified; not a numeric day count.",
        applicability="pcsw_service",
    )
    put(
        "police-cyber-support-women::c-pcsw-hotline",
        service_id="police-cyber-support-women",
        priority=2,
        claim_type="office",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_POLICE_CHARTER],
        evidence_excerpt="Charter row 1: Hotline 01320-000888; email cybersupport.women@police.gov.bd.",
        reasoning="Contact details on live charter.",
        applicability="pcsw_service",
    )
    put(
        "police-cyber-support-women::c-pcsw-facebook-page",
        service_id="police-cyber-support-women",
        priority=2,
        claim_type="application_url",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_POLICE_CHARTER],
        evidence_excerpt="Charter row 1 references Facebook page m.facebook.com/PCSw.PHQ/.",
        reasoning="Official contact channel listed on charter (Facebook).",
        applicability="pcsw_service",
    )

    # ===================== employment verification =====================
    put(
        "police-employment-verification::c-ev-charter-pathway",
        service_id="police-employment-verification",
        priority=2,
        claim_type="procedure_step",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_POLICE_CHARTER],
        evidence_excerpt="Charter row 6: employment verification at District SB / Metro SB / SB on application.",
        reasoning="Service pathway on live charter.",
        applicability="employment_verification_service",
        verification_scope="SERVICE_SPECIFIC",
    )
    put(
        "police-employment-verification::c-ev-charter-fee",
        service_id="police-employment-verification",
        priority=1,
        claim_type="fee",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_POLICE_CHARTER],
        evidence_excerpt="Charter row 6: 'সরকার কর্তৃক নির্ধারিত ফি প্রদান সাপেক্ষে' — no amount.",
        reasoning="Fee requirement exists but numeric amount not on Tier 1–2 sources captured.",
        applicability="employment_verification_service",
        knowledge_gap="MISSING_EMPLOYMENT_VERIFICATION_FEE_AMOUNT",
    )
    put(
        "police-employment-verification::c-ev-charter-sla",
        service_id="police-employment-verification",
        priority=1,
        claim_type="processing_time",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_POLICE_CHARTER],
        evidence_excerpt="Charter row 6: 'যথাসময়ে' — no numeric days.",
        reasoning="Qualitative official SLA only; no numeric SLA to verify.",
        applicability="employment_verification_service",
    )
    put(
        "police-employment-verification::c-ev-responsible-officer",
        service_id="police-employment-verification",
        priority=2,
        claim_type="office",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_POLICE_CHARTER],
        evidence_excerpt="Charter row 6: SP (DSB) / DC Metro / Special Superintendent (City SB).",
        reasoning="Responsible officers on live charter.",
        applicability="employment_verification_service",
    )
    put(
        "police-employment-verification::c-ev-no-universal-rule",
        service_id="police-employment-verification",
        priority=2,
        claim_type="eligibility",
        information_class="DISCOVERY",
        verification_status="VERIFIED",
        evidence=[E_POLICE_CHARTER],
        evidence_excerpt="Charter describes application-driven service; no universal document checklist published.",
        reasoning="Absence of universal doc list confirmed — service is request-specific per charter framing.",
        applicability="employment_verification_service",
        verification_scope="SERVICE_SPECIFIC",
    )

    # ===================== NID address verification =====================
    put(
        "police-nid-address-verification::c-nid-verify-when-no-passport-address",
        service_id="police-nid-address-verification",
        priority=1,
        claim_type="conditional_document",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_PCC_PORTAL, E_PCC_OFFLINE],
        evidence_excerpt="PCC portal/offline pages: NID/birth/ward councillor when passport lacks address.",
        reasoning="Conditional verification document rule verified on Tier 1–2 PCC sources; not a standalone portal service.",
        applicability="conditional_when_passport_lacks_address",
        condition={"requirement_class": "CONDITIONAL", "if": "passport_lacks_address"},
        verification_scope="CONDITIONAL",
    )
    put(
        "police-nid-address-verification::c-nid-address-match",
        service_id="police-nid-address-verification",
        priority=1,
        claim_type="eligibility",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_PCC_OFFLINE],
        evidence_excerpt="Offline footnote 5: present address must match NID/birth/ward councillor certificate.",
        reasoning="Address match rule on live Tier-2 page.",
        applicability="conditional_when_passport_lacks_address",
        condition={"requirement_class": "MUST_NEED", "if": "passport_lacks_address"},
    )
    put(
        "police-nid-address-verification::c-nid-not-standalone-service-url",
        service_id="police-nid-address-verification",
        priority=2,
        claim_type="application_url",
        information_class="DISCOVERY",
        verification_status="VERIFIED",
        evidence=[E_POLICE_CHARTER, E_PCC_OFFLINE],
        evidence_excerpt="No dedicated URL; verification routed via local police unit / PCC / verification request context.",
        reasoning="Confirmed no standalone portal — catalogue points to PCC info page as discovery source only.",
        applicability="location_specific_local_unit",
        verification_scope="LOCATION_SPECIFIC",
    )

    # ===================== passport PV (batch 2B extensions) =====================
    put(
        "police-passport-police-verification::c-pv-e-passport-pathway-sb",
        service_id="police-passport-police-verification",
        priority=2,
        claim_type="availability",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_POLICE_CHARTER, E_BATCH_02A],
        evidence_excerpt="Charter row 5 passport verification at SB; batch-02a cites DIP/SB pathway.",
        reasoning="SB involvement for passport verification verified via charter; e-Passport-specific SB procedure page not captured.",
        applicability="passport_verification_service",
        verification_scope="SERVICE_SPECIFIC",
    )
    put(
        "police-passport-police-verification::c-pv-onboarding-station-select",
        service_id="police-passport-police-verification",
        priority=2,
        claim_type="procedure_step",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_BATCH_02A],
        evidence_excerpt="Batch-02a verification: onboarding police-station selection PARTIALLY_VERIFIED via index/SPA limitation.",
        reasoning="e-Passport onboarding station rule not independently live-verified in batch-2B pass; inherited partial status from batch-02a.",
        applicability="e_passport_onboarding_pathway_only",
        verification_scope="SERVICE_SPECIFIC",
    )
    put(
        "police-passport-police-verification::c-pv-not-universal-all-police-services",
        service_id="police-passport-police-verification",
        priority=1,
        claim_type="restriction",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_PCC_PORTAL, E_POLICE_CHARTER],
        evidence_excerpt="Distinct charter rows for passport verification vs clearance vs employment; portal separates online PCC from domestic employment.",
        reasoning="Service boundary claim verified — rules must not be generalized across police services.",
        applicability="cross_service_boundary_rule",
    )
    put(
        "police-passport-police-verification::c-pv-online-pcc-domestic-employment-elsewhere",
        service_id="police-passport-police-verification",
        priority=1,
        claim_type="procedure_step",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_PCC_PORTAL],
        evidence_excerpt="Portal terms item 8: domestic employment PCC via DSB/CSB not online portal.",
        reasoning="Routing exception verified on Tier-1 portal.",
        applicability="domestic_employment_pcc",
        condition={"requirement_class": "CONDITIONAL", "if": "purpose_domestic_employment"},
    )

    # ===================== district passport verification (charter) =====================
    put(
        "police-passport-verification::c-pv-charter-sla-normal",
        service_id="police-passport-verification",
        priority=1,
        claim_type="processing_time",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_POLICE_CHARTER],
        evidence_excerpt="Charter row 5 (পার্সপোর্ট ভেরিফিকেশন): normal 'নরমাল-১৫-২১ দিন'.",
        reasoning="Official numeric SLA for passport verification (normal tier) — separate from PCC 3–7 days.",
        applicability="passport_verification_service_charter",
        fee_metadata={"official_sla_days_min": 15, "official_sla_days_max": 21, "tier": "normal"},
    )
    put(
        "police-passport-verification::c-pv-charter-sla-urgent",
        service_id="police-passport-verification",
        priority=1,
        claim_type="processing_time",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_POLICE_CHARTER],
        evidence_excerpt="Charter row 5: urgent 'জরুরী-৭ দিন'.",
        reasoning="Official urgent SLA for passport verification service — not PCC.",
        applicability="passport_verification_service_charter",
        condition={"requirement_class": "CONDITIONAL", "if": "urgent_request"},
        fee_metadata={"official_sla_days": 7, "tier": "urgent"},
    )
    put(
        "police-passport-verification::c-pv-charter-fee",
        service_id="police-passport-verification",
        priority=1,
        claim_type="fee",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_POLICE_CHARTER],
        evidence_excerpt="Charter row 5: government-prescribed fee required; amount not stated.",
        reasoning="Fee requirement verified; numeric amount missing from Tier 1–2 sources.",
        applicability="passport_verification_service_charter",
        knowledge_gap="MISSING_PASSPORT_VERIFICATION_FEE_AMOUNT",
    )
    put(
        "police-passport-verification::c-pv-district-sb-office",
        service_id="police-passport-verification",
        priority=2,
        claim_type="office",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_POLICE_CHARTER],
        evidence_excerpt="Charter row 5 units: District SB / Metro SB / SB.",
        reasoning="Office routing on live charter.",
        applicability="passport_verification_service_charter",
        verification_scope="LOCATION_SPECIFIC",
    )
    put(
        "police-passport-verification::c-pv-distinct-from-online-pcc",
        service_id="police-passport-verification",
        priority=1,
        claim_type="restriction",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_POLICE_CHARTER, E_PCC_PORTAL],
        evidence_excerpt="Charter rows 5 vs 7: passport verification 15–21/7 days vs online clearance 3–7 days/1500 online.",
        reasoning="Distinct services with different SLAs verified — not merged.",
        applicability="service_boundary",
        conflict_id="conflict-passport-verification-vs-pcc",
    )

    # ===================== visa / immigration =====================
    put(
        "migration-visa-application-dip::c-visa-online-portal",
        service_id="migration-visa-application-dip",
        priority=1,
        claim_type="application_url",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_DIP_VISA_ONLINE, E_VISA_GOV],
        evidence_excerpt="Live DIP Apply Visa Online page links to https://visa.gov.bd/; direct visa.gov.bd fetch failed.",
        reasoning="Official portal URL corroborated via Tier-1 DIP page; portal itself not reachable for workflow verification.",
        applicability="bangladesh_mrv_visa_issuance",
        knowledge_gap="MISSING_VISA_GOV_BD_SNAPSHOT",
    )
    put(
        "migration-visa-application-dip::c-visa-dip-responsible",
        service_id="migration-visa-application-dip",
        priority=1,
        claim_type="eligibility",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_DIP_HOME, E_DIP_VISA_ONLINE],
        evidence_excerpt="DIP site identity: Department of Immigration and Passports, Ministry of Home Affairs.",
        reasoning="Responsible authority verified on live Tier-1 DIP pages.",
        applicability="bangladesh_government_visa_authority",
    )
    put(
        "migration-visa-application-dip::c-visa-types-page",
        service_id="migration-visa-application-dip",
        priority=1,
        claim_type="document",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_DIP_VISA_TYPES_PAGE],
        evidence_excerpt=(
            "DIP page hosts Dec 2024 PDF 'Types and Essential Documents of Visa' with visa-type matrix "
            "(A, A1, A2, B, C, etc.) and issue/extend document columns."
        ),
        reasoning=(
            "Document matrix exists on official DIP-hosted PDF (Dec 2024 path). HTML page metadata stale (2022) "
            "but attachment is newer; per-visa-type completeness not fully audited in this pass."
        ),
        applicability="visa_document_requirements_by_type",
    )
    put(
        "migration-visa-application-dip::c-visa-types-freshness-2022",
        service_id="migration-visa-application-dip",
        priority=1,
        claim_type="restriction",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_DIP_VISA_TYPES_PAGE],
        evidence_excerpt="HTML page footer: last updated 29 March 2022; PDF attachment dated Dec 2024 in object storage path.",
        reasoning="Freshness warning verified: page metadata is 2022 though newer PDF attachment exists — users must not rely on page date alone.",
        applicability="visa_types_page_freshness",
    )
    put(
        "migration-visa-application-dip::c-visa-mrv-fees-page",
        service_id="migration-visa-application-dip",
        priority=1,
        claim_type="fee",
        information_class="DISCOVERY",
        verification_status="UNVERIFIED",
        evidence=[E_DIP_MRV_FEES_PAGE],
        evidence_excerpt="MRV fee page links Dec 2024 PDF; scanned PDF text not machine-readable; no fee amounts extracted.",
        reasoning="Fee schedule existence implied by official page+PDF link but amounts not verified — do not invent fees.",
        applicability="mrv_visa_fees",
        knowledge_gap="MISSING_MRV_FEE_TABLE_EXTRACT",
        do_not_promote_to_must=True,
    )
    put(
        "migration-visa-application-dip::c-visa-foreign-embassy-not-in-scope",
        service_id="migration-visa-application-dip",
        priority=2,
        claim_type="restriction",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_DIP_VISA_TYPES_PAGE],
        evidence_excerpt="Visa types PDF: 'Visa is usually issued by Bangladesh High Commission/Embassy ... and extended by DIP'.",
        reasoning="Scope boundary verified: Bangladesh-government visa issuance/extension vs foreign embassy rules for BD citizens abroad.",
        applicability="scope_boundary",
    )
    put(
        "migration-visa-application-dip::c-visa-dip-eservice-link",
        service_id="migration-visa-application-dip",
        priority=1,
        claim_type="application_url",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_DIP_HOME],
        evidence_excerpt="DIP home internal e-services: 'অনলাইন এমআরভি আবেদন' → https://www.visa.gov.bd",
        reasoning="Official e-service link on live Tier-1 DIP home.",
        applicability="bangladesh_mrv_online_application",
    )

    # ===================== expatriate cell =====================
    put(
        "police-expatriate-services::c-expat-charter-services",
        service_id="police-expatriate-services",
        priority=2,
        claim_type="availability",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_POLICE_CHARTER],
        evidence_excerpt="Charter row 23: passport verification, legal action, family security, investment protection.",
        reasoning="Service scope on live charter.",
        applicability="expatriate_cell_charter",
    )
    put(
        "police-expatriate-services::c-expat-charter-free",
        service_id="police-expatriate-services",
        priority=1,
        claim_type="fee",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_POLICE_CHARTER],
        evidence_excerpt="Charter row 23: 'বিনামূল্যে'.",
        reasoning="Free service on charter.",
        applicability="expatriate_cell_charter",
    )
    put(
        "police-expatriate-services::c-expat-charter-sla",
        service_id="police-expatriate-services",
        priority=1,
        claim_type="processing_time",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_POLICE_CHARTER],
        evidence_excerpt="Charter row 23: 'দ্রুততম সময়' (qualitative, no numeric days).",
        reasoning="Qualitative official SLA verified.",
        applicability="expatriate_cell_charter",
    )
    put(
        "police-expatriate-services::c-expat-responsible-aig",
        service_id="police-expatriate-services",
        priority=2,
        claim_type="office",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_POLICE_CHARTER],
        evidence_excerpt="Charter row 23: AIG (Expatriate Cell), PHQ; mobile 55101678.",
        reasoning="Responsible officer on live charter.",
        applicability="expatriate_cell_charter",
    )
    put(
        "police-expatriate-services::c-expat-pcc-auth-letter-link",
        service_id="police-expatriate-services",
        priority=2,
        claim_type="conditional_document",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_PCC_PORTAL],
        evidence_excerpt="PCC portal terms item 7: expatriate authorization letter for representative collection.",
        reasoning="Related PCC rule verified; distinct from Expatriate Cell charter entry — not merged.",
        applicability="online_pcc_expatriate_representative",
        condition={"requirement_class": "CONDITIONAL", "if": "pcc_via_representative"},
    )

    # ===================== firearms license =====================
    put(
        "police-firearms-license::c-firearms-charter-pathway",
        service_id="police-firearms-license",
        priority=2,
        claim_type="procedure_step",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_POLICE_CHARTER],
        evidence_excerpt="Charter row 8: firearms license on application at District Special Branch.",
        reasoning="Application pathway on live charter only — no separate forms captured.",
        applicability="firearms_license_service_charter",
    )
    put(
        "police-firearms-license::c-firearms-charter-fee-na",
        service_id="police-firearms-license",
        priority=1,
        claim_type="fee",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_POLICE_CHARTER],
        evidence_excerpt="Charter row 8 fee column: 'প্রযোজ্য নহে' (not applicable on charter table).",
        reasoning="Charter explicitly marks fee as N/A in table — verified as charter-stated, not inferred zero cost elsewhere.",
        applicability="firearms_license_service_charter",
    )
    put(
        "police-firearms-license::c-firearms-charter-sla",
        service_id="police-firearms-license",
        priority=1,
        claim_type="processing_time",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_POLICE_CHARTER],
        evidence_excerpt="Charter row 8: '২১-৩০ দিন'.",
        reasoning="Official numeric SLA 21–30 days on live charter.",
        applicability="firearms_license_service_charter",
        fee_metadata={"official_sla_days_min": 21, "official_sla_days_max": 30},
    )
    put(
        "police-firearms-license::c-firearms-responsible-officer",
        service_id="police-firearms-license",
        priority=2,
        claim_type="office",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_POLICE_CHARTER],
        evidence_excerpt="Charter row 8: SP (DSB) / metro unit / Special Superintendent (City SB).",
        reasoning="Responsible officers on live charter.",
        applicability="firearms_license_service_charter",
    )

    return R


def build_conflicts() -> list[dict]:
    return [
        {
            "conflict_id": "conflict-pcc-fee-online-vs-offline",
            "resolution_status": "PARTIALLY_RESOLVED",
            "classification": "channel_specific_unreconciled",
            "old_claim": "Offline police.gov.bd page: BDT 500, treasury code 1-2201-0001-2681 (paper/chalan to SP/Commissioner).",
            "new_claim": "Online pcc.police.gov.bd + charter online row: BDT 1,500, code 1-7301-0001-2681.",
            "old_evidence": [E_PCC_OFFLINE],
            "new_evidence": [E_PCC_PORTAL, E_POLICE_CHARTER],
            "authority": "Bangladesh Police Tier 1 portal vs Tier 2 static instruction page",
            "freshness": "Both pages live as of 2026-08-24; charter aligns with online 1500 only",
            "outcome": (
                "Likely channel-specific (online vs legacy paper procedure) but NOT authoritatively reconciled: "
                "no circular/gazette found stating offline paper path fee. Online 1500 VERIFIED for online channel. "
                "Offline 500 claim marked CONFLICTING — do not publish as current universal PCC fee."
            ),
            "blocks_official_publication": True,
            "claim_ids": [
                "police-clearance-certificate::c-online-fee-1500",
                "police-clearance-certificate::c-offline-fee-500-chalan",
            ],
        },
        {
            "conflict_id": "conflict-pcc-treasury-code",
            "resolution_status": "PARTIALLY_RESOLVED",
            "classification": "channel_specific",
            "old_claim": "Treasury code 1-2201-0001-2681 (offline page)",
            "new_claim": "Treasury code 1-7301-0001-2681 (online portal + payment instructions)",
            "old_evidence": [E_PCC_OFFLINE],
            "new_evidence": [E_PCC_PORTAL],
            "authority": "Same sources as fee conflict",
            "freshness": "2026-08-24 live fetch",
            "outcome": "Treasury codes differ by channel documentation; treat as paired with fee conflict.",
            "blocks_official_publication": True,
        },
        {
            "conflict_id": "conflict-gd-online-scope-timeline",
            "resolution_status": "UNRESOLVED",
            "classification": "historical_rollout_vs_current_capability_unknown",
            "old_claim": "Online GD limited to lost-and-found (Tier-5 TBS Jun 2025 reporting).",
            "new_claim": "All GD types available online nationwide (Tier-5 BSS Sep 2025).",
            "old_evidence": [E_TBS_GD],
            "new_evidence": [E_BSS_GD],
            "authority": "Tier-5 news only — no Tier 1–2 confirmation",
            "freshness": "2025 press statements; gd.police.gov.bd unreachable",
            "outcome": "Current online GD scope UNVERIFIED. Charter confirms online channel exists but not complaint-type matrix.",
            "blocks_official_publication": True,
            "claim_ids": [
                "police-general-diary-online::c-gd-all-types-expansion",
                "police-general-diary::c-gd-not-all-types-historically",
            ],
        },
        {
            "conflict_id": "conflict-passport-verification-vs-pcc",
            "resolution_status": "RESOLVED",
            "classification": "distinct_services_not_contradiction",
            "old_claim": "Passport verification SLA 15–21 days normal / 7 urgent (charter row 5).",
            "new_claim": "Online police clearance SLA 3–7 days (charter row 7).",
            "old_evidence": [E_POLICE_CHARTER],
            "new_evidence": [E_POLICE_CHARTER],
            "authority": "Bangladesh Police citizen charter",
            "freshness": "Live charter 2026-08-24",
            "outcome": (
                "Not a factual conflict — different catalogue services with different charter rows. "
                "Must not merge SLAs in product answers."
            ),
            "blocks_official_publication": False,
        },
        {
            "conflict_id": "conflict-pcc-portal-url-variants",
            "resolution_status": "RESOLVED",
            "classification": "same_apex_app_multiple_entry_routes",
            "old_claim": "Catalogue URL pcc.police.gov.bd/ords/r/pcc/pcc/9",
            "new_claim": "police.gov.bd menu links f?p=500:1 alternate APEX route",
            "old_evidence": [E_PCC_PORTAL],
            "new_evidence": [E_PCC_OFFLINE],
            "authority": "Same Bangladesh Police PCC Oracle APEX application",
            "freshness": "2026-08-24",
            "outcome": "Multiple entry URLs for same PCC system; catalogue canonical URL live-verified.",
            "blocks_official_publication": False,
        },
    ]


def build_gaps(enriched: list[dict], raw_gaps: list[dict]) -> list[dict]:
    gaps = {g["gap_id"]: {**g, "status": g.get("status", "OPEN")} for g in raw_gaps}
    for x in enriched:
        g = x.get("knowledge_gap")
        if not g:
            continue
        if g not in gaps:
            gaps[g] = {
                "gap_id": g,
                "classification": "verification_discovered",
                "priority": "HIGH",
                "status": "OPEN",
                "related_claims": [],
                "description": "Identified during Batch 2B independent verification.",
            }
        gaps[g].setdefault("related_claims", [])
        if x["claim_id"] not in gaps[g]["related_claims"]:
            gaps[g]["related_claims"].append(x["claim_id"])
    return list(gaps.values())


def service_readiness(claims: list[dict], results: dict[str, dict]) -> dict:
    high_risk_types = {
        "fee",
        "eligibility",
        "document",
        "conditional_document",
        "application_url",
        "payment_method",
        "processing_time",
        "restriction",
        "office",
        "availability",
    }
    by_svc: dict[str, list] = defaultdict(list)
    for c in claims:
        by_svc[c["service_id"]].append({**c, "verification": results[c["claim_id"]]})

    readiness = {}
    for sid, items in sorted(by_svc.items()):
        statuses = [i["verification"]["verification_status"] for i in items]
        high = [
            i
            for i in items
            if i["verification"].get("priority", 3) == 1
            or i["verification"].get("claim_type") in high_risk_types
        ]
        high_stat = [i["verification"]["verification_status"] for i in high]
        has_conflicting = any(s == "CONFLICTING" for s in high_stat)
        has_unverified_high = any(s in {"UNVERIFIED", "OUTDATED"} for s in high_stat)
        high_verified = sum(1 for s in high_stat if s == "VERIFIED")

        if sid == "police-clearance-certificate":
            color = "YELLOW"
            reason = (
                "Online PCC core rules live-verified (Tier 1 portal + charter) but offline fee CONFLICTING; "
                "collection/delivery and correction workflows still gapped."
            )
        elif sid in {"police-general-diary", "police-general-diary-online"}:
            color = "YELLOW"
            reason = (
                "Charter SLA/fee/channels verified; gd.police.gov.bd unreachable; online scope/expansion UNVERIFIED."
            )
        elif sid == "migration-visa-application-dip":
            color = "YELLOW"
            reason = (
                "DIP portal links and Dec 2024 visa-types PDF partially verified; visa.gov.bd unreachable; "
                "MRV fee matrix UNVERIFIED (scanned PDF)."
            )
        elif sid == "police-cyber-support-women":
            color = "GREEN"
            reason = "All charter-sourced PCSW claims VERIFIED on live citizen charter."
        elif sid == "police-employment-verification":
            color = "YELLOW"
            reason = "Pathway verified; fee amount and numeric SLA not on Tier 1–2 sources."
        elif sid == "police-firearms-license":
            color = "YELLOW"
            reason = "Charter pathway/SLA verified; eligibility/documents/legal basis beyond charter not captured."
        elif sid == "police-passport-verification":
            color = "YELLOW"
            reason = "Passport verification SLAs VERIFIED on charter; fee amount missing; distinct from PCC."
        elif sid == "police-passport-police-verification":
            color = "YELLOW"
            reason = "Service boundaries verified; e-Passport onboarding PV steps only partially verified (batch-02a)."
        elif sid == "police-nid-address-verification":
            color = "YELLOW"
            reason = "Conditional NID/address rules verified via PCC pages; no standalone service portal."
        elif sid == "police-expatriate-services":
            color = "YELLOW"
            reason = "Charter scope verified; detailed procedures beyond charter not captured."
        elif has_conflicting:
            color = "RED"
            reason = "Critical CONFLICTING high-risk claims remain."
        elif has_unverified_high and high_verified == 0:
            color = "RED"
            reason = "Critical claims largely UNVERIFIED."
        elif has_unverified_high or has_conflicting:
            color = "YELLOW"
            reason = "Material gaps or conflicts on high-risk fields."
        elif high_verified >= max(1, len(high) // 2):
            color = "GREEN"
            reason = "Critical claims largely verified with Tier 1–2 evidence."
        else:
            color = "YELLOW"
            reason = "Partial verification coverage."

        readiness[sid] = {
            "service_id": sid,
            "readiness": color,
            "claim_count": len(items),
            "status_counts": dict(Counter(statuses)),
            "reason": reason,
            "manual_review_recommended": color != "GREEN",
        }
    return readiness


def write_docs(summary: dict, readiness: dict, conflicts: list[dict], gaps: list[dict]) -> None:
    green = [k for k, v in readiness.items() if v["readiness"] == "GREEN"]
    yellow = [k for k, v in readiness.items() if v["readiness"] == "YELLOW"]
    red = [k for k, v in readiness.items() if v["readiness"] == "RED"]
    sc = summary["status_counts"]
    lines = [
        "# Batch 2B — Independent Claim Verification (Police + Immigration)",
        "",
        f"**Date:** 2026-08-24  ",
        f"**Verifier:** `{VERIFIER}`  ",
        "**Layer:** `data/research/verification/batch-02b-police-immigration` (STAGING ONLY)  ",
        "**Published to runtime:** No  ",
        "**publish_verified_knowledge.py run:** No",
        "",
        "## Policy used",
        "",
        "- High-risk OFFICIAL claims require Tier 1–2 explicit support on live fetches.",
        "- Tier 5 news (GD expansion) does NOT promote to VERIFIED.",
        "- PCC fee conflict: online BDT 1,500 VERIFIED for online channel; offline BDT 500 CONFLICTING — not published as universal fee.",
        "- Passport verification SLAs kept separate from PCC SLAs.",
        "- See `verification_policy.json`.",
        "",
        "## Totals",
        "",
        f"1. Total claims: **{summary['total_claims']}**",
        f"2. VERIFIED: **{sc.get('VERIFIED', 0)}**",
        f"3. PARTIALLY_VERIFIED: **{sc.get('PARTIALLY_VERIFIED', 0)}**",
        f"4. UNVERIFIED: **{sc.get('UNVERIFIED', 0)}**",
        f"5. CONFLICTING: **{sc.get('CONFLICTING', 0)}**",
        f"6. OUTDATED: **{sc.get('OUTDATED', 0)}**",
        f"7. REJECTED: **{sc.get('REJECTED', 0)}**",
        f"8. Official claims verified: **{summary['official_claims_verified']}**",
        f"9. Practical claims: **{summary['practical_claims']}**",
        f"10. Resolved conflicts: **{summary['conflicts_resolved']}**",
        f"11. Unresolved conflicts: **{summary['conflicts_unresolved']}**",
        f"12. Knowledge gaps: **{summary['knowledge_gaps_open']}**",
        f"13. GREEN services: **{summary['services_green']}**",
        f"14. YELLOW services: **{summary['services_yellow']}**",
        f"15. RED services: **{summary['services_red']}**",
        "",
        "## PCC fee conflict (critical)",
        "",
        "| Channel | Amount | Treasury code | Status |",
        "|---------|--------|---------------|--------|",
        "| Online (`pcc.police.gov.bd`) | BDT 1,500 | 1-7301-0001-2681 | **VERIFIED** (online channel) |",
        "| Offline page (`police.gov.bd/en/police_clearance_certificate`) | BDT 500 | 1-2201-0001-2681 | **CONFLICTING** |",
        "| Citizen charter (online clearance row) | BDT 1,500 | — | **VERIFIED** |",
        "",
        "Classification: **channel_specific_unreconciled**. No gazette/circular captured to confirm whether legacy paper path remains at 500.",
        "",
        "## Evidence limitations",
        "",
        summary["evidence_coverage_notes"],
        "",
        "## Conflict outcomes",
        "",
    ]
    for c in conflicts:
        lines.append(f"- `{c['conflict_id']}` — **{c['resolution_status']}** ({c['classification']}): {c['outcome']}")
    lines.extend(["", "## Service readiness", "", "### GREEN"])
    for s in green:
        lines.append(f"- `{s}` — {readiness[s]['reason']}")
    lines.extend(["", "### YELLOW"])
    for s in yellow:
        lines.append(f"- `{s}` — {readiness[s]['reason']}")
    lines.extend(["", "### RED"])
    for s in red:
        lines.append(f"- `{s}` — {readiness[s]['reason']}")
    lines.extend(["", "## Knowledge gaps (open)", ""])
    for g in gaps:
        if g.get("status", "OPEN") == "OPEN":
            lines.append(f"- `{g['gap_id']}` — {g.get('description', g.get('classification', ''))}")
    lines.extend(
        [
            "",
            "## Explicit non-actions",
            "",
            "- Did not publish claims",
            "- Did not start Batch 3 / BRTA / Tax / Land / Education",
            "- Did not deploy or modify frontend",
            "",
            "## Machine-readable outputs",
            "",
            "- `data/research/verification/batch-02b-police-immigration/claims_verification.json`",
            "- `data/research/verification/batch-02b-police-immigration/conflicts_resolution.json`",
            "- `data/research/verification/batch-02b-police-immigration/knowledge_gaps.json`",
            "- `data/research/verification/batch-02b-police-immigration/service_readiness.json`",
            "- `data/research/verification/batch-02b-police-immigration/summary.json`",
            "- `data/research/verification/batch-02b-police-immigration/verification_policy.json`",
            "- `data/research/verification/batch-02b-police-immigration/source_evidence.json`",
            "",
        ]
    )
    DOCS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    SNAP.mkdir(parents=True, exist_ok=True)

    claims = json.loads((RAW / "claims.json").read_text(encoding="utf-8"))["claims"]
    raw_gaps = json.loads((RAW / "knowledge_gaps.json").read_text(encoding="utf-8"))["knowledge_gaps"]
    results = build_results()

    missing = [c["claim_id"] for c in claims if c["claim_id"] not in results]
    if missing:
        raise SystemExit(f"Missing verification for claims: {missing}")

    enriched = []
    for c in claims:
        r = results[c["claim_id"]]
        enriched.append(
            {
                "claim_id": c["claim_id"],
                "service_id": c["service_id"],
                "claim_text": c["claim_text"],
                "staging_pipeline_status": c["pipeline_status"],
                "information_class": r.get("information_class", c["information_class"]),
                "claim_type": r.get("claim_type", c.get("claim_type")),
                "priority": r.get("priority"),
                "verification_status": r["verification_status"],
                "reasoning": r["reasoning"],
                "evidence": r.get("evidence"),
                "evidence_excerpt": r.get("evidence_excerpt"),
                "evidence_locator": (r.get("evidence") or [{}])[0].get("evidence_locator") if r.get("evidence") else None,
                "retrieval_method": (r.get("evidence") or [{}])[0].get("retrieval_method") if r.get("evidence") else None,
                "condition": r.get("condition") or c.get("condition"),
                "applicability": r.get("applicability"),
                "fee_metadata": r.get("fee_metadata"),
                "conflict_id": r.get("conflict_id"),
                "conflict_classification": r.get("conflict_classification"),
                "knowledge_gap": r.get("knowledge_gap"),
                "verification_scope": r.get("verification_scope"),
                "do_not_promote_to_must": r.get("do_not_promote_to_must", False),
                "verifier": r["verifier"],
                "verified_at": r["verified_at"],
                "publication_status": "STAGING_ONLY",
            }
        )

    status_counts = Counter(x["verification_status"] for x in enriched)
    official_verified = sum(
        1 for x in enriched if x["information_class"] == "OFFICIAL" and x["verification_status"] == "VERIFIED"
    )
    conflicts = build_conflicts()
    gaps = build_gaps(enriched, raw_gaps)
    readiness = service_readiness(claims, results)
    color_counts = Counter(v["readiness"] for v in readiness.values())

    policy = {
        "version": "1.0",
        "batch_id": "batch-02b-police-immigration",
        "verified_at": VERIFIED_AT,
        "rules": {
            "high_risk_official": {
                "preferred_tiers": [1, 2],
                "require_explicit_support": True,
                "tier5_news_not_equal_to_official_fact": True,
                "conflicting_fees_do_not_publish_as_universal": True,
            },
            "service_separation": {
                "passport_verification_vs_pcc_vs_employment": True,
                "do_not_merge_slas": True,
            },
            "pcc_fee_conflict": {
                "online_1500_verified_channel": "online_pcc",
                "offline_500_status": "CONFLICTING",
                "do_not_publish_universal_current_fee": True,
            },
            "publication": "STAGING_ONLY — do not run publish_verified_knowledge.py",
        },
    }

    summary = {
        "batch_id": "batch-02b-police-immigration",
        "layer": "research/verification",
        "publication_status": "STAGING_ONLY",
        "published": False,
        "verifier": VERIFIER,
        "verified_at": VERIFIED_AT,
        "total_claims": len(enriched),
        "status_counts": dict(status_counts),
        "official_claims_verified": official_verified,
        "practical_claims": sum(1 for x in enriched if x["information_class"] == "PRACTICAL"),
        "conflicts_resolved": sum(1 for c in conflicts if c["resolution_status"] == "RESOLVED"),
        "conflicts_unresolved": sum(
            1 for c in conflicts if c["resolution_status"] not in {"RESOLVED", "PARTIALLY_RESOLVED"}
        ),
        "conflicts_partially_resolved": sum(
            1 for c in conflicts if c["resolution_status"] == "PARTIALLY_RESOLVED"
        ),
        "knowledge_gaps_open": len([g for g in gaps if g.get("status") == "OPEN"]),
        "services_green": color_counts.get("GREEN", 0),
        "services_yellow": color_counts.get("YELLOW", 0),
        "services_red": color_counts.get("RED", 0),
        "evidence_coverage_notes": (
            "Live Tier-1: pcc.police.gov.bd (full PCC terms/fees/steps), dip.gov.bd, dip visa-online page. "
            "Live Tier-2: police citizen charter (GD/PCC/passport verification/employment/firearms/expatriate rows), "
            "police.gov.bd offline PCC page. "
            "Official PDFs: DIP visa types Dec 2024 (machine-readable); MRV fees Dec 2024 PDF scanned/unreadable. "
            "Failed fetches: gd.police.gov.bd (502), visa.gov.bd (SSL). "
            "Tier-5 GD expansion claims left UNVERIFIED."
        ),
        "verification_coverage": f"{len(enriched)}/{len(enriched)} claims assigned a primary verification status",
        "main_limitations": [
            "PCC offline BDT 500 CONFLICTING with online BDT 1500 — not published as universal fee",
            "GD portal unreachable; online scope UNVERIFIED",
            "visa.gov.bd unreachable; MRV fee amounts UNVERIFIED",
            "Employment/passport verification numeric fees not on charter",
        ],
    }

    source_evidence = {
        "snapshots_dir": "data/research/verification/batch-02b-police-immigration/source_snapshots/",
        "url_checks": {
            "https://pcc.police.gov.bd/ords/r/pcc/pcc/9": 200,
            "https://www.police.gov.bd/index.php/en/citizen_charter": 200,
            "https://www.police.gov.bd/en/police_clearance_certificate": 200,
            "https://www.dip.gov.bd/": 200,
            "https://dip.gov.bd/site/page/29bf208d-7729-4149-b17b-2a76efea59c9/": 200,
            "https://gd.police.gov.bd/": 502,
            "https://www.visa.gov.bd/": "fetch_failed_ssl",
        },
        "official_pdfs": {
            "dip_visa_types_dec2024.pdf": "machine_readable",
            "dip_mrv_fees_dec2024.pdf": "scanned_unreadable",
        },
    }

    (OUT / "verification_policy.json").write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
    (OUT / "claims_verification.json").write_text(
        json.dumps(
            {"schema": "bda.research.verification.claims/1.0", "batch_id": "batch-02b-police-immigration", "claims": enriched},
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    (OUT / "conflicts_resolution.json").write_text(json.dumps({"conflicts": conflicts}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT / "knowledge_gaps.json").write_text(json.dumps({"knowledge_gaps": gaps}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT / "service_readiness.json").write_text(json.dumps({"services": readiness}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (OUT / "source_evidence.json").write_text(json.dumps(source_evidence, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(
        "# Batch 2B verification artifacts (STAGING ONLY)\n\nDo not publish without publish gate.\n",
        encoding="utf-8",
    )

    write_docs(summary, readiness, conflicts, gaps)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
