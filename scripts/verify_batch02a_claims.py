#!/usr/bin/env python3
"""Independent Batch 2A passport claim verification (STAGING ONLY — does not publish)."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RAW = REPO / "data/research/raw/batch-02a-passport"
OUT = REPO / "data/research/verification/batch-02a-passport"
DOCS = REPO / "docs/research/batch-02a-passport-independent-verification.md"
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

# Shared evidence bundles
E_MRP_HOME = {
    "source_id": "src-mrp-home",
    "source_url": "http://passport.gov.bd/",
    "authority_tier": 1,
    "retrieval_method": "live_html",
    "live_http_status": 200,
    "snapshot": "data/research/verification/batch-02a-passport/source_snapshots/mrp_home.html",
    "retrieved_at": "2026-08-24",
}
E_MRP_USERHOME = {
    "source_id": "src-mrp-reissue",
    "source_url": "http://passport.gov.bd/UserHome.aspx",
    "authority_tier": 1,
    "retrieval_method": "live_html",
    "live_http_status": 200,
    "snapshot": "data/research/verification/batch-02a-passport/source_snapshots/mrp_userhome.html",
    "retrieved_at": "2026-08-24",
}
E_MRP_STATUS = {
    "source_id": "src-mrp-status",
    "source_url": "http://passport.gov.bd/OnlineStatus.aspx",
    "authority_tier": 1,
    "retrieval_method": "live_html",
    "live_http_status": 200,
    "snapshot": "data/research/verification/batch-02a-passport/source_snapshots/mrp_status.html",
    "retrieved_at": "2026-08-24",
}
E_DIP_HOME = {
    "source_id": "src-dip-home",
    "source_url": "https://www.dip.gov.bd/",
    "authority_tier": 1,
    "retrieval_method": "live_html",
    "live_http_status": 200,
    "snapshot": "data/research/verification/batch-02a-passport/source_snapshots/dip_home.html",
    "retrieved_at": "2026-08-24",
}
E_DUBAI = {
    "source_id": "src-mofa-dubai-epassport",
    "source_url": "https://bcgdubai.gov.bd/e-passport/",
    "authority_tier": 2,
    "retrieval_method": "live_html",
    "live_http_status": 200,
    "snapshot": "data/research/verification/batch-02a-passport/source_snapshots/mission_dubai.html",
    "retrieved_at": "2026-08-24",
}
E_POLICE_CHARTER = {
    "source_id": "src-police-charter",
    "source_url": "https://www.police.gov.bd/index.php/en/citizen_charter",
    "authority_tier": 2,
    "retrieval_method": "live_html",
    "live_http_status": 200,
    "snapshot": "data/research/verification/batch-02a-passport/source_snapshots/police_charter.html",
    "retrieved_at": "2026-08-24",
}
E_EPASSPORT_LANDING = {
    "source_id": "src-epassport-landing",
    "source_url": "https://epassport.gov.bd/landing",
    "authority_tier": 1,
    "retrieval_method": "live_spa_shell",
    "live_http_status": 200,
    "evidence_limitation": "Angular SPA shell only; instructional text not in HTML",
    "retrieved_at": "2026-08-24",
}
E_EPASSPORT_ONBOARDING = {
    "source_id": "src-epassport-onboarding",
    "source_url": "https://www.epassport.gov.bd/onboarding",
    "authority_tier": 1,
    "retrieval_method": "blocked",
    "live_http_status": 403,
    "evidence_limitation": "Akamai 403 from verifier network; Wayback captures also SPA shell without text",
    "retrieved_at": "2026-08-24",
}
E_EPASSPORT_FEES_INDEX = {
    "source_id": "src-epassport-fees",
    "source_url": "https://epassport.gov.bd/instructions/passport-fees",
    "authority_tier": 1,
    "retrieval_method": "search_index_excerpt_only",
    "source_last_updated_on_page": "2026-03-08",
    "evidence_limitation": "Live and Wayback return SPA shell; fee text only via search-engine indexed excerpt citing official URL",
    "retrieved_at": "2026-08-24",
}
E_EPASSPORT_URGENT_INDEX = {
    "source_id": "src-epassport-urgent",
    "source_url": "https://epassport.gov.bd/instructions/urgent-applications",
    "authority_tier": 1,
    "retrieval_method": "search_index_excerpt_only",
    "source_last_updated_on_page": "2022-10-22",
    "evidence_limitation": "SPA shell only; urgent rules from indexed excerpt of same official URL",
    "retrieved_at": "2026-08-24",
}
E_EPASSPORT_INSTRUCTIONS_INDEX = {
    "source_id": "src-epassport-instructions",
    "source_url": "https://epassport.gov.bd/instructions/instructions",
    "authority_tier": 1,
    "retrieval_method": "search_index_excerpt_only",
    "evidence_limitation": "SPA shell only; Bengali instruction bullets from indexed excerpt",
    "retrieved_at": "2026-08-24",
}
E_NOTICE34_INDEX = {
    "source_id": "src-epassport-enrollment-docs",
    "source_url": "https://www.epassport.gov.bd/landing/notices/34",
    "authority_tier": 1,
    "retrieval_method": "search_index_excerpt_only",
    "source_last_updated_on_page": "2025-05-07",
    "evidence_limitation": "Live timeout; Wayback SPA shell; enrollment doc list from indexed excerpt dated 7 May 2025",
    "retrieved_at": "2026-08-24",
}
E_SINGAPORE_404 = {
    "source_id": "src-mofa-singapore-epassport",
    "source_url": "https://singapore.mofa.gov.bd/en/site/page/E-passport-application-rules",
    "authority_tier": 2,
    "retrieval_method": "live_html",
    "live_http_status": 404,
    "evidence_limitation": "Page returns 'The requested page could not be found' as of verification date",
    "retrieved_at": "2026-08-24",
}
E_ABUDHABI_UNREACHABLE = {
    "source_id": "src-mofa-abudhabi-epassport",
    "source_url": "https://abudhabi.mofa.gov.bd/en/site/page/E-Passport-Issue--Reissue:",
    "authority_tier": 2,
    "retrieval_method": "fetch_timeout",
    "evidence_limitation": "Page body not retrieved; CMS shell only",
    "retrieved_at": "2026-08-24",
}
E_PRACTICAL_QNA = {
    "source_id": "src-practical-qna-fees",
    "source_url": "https://en.qnabangla.com/passport-fee-bangladesh/",
    "authority_tier": 6,
    "retrieval_method": "third_party",
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

    SPA_PARTIAL = (
        "Official epassport.gov.bd instructional routes return Angular SPA shells from live fetch, "
        "Wayback, and verifier network (onboarding 403). Indexed search excerpts cite the official URL "
        "but are NOT equivalent to direct page evidence per verification policy."
    )

    # --- epassport-new-application ---
    put(
        "epassport-new-application::c-apply-online",
        service_id="epassport-new-application",
        priority=1,
        claim_type="application_url",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_DIP_HOME, E_EPASSPORT_LANDING, E_EPASSPORT_ONBOARDING],
        evidence_excerpt="DIP lists 'ই-পাসপোর্ট আবেদন' → https://www.epassport.gov.bd/; landing HTTP 200.",
        reasoning=(
            f"{SPA_PARTIAL} Onboarding URL is catalogue-official but returned 403 here; "
            "cannot confirm Step-1 UI text live. DIP Tier-1 link corroborates e-Passport as official channel."
        ),
        applicability="universal",
    )
    put(
        "epassport-new-application::c-no-attestation-online",
        service_id="epassport-new-application",
        priority=1,
        claim_type="procedure_step",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_EPASSPORT_INSTRUCTIONS_INDEX],
        evidence_excerpt="Indexed excerpt: 'ই-পাসপোর্ট আবেদনের ক্ষেত্রে কোন কাগজপত্র সত্যায়ন করার প্রয়োজন হবে না'",
        reasoning=f"{SPA_PARTIAL} Wording matches indexed official instructions URL; no direct HTML/PDF snapshot.",
        applicability="universal_for_epassport_online_apply",
    )
    put(
        "epassport-new-application::c-id-nid-or-brc",
        service_id="epassport-new-application",
        priority=1,
        claim_type="document",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_EPASSPORT_INSTRUCTIONS_INDEX, E_DUBAI, E_NOTICE34_INDEX],
        evidence_excerpt="Instructions index: NID or online BRC English; Dubai: 17-digit verifiable BRC or NID.",
        reasoning=(
            "Tier-2 Dubai page live-confirms NID/BRC requirement. Tier-1 instructions text only via index excerpt."
        ),
        applicability="universal",
    )
    put(
        "epassport-new-application::c-minor-parent-nid",
        service_id="epassport-new-application",
        priority=1,
        claim_type="conditional_document",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_EPASSPORT_INSTRUCTIONS_INDEX],
        evidence_excerpt="Indexed excerpt: under-18 without NID must provide father or mother NID number.",
        reasoning=f"{SPA_PARTIAL} Conditional rule plausible and indexed; not directly snapshotted.",
        applicability="conditional",
        condition={"field": "age", "op": "lt", "value": 18},
    )
    put(
        "epassport-new-application::c-minor-3r-photo",
        service_id="epassport-new-application",
        priority=1,
        claim_type="conditional_document",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_EPASSPORT_INSTRUCTIONS_INDEX],
        evidence_excerpt="Indexed excerpt: under 6 years → 3R lab-print photo at enrollment.",
        reasoning=f"{SPA_PARTIAL} Indexed-only evidence for age<6 photo rule.",
        applicability="conditional",
        condition={"field": "age", "op": "lt", "value": 6},
    )
    put(
        "epassport-new-application::c-police-station-select",
        service_id="epassport-new-application",
        priority=2,
        claim_type="procedure_step",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_EPASSPORT_ONBOARDING],
        evidence_excerpt="Indexed onboarding UI: select district and nearest police station (onboarding 403 live).",
        reasoning=(
            "Police station selection is standard e-Passport onboarding step per indexed portal UI; "
            "live onboarding blocked; not independently readable."
        ),
        applicability="domestic_applicants",
    )
    put(
        "epassport-new-application::c-govt-noc",
        service_id="epassport-new-application",
        priority=1,
        claim_type="conditional_document",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_NOTICE34_INDEX, E_EPASSPORT_INSTRUCTIONS_INDEX],
        evidence_excerpt="Notice 34 index: 'GO/NOC for government service holder (as applicable)'.",
        reasoning="Enrollment notice list indexed (updated 7 May 2025 on page label); SPA body not captured.",
        applicability="conditional",
        condition={"field": "employment_type", "op": "eq", "value": "government"},
    )
    put(
        "epassport-new-application::c-enrollment-docs-list",
        service_id="epassport-new-application",
        priority=1,
        claim_type="document",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_NOTICE34_INDEX],
        evidence_excerpt=(
            "Required: printed summary+appointment; original NID/BRC; payment slip if offline; "
            "previous passport; GO/NOC; printed form; correction docs if any."
        ),
        reasoning="Notice 34 document checklist matches claim; evidence is search-index excerpt only (Tier-1 URL).",
        applicability="enrollment_visit",
    )
    put(
        "epassport-new-application::c-five-step-workflow",
        service_id="epassport-new-application",
        priority=3,
        claim_type="procedure_step",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_EPASSPORT_LANDING],
        evidence_excerpt="Landing SPA shell links to ./instructions/five-step-to-your-epassport (link target not rendered in shell).",
        reasoning="Five-step page existence inferred from landing route reference; step content not captured.",
        applicability="universal",
    )
    put(
        "epassport-new-application::c-expatriate-onboarding-no",
        service_id="epassport-new-application",
        priority=1,
        claim_type="procedure_step",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_EPASSPORT_ONBOARDING, E_DUBAI],
        evidence_excerpt="Indexed onboarding: 'Are you applying from Bangladesh? Yes/No'; Dubai guides online apply from UAE.",
        reasoning=(
            "Expatriate flow (No → mission/country) indexed on onboarding; live page blocked. "
            "Dubai Tier-2 corroborates abroad application via epassport.gov.bd."
        ),
        applicability="expatriate",
    )
    put(
        "epassport-new-application::c-brc-everify",
        service_id="epassport-new-application",
        priority=1,
        claim_type="conditional_document",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_DUBAI],
        evidence_excerpt="Dubai: 'online verifiable from https://everify.bdris.gov.bd/' for Birth Certificate.",
        reasoning="Tier-2 mission page live-confirms everify requirement when BRC used.",
        applicability="conditional",
        condition={"field": "id_document_type", "op": "eq", "value": "brc"},
    )

    # --- epassport-reissue ---
    put(
        "epassport-reissue::c-reissue-portal",
        service_id="epassport-reissue",
        priority=1,
        claim_type="application_url",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_EPASSPORT_LANDING, E_DIP_HOME],
        evidence_excerpt="DIP links epassport.gov.bd; landing HTTP 200 (SPA).",
        reasoning="Re-issue entry on landing not readable in shell; official channel confirmed via DIP.",
        applicability="universal",
    )
    put(
        "epassport-reissue::c-show-previous-passport",
        service_id="epassport-reissue",
        priority=1,
        claim_type="conditional_document",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_NOTICE34_INDEX, E_DUBAI],
        evidence_excerpt="Notice 34: 'Previous Passport (if any)'; Dubai Category 1: current original MRP/e-Passport.",
        reasoning="Enrollment/previous passport requirement supported by notice index + Dubai live page.",
        applicability="conditional",
        condition={"field": "application_type", "op": "in", "value": ["reissue", "renewal"]},
    )
    put(
        "epassport-reissue::c-lost-gd-copy",
        service_id="epassport-reissue",
        priority=1,
        claim_type="conditional_document",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_EPASSPORT_INSTRUCTIONS_INDEX],
        evidence_excerpt="Indexed instructions reference GD for lost passport (research-phase citation).",
        reasoning=f"{SPA_PARTIAL} Lost-passport GD rule indexed on Tier-1 instructions; not directly snapshotted.",
        applicability="conditional",
        condition={"field": "application_type", "op": "eq", "value": "lost"},
    )
    put(
        "epassport-reissue::c-lost-gd-immediate",
        service_id="epassport-reissue",
        priority=2,
        claim_type="practical_tip",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_EPASSPORT_INSTRUCTIONS_INDEX],
        evidence_excerpt="Indexed instructions advise filing GD promptly when passport lost/damaged.",
        reasoning="Procedural advice indexed on Tier-1 URL; treat as official guidance pending direct capture.",
        applicability="lost_or_damaged",
    )
    put(
        "epassport-reissue::c-correction-extra-docs",
        service_id="epassport-reissue",
        priority=1,
        claim_type="conditional_document",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_NOTICE34_INDEX],
        evidence_excerpt="Notice 34 item 7: further documents depend on nature of application/corrections.",
        reasoning="Conditional correction docs explicitly deferred to case type in notice index.",
        applicability="conditional",
        condition={"field": "application_type", "op": "eq", "value": "correction"},
    )
    put(
        "epassport-reissue::c-mission-lost-report",
        service_id="epassport-reissue",
        priority=1,
        claim_type="conditional_document",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_DUBAI],
        evidence_excerpt="Dubai: lost e-passport/MRP with copy → 'lost report from the UAE police will be required'.",
        reasoning="Mission-specific lost report rule live-verified for Dubai/UAE context.",
        applicability="mission_specific",
        condition={"field": "applicant_location", "op": "eq", "value": "foreign_mission"},
    )
    put(
        "epassport-reissue::c-dubai-mrp-validity-limit",
        service_id="epassport-reissue",
        priority=1,
        claim_type="eligibility",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_DUBAI],
        evidence_excerpt=(
            "Dubai: e-Passport not accepted if existing MRP has more than one year validity remaining."
        ),
        reasoning="Live Dubai consulate page explicitly states MRP validity gate.",
        applicability="mission_specific",
        condition={"field": "applicant_location", "op": "eq", "value": "dubai_mission"},
    )
    put(
        "epassport-reissue::c-mission-biometric-presence",
        service_id="epassport-reissue",
        priority=1,
        claim_type="procedure_step",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_DUBAI, E_SINGAPORE_404],
        evidence_excerpt="Dubai: physical appearance mandatory except under 5 years old.",
        reasoning=(
            "Dubai live-verified under-5 exemption. Singapore source URL 404 — cannot verify Singapore-specific "
            "wording; do not merge into universal rule."
        ),
        applicability="mission_varying",
    )

    # --- epassport-fee-payment (fees OUTDATED pending fresher Tier-1 capture) ---
    fee_specs = [
        ("c-fee-48p-5y-regular", 4025, 48, 5),
        ("c-fee-48p-10y-regular", 5750, 48, 10),
        ("c-fee-64p-5y-regular", 6325, 64, 5),
        ("c-fee-64p-10y-regular", 8050, 64, 10),
    ]
    for legacy_id, amount, pages, years in fee_specs:
        put(
            f"epassport-fee-payment::{legacy_id}",
            service_id="epassport-fee-payment",
            priority=1,
            claim_type="fee",
            information_class="OFFICIAL",
            verification_status="OUTDATED",
            evidence=[E_EPASSPORT_FEES_INDEX],
            evidence_excerpt=f"Indexed official fee page (last updated 8 March 2023): regular BDT {amount} for {pages}p/{years}y incl VAT.",
            reasoning=(
                "Amount matches indexed excerpt of Tier-1 fee URL, but page last-updated date is March 2023 and "
                "no newer official fee gazette/notice superseding it was captured in this verification pass. "
                "Do not publish as current fee without fresh Tier-1 snapshot or calculator."
            ),
            applicability="domestic_regular_delivery",
            fee_metadata={
                "amount_bdt": amount,
                "currency": "BDT",
                "pages": pages,
                "validity_years": years,
                "delivery": "regular",
                "effective_date_status": "HISTORICAL_POSSIBLY_OUTDATED",
                "source_page_last_updated": "2023-03-08",
                "verification_date": "2026-08-24",
            },
            knowledge_gap="MISSING_CURRENT_EPASSPORT_FEE_TIER1_SNAPSHOT",
        )
    put(
        "epassport-fee-payment::c-fee-vat-included",
        service_id="epassport-fee-payment",
        priority=1,
        claim_type="fee",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_EPASSPORT_FEES_INDEX],
        evidence_excerpt="Indexed heading: 'fees for inside Bangladesh (Including 15% VAT)'.",
        reasoning="VAT inclusion stated on indexed Tier-1 fee page; direct page not captured.",
        applicability="domestic_fees",
    )
    put(
        "epassport-fee-payment::c-fee-mission-general-usd",
        service_id="epassport-fee-payment",
        priority=1,
        claim_type="fee",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_EPASSPORT_FEES_INDEX],
        evidence_excerpt="Indexed sections for Mission General Applicants USD tiers by pages/validity/delivery.",
        reasoning="Mission USD schedule structure indexed; individual amounts not independently snapshotted.",
        applicability="mission_general",
    )
    put(
        "epassport-fee-payment::c-fee-mission-labor-student-usd",
        service_id="epassport-fee-payment",
        priority=1,
        claim_type="fee",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_EPASSPORT_FEES_INDEX],
        evidence_excerpt="Indexed section: Mission Labors and Students separate USD table.",
        reasoning="Separate labor/student fee table referenced on indexed Tier-1 page; amounts not snapshotted.",
        applicability="mission_labor_student",
    )
    put(
        "epassport-fee-payment::c-payment-online-offline",
        service_id="epassport-fee-payment",
        priority=1,
        claim_type="payment_method",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_EPASSPORT_FEES_INDEX],
        evidence_excerpt="Indexed: fees paid online via gateways or offline via bank/A-Challan.",
        reasoning="Payment channel types indexed on Tier-1 fee page; gateway enumeration incomplete.",
        applicability="universal",
    )
    put(
        "epassport-fee-payment::c-payment-slip-offline-only",
        service_id="epassport-fee-payment",
        priority=1,
        claim_type="conditional_document",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_NOTICE34_INDEX],
        evidence_excerpt="Notice 34: 'Payment Slip for Offline Payment only'.",
        reasoning="Conditional payment slip rule in notice index; SPA not captured.",
        applicability="conditional",
        condition={"field": "payment_method", "op": "eq", "value": "offline"},
    )
    put(
        "epassport-fee-payment::c-practical-ekpay-mention",
        service_id="epassport-fee-payment",
        priority=3,
        claim_type="practical_tip",
        information_class="PRACTICAL",
        verification_status="VERIFIED",
        evidence=[E_PRACTICAL_QNA, E_EPASSPORT_FEES_INDEX],
        evidence_excerpt="Claim correctly scoped PRACTICAL; official index also names ekpay.",
        reasoning="PRACTICAL claim appropriately warns to confirm gateways; not promoted to MUST_NEED.",
        applicability="practical_only",
        do_not_promote_to_must=True,
    )
    put(
        "epassport-fee-payment::c-regular-delivery-sla",
        service_id="epassport-fee-payment",
        priority=1,
        claim_type="processing_time",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_EPASSPORT_FEES_INDEX],
        evidence_excerpt="Indexed: Regular delivery within 15 working days / 21 days from biometric enrolment.",
        reasoning="SLA wording indexed on fee page (March 2023 label); not live-snapshotted.",
        applicability="regular_delivery",
    )
    put(
        "epassport-fee-payment::c-payment-ekpay-official",
        service_id="epassport-fee-payment",
        priority=1,
        claim_type="payment_method",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_EPASSPORT_FEES_INDEX],
        evidence_excerpt="Indexed: online payment via ekpay platform; offline A-Challan at banks.",
        reasoning="ekpay named on indexed Tier-1 fee page; full gateway list not verified.",
        applicability="universal",
    )
    put(
        "epassport-fee-payment::c-mission-weff-surcharge",
        service_id="epassport-fee-payment",
        priority=1,
        claim_type="fee",
        information_class="OFFICIAL",
        verification_status="UNVERIFIED",
        evidence=[E_ABUDHABI_UNREACHABLE],
        evidence_excerpt="Abu Dhabi page cited in research; body not retrieved during verification.",
        reasoning="10% WEWB surcharge not independently confirmed; Abu Dhabi page content unavailable.",
        applicability="mission_specific",
        condition={"field": "applicant_location", "op": "eq", "value": "abudhabi_mission"},
        knowledge_gap="MISSING_ABUDHABI_MISSION_EPASSPORT_PAGE",
    )

    # --- enrollment ---
    put(
        "epassport-enrollment-appointment::c-appointment-required",
        service_id="epassport-enrollment-appointment",
        priority=1,
        claim_type="procedure_step",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_NOTICE34_INDEX],
        evidence_excerpt="Notice 34: printed application summary including appointment (if any).",
        reasoning="Appointment/summary requirement in notice index; biometric appointment mechanics not snapshotted.",
        applicability="enrollment_visit",
    )
    put(
        "epassport-enrollment-appointment::c-bring-original-id",
        service_id="epassport-enrollment-appointment",
        priority=1,
        claim_type="document",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_NOTICE34_INDEX, E_DUBAI],
        evidence_excerpt="Notice 34: original NID/Birth Certificate; Dubai requires original NID/BRC.",
        reasoning="Original ID at enrollment supported by notice index + Dubai live page.",
        applicability="enrollment_visit",
    )

    # --- status ---
    put(
        "epassport-application-status::c-status-portal",
        service_id="epassport-application-status",
        priority=1,
        claim_type="application_url",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_DIP_HOME, {"source_url": "https://www.epassport.gov.bd/authorization/application-status", "live_http_status": "not_tested_spa", "authority_tier": 1}],
        evidence_excerpt="Catalogue official URL; epassport portal family confirmed via DIP.",
        reasoning="Status route not independently tested (SPA); official URL from catalogue + DIP link family.",
        applicability="universal",
    )
    put(
        "epassport-application-status::c-status-oid-dob",
        service_id="epassport-application-status",
        priority=2,
        claim_type="eligibility",
        information_class="OFFICIAL",
        verification_status="UNVERIFIED",
        evidence=[{"source_url": "https://www.epassport.gov.bd/authorization/application-status", "authority_tier": 1, "retrieval_method": "spa_unread"}],
        evidence_excerpt="Research cited OID/DOB fields; SPA not readable.",
        reasoning="Input field requirements not captured from live or archived SPA.",
        applicability="universal",
        knowledge_gap="MISSING_EPASSPORT_STATUS_PORTAL_FIELDS",
    )

    # --- super express ---
    put(
        "epassport-urgent-super-express::c-super-express-2-days",
        service_id="epassport-urgent-super-express",
        priority=1,
        claim_type="processing_time",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_EPASSPORT_URGENT_INDEX, E_EPASSPORT_FEES_INDEX],
        evidence_excerpt="Urgent index: issued within 2 working days; fee index: Super Express delivery 2 working days from enrolment.",
        reasoning="2-day SLA indexed on official urgent + fee pages (Oct 2022 / Mar 2023 labels); SPA not captured.",
        applicability="conditional_super_express",
    )
    put(
        "epassport-urgent-super-express::c-super-express-domestic-only",
        service_id="epassport-urgent-super-express",
        priority=1,
        claim_type="restriction",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_EPASSPORT_URGENT_INDEX],
        evidence_excerpt="Indexed: 'This service is not available in Bangladesh Missions'.",
        reasoning="Mission exclusion indexed on urgent page; not directly snapshotted.",
        applicability="domestic_only",
    )
    put(
        "epassport-urgent-super-express::c-super-express-pickup-agargaon",
        service_id="epassport-urgent-super-express",
        priority=1,
        claim_type="office",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_EPASSPORT_URGENT_INDEX],
        evidence_excerpt="Indexed pickup: Divisional Passport and Visa Office, Agargaon, Dhaka-1207.",
        reasoning="Agargaon-only pickup indexed on urgent page.",
        applicability="super_express_collection",
    )
    put(
        "epassport-urgent-super-express::c-super-express-mrp-no-address-change",
        service_id="epassport-urgent-super-express",
        priority=1,
        claim_type="eligibility",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_EPASSPORT_URGENT_INDEX],
        evidence_excerpt=(
            "Indexed NOTE: Super Express currently for e-Passport issuance where applicant already holds MRP "
            "without changing permanent address."
        ),
        reasoning=(
            "Conflict #1 resolved as conditional eligibility (see conflicts_resolution.json). "
            "Headline 'any citizen' vs NOTE is applicant-path distinction, not publishable universal rule."
        ),
        applicability="conditional",
        condition={
            "field": "super_express_eligibility",
            "op": "requires",
            "value": "existing_mrp_no_permanent_address_change",
        },
        conflict_id="conflict-super-express-eligibility",
        conflict_classification="resolved_conditional_paths",
    )
    put(
        "epassport-urgent-super-express::c-super-express-fee-tier",
        service_id="epassport-urgent-super-express",
        priority=1,
        claim_type="fee",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_EPASSPORT_FEES_INDEX, E_EPASSPORT_URGENT_INDEX],
        evidence_excerpt="Indexed fee tables include Super Express delivery tier alongside Regular/Express.",
        reasoning="Fee tier existence supported; specific super-express amounts marked OUTDATED separately.",
        applicability="super_express_delivery",
    )

    # --- rpo secretariat ---
    put(
        "epassport-rpo-secretariat::c-rpo-secretariat-form",
        service_id="epassport-rpo-secretariat",
        priority=2,
        claim_type="application_url",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_EPASSPORT_LANDING],
        evidence_excerpt="Landing references ./instructions/application-form for RPO Bangladesh Secretariat.",
        reasoning="Secretariat guidance route linked from landing; page body not captured (SPA).",
        applicability="rpo_secretariat_applicants",
    )

    # --- MRP (live Tier-1 HTML) ---
    put(
        "passport-mrp-initial::c-mrp-form1",
        service_id="passport-mrp-initial",
        priority=1,
        claim_type="application_url",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_MRP_HOME, E_DIP_HOME],
        evidence_excerpt="MRP portal menu: DIP Form 1 Primary/Initial Application; DIP links passport.gov.bd.",
        reasoning="Live MRP portal and DIP both confirm Form 1 initial channel operational.",
        applicability="mrp_initial",
    )
    put(
        "passport-mrp-initial::c-mrp-email-credentials",
        service_id="passport-mrp-initial",
        priority=2,
        claim_type="procedure_step",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_MRP_HOME],
        evidence_excerpt="After first page save, email contains Application ID and Password.",
        reasoning="Explicit English instruction bullet on live MRP home page.",
        applicability="mrp_online_apply",
    )
    put(
        "passport-mrp-initial::c-mrp-biometric-visit",
        service_id="passport-mrp-initial",
        priority=1,
        claim_type="procedure_step",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_MRP_HOME],
        evidence_excerpt="Report to Passport Office for biometric data with printed Online Application form.",
        reasoning="Live MRP portal instruction.",
        applicability="post_online_submit",
    )
    put(
        "passport-mrp-initial::c-mrp-govt-single-form",
        service_id="passport-mrp-initial",
        priority=1,
        claim_type="conditional_document",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_MRP_HOME],
        evidence_excerpt="Bangla bullet: govt/retired/surrendered categories one form; others two copies for new passport.",
        reasoning="Live Bangla instruction on MRP home distinguishes form copy count by category.",
        applicability="conditional",
        condition={"field": "applicant_category", "op": "in", "value": ["government", "retired_government", "surrendered"]},
    )
    put(
        "passport-mrp-initial::c-mrp-attested-copies",
        service_id="passport-mrp-initial",
        priority=1,
        claim_type="document",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_MRP_HOME],
        evidence_excerpt="Bangla bullet 3: attested photocopies of NID/BRC and relevant certificates required for MRP.",
        reasoning="Live MRP portal explicitly requires attestation — contrasts with e-Passport no-attestation rule.",
        applicability="mrp_pathway",
    )
    put(
        "passport-mrp-initial::c-mrp-appointment-validity",
        service_id="passport-mrp-initial",
        priority=2,
        claim_type="processing_time",
        information_class="OFFICIAL",
        verification_status="REJECTED",
        evidence=[E_MRP_HOME, E_MRP_USERHOME],
        evidence_excerpt="Live MRP: 'application shall remain valid for 15 days from the date of submission' — not 5 days.",
        reasoning="Claim states 5 days; live portal states 15 days. Wrong duration and wrong source attribution.",
        applicability="mrp_online_submit",
    )
    put(
        "passport-mrp-reissue::c-mrp-form2",
        service_id="passport-mrp-reissue",
        priority=1,
        claim_type="application_url",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_MRP_USERHOME],
        evidence_excerpt="UserHome lists DIP Form 2 Reissue/Correction/Alternation for MRP.",
        reasoning="Live MRP UserHome confirms Form 2 channel.",
        applicability="mrp_reissue_correction",
    )
    put(
        "passport-application-status::c-mrp-status-portal",
        service_id="passport-application-status",
        priority=1,
        claim_type="application_url",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_MRP_STATUS],
        evidence_excerpt="OnlineStatus.aspx live; nav 'Application Status'; Application ID input present.",
        reasoning="Live status portal reachable and matches claim URL.",
        applicability="mrp_applications",
    )

    # --- police verification ---
    put(
        "police-passport-police-verification::c-pv-pathway-exists",
        service_id="police-passport-police-verification",
        priority=1,
        claim_type="availability",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_DUBAI, E_POLICE_CHARTER, E_DIP_HOME],
        evidence_excerpt=(
            "Police charter row 5: Passport verification via DSB/SB; "
            "Dubai: first-time e-Passport police verification mandatory in Bangladesh."
        ),
        reasoning=(
            "PV pathway exists per citizen charter and Dubai mission. Universal requirement for all "
            "e-Passport applicants NOT verified — Dubai states first-time only; Feb 2025 policy changes "
            "reported in news but no Tier-1 circular captured here."
        ),
        applicability="pathway_exists_not_universal_requirement",
        knowledge_gap="MISSING_TIER1_PV_REQUIREMENT_RULE_2025",
    )
    put(
        "police-passport-police-verification::c-pv-station-onboarding",
        service_id="police-passport-police-verification",
        priority=2,
        claim_type="procedure_step",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_EPASSPORT_ONBOARDING],
        evidence_excerpt="Indexed onboarding selects nearest police station to present address.",
        reasoning="Police station selection indexed; onboarding not readable live.",
        applicability="domestic_epassport_onboarding",
    )
    put(
        "police-passport-police-verification::c-pv-delay-note",
        service_id="police-passport-police-verification",
        priority=3,
        claim_type="practical_tip",
        information_class="PRACTICAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_DUBAI],
        evidence_excerpt="Dubai: delivery depends on police verification process for first-time applications.",
        reasoning="PRACTICAL timing impact supported by mission text; not an official SLA.",
        applicability="practical_only",
        do_not_promote_to_must=True,
    )
    put(
        "police-passport-verification::c-pv-charter-sla",
        service_id="police-passport-verification",
        priority=1,
        claim_type="processing_time",
        information_class="DISCOVERY",
        verification_status="VERIFIED",
        evidence=[E_POLICE_CHARTER],
        evidence_excerpt="Citizen charter service 5 Passport verification: normal 15-21 days; urgent 7 days.",
        reasoning="Live citizen charter table row explicitly states passport verification SLAs.",
        applicability="police_verification_service_charter",
    )
    put(
        "police-passport-verification::c-pv-district-scope",
        service_id="police-passport-verification",
        priority=2,
        claim_type="office",
        information_class="DISCOVERY",
        verification_status="VERIFIED",
        evidence=[E_POLICE_CHARTER],
        evidence_excerpt="Charter row 5: responsible units District/National SB; service 'Passport verification'.",
        reasoning="District/SB scope live-verified in citizen charter.",
        applicability="police_verification_service",
    )

    return R


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
        has_outdated_fee = any(s == "OUTDATED" for s in high_stat)
        has_rejected = any(s == "REJECTED" for s in statuses)
        high_verified = sum(1 for s in high_stat if s == "VERIFIED")
        high_bad = sum(
            1
            for s in high_stat
            if s in {"UNVERIFIED", "CONFLICTING", "REJECTED", "OUTDATED"}
        )

        if sid == "epassport-fee-payment" or has_outdated_fee:
            color = "RED"
            reason = "Critical fee amounts OUTDATED or only index-excerpt sourced; not safe for authoritative fee publication."
        elif sid in {"passport-mrp-initial", "passport-application-status"} and high_verified >= 2 and not has_rejected:
            color = "GREEN"
            reason = "MRP portal claims live-verified against Tier-1 HTML."
        elif sid == "passport-mrp-initial" and has_rejected:
            color = "YELLOW"
            reason = "Core MRP portal facts verified; one REJECTED claim (5-day validity error)."
        elif sid == "passport-mrp-reissue":
            color = "YELLOW"
            reason = "Form 2 URL verified; reissue/lost/damaged document matrix incomplete."
        elif sid == "police-passport-verification" and high_verified >= 1:
            color = "YELLOW"
            reason = "Charter SLAs verified; linkage to e-Passport universal PV requirement not established."
        elif sid == "police-passport-police-verification":
            color = "YELLOW"
            reason = "PV pathway partially corroborated; universal requirement and SB procedure page missing."
        elif sid.startswith("epassport-") and high_bad > 0:
            color = "YELLOW"
            reason = "e-Passport claims rely on SPA/index excerpts; material gaps on fees, status fields, or mission rules."
        elif high_bad == 0 and high_verified >= max(1, len(high) // 2):
            color = "GREEN"
            reason = "Critical claims largely verified with Tier 1–2 evidence."
        elif any(s in {"VERIFIED", "PARTIALLY_VERIFIED"} for s in statuses):
            color = "YELLOW"
            reason = "Useful partial verification; gaps remain."
        else:
            color = "RED"
            reason = "Important facts unresolved."

        if sid == "passport-mrp-initial":
            color = "YELLOW" if has_rejected else "GREEN"

        readiness[sid] = {
            "service_id": sid,
            "readiness": color,
            "claim_count": len(items),
            "status_counts": dict(Counter(statuses)),
            "reason": reason,
            "manual_review_recommended": color != "GREEN",
        }
    return readiness


def build_conflicts() -> list[dict]:
    return [
        {
            "conflict_id": "conflict-super-express-eligibility",
            "resolution_status": "RESOLVED",
            "classification": "conditional_applicant_paths_not_contradiction",
            "outcome": (
                "Urgent page headline allows any citizen to apply for Super Express delivery type, but NOTE "
                "restricts current operational availability to existing MRP holders not changing permanent address. "
                "Represent as IF existing_mrp AND NOT permanent_address_change THEN super_express_available."
            ),
            "blocks_official_publication": False,
        },
        {
            "conflict_id": "conflict-mrp-vs-epassport-primary",
            "resolution_status": "RESOLVED",
            "classification": "transitional_dual_channel",
            "outcome": (
                "DIP home (live Tier-1) lists BOTH 'ই-পাসপোর্ট আবেদন' (epassport.gov.bd) and "
                "'অনলাইন এমআরপি আবেদন' (passport.gov.bd) as active internal e-services. "
                "e-Passport is primary/current for new biometric passports; MRP portal remains operational (legacy channel). "
                "Do not collapse to single channel."
            ),
            "blocks_official_publication": False,
        },
        {
            "conflict_id": "conflict-fee-freshness",
            "resolution_status": "PARTIALLY_RESOLVED",
            "classification": "historical_fee_page_no_superseding_doc_found",
            "outcome": (
                "Tier-1 fee page last updated 8 March 2023 per indexed metadata. No newer official fee gazette, "
                "notice, or machine-readable fee snapshot captured in verification pass. Domestic BDT amounts marked "
                "OUTDATED; fee tier structure PARTIALLY_VERIFIED via index excerpt only."
            ),
            "blocks_official_publication": True,
        },
    ]


def build_gaps(enriched: list[dict], raw_gaps: list[dict]) -> list[dict]:
    gaps = {g["gap_id"]: g for g in raw_gaps}
    for x in enriched:
        g = x.get("knowledge_gap")
        if g and g not in gaps:
            gaps[g] = {
                "gap_id": g,
                "classification": "verification_discovered",
                "priority": "HIGH",
                "status": "OPEN",
                "related_claims": [],
                "description": "Identified during Batch 2A independent verification.",
            }
        if g:
            gaps[g].setdefault("related_claims", [])
            if x["claim_id"] not in gaps[g]["related_claims"]:
                gaps[g]["related_claims"].append(x["claim_id"])
    return list(gaps.values())


def write_docs(summary: dict, readiness: dict, conflicts: list[dict], gaps: list[dict]) -> None:
    green = [k for k, v in readiness.items() if v["readiness"] == "GREEN"]
    yellow = [k for k, v in readiness.items() if v["readiness"] == "YELLOW"]
    red = [k for k, v in readiness.items() if v["readiness"] == "RED"]
    lines = [
        "# Batch 2A — Independent Claim Verification (Passport Services)",
        "",
        f"**Date:** 2026-08-24  ",
        f"**Verifier:** `{VERIFIER}`  ",
        "**Layer:** `data/research/verification/batch-02a-passport` (STAGING ONLY)  ",
        "**Published to runtime:** No  ",
        "**publish_verified_knowledge.py run:** No",
        "",
        "## Policy used",
        "",
        "- High-risk OFFICIAL claims require Tier 1–2 explicit support; search-index excerpts alone → PARTIAL/OUTDATED, not VERIFIED.",
        "- epassport.gov.bd instructional pages are Angular SPAs; live/Wayback returned shells without instructional text.",
        "- Conditional requirements stay conditional.",
        "- PRACTICAL never promoted to MUST_NEED.",
        "- See `data/research/verification/batch-02a-passport/verification_policy.json`.",
        "",
        "## Totals",
        "",
        f"1. Total claims: **{summary['total_claims']}**",
        f"2. VERIFIED: **{summary['status_counts'].get('VERIFIED', 0)}**",
        f"3. PARTIALLY_VERIFIED: **{summary['status_counts'].get('PARTIALLY_VERIFIED', 0)}**",
        f"4. UNVERIFIED: **{summary['status_counts'].get('UNVERIFIED', 0)}**",
        f"5. CONFLICTING: **{summary['status_counts'].get('CONFLICTING', 0)}**",
        f"6. OUTDATED: **{summary['status_counts'].get('OUTDATED', 0)}**",
        f"7. REJECTED: **{summary['status_counts'].get('REJECTED', 0)}**",
        f"8. Official claims verified: **{summary['official_claims_verified']}**",
        f"9. Practical claims: **{summary['practical_claims']}**",
        f"10. Resolved conflicts: **{summary['conflicts_resolved']}**",
        f"11. Unresolved conflicts: **{summary['conflicts_unresolved']}**",
        f"12. Knowledge gaps: **{summary['knowledge_gaps_open']}**",
        f"13. GREEN services: **{summary['services_green']}**",
        f"14. YELLOW services: **{summary['services_yellow']}**",
        f"15. RED services: **{summary['services_red']}**",
        "",
        "## Evidence limitations",
        "",
        summary["evidence_coverage_notes"],
        "",
        "## Conflict outcomes",
        "",
    ]
    for c in conflicts:
        lines.append(f"- `{c['conflict_id']}` — **{c['resolution_status']}**: {c['outcome']}")
    lines.extend(["", "## Service readiness", "", "### GREEN"])
    for s in green:
        lines.append(f"- `{s}` — {readiness[s]['reason']}")
    lines.extend(["", "### YELLOW"])
    for s in yellow:
        lines.append(f"- `{s}` — {readiness[s]['reason']}")
    lines.extend(["", "### RED"])
    for s in red:
        lines.append(f"- `{s}` — {readiness[s]['reason']}")
    lines.extend(["", "## Knowledge gaps", ""])
    for g in gaps:
        if g.get("status", "OPEN") == "OPEN":
            lines.append(f"- `{g['gap_id']}` — {g.get('description', g.get('classification', ''))}")
    lines.extend(
        [
            "",
            "## Explicit non-actions",
            "",
            "- Did not publish claims",
            "- Did not start Batch 2B",
            "- Did not deploy",
            "- Did not modify frontend",
            "",
            "## Machine-readable outputs",
            "",
            "- `data/research/verification/batch-02a-passport/claims_verification.json`",
            "- `data/research/verification/batch-02a-passport/conflicts_resolution.json`",
            "- `data/research/verification/batch-02a-passport/knowledge_gaps.json`",
            "- `data/research/verification/batch-02a-passport/service_readiness.json`",
            "- `data/research/verification/batch-02a-passport/summary.json`",
            "- `data/research/verification/batch-02a-passport/verification_policy.json`",
            "- `data/research/verification/batch-02a-passport/source_evidence.json`",
            "",
        ]
    )
    DOCS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
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
                "condition": r.get("condition") or c.get("condition"),
                "applicability": r.get("applicability"),
                "fee_metadata": r.get("fee_metadata"),
                "conflict_id": r.get("conflict_id"),
                "conflict_classification": r.get("conflict_classification"),
                "knowledge_gap": r.get("knowledge_gap"),
                "do_not_promote_to_must": r.get("do_not_promote_to_must", False),
                "verifier": r["verifier"],
                "verified_at": r["verified_at"],
                "publication_status": "STAGING_ONLY",
            }
        )

    status_counts = Counter(x["verification_status"] for x in enriched)
    official_verified = sum(
        1
        for x in enriched
        if x["information_class"] == "OFFICIAL" and x["verification_status"] == "VERIFIED"
    )
    conflicts = build_conflicts()
    gaps = build_gaps(enriched, raw_gaps)
    readiness = service_readiness(claims, results)
    color_counts = Counter(v["readiness"] for v in readiness.values())

    policy = {
        "version": "1.0",
        "batch_id": "batch-02a-passport",
        "verified_at": VERIFIED_AT,
        "rules": {
            "high_risk_official": {
                "preferred_tiers": [1, 2],
                "require_explicit_support": True,
                "search_index_excerpt_not_equal_to_direct_page": True,
                "spa_shell_not_equal_to_instruction_text": True,
                "verdict_if_only_index_excerpt": ["PARTIALLY_VERIFIED", "OUTDATED", "UNVERIFIED"],
            },
            "fee_freshness": {
                "outdated_if_source_older_than_verification_without_superseding_doc": True,
                "do_not_publish_stale_amounts_as_current": True,
            },
            "mission_rules": {
                "no_merge_dubai_singapore_abudhabi_without_evidence": True,
            },
            "publication": "STAGING_ONLY — do not run publish_verified_knowledge.py",
        },
    }

    summary = {
        "batch_id": "batch-02a-passport",
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
            "Live Tier-1 HTML: passport.gov.bd (MRP), dip.gov.bd (dual e-Passport+MRP links), "
            "police.gov.bd citizen charter (passport verification SLAs). "
            "Live Tier-2: bcgdubai.gov.bd/e-passport/ (mission rules). "
            "epassport.gov.bd landing HTTP 200 but instructional routes are Angular SPA shells; "
            "onboarding returned 403; Wayback captures also SPA-only. "
            "Fee/instruction/urgent/enrollment claims rely on search-index excerpts of official URLs — "
            "explicitly NOT treated as direct page evidence. "
            "Singapore e-passport rules URL returned 404. Abu Dhabi page body not retrieved."
        ),
        "verification_coverage": f"{len(enriched)}/{len(enriched)} claims assigned a primary verification status",
        "main_limitations": [
            "Cannot render epassport.gov.bd instructional text via curl/Wayback",
            "Domestic fee BDT amounts marked OUTDATED (fee page March 2023)",
            "No claims published to runtime",
            "Police verification universal requirement post-2025 not Tier-1 confirmed",
        ],
    }

    source_evidence = {
        "snapshots_dir": "data/research/verification/batch-02a-passport/source_snapshots/",
        "url_checks": {
            "https://epassport.gov.bd/landing": 200,
            "https://www.epassport.gov.bd/onboarding": 403,
            "http://passport.gov.bd/": 200,
            "http://passport.gov.bd/OnlineStatus.aspx": 200,
            "https://www.dip.gov.bd/": 200,
            "https://bcgdubai.gov.bd/e-passport/": 200,
            "https://singapore.mofa.gov.bd/en/site/page/E-passport-application-rules": 404,
        },
    }

    (OUT / "verification_policy.json").write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
    (OUT / "claims_verification.json").write_text(
        json.dumps({"schema": "bda.research.verification.claims/1.0", "batch_id": "batch-02a-passport", "claims": enriched}, indent=2, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    (OUT / "conflicts_resolution.json").write_text(json.dumps({"conflicts": conflicts}, indent=2) + "\n", encoding="utf-8")
    (OUT / "knowledge_gaps.json").write_text(json.dumps({"knowledge_gaps": gaps}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT / "service_readiness.json").write_text(json.dumps({"services": readiness}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (OUT / "source_evidence.json").write_text(json.dumps(source_evidence, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(
        "# Batch 2A verification artifacts (STAGING ONLY)\n\nDo not publish without publish gate.\n",
        encoding="utf-8",
    )

    write_docs(summary, readiness, conflicts, gaps)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
