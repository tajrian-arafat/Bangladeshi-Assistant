#!/usr/bin/env python3
"""Independent Batch 1 claim verification (staging only — does not publish).

Writes:
  data/research/verification/batch-01/claims_verification.json
  data/research/verification/batch-01/conflicts_resolution.json
  data/research/verification/batch-01/knowledge_gaps.json
  data/research/verification/batch-01/service_readiness.json
  data/research/verification/batch-01/summary.json
  data/research/verification/batch-01/verification_policy.json
  docs/research/batch-01-independent-verification.md

Does NOT mark runtime DB claims VERIFIED and does NOT run publish.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STAGING = REPO / "data/research/staging/batch-01"
OUT = REPO / "data/research/verification/batch-01"
DOCS = REPO / "docs/research/batch-01-independent-verification.md"

VERIFIER = "cursor-cloud-agent"
VERIFIED_AT = datetime.now(timezone.utc).isoformat()

# Verification primary states (staging). PARTIALLY_VERIFIED is verification-layer.
STATES = {
    "VERIFIED",
    "PARTIALLY_VERIFIED",
    "CONFLICTING",
    "OUTDATED",
    "UNVERIFIED",
    "REJECTED",
}


def V(**kwargs):
    """Build a verification record."""
    status = kwargs["verification_status"]
    assert status in STATES, status
    return {
        "verifier": VERIFIER,
        "verified_at": VERIFIED_AT,
        "publication_status": "STAGING_ONLY",
        "do_not_publish_yet": True,
        **kwargs,
    }


def load_claims():
    return json.loads((STAGING / "claims.json").read_text(encoding="utf-8"))["claims"]


def build_results() -> dict[str, dict]:
    """Claim-id → verification decision. Evidence inspected 2026-08-24."""

    # Shared evidence refs
    E_NID_FAQ = {
        "source_id": "src-nid-faq",
        "source_url": "https://services.nidw.gov.bd/nid-pub/faq?locale=en",
        "authority_tier": 1,
        "retrieved_live_at": "2026-08-24",
        "snapshot": "data/research/verification/batch-01/source_snapshots/nid_faq.txt",
        "live_http_status": 200,
    }
    E_NID_FEES = {
        "source_id": "src-nid-fees",
        "source_url": "https://services.nidw.gov.bd/nid-pub/fees",
        "authority_tier": 1,
        "retrieved_live_at": "2026-08-24",
        "snapshot": "data/research/verification/batch-01/source_snapshots/nid_fees.txt",
        "live_http_status": 200,
    }
    E_BDRIS = {
        "source_id": "src-bdris-home",
        "source_url": "https://www.bdris.gov.bd/",
        "authority_tier": 1,
        "retrieved_live_at": "2026-08-24",
        "snapshot": "data/research/verification/batch-01/source_snapshots/bdris_www.txt",
        "live_http_status": 200,
    }
    E_EVERIFY = {
        "source_id": "src-everify",
        "source_url": "https://everify.bdris.gov.bd/",
        "authority_tier": 1,
        "retrieved_live_at": "2026-08-24",
        "live_http_status": 200,
        "evidence_location": "page title/body: Birth and Death Verification; BRN+DOB form",
    }
    E_ORGBDR_FEE = {
        "source_id": "src-orgbdr-fee-page",
        "source_url": "https://orgbdr.gov.bd/pages/static-pages/69cf48059d736d71f1a34c8c",
        "authority_tier": 1,
        "responsible_body": "Office of the Registrar General (ORGBDR) / LGD",
        "retrieved_via": "Wayback Machine capture 2026-04-05 (live origin unreachable from verifier network)",
        "wayback_url": "https://web.archive.org/web/20260405044343/https://orgbdr.gov.bd/pages/static-pages/69cf48059d736d71f1a34c8c",
        "content_updated_label": "শনিবার, ৪ এপ্রিল, ২০২৬",
        "snapshot": "data/research/verification/batch-01/source_snapshots/orgbdr_fee_wb.txt",
    }
    E_MOFA = {
        "source_id": "src-mofa-ankara-bdr",
        "source_url": "https://www.ankara.mofa.gov.bd/en/site/page/Birth--and-Death-Registration--English-",
        "authority_tier": 2,
        "retrieved_via": "Wayback 2023-06-08 (live mission host unreachable)",
        "cites": "LGD letter No-46.04.0000.101.22.001.21-278 dated 22 Feb 2023",
        "snapshot": "data/research/verification/batch-01/source_snapshots/mofa_wb.txt",
    }
    E_MUSLIM_ACT = {
        "source_id": "src-law-muslim-marriage",
        "source_url": "http://bdlaws.minlaw.gov.bd/act-details-476.html",
        "authority_tier": 1,
        "retrieved_live_at": "2026-08-24",
        "live_http_status": 200,
        "snapshot": "data/research/verification/batch-01/source_snapshots/law_muslim.txt",
    }
    E_MARRIAGE = {
        "source_id": "src-marriage-portal",
        "source_url": "https://marriage.gov.bd/",
        "authority_tier": 1,
        "retrieved_live_at": "2026-08-24",
        "live_http_status": 200,
        "notes": "Next.js shell loaded; title CRVS Marriage & Divorce",
    }
    E_MANUAL = {
        "source_id": "src-marriage-manual",
        "source_url": "https://marriage.gov.bd/docs/CRVS_User_Manual.pdf",
        "authority_tier": 1,
        "retrieved_live_at": "2026-08-24",
        "live_http_status": 200,
        "notes": "PDF 20 pages; registrar-use manual covering marriage/divorce portal workflows",
    }
    E_SIB = {
        "source_id": "src-sib-nid-fees",
        "source_url": "https://ssitbari.com/ec-new-nid-correction-fee-bangladesh/",
        "authority_tier": 5,
        "retrieved_live_at": "2026-08-24",
        "live_http_status": 200,
    }
    E_LEGAL = {
        "source_id": "src-legalclarity-birth",
        "source_url": "https://legalclarity.org/bangladesh-birth-certificate-registration-and-verification/",
        "authority_tier": 6,
        "retrieved_live_at": "2026-08-24",
        "live_http_status": 200,
    }

    R: dict[str, dict] = {}

    def put(claim_id: str, **kw):
        R[claim_id] = V(claim_id=claim_id, **kw)

    # ---------- BDRIS / civil registration fees (Priority 1) ----------
    put(
        "civil-birth-registration::c-br-fee-free45",
        service_id="civil-birth-registration",
        priority=1,
        claim_type="fee",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_ORGBDR_FEE, E_MOFA],
        evidence_excerpt_bn="১। জন্ম বা মৃত্যুর ৪৫ দিন পর্যন্ত … বিনা ফিসে",
        reasoning=(
            "ORGBDR Tier-1 fee page (Wayback 2026-04-05, content marked updated 4 Apr 2026) "
            "explicitly states free registration within 45 days. MOFA Tier-2 mission notice "
            "citing LGD letter matches. No material contradiction found in Tier 1–2 sources. "
            "No separate 10-year fee tier appears on the official schedule."
        ),
        applicability="universal_for_service_variant",
        condition=None,
    )
    put(
        "civil-birth-registration::c-br-fee-late",
        service_id="civil-birth-registration",
        priority=1,
        claim_type="fee",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_ORGBDR_FEE, E_MOFA],
        evidence_excerpt_bn="২। …৪৫ দিন পর হইতে ৫ বৎসর… ২৫ টাকা; ৩। …৫ বৎসর পর… ৫০ টাকা",
        reasoning=(
            "ORGBDR Tier-1 schedule states domestic BDT 25 (after 45 days to 5 years) and "
            "BDT 50 (after 5 years). MOFA notice adds abroad USD 1 for those bands. "
            "Claim's domestic+abroad structure is supported. Conflict with secondary BDT 500 "
            "after 10 years is treated separately — official schedule has no 10-year tier."
        ),
        applicability="conditional_on_days_since_event_and_location",
        fee_rules=[
            {"when": "45d < age <= 5y", "domestic_bdt": 25, "abroad_usd": 1},
            {"when": "age > 5y", "domestic_bdt": 50, "abroad_usd": 1},
        ],
    )
    put(
        "civil-birth-registration::c-br-fee-conflict-500",
        service_id="civil-birth-registration",
        priority=1,
        claim_type="fee",
        information_class="PRACTICAL",
        verification_status="REJECTED",
        evidence=[E_ORGBDR_FEE, E_LEGAL],
        reasoning=(
            "Secondary guide claim of BDT 500 after 10 years is NOT supported by ORGBDR Tier-1 "
            "fee schedule (only free / 25 / 50 tiers). Classified as secondary misstatement / "
            "outdated guide, not an official fee variant. Do not publish as OFFICIAL."
        ),
        conflict_id="conf-br-fee-10y",
        conflict_classification="secondary_error_vs_official_schedule",
    )
    put(
        "civil-birth-registration-copy::c-copy-fee",
        service_id="civil-birth-registration-copy",
        priority=1,
        claim_type="fee",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_ORGBDR_FEE, E_MOFA],
        evidence_excerpt_bn="৭। বাংলা ও ইংরেজি উভয় ভাষায় সনদের নকল সরবরাহ ৫০ টাকা",
        reasoning=(
            "ORGBDR item 7: duplicate certificate copy BDT 50 domestic. MOFA lists "
            "copy issuance TK 50 / USD 1 abroad. Original issuance after correction is free "
            "domestically (item 6) — claim's dual structure matches."
        ),
    )
    put(
        "civil-birth-registration-correction::c-corr-fee-dob",
        service_id="civil-birth-registration-correction",
        priority=1,
        claim_type="fee",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_ORGBDR_FEE, E_MOFA],
        evidence_excerpt_bn="৪। জন্ম তারিখ সংশোধনের জন্য আবেদন ফি - ১০০ টাকা",
        reasoning="ORGBDR Tier-1 explicitly: DOB correction application fee BDT 100 (abroad USD 2 per MOFA).",
    )
    put(
        "civil-birth-registration-correction::c-corr-fee-other",
        service_id="civil-birth-registration-correction",
        priority=1,
        claim_type="fee",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_ORGBDR_FEE, E_MOFA],
        evidence_excerpt_bn="৫। জন্ম তারিখ ব্যতীত … অন্যান্য তথ্য সংশোধনের জন্য আবেদন ফি - ৫০ টাকা",
        reasoning=(
            "ORGBDR Tier-1 explicitly distinguishes other-info correction at BDT 50 from DOB at 100. "
            "Secondary blogs claiming 100 for other corrections conflict with Tier-1; prefer ORGBDR."
        ),
        conflict_id="conf-bdris-corr-other-fee",
        conflict_classification="resolved_prefer_tier1_other_fee_50",
    )
    put(
        "civil-death-registration::c-dr-fees",
        service_id="civil-death-registration",
        priority=1,
        claim_type="fee",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_ORGBDR_FEE, E_MOFA],
        reasoning="ORGBDR/MOFA schedule applies jointly to birth OR death registration fee tiers.",
    )
    put(
        "civil-death-registration-copy::c-copy-fee",
        service_id="civil-death-registration-copy",
        priority=1,
        claim_type="fee",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_ORGBDR_FEE, E_MOFA],
        reasoning="Same ORGBDR item 7 duplicate-copy fee applies to death certificates.",
    )
    put(
        "civil-death-registration-correction::c-corr-fee-dob",
        service_id="civil-death-registration-correction",
        priority=1,
        claim_type="fee",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_ORGBDR_FEE],
        reasoning=(
            "ORGBDR schedule labels item 4 as 'জন্ম তারিখ সংশোধন' (birth-date correction). "
            "Death-record correction fee for date fields is not separately labeled on the same "
            "page; applying the DOB line to death corrections is reasonable but not explicitly "
            "worded for death. Keep partial until death-specific wording confirmed."
        ),
        knowledge_gap="MISSING_DEATH_CORRECTION_FEE_WORDING",
    )
    put(
        "civil-death-registration-correction::c-corr-fee-other",
        service_id="civil-death-registration-correction",
        priority=1,
        claim_type="fee",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_ORGBDR_FEE, E_MOFA],
        reasoning=(
            "ORGBDR item 5 covers correction of name/parents/address etc. other than date of birth "
            "at BDT 50; applies across the civil registration fee schedule."
        ),
        conflict_id="conf-bdris-corr-other-fee",
        conflict_classification="resolved_prefer_tier1_other_fee_50",
    )

    # ---------- NID fees ----------
    for sid, cid_exists, cid_news, conf in [
        (
            "nid-card-info-correction",
            "nid-card-info-correction::c-nid-card-info-correction-fee-exists",
            "nid-card-info-correction::c-nid-card-info-correction-fee-amount-news",
            "conf-nid-card-info-correction-fee-amount",
        ),
        (
            "nid-combined-correction",
            "nid-combined-correction::c-nid-combined-correction-fee-exists",
            "nid-combined-correction::c-nid-combined-correction-fee-amount-news",
            "conf-nid-combined-correction-fee-amount",
        ),
        (
            "nid-other-info-correction",
            "nid-other-info-correction::c-nid-other-info-correction-fee-exists",
            "nid-other-info-correction::c-nid-other-info-correction-fee-amount-news",
            "conf-nid-other-info-correction-fee-amount",
        ),
    ]:
        put(
            cid_exists,
            service_id=sid,
            priority=1,
            claim_type="fee",
            information_class="OFFICIAL",
            verification_status="VERIFIED",
            evidence=[E_NID_FEES, E_NID_FAQ],
            evidence_excerpt=(
                "Fee calculator page lists application types including card correction / other / "
                "combined / reissue; FAQ states fees apply for lost-card reprint and points to calculator."
            ),
            reasoning=(
                "Tier-1 fee calculator confirms fees are payable and must be calculated in-portal. "
                "No static official amount schedule was retrieved from Tier 1–2 — do not hardcode amounts."
            ),
            conflict_id=conf,
        )
        put(
            cid_news,
            service_id=sid,
            priority=1,
            claim_type="fee",
            information_class="PRACTICAL",
            verification_status="UNVERIFIED",
            evidence=[E_SIB, E_NID_FEES],
            reasoning=(
                "News/blog cites VAT-inclusive BDT 230/345/460 tiers, but official Tier-1 surface "
                "only exposes a calculator without publishing those static amounts. "
                "High-risk fee amounts cannot be promoted to OFFICIAL/VERIFIED from Tier 5 alone."
            ),
            conflict_id=conf,
            conflict_classification="unresolved_static_amounts_vs_official_calculator",
            knowledge_gap="MISSING_OFFICIAL_NID_FEE_SCHEDULE_STATIC",
        )

    put(
        "nid-fee-calculator::c-fee-types",
        service_id="nid-fee-calculator",
        priority=1,
        claim_type="fee",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_NID_FEES],
        evidence_excerpt=(
            "আবেদনের ধরন: জাতীয় পরিচয়পত্র সংশোধন; অন্যান্য তথ্য সংশোধন; "
            "জাতীয় পরিচয়পত্র ও অন্যান্য তথ্য সংশোধন; রিইস্যু"
        ),
        reasoning="Live Tier-1 calculator dropdown options match the claimed application types.",
    )
    put(
        "nid-reissue-lost::c-reissue-fee",
        service_id="nid-reissue-lost",
        priority=1,
        claim_type="fee",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_NID_FAQ, E_NID_FEES],
        evidence_excerpt="হারানো আইডি কার্ড পেতে … ফি দিতে হয়। আপনার আবেদনের ফি জানতে এখানে ক্লিক করুন।",
        reasoning="FAQ explicitly requires fee; calculator includes reissue type.",
    )
    put(
        "nid-reissue-lost::c-reissue-law",
        service_id="nid-reissue-lost",
        priority=1,
        claim_type="legal_basis",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_NID_FAQ],
        reasoning=(
            "FAQ confirms lost/damaged card reissue process with prescribed fees, but the claim's "
            "broader legal formulation was not matched to a specific Act/section text in this pass."
        ),
        knowledge_gap="MISSING_NID_REISSUE_STATUTORY_CITATION",
    )

    # ---------- URLs / portals ----------
    put(
        "civil-bdris-application-print::c-print",
        service_id="civil-bdris-application-print",
        priority=1,
        claim_type="application_url",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_BDRIS],
        evidence_excerpt="Menu links include /application/print for birth and death sections",
        reasoning=(
            "BDRIS homepage exposes application-print menu routes. Direct GET to "
            "/application/print returned 403 from verifier network (bot gate). "
            "Endpoint existence supported; full page content not independently readable."
        ),
        canonical_paths=["/application/print"],
    )
    put(
        "civil-birth-death-verify::c-verify",
        service_id="civil-birth-death-verify",
        priority=1,
        claim_type="application_url",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_EVERIFY, E_BDRIS],
        reasoning="Live everify.bdris.gov.bd serves Birth and Death Verification UI; linked from BDRIS home.",
        canonical_url="https://everify.bdris.gov.bd/",
    )
    put(
        "civil-birth-registration::c-br-portal",
        service_id="civil-birth-registration",
        priority=1,
        claim_type="application_url",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_BDRIS],
        evidence_excerpt="Homepage menus: জন্ম নিবন্ধন আবেদন → https://bdris.gov.bd/br/application",
        reasoning=(
            "Official portal path confirmed via homepage links. Direct application page GET returned "
            "403 bot interstitial; form details (address-type chooser) not re-read."
        ),
        canonical_url="https://bdris.gov.bd/br/application",
    )
    put(
        "civil-birth-registration::c-br-helpline",
        service_id="civil-birth-registration",
        priority=2,
        claim_type="office",
        information_class="OFFICIAL",
        verification_status="UNVERIFIED",
        evidence=[E_BDRIS],
        reasoning=(
            "Helpline ১৬১৫২ appears only inside an HTML comment on the live BDRIS homepage "
            "(not visibly published). support@bdris.gov.bd / help@bdris.gov.bd not found on retrieved "
            "homepage (only programmer_rg@lgd.gov.bd). Do not verify contact claim from commented markup."
        ),
        knowledge_gap="MISSING_CURRENT_BDRIS_HELPLINE_PUBLICATION",
    )
    put(
        "civil-death-registration::c-dr-portal",
        service_id="civil-death-registration",
        priority=1,
        claim_type="application_url",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_BDRIS],
        evidence_excerpt="Menu: নতুন মৃত্যু নিবন্ধন আবেদন → /dr/application",
        reasoning="Path confirmed on homepage; application page itself 403 to verifier.",
        canonical_url="https://bdris.gov.bd/dr/application",
    )
    put(
        "civil-birth-registration-duplicate-cancel::c-dup-cancel",
        service_id="civil-birth-registration-duplicate-cancel",
        priority=2,
        claim_type="application_url",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_BDRIS],
        evidence_excerpt="Menu: সার্টিফিকেট বাতিলের আবেদন under birth registration",
        reasoning="Service listed on BDRIS; deep page not opened (403). ORGBDR live host unreachable.",
    )
    put(
        "civil-death-registration-duplicate-cancel::c-dup-cancel",
        service_id="civil-death-registration-duplicate-cancel",
        priority=2,
        claim_type="application_url",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_BDRIS],
        evidence_excerpt="Death section also lists certificate cancellation application",
        reasoning="Listed on BDRIS death menus; full workflow page not independently opened.",
    )
    put(
        "civil-marriage-registration::c-portal",
        service_id="civil-marriage-registration",
        priority=1,
        claim_type="application_url",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_MARRIAGE, E_MANUAL],
        reasoning=(
            "marriage.gov.bd returns 200 with CRVS Marriage & Divorce title; official PDF manual "
            "exists for registrar workflows. Civilian multi-step form details not fully extracted "
            "from JS-rendered UI in this pass."
        ),
    )
    put(
        "civil-divorce-registration::c-div-portal",
        service_id="civil-divorce-registration",
        priority=2,
        claim_type="application_url",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_MARRIAGE, E_MANUAL],
        reasoning="Portal branding and registrar manual cover divorce alongside marriage; citizen divorce path not fully walked.",
    )
    put(
        "civil-marriage-registrar-hindu-list::c-reg-list",
        service_id="civil-marriage-registrar-hindu-list",
        priority=2,
        claim_type="application_url",
        information_class="OFFICIAL",
        verification_status="UNVERIFIED",
        evidence=[E_MARRIAGE],
        reasoning="Portal home loaded but registrar list/search UI for Hindu registrars not independently confirmed in retrieved markup.",
        knowledge_gap="MISSING_HINDU_REGISTRAR_LIST_EVIDENCE",
    )
    put(
        "civil-marriage-registrar-muslim-list::c-reg-list",
        service_id="civil-marriage-registrar-muslim-list",
        priority=2,
        claim_type="application_url",
        information_class="OFFICIAL",
        verification_status="UNVERIFIED",
        evidence=[E_MARRIAGE],
        reasoning="Same limitation as Hindu registrar list — search function not confirmed beyond portal existence.",
        knowledge_gap="MISSING_MUSLIM_REGISTRAR_LIST_EVIDENCE",
    )

    # ---------- Marriage legal ----------
    put(
        "civil-marriage-registration::c-mm-mandatory",
        service_id="civil-marriage-registration",
        priority=1,
        claim_type="legal_basis",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_MUSLIM_ACT],
        evidence_excerpt=(
            "every marriage solemnized under Muslim law shall be registered in accordance "
            "with the provisions of this Act."
        ),
        reasoning="Live bdlaws text of Muslim Marriages and Divorces (Registration) Act, 1974 s.3.",
    )
    put(
        "civil-marriage-registration::c-hm-optional",
        service_id="civil-marriage-registration",
        priority=1,
        claim_type="legal_basis",
        information_class="OFFICIAL",
        verification_status="UNVERIFIED",
        evidence=[
            {
                "source_id": "src-law-hindu-marriage",
                "source_url": "http://bdlaws.minlaw.gov.bd/act-1105.html?lang=en",
                "authority_tier": 1,
                "retrieved_live_at": "2026-08-24",
                "live_http_status": 200,
                "notes": "Page retrieved but UTF-16 content could not be reliably decoded in verifier toolchain",
            }
        ],
        reasoning=(
            "Hindu Marriage Registration Act page responded 200 but text extraction failed "
            "(encoding). Optional-vs-mandatory characterization not independently confirmed."
        ),
        knowledge_gap="MISSING_HINDU_MARRIAGE_ACT_TEXT_EXTRACTION",
    )
    put(
        "civil-marriage-registration::c-report-30",
        service_id="civil-marriage-registration",
        priority=1,
        claim_type="deadline",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_MUSLIM_ACT],
        evidence_excerpt="thirty days from the date of such solemnization",
        reasoning=(
            "Act requires reporting to Nikah Registrar within thirty days when marriage is "
            "solemnized by someone other than the Nikah Registrar — conditional, not universal MUST for all applicants."
        ),
        applicability="conditional",
        condition="IF solemnized_by_person_other_than_nikah_registrar THEN report_within_30_days",
    )

    # ---------- NID eligibility / docs / procedures from FAQ ----------
    put(
        "nid-new-voter-registration::c-nid-new-age10",
        service_id="nid-new-voter-registration",
        priority=1,
        claim_type="eligibility",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_NID_FAQ],
        evidence_excerpt="আপনার বয়স যদি ১০ বছর বা বেশি হয়ে থাকে কিন্তু এখনও ভোটার হিসেবে নিবন্ধিত হননি",
        reasoning="Live FAQ explicitly states age 10+ unregistered citizens may apply online then biometrics.",
    )
    put(
        "nid-new-voter-registration::c-nid-new-voter18",
        service_id="nid-new-voter-registration",
        priority=1,
        claim_type="eligibility",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_NID_FAQ],
        evidence_excerpt="চলতি বছরের ১ জানুয়ারী বা তার পূর্বে ১৮ বছর হয়ে থাকে তাহলে আপনি ভোটার তালিকায় অন্তর্ভুক্ত হবেন",
        reasoning="Live FAQ voter-list inclusion rule matches claim.",
    )
    put(
        "nid-new-voter-registration::c-nid-new-docs",
        service_id="nid-new-voter-registration",
        priority=1,
        claim_type="document",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_NID_FAQ],
        evidence_excerpt="বায়োমেট্রিক প্রদানের সময় … অনলাইনে পূরণকৃত ফর্মের প্রিন্ট কপি এস.এস.সি সনদ … জন্ম নি",
        reasoning=(
            "FAQ lists printed form and age-proof documents at biometric appointment. Full MUST NEED "
            "matrix (address proof variants) partially truncated in extract — treat as partial; "
            "documents are appointment-conditional not universal online-only MUST."
        ),
        applicability="conditional",
        condition="IF attending_biometric_appointment THEN bring_printed_form_and_age_proof_etc",
    )
    put(
        "nid-new-voter-registration::c-nid-ssc-priority",
        service_id="nid-new-voter-registration",
        priority=1,
        claim_type="conditional_document",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_NID_FAQ],
        evidence_excerpt="শিক্ষাগত যোগ্যতা ন্যূনতম এসএসসি/সমমান হইলে এসএসসি/সমমান সনদপত্র",
        reasoning="FAQ states SSC priority when applicant is SSC-qualified — conditional rule, not universal MUST.",
        condition="IF minimum_qualification_ssc_or_equivalent THEN ssc_certificate_required_for_name_dob",
    )
    put(
        "nid-new-voter-registration::c-nid-new-duplicate-crime",
        service_id="nid-new-voter-registration",
        priority=1,
        claim_type="restriction",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_NID_FAQ],
        evidence_excerpt="নিবন্ধিত ব্যাক্তি পুনরায় আবেদন করলে সেটি দন্ডনীয় অপরাধ",
        reasoning="Live FAQ states re-application when already registered is a punishable offence.",
    )
    put(
        "nid-claim-account::c-claim",
        service_id="nid-claim-account",
        priority=2,
        claim_type="procedure_step",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_NID_FAQ],
        evidence_excerpt="Claim Account … ফর্ম নম্বর এবং আপনার জন্ম তারিখ, ক্যাপচা ও প্রয়োজনী তথ্য",
        reasoning="Live FAQ Claim Account instructions match.",
    )
    put(
        "nid-online-account-registration::c-acct-reg",
        service_id="nid-online-account-registration",
        priority=2,
        claim_type="eligibility",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_NID_FAQ],
        evidence_excerpt="কার্ডের নম্বর ও একটি কার্যকর মোবাইল নম্বর অথবা ইমেইল, আপনার জন্মতারিখ ও ঠিকানা",
        reasoning="Live FAQ account registration requirements match.",
    )
    put(
        "nid-online-account-registration::c-acct-wallet",
        service_id="nid-online-account-registration",
        priority=3,
        claim_type="procedure_step",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_NID_FAQ],
        evidence_excerpt="এনআইডি ওয়ালেট অ্যাপটি ডাউনলোড করুন এবং মুখমণ্ডল যাচাই (Face Verification)",
        reasoning="Live FAQ instructs NID Wallet download + face verification after registration.",
    )
    put(
        "nid-download-copy::c-dl",
        service_id="nid-download-copy",
        priority=2,
        claim_type="procedure_step",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_NID_FAQ],
        evidence_excerpt="লগইন করে ডাউনলোড মেন্যুতে গিয়ে আপনার পরিচয়পত্র কপি ডাউনলোড",
        reasoning="Live FAQ download-menu instruction matches.",
    )
    put(
        "nid-voter-area-change::c-f13",
        service_id="nid-voter-area-change",
        priority=2,
        claim_type="procedure_step",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_NID_FAQ],
        evidence_excerpt="উপজেলা/থানা নির্বাচন অফিসে ফর্ম ১৩ এর মাধ্যমে আবেদন",
        reasoning="Live FAQ Form 13 residence-area change rule matches; spelling-only changes use ordinary correction form.",
        condition="IF change_of_residence_area THEN apply_form_13_at_current_upazila_thana_election_office",
    )

    for sid, prefix in [
        ("nid-card-info-correction", "nid-card-info-correction"),
        ("nid-combined-correction", "nid-combined-correction"),
        ("nid-other-info-correction", "nid-other-info-correction"),
    ]:
        put(
            f"{sid}::c-{prefix}-channel",
            service_id=sid,
            priority=2,
            claim_type="procedure_step",
            information_class="OFFICIAL",
            verification_status="VERIFIED",
            evidence=[E_NID_FAQ],
            evidence_excerpt="অনলাইন/এনআইডি রেজিস্ট্রেশন উইং/উপজেলা/থানা/জেলা নির্বাচন অফিসে … আবেদন",
            reasoning="Live FAQ correction channels match.",
        )
        put(
            f"{sid}::c-{prefix}-once",
            service_id=sid,
            priority=1,
            claim_type="restriction",
            information_class="OFFICIAL",
            verification_status="VERIFIED",
            evidence=[E_NID_FAQ],
            evidence_excerpt="এক তথ্য শুধুমাত্র একবার সংশোধন করা যাবে। তবে যুক্তিযুক্ত না হলে কোন সংশোধন গ্রহণযোগ্য হবে না।",
            reasoning="Live FAQ one-time-per-field correction rule matches.",
        )
        put(
            f"{sid}::c-{prefix}-ssc-priority",
            service_id=sid,
            priority=1,
            claim_type="conditional_document",
            information_class="OFFICIAL",
            verification_status="VERIFIED",
            evidence=[E_NID_FAQ],
            evidence_excerpt="নাম (বাংলা/ইংরেজি) এবং জন্মতারিখ সংশোধনের ক্ষেত্রে … এসএসসি/সমমান হইলে এসএসসি/সমমান সনদপত্র",
            reasoning="Conditional SSC requirement for name/DOB correction confirmed; not universal MUST NEED.",
            condition="IF correcting_name_or_dob AND has_ssc_or_equivalent THEN require_ssc_certificate",
        )

    put(
        "nid-reissue-lost::c-reissue-online",
        service_id="nid-reissue-lost",
        priority=2,
        claim_type="procedure_step",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_NID_FAQ],
        evidence_excerpt="অনলাইনে পুনরায় মুদ্রণের (রিইস্যু) জন্য আবেদন করুন। … মোবাইল অথবা ইমেইলে বার্তা … ডাউনলোড",
        reasoning="Live FAQ lost-card reissue steps match.",
    )
    put(
        "nid-reissue-lost::c-reissue-no-combo",
        service_id="nid-reissue-lost",
        priority=1,
        claim_type="restriction",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_NID_FAQ],
        evidence_excerpt="হারানো ও সংশোধন একই সাথে সম্ভব নয়। আগে হারানো কার্ড তুলতে হবে",
        reasoning="Live FAQ forbids simultaneous lost-card reissue and correction.",
    )
    put(
        "nid-photo-signature-appointment::c-photo",
        service_id="nid-photo-signature-appointment",
        priority=2,
        claim_type="procedure_step",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_NID_FAQ],
        evidence_excerpt="ছবি,স্বাক্ষর ইত্যাদি পরিবর্তনের এপয়েন্টমেন্ট",
        reasoning="FAQ lists photo/signature appointment service; 'unclear photo may require in-person' nuance not fully quoted.",
    )
    put(
        "nid-photo-signature-appointment::c-sign-once",
        service_id="nid-photo-signature-appointment",
        priority=2,
        claim_type="restriction",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_NID_FAQ],
        evidence_excerpt="নতুন স্বাক্ষর এর নমুনাসহ গ্রহণযোগ্য প্রমাণপত্র … তবে স্বাক্ষর একবারই পরিবর্তন করা যাবে।",
        reasoning="Live FAQ signature-change-once rule matches.",
    )
    put(
        "nid-expatriate-registration::c-exp-apply",
        service_id="nid-expatriate-registration",
        priority=2,
        claim_type="eligibility",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_NID_FAQ],
        evidence_excerpt="প্রবাসী বা বাদপড়া ভোটারগণ এই প্রক্রিয়ার মাধ্যমে নিবন্ধন করতে পারবেন",
        reasoning="FAQ includes expatriates in new-registration pathway; 'any time' wording not explicitly confirmed.",
    )
    put(
        "nid-expatriate-registration::c-exp-otp",
        service_id="nid-expatriate-registration",
        priority=2,
        claim_type="procedure_step",
        information_class="OFFICIAL",
        verification_status="UNVERIFIED",
        evidence=[E_NID_FAQ],
        reasoning=(
            "Live FAQ discusses email/mobile messages generally but does not explicitly state "
            "OTP/notifications for expatriate applicants are email-only."
        ),
        knowledge_gap="MISSING_EXPATRIATE_OTP_CHANNEL_RULE",
    )

    # ---------- Practical / local / misc ----------
    put(
        "civil-birth-registration::c-br-docs-practical",
        service_id="civil-birth-registration",
        priority=3,
        claim_type="practical_tip",
        information_class="PRACTICAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_MOFA],
        reasoning=(
            "MOFA/LGD-referenced document list includes medical/birth-attendant proof and parents' "
            "NID/birth certificate variants — aligns with practical guides. Keep PRACTICAL; "
            "requirements are conditional by timing/applicant, not blanket MUST NEED."
        ),
        do_not_promote_to_must=True,
    )
    put(
        "civil-birth-registration::c-br-upload",
        service_id="civil-birth-registration",
        priority=2,
        claim_type="restriction",
        information_class="OFFICIAL",
        verification_status="UNVERIFIED",
        evidence=[E_BDRIS],
        reasoning=(
            "Birth application page returned 403; jpg/png/2MB upload constraint not independently "
            "confirmed (note: orgbdr feedback widget mentions jpg/png/pdf 2MB — different surface)."
        ),
        knowledge_gap="MISSING_BDRIS_APPLICATION_UPLOAD_CONSTRAINTS",
    )
    put(
        "identity-voter-slip-download::c-slip",
        service_id="identity-voter-slip-download",
        priority=3,
        claim_type="availability",
        information_class="OFFICIAL",
        verification_status="VERIFIED",
        evidence=[E_NID_FAQ],
        evidence_excerpt="নির্বাচনকালীন ভোটকেন্দ্র সম্পর্কিত তথ্য",
        reasoning="FAQ lists election-time vote-centre related information among online account services.",
    )
    put(
        "local-death-certificate-union::c-local-death-vs-bdris",
        service_id="local-death-certificate-union",
        priority=2,
        claim_type="other",
        information_class="OFFICIAL",
        verification_status="PARTIALLY_VERIFIED",
        evidence=[E_BDRIS],
        reasoning=(
            "BDRIS death registration is a national CRVS pathway; union-level death certificates "
            "are a distinct LGI product conceptually. Direct comparative official notice not retrieved."
        ),
    )

    # Local LGI existence claims
    local_checks = [
        ("dc-attestation-photocopy::c-dc-attestation-photocopy-exists", "dc-attestation-photocopy", "https://www.dhaka.gov.bd/en", None),
        ("dc-guardianship-certificate::c-dc-guardianship-certificate-exists", "dc-guardianship-certificate", "https://www.dhaka.gov.bd/en", None),
        ("local-character-certificate::c-local-character-certificate-exists", "local-character-certificate", "https://www.chandanpurup.gov.bd/new/application/citizen", 200),
        ("local-death-certificate-union::c-local-death-certificate-union-exists", "local-death-certificate-union", "https://www.chandanpurup.gov.bd/new/application/citizen", 200),
        ("local-nationality-certificate::c-local-nationality-certificate-exists", "local-nationality-certificate", "https://tilokpursonod.gov.bd/select_certificate/", 200),
        ("local-passport-attestation::c-local-passport-attestation-exists", "local-passport-attestation", "https://tilokpursonod.gov.bd/select_certificate/", 200),
        ("local-voter-transfer-attestation::c-local-voter-transfer-attestation-exists", "local-voter-transfer-attestation", "https://tilokpursonod.gov.bd/select_certificate/", 200),
    ]
    for cid, sid, url, status in local_checks:
        if status == 200:
            put(
                cid,
                service_id=sid,
                priority=3,
                claim_type="application_url",
                information_class="OFFICIAL",
                verification_status="PARTIALLY_VERIFIED",
                evidence=[{"source_url": url, "authority_tier": 3, "live_http_status": 200, "retrieved_live_at": "2026-08-24"}],
                reasoning=(
                    "Example LGI URL is live and related to citizen certificate applications. "
                    "Claim correctly frames as geographic instance, not national fee/doc schedule. "
                    "Service-specific page mapping not exhaustively proven."
                ),
            )
        else:
            put(
                cid,
                service_id=sid,
                priority=3,
                claim_type="application_url",
                information_class="OFFICIAL",
                verification_status="UNVERIFIED",
                evidence=[{"source_url": url, "authority_tier": 3, "live_http_status": status, "retrieved_live_at": "2026-08-24"}],
                reasoning="Example URL did not respond successfully from verifier network; leave unverified.",
                knowledge_gap="MISSING_LGI_EXAMPLE_URL_REACHABILITY",
            )

    return R


def service_readiness(claims: list[dict], results: dict[str, dict]) -> dict:
    by_svc: dict[str, list[dict]] = defaultdict(list)
    for c in claims:
        r = results[c["claim_id"]]
        by_svc[c["service_id"]].append({**c, "verification": r})

    high_risk_types = {
        "fee",
        "eligibility",
        "document",
        "conditional_document",
        "application_url",
        "legal_basis",
        "payment_method",
        "deadline",
        "restriction",
    }

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
        has_conflict = any(s == "CONFLICTING" for s in statuses)
        has_unresolved_fee_gap = any(
            i["verification"].get("knowledge_gap") == "MISSING_OFFICIAL_NID_FEE_SCHEDULE_STATIC"
            for i in items
        )
        verified_ratio = statuses.count("VERIFIED") / max(len(statuses), 1)
        high_verified = sum(1 for s in high_stat if s == "VERIFIED")
        high_bad = sum(1 for s in high_stat if s in {"UNVERIFIED", "CONFLICTING", "REJECTED", "OUTDATED"})

        # Heuristic readiness
        if sid.startswith("local-") or sid.startswith("dc-"):
            color = "YELLOW"
            reason = "Local/LGI instance services — example URLs only; no national authoritative fee/doc pack."
        elif has_conflict:
            color = "RED"
            reason = "Material CONFLICTING status remains on one or more claims."
        elif any(
            i["verification"]["verification_status"] == "UNVERIFIED"
            and i["verification"].get("priority", 3) == 1
            and i["verification"].get("claim_type")
            in {"fee", "eligibility", "legal_basis", "document"}
            for i in items
        ) and high_verified == 0:
            color = "RED"
            reason = "High-risk official facts remain unverified."
        elif has_unresolved_fee_gap and any("fee-amount-news" in i["claim_id"] for i in items):
            color = "YELLOW"
            reason = "Official fee calculator verified; static NID fee amounts remain unverified."
        elif high and high_bad == 0 and high_verified >= max(1, len(high) // 2) and verified_ratio >= 0.5:
            color = "GREEN"
            reason = "Critical/high-priority claims largely VERIFIED with Tier 1–2 evidence; safe for selective publication after publish gate."
        elif any(s in {"VERIFIED", "PARTIALLY_VERIFIED"} for s in statuses):
            color = "YELLOW"
            reason = "Useful verified/partial information exists but material gaps remain."
        else:
            color = "RED"
            reason = "Important facts unresolved."

        # Overrides for known strong services
        if sid in {
            "civil-birth-registration",
            "civil-birth-registration-copy",
            "civil-birth-registration-correction",
            "civil-death-registration",
            "civil-death-registration-copy",
            "nid-new-voter-registration",
            "nid-fee-calculator",
            "nid-reissue-lost",
            "nid-claim-account",
            "nid-download-copy",
            "civil-birth-death-verify",
            "nid-online-account-registration",
            "nid-photo-signature-appointment",
            "nid-voter-area-change",
        }:
            if not has_conflict and high_bad <= 1:
                color = "GREEN" if high_bad == 0 else "YELLOW"
                reason = (
                    "Core official facts verified against Tier 1 sources."
                    if color == "GREEN"
                    else "Core mostly verified with minor gaps."
                )

        if sid == "civil-death-registration-correction":
            color = "YELLOW"
            reason = "Other-info fee verified; DOB-analog fee only partially verified for death records."

        if sid in {
            "nid-card-info-correction",
            "nid-combined-correction",
            "nid-other-info-correction",
        }:
            color = "YELLOW"
            reason = (
                "Correction rules/channels/fees-exist verified; exact static fee amounts unresolved "
                "(use calculator). Not GREEN for authoritative amount publication."
            )

        if sid == "civil-birth-registration" and results.get(
            "civil-birth-registration::c-br-fee-late", {}
        ).get("verification_status") == "VERIFIED":
            color = "GREEN"
            reason = (
                "Fee schedule and key portal facts verified; helpline/email claim unverified "
                "(does not block fee publication)."
            )

        # Portal/shell services with only partial URL evidence → YELLOW not RED
        if sid in {
            "civil-bdris-application-print",
            "civil-birth-registration-duplicate-cancel",
            "civil-death-registration-duplicate-cancel",
            "civil-divorce-registration",
            "civil-marriage-registration",
            "nid-expatriate-registration",
        }:
            color = "YELLOW"
            reason = "Service existence partially corroborated; deep-page or channel details incomplete."

        if sid in {
            "civil-marriage-registrar-hindu-list",
            "civil-marriage-registrar-muslim-list",
        }:
            color = "RED"
            reason = "Registrar list/search function not independently confirmed; do not expose as authoritative."

        readiness[sid] = {
            "service_id": sid,
            "readiness": color,
            "claim_count": len(items),
            "status_counts": dict(Counter(statuses)),
            "reason": reason,
            "manual_review_recommended": color != "GREEN",
        }
    return readiness


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    claims = load_claims()
    results = build_results()

    missing = [c["claim_id"] for c in claims if c["claim_id"] not in results]
    extra = [k for k in results if k not in {c["claim_id"] for c in claims}]
    if missing or extra:
        raise SystemExit(f"Claim coverage mismatch missing={missing} extra={extra}")

    # Enrich with staging claim text
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
                "condition": r.get("condition"),
                "applicability": r.get("applicability"),
                "conflict_id": r.get("conflict_id"),
                "conflict_classification": r.get("conflict_classification"),
                "knowledge_gap": r.get("knowledge_gap"),
                "do_not_promote_to_must": r.get("do_not_promote_to_must", c.get("do_not_promote_to_must")),
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
    practical = [x for x in enriched if x["information_class"] == "PRACTICAL"]
    manual_review = [
        x["claim_id"]
        for x in enriched
        if x["verification_status"]
        in {"PARTIALLY_VERIFIED", "CONFLICTING", "UNVERIFIED", "OUTDATED"}
        or x.get("knowledge_gap")
    ]

    conflicts = [
        {
            "conflict_id": "conf-br-fee-10y",
            "resolution_status": "RESOLVED",
            "classification": "secondary_error_vs_official_schedule",
            "outcome": (
                "Official ORGBDR schedule has free/25/50 tiers only. BDT 500 after 10 years "
                "REJECTED for official use."
            ),
            "blocks_official_publication": False,
        },
        {
            "conflict_id": "conf-bdris-corr-other-fee",
            "resolution_status": "RESOLVED",
            "classification": "resolved_prefer_tier1_other_fee_50",
            "outcome": "ORGBDR Tier-1: other-info correction BDT 50; DOB BDT 100.",
            "blocks_official_publication": False,
        },
        {
            "conflict_id": "conf-nid-card-info-correction-fee-amount",
            "resolution_status": "UNRESOLVED",
            "classification": "unresolved_static_amounts_vs_official_calculator",
            "outcome": "Use official calculator; do not publish news static amounts as OFFICIAL.",
            "blocks_official_publication": True,
        },
        {
            "conflict_id": "conf-nid-combined-correction-fee-amount",
            "resolution_status": "UNRESOLVED",
            "classification": "unresolved_static_amounts_vs_official_calculator",
            "outcome": "Same as card-info correction fee conflict.",
            "blocks_official_publication": True,
        },
        {
            "conflict_id": "conf-nid-other-info-correction-fee-amount",
            "resolution_status": "UNRESOLVED",
            "classification": "unresolved_static_amounts_vs_official_calculator",
            "outcome": "Same as card-info correction fee conflict.",
            "blocks_official_publication": True,
        },
    ]
    # Note: staging listed 6 conflicts; two corr-other-fee rows share one conflict_id across birth/death.

    gaps = []
    seen = set()
    for x in enriched:
        g = x.get("knowledge_gap")
        if g and g not in seen:
            seen.add(g)
            gaps.append(
                {
                    "gap_id": g,
                    "gap_type": g,
                    "status": "OPEN",
                    "related_claims": [y["claim_id"] for y in enriched if y.get("knowledge_gap") == g],
                    "notes": "Created during Batch 1 independent verification; do not fill with AI inference.",
                }
            )

    readiness = service_readiness(claims, results)
    color_counts = Counter(v["readiness"] for v in readiness.values())

    policy = {
        "version": "1.0",
        "batch_id": "batch-01-identity-civil-registration",
        "verified_at": VERIFIED_AT,
        "rules": {
            "high_risk_official": {
                "preferred_tiers": [1, 2],
                "require_explicit_support": True,
                "no_material_unresolved_conflict": True,
                "no_promotion_from_tier_ge_5_to_official": True,
                "verdict_if_only_weak_source": ["UNVERIFIED", "PARTIALLY_VERIFIED"],
            },
            "medium_risk": {"prefer_cross_check": True},
            "low_risk_practical": {
                "may_remain_practical": True,
                "never_auto_must_need": True,
            },
            "url_policy": "Live check preferred; 403/unreachable without homepage link corroboration → PARTIAL/UNVERIFIED",
            "wayback_policy": (
                "Allowed for Tier-1/2 pages unreachable live when capture is recent or cites "
                "identifiable LGD letter; record retrieval provenance."
            ),
            "publication": "STAGING_ONLY — do not run publish_verified_knowledge.py in this phase",
        },
    }

    summary = {
        "batch_id": "batch-01-identity-civil-registration",
        "layer": "research/verification",
        "publication_status": "STAGING_ONLY",
        "published": False,
        "verifier": VERIFIER,
        "verified_at": VERIFIED_AT,
        "total_claims": len(enriched),
        "status_counts": dict(status_counts),
        "official_claims_verified": official_verified,
        "practical_claims": len(practical),
        "claims_requiring_manual_review": len(manual_review),
        "conflicts_resolved": sum(1 for c in conflicts if c["resolution_status"] == "RESOLVED"),
        "conflicts_unresolved": sum(1 for c in conflicts if c["resolution_status"] == "UNRESOLVED"),
        "knowledge_gaps_created": len(gaps),
        "services_green": color_counts.get("GREEN", 0),
        "services_yellow": color_counts.get("YELLOW", 0),
        "services_red": color_counts.get("RED", 0),
        "evidence_coverage_notes": (
            "Primary live Tier-1: services.nidw.gov.bd FAQ/fees; www.bdris.gov.bd home; "
            "everify.bdris.gov.bd; bdlaws Muslim Marriage Act; marriage.gov.bd (+ manual PDF). "
            "Tier-1 ORGBDR fee page via Wayback 2026-04-05. MOFA fee notice via Wayback 2023-06. "
            "Bright Data unlocker unavailable (401). Several BDRIS deep pages 403."
        ),
        "verification_coverage": "69/69 claims assigned a primary verification status",
        "main_limitations": [
            "BDRIS application deep pages blocked (403) — portal claims often PARTIAL",
            "Live ORGBDR/MOFA hosts unreachable — used Wayback for fee schedule",
            "NID static fee amounts not on official calculator page",
            "Hindu Marriage Act text extraction failed",
            "No claims published to runtime Fee/Checklist tables",
        ],
    }

    (OUT / "verification_policy.json").write_text(
        json.dumps(policy, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (OUT / "claims_verification.json").write_text(
        json.dumps(
            {
                "schema": "bda.research.verification.claims/1.0",
                "batch_id": summary["batch_id"],
                "claims": enriched,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (OUT / "conflicts_resolution.json").write_text(
        json.dumps({"conflicts": conflicts}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (OUT / "knowledge_gaps.json").write_text(
        json.dumps({"knowledge_gaps": gaps}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (OUT / "service_readiness.json").write_text(
        json.dumps({"services": readiness}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (OUT / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    # Update staging claim pipeline statuses to verification outcomes (file SoT only)
    staging = json.loads((STAGING / "claims.json").read_text(encoding="utf-8"))
    status_map = {
        "VERIFIED": "VERIFIED",
        "PARTIALLY_VERIFIED": "PARTIALLY_VERIFIED",
        "CONFLICTING": "CONFLICTING",
        "OUTDATED": "OUTDATED",
        "UNVERIFIED": "UNVERIFIED",
        "REJECTED": "REJECTED",
    }
    for c in staging["claims"]:
        r = results[c["claim_id"]]
        c["independent_verification_status"] = r["verification_status"]
        c["independent_verification"] = {
            "verifier": VERIFIER,
            "verified_at": VERIFIED_AT,
            "reasoning": r["reasoning"],
            "priority": r.get("priority"),
            "claim_type": r.get("claim_type"),
            "knowledge_gap": r.get("knowledge_gap"),
            "conflict_classification": r.get("conflict_classification"),
        }
        # Do NOT set pipeline_status=VERIFIED in a way that implies published.
        # Record mapped staging pipeline hint separately.
        c["suggested_pipeline_status"] = status_map[r["verification_status"]]
        c["provenance"]["independent_verified_at"] = VERIFIED_AT
        c["provenance"]["publication_status"] = "STAGING_ONLY"
    (STAGING / "claims.json").write_text(
        json.dumps(staging, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    # Markdown report
    lines = [
        "# Batch 1 — Independent Claim Verification",
        "",
        f"**Date:** {VERIFIED_AT[:10]}  ",
        f"**Verifier:** `{VERIFIER}`  ",
        "**Layer:** `data/research/verification/batch-01` (STAGING ONLY)  ",
        "**Published to runtime:** No  ",
        "**publish_verified_knowledge.py run:** No",
        "",
        "## Policy used",
        "",
        "- High-risk OFFICIAL claims require Tier 1–2 explicit support; Tier ≥5 never promoted to OFFICIAL VERIFIED.",
        "- Finding a source ≠ VERIFIED; live/Wayback inspection required.",
        "- Conditional requirements stay conditional (never auto MUST NEED).",
        "- PRACTICAL stays PRACTICAL.",
        "- Conflicts resolved only with evidence; otherwise left UNRESOLVED.",
        "- See `data/research/verification/batch-01/verification_policy.json`.",
        "",
        "## Totals",
        "",
        f"1. Total claims: **{summary['total_claims']}**",
        f"2. VERIFIED: **{status_counts.get('VERIFIED', 0)}**",
        f"3. PARTIALLY_VERIFIED: **{status_counts.get('PARTIALLY_VERIFIED', 0)}**",
        f"4. CONFLICTING: **{status_counts.get('CONFLICTING', 0)}**",
        f"5. OUTDATED: **{status_counts.get('OUTDATED', 0)}**",
        f"6. UNVERIFIED: **{status_counts.get('UNVERIFIED', 0)}**",
        f"7. REJECTED: **{status_counts.get('REJECTED', 0)}**",
        f"8. Official claims verified: **{official_verified}**",
        f"9. Practical claims: **{len(practical)}**",
        f"10. Claims requiring manual review: **{len(manual_review)}**",
        f"11. Conflicts resolved: **{summary['conflicts_resolved']}**",
        f"12. Conflicts unresolved: **{summary['conflicts_unresolved']}**",
        f"13. Knowledge gaps created: **{summary['knowledge_gaps_created']}**",
        f"14. Services GREEN: **{summary['services_green']}**",
        f"15. Services YELLOW: **{summary['services_yellow']}**",
        f"16. Services RED: **{summary['services_red']}**",
        f"17. Evidence coverage: {summary['evidence_coverage_notes']}",
        f"18. Verification coverage: {summary['verification_coverage']}",
        "19. Main limitations:",
        "",
    ]
    for lim in summary["main_limitations"]:
        lines.append(f"   - {lim}")

    lines += [
        "",
        "## Conflict outcomes",
        "",
    ]
    for c in conflicts:
        lines.append(
            f"- `{c['conflict_id']}` — **{c['resolution_status']}** ({c['classification']}): {c['outcome']}"
        )

    lines += ["", "## Service readiness", ""]
    for color in ("GREEN", "YELLOW", "RED"):
        lines.append(f"### {color}")
        for sid, row in readiness.items():
            if row["readiness"] == color:
                lines.append(f"- `{sid}` — {row['reason']}")
        lines.append("")

    lines += [
        "## Knowledge gaps",
        "",
    ]
    for g in gaps:
        lines.append(f"- `{g['gap_id']}` — claims: {', '.join(f'`{c}`' for c in g['related_claims'])}")

    lines += [
        "",
        "## Explicit non-actions",
        "",
        "- Did not start Batch 2",
        "- Did not publish Fee/Checklist/Procedure rows",
        "- Did not invent fees/URLs",
        "- Did not convert PRACTICAL → MUST NEED",
        "",
        "## Machine-readable outputs",
        "",
        "- `data/research/verification/batch-01/claims_verification.json`",
        "- `data/research/verification/batch-01/conflicts_resolution.json`",
        "- `data/research/verification/batch-01/knowledge_gaps.json`",
        "- `data/research/verification/batch-01/service_readiness.json`",
        "- `data/research/verification/batch-01/summary.json`",
        "- `data/research/verification/batch-01/verification_policy.json`",
        "",
    ]
    DOCS.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
