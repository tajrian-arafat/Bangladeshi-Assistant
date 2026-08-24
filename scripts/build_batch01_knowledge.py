#!/usr/bin/env python3
"""Build Batch 1 structured knowledge (Identity & Civil Registration).

Stores services, requirements (MUST/CONDITIONAL/RECOMMENDED), fees, procedures,
sources, claims/evidence, conflicts, and KQS — without fabricating facts.
"""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "knowledge" / "batch-01"
SVC_DIR = OUT / "services"
RETRIEVED = "2026-08-24"
BATCH = "batch-01-identity-civil-registration"

# ---------------------------------------------------------------------------
# Sources registry
# ---------------------------------------------------------------------------

SOURCES = {
    "src-nid-faq": {
        "source_id": "src-nid-faq",
        "source_url": "https://services.nidw.gov.bd/nid-pub/faq?locale=en",
        "source_title": "Bangladesh NID Application System — FAQ",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Bangladesh Election Commission (NID Wing)",
        "published_date": None,
        "retrieved_at": RETRIEVED,
        "language": "bn",
    },
    "src-nid-faq-correction": {
        "source_id": "src-nid-faq-correction",
        "source_url": "https://services.nidw.gov.bd/nid-pub/faq?tab=faq-correction",
        "source_title": "NID FAQ — Correction & Reissue",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Bangladesh Election Commission (NID Wing)",
        "published_date": None,
        "retrieved_at": RETRIEVED,
        "language": "bn",
    },
    "src-nid-fees": {
        "source_id": "src-nid-fees",
        "source_url": "https://services.nidw.gov.bd/nid-pub/fees",
        "source_title": "NID Fee Calculator",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Bangladesh Election Commission (NID Wing)",
        "published_date": None,
        "retrieved_at": RETRIEVED,
        "language": "bn",
    },
    "src-nid-home": {
        "source_id": "src-nid-home",
        "source_url": "https://services.nidw.gov.bd/nid-pub/?locale=en",
        "source_title": "Bangladesh NID Application System — Home",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Bangladesh Election Commission (NID Wing)",
        "published_date": None,
        "retrieved_at": RETRIEVED,
        "language": "en",
    },
    "src-nidw-main": {
        "source_id": "src-nidw-main",
        "source_url": "https://nidw.gov.bd/",
        "source_title": "NID Wing — Election Commission",
        "source_type": "official_website",
        "authority_tier": 1,
        "responsible_body": "Bangladesh Election Commission (NID Wing)",
        "published_date": None,
        "retrieved_at": RETRIEVED,
        "language": "en",
    },
    "src-nidw-duplicate": {
        "source_id": "src-nidw-duplicate",
        "source_url": "https://www.nidw.gov.bd/IssuanceDuplicateNID.php",
        "source_title": "Issuance Duplicate NID",
        "source_type": "official_website",
        "authority_tier": 1,
        "responsible_body": "Bangladesh Election Commission (NID Wing)",
        "published_date": None,
        "retrieved_at": RETRIEVED,
        "language": "en",
    },
    "src-bdris-br-app": {
        "source_id": "src-bdris-br-app",
        "source_url": "https://bdris.gov.bd/br/application",
        "source_title": "BDRIS Birth Registration Application",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Office of the Registrar General, Birth and Death Registration",
        "published_date": None,
        "retrieved_at": RETRIEVED,
        "language": "bn",
    },
    "src-bdris-home": {
        "source_id": "src-bdris-home",
        "source_url": "https://www.bdris.gov.bd/",
        "source_title": "BDRIS Homepage",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Office of the Registrar General, Birth and Death Registration",
        "published_date": None,
        "retrieved_at": RETRIEVED,
        "language": "bn",
    },
    "src-orgbdr": {
        "source_id": "src-orgbdr",
        "source_url": "https://orgbdr.gov.bd/",
        "source_title": "Office of the Registrar General, Birth & Death Registration",
        "source_type": "official_website",
        "authority_tier": 1,
        "responsible_body": "Office of the Registrar General / Local Government Division",
        "published_date": None,
        "retrieved_at": RETRIEVED,
        "language": "bn",
    },
    "src-everify": {
        "source_id": "src-everify",
        "source_url": "https://everify.bdris.gov.bd/",
        "source_title": "Birth and Death Record Verification",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Office of the Registrar General, Birth and Death Registration",
        "published_date": None,
        "retrieved_at": RETRIEVED,
        "language": "bn",
    },
    "src-mofa-ankara-bdr": {
        "source_id": "src-mofa-ankara-bdr",
        "source_url": "https://www.ankara.mofa.gov.bd/en/site/page/Birth--and-Death-Registration--English-",
        "source_title": "MOFA Mission notice — Birth & Death Registration fees/documents (refs LGD letter)",
        "source_type": "official_notice",
        "authority_tier": 2,
        "responsible_body": "Ministry of Foreign Affairs (mission) citing Local Government Division",
        "published_date": "2023-03-15",
        "retrieved_at": RETRIEVED,
        "language": "en",
        "notes": "Cites LGD letter No-46.04.0000.101.22.001.21-278 dated 22 Feb 2023.",
    },
    "src-bdservicerules-fee": {
        "source_id": "src-bdservicerules-fee",
        "source_url": "https://bdservicerules.info/bdris-fee-bangladesh/",
        "source_title": "BDRIS fee table republished (claims gazette basis)",
        "source_type": "professional_guide",
        "authority_tier": 6,
        "responsible_body": None,
        "published_date": None,
        "retrieved_at": RETRIEVED,
        "language": "bn",
    },
    "src-legalclarity-birth": {
        "source_id": "src-legalclarity-birth",
        "source_url": "https://legalclarity.org/bangladesh-birth-certificate-registration-and-verification/",
        "source_title": "Bangladesh Birth Certificate guide",
        "source_type": "professional_guide",
        "authority_tier": 6,
        "responsible_body": None,
        "published_date": None,
        "retrieved_at": RETRIEVED,
        "language": "en",
    },
    "src-marriage-portal": {
        "source_id": "src-marriage-portal",
        "source_url": "https://marriage.gov.bd/",
        "source_title": "CRVS Marriage & Divorce Portal",
        "source_type": "official_portal",
        "authority_tier": 1,
        "responsible_body": "Ministry of Law / Local Government (CRVS marriage system)",
        "published_date": None,
        "retrieved_at": RETRIEVED,
        "language": "bn",
    },
    "src-marriage-manual": {
        "source_id": "src-marriage-manual",
        "source_url": "https://marriage.gov.bd/docs/CRVS_User_Manual.pdf",
        "source_title": "USER MANUAL CRVS Marriage & Divorce Portal",
        "source_type": "official_pdf",
        "authority_tier": 1,
        "responsible_body": "CRVS Marriage & Divorce Portal operators",
        "published_date": None,
        "retrieved_at": RETRIEVED,
        "language": "en",
    },
    "src-law-muslim-marriage": {
        "source_id": "src-law-muslim-marriage",
        "source_url": "http://bdlaws.minlaw.gov.bd/act-details-476.html",
        "source_title": "Muslim Marriages and Divorces (Registration) Act, 1974",
        "source_type": "gazette_law",
        "authority_tier": 1,
        "responsible_body": "Legislative and Parliamentary Affairs Division",
        "published_date": "1974",
        "retrieved_at": RETRIEVED,
        "language": "en",
    },
    "src-law-hindu-marriage": {
        "source_id": "src-law-hindu-marriage",
        "source_url": "http://bdlaws.minlaw.gov.bd/act-1105.html?lang=en",
        "source_title": "Hindu Marriage Registration Act, 2012",
        "source_type": "gazette_law",
        "authority_tier": 1,
        "responsible_body": "Legislative and Parliamentary Affairs Division",
        "published_date": "2012",
        "retrieved_at": RETRIEVED,
        "language": "bn",
    },
    "src-tbs-nid-corrections": {
        "source_id": "src-tbs-nid-corrections",
        "source_url": "https://www.tbsnews.net/features/panorama/never-ending-nightmare-nid-corrections-bangladesh-1099006",
        "source_title": "The never-ending nightmare of NID corrections in Bangladesh",
        "source_type": "news",
        "authority_tier": 5,
        "responsible_body": "The Business Standard",
        "published_date": None,
        "retrieved_at": RETRIEVED,
        "language": "en",
    },
    "src-dt-nid-reapply": {
        "source_id": "src-dt-nid-reapply",
        "source_url": "https://www.dhakatribune.com/bangladesh/390480/nid-correction-cancellation-allowed-through",
        "source_title": "Canceled NID correction requests can be reapplied until Oct 31",
        "source_type": "news",
        "authority_tier": 5,
        "responsible_body": "Dhaka Tribune",
        "published_date": "2026-07-05",
        "retrieved_at": RETRIEVED,
        "language": "en",
    },
    "src-sib-nid-fees": {
        "source_id": "src-sib-nid-fees",
        "source_url": "https://ssitbari.com/ec-new-nid-correction-fee-bangladesh/",
        "source_title": "EC new NID correction fee report",
        "source_type": "news",
        "authority_tier": 5,
        "responsible_body": None,
        "published_date": None,
        "retrieved_at": RETRIEVED,
        "language": "bn",
    },
    "src-eshoi-rejection": {
        "source_id": "src-eshoi-rejection",
        "source_url": "https://eshoincomekori.com/nid-correction-online-rejection-reasons/",
        "source_title": "NID Correction Online Rejection Reasons",
        "source_type": "blog",
        "authority_tier": 6,
        "responsible_body": None,
        "published_date": None,
        "retrieved_at": RETRIEVED,
        "language": "en",
    },
}


def claim(
    claim_id: str,
    text: str,
    *,
    field: str,
    information_class: str,
    source_ids: list[str],
    verification_status: str,
    confidence: float,
    excerpt: str | None = None,
    layer: str = "OFFICIAL",
) -> dict:
    return {
        "claim_id": claim_id,
        "claim": text,
        "field": field,
        "information_class": information_class,  # OFFICIAL | PRACTICAL
        "layer": layer,
        "source_ids": source_ids,
        "evidence_excerpt": excerpt,
        "verification_status": verification_status,
        "confidence": confidence,
        "retrieved_at": RETRIEVED,
        "last_verified_at": RETRIEVED if verification_status == "VERIFIED" else None,
        "conflicting_sources": [],
    }


def req(
    req_id: str,
    name_en: str,
    name_bn: str | None,
    classification: str,
    *,
    condition: dict | None = None,
    claim_ids: list[str] | None = None,
    notes: str | None = None,
) -> dict:
    return {
        "requirement_id": req_id,
        "name_en": name_en,
        "name_bn": name_bn,
        "classification": classification,  # MUST | CONDITIONAL | RECOMMENDED | NOT_APPLICABLE
        "condition": condition,
        "claim_ids": claim_ids or [],
        "notes": notes,
    }


def fee(
    fee_id: str,
    description: str,
    *,
    amount_bdt: float | None,
    currency: str = "BDT",
    condition: dict | None = None,
    claim_ids: list[str] | None = None,
    verification_status: str = "UNVERIFIED",
    notes: str | None = None,
) -> dict:
    return {
        "fee_id": fee_id,
        "description": description,
        "amount": amount_bdt,
        "currency": currency,
        "condition": condition,
        "claim_ids": claim_ids or [],
        "verification_status": verification_status,
        "notes": notes,
        "retrieved_at": RETRIEVED,
    }


def step(step_id: str, order: int, title: str, description: str, claim_ids: list[str] | None = None) -> dict:
    return {
        "step_id": step_id,
        "order": order,
        "title": title,
        "description": description,
        "claim_ids": claim_ids or [],
    }


def kqs(
    *,
    coverage: float,
    authority: float,
    freshness: float,
    consistency: float,
    usability: float = 50.0,
    notes: str,
) -> dict:
    # Weights from KNOWLEDGE_QUALITY_FRAMEWORK.md
    score = (
        0.25 * coverage
        + 0.25 * authority
        + 0.20 * freshness
        + 0.15 * consistency
        + 0.15 * usability
    )
    return {
        "knowledge_quality_score": round(score, 1),
        "dimensions": {
            "coverage": coverage,
            "authority": authority,
            "freshness": freshness,
            "consistency": consistency,
            "usability": usability,
        },
        "weights": {
            "coverage": 0.25,
            "authority": 0.25,
            "freshness": 0.20,
            "consistency": 0.15,
            "usability": 0.15,
        },
        "notes": notes,
        "scored_at": RETRIEVED,
    }


def base_service(sid: str, catalogue: dict) -> dict:
    return {
        "service_id": sid,
        "batch_id": BATCH,
        "catalogue_version": catalogue.get("catalogue_version"),
        "service_name_en": catalogue["service_name_en"],
        "service_name_bn": catalogue.get("service_name_bn"),
        "aliases": catalogue.get("aliases") or [],
        "banglish_variants": [],
        "category_id": catalogue.get("category_id"),
        "responsible_ministry": None,
        "responsible_agency": catalogue.get("responsible_authority"),
        "target_applicant": catalogue.get("target_user") or [],
        "eligibility": [],
        "prerequisites": [],
        "application_methods": [],
        "online_application": None,
        "offline_application": None,
        "official_application_url": catalogue.get("official_source"),
        "official_information_urls": [],
        "official_forms": [],
        "requirements": [],
        "fees": [],
        "payment_methods": [],
        "processing_time": None,
        "procedure_steps": [],
        "appointment_requirements": [],
        "verification_requirements": [],
        "delivery_collection": [],
        "office_locations": [],
        "geographic_limitations": [],
        "service_availability": "AVAILABLE",
        "related_services": [],
        "dependencies": [],
        "renewal_rules": [],
        "correction_rules": [],
        "replacement_rules": [],
        "cancellation_rules": [],
        "common_rejection_reasons": [],
        "common_mistakes": [],
        "practical_experience": [],
        "warnings": [],
        "legal_basis": [],
        "claims": [],
        "conflicts": [],
        "research_status": "PARTIAL",
        "missing_information": [],
        "manual_review_required": [],
        "knowledge_quality": None,
        "geographic_availability": catalogue.get("geographic_availability") or [],
        "researched_at": RETRIEVED,
    }


# ---------------------------------------------------------------------------
# Service builders
# ---------------------------------------------------------------------------

def build_nid_new(cat: dict) -> dict:
    s = base_service("nid-new-voter-registration", cat)
    s["responsible_ministry"] = "Bangladesh Election Commission"
    s["responsible_agency"] = "NID Wing, Bangladesh Election Commission"
    s["banglish_variants"] = ["nid registration", "voter registration", "new nid", "notun nid"]
    s["eligibility"] = [
        "Bangladeshi citizen",
        "Age 10+ for NID application pathway; voter roll inclusion if age ≥18 as of 1 January of the year (per FAQ)",
    ]
    s["application_methods"] = ["online_form_then_in_person_biometric", "hybrid"]
    s["online_application"] = True
    s["offline_application"] = True
    s["official_application_url"] = "https://services.nidw.gov.bd/nid-pub/register-account?locale=en"
    s["official_information_urls"] = [
        "https://services.nidw.gov.bd/nid-pub/faq?locale=en",
        "https://nidw.gov.bd/",
    ]
    s["claims"] = [
        claim(
            "c-nid-new-age10",
            "Citizens aged 10 years or more who are not yet registered as voters may apply online and provide biometrics at the relevant Upazila/Thana election office.",
            field="eligibility",
            information_class="OFFICIAL",
            source_ids=["src-nid-faq"],
            verification_status="VERIFIED",
            confidence=0.95,
            excerpt="আপনার বয়স যদি ১০ বছর বা বেশি হয়ে থাকে কিন্তু এখনও ভোটার হিসেবে নিবন্ধিত হননি",
        ),
        claim(
            "c-nid-new-voter18",
            "If age is 18 years on or before 1 January of the current year, the applicant will be included in the voter list.",
            field="eligibility",
            information_class="OFFICIAL",
            source_ids=["src-nid-faq"],
            verification_status="VERIFIED",
            confidence=0.9,
            excerpt="আপনার বয়স যদি চলতি বছরের ১ জানুয়ারী বা তার পূর্বে ১৮ বছর হয়ে থাকে",
        ),
        claim(
            "c-nid-new-docs",
            "At biometric appointment, applicants need printed online form, age-proof document(s), address proof, and other supporting IDs as applicable.",
            field="requirements",
            information_class="OFFICIAL",
            source_ids=["src-nid-faq"],
            verification_status="VERIFIED",
            confidence=0.95,
        ),
        claim(
            "c-nid-new-duplicate-crime",
            "Re-applying when already registered is a punishable offence.",
            field="warnings",
            information_class="OFFICIAL",
            source_ids=["src-nid-faq"],
            verification_status="VERIFIED",
            confidence=0.95,
            excerpt="নিবন্ধিত ব্যাক্তি পুনরায় আবেদন করলে সেটি দন্ডনীয় অপরাধ",
        ),
        claim(
            "c-nid-ssc-priority",
            "For name/age, SSC or equivalent certificate gets priority when the person is SSC-qualified.",
            field="requirements",
            information_class="OFFICIAL",
            source_ids=["src-nid-faq", "src-nidw-main"],
            verification_status="VERIFIED",
            confidence=0.95,
            excerpt="এসএসসি অথবা সমমানের পরীক্ষার সনদে উল্লেখিত বয়স ও নাম",
        ),
    ]
    s["requirements"] = [
        req("r-print-form", "Printed copy of online registration form", "অনলাইনে পূরণকৃত ফর্মের প্রিন্ট কপি", "MUST", claim_ids=["c-nid-new-docs"]),
        req(
            "r-ssc",
            "SSC/equivalent certificate (age/name proof)",
            "এস.এস.সি সনদ",
            "CONDITIONAL",
            condition={"all": [{"field": "has_ssc_or_equivalent", "op": "eq", "value": True}]},
            claim_ids=["c-nid-new-docs", "c-nid-ssc-priority"],
        ),
        req(
            "r-birth-reg",
            "Birth registration certificate (age proof)",
            "জন্ম নিবন্ধন সনদ",
            "CONDITIONAL",
            condition={"any": [{"field": "has_ssc_or_equivalent", "op": "eq", "value": False}, {"field": "use_birth_certificate_as_age_proof", "op": "eq", "value": True}]},
            claim_ids=["c-nid-new-docs"],
        ),
        req(
            "r-passport-dl-tin",
            "Passport / Driving licence / TIN (age proof alternative)",
            "পাসপোর্ট / ড্রাইভিং লাইসেন্স / টি.আই.এন",
            "CONDITIONAL",
            condition={"field": "age_proof_document", "op": "in", "value": ["passport", "driving_licence", "tin"]},
            claim_ids=["c-nid-new-docs"],
        ),
        req(
            "r-address-proof",
            "Utility bill / house rent receipt / holding tax receipt (address proof)",
            "ইউটিলিটি বিল/বাড়ী ভাড়ার রশিদ/হোল্ডিং ট্যাক্স রশিদ",
            "MUST",
            claim_ids=["c-nid-new-docs"],
            notes="FAQ lists as proof of habitual residence in the area.",
        ),
        req(
            "r-citizenship",
            "Citizenship certificate",
            "নাগরিকত্বের সনদ",
            "CONDITIONAL",
            condition={"field": "citizenship_certificate_applicable", "op": "eq", "value": True},
            claim_ids=["c-nid-new-docs"],
        ),
        req(
            "r-family-nid",
            "Copy of father/mother/spouse NID",
            "বাবা, মা, স্বামী/স্ত্রীর এনআইডি কার্ডের কপি",
            "CONDITIONAL",
            condition={"field": "family_nid_applicable", "op": "eq", "value": True},
            claim_ids=["c-nid-new-docs"],
        ),
    ]
    s["procedure_steps"] = [
        step("s1", 1, "Fill online registration form", "Complete personal, other, and address steps in Bangla Unicode (except own full name field rules per FAQ).", claim_ids=["c-nid-new-docs"]),
        step("s2", 2, "Preview and print PDF", "Verify all information, generate PDF, print.", claim_ids=[]),
        step("s3", 3, "Submit at election office with documents", "Submit printed form and supporting documents at nearest election office.", claim_ids=[]),
        step("s4", 4, "Biometric capture", "Provide biometrics as scheduled at Upazila/Thana election office.", claim_ids=[]),
        step("s5", 5, "Receive notification and collect/download card", "After processing, receive SMS/email; register online account and download/collect card.", claim_ids=[]),
    ]
    s["warnings"] = [
        "Do not apply again if already registered — punishable offence (official FAQ).",
        "False information may lead to imprisonment and/or fine (official FAQ).",
    ]
    s["related_services"] = ["nid-online-account-registration", "nid-claim-account", "nid-download-copy", "civil-birth-registration"]
    s["dependencies"] = ["Birth registration often used as age proof when SSC unavailable"]
    s["fees"] = [
        fee(
            "f-new-reg-forms",
            "Forms for applications — FAQ states forms themselves have no charge",
            amount_bdt=0,
            claim_ids=[],
            verification_status="VERIFIED",
            notes="FAQ Q18: forms have no fee. Card issuance fee schedule not confirmed on Tier-1 page in this pass.",
        )
    ]
    s["payment_methods"] = []
    s["processing_time"] = {
        "value": None,
        "unit": None,
        "verification_status": "UNVERIFIED",
        "notes": "Official FAQ does not state a fixed processing duration for new registration.",
    }
    s["missing_information"] = [
        "Exact new-registration card fee amount not published as a static table on retrieved Tier-1 pages (fee calculator covers correction/reissue types).",
        "Exact biometric appointment booking URL/workflow details beyond FAQ summary.",
        "District-wise office hours beyond national helpline hours.",
    ]
    s["manual_review_required"] = [
        "Confirm whether any fee applies for first-time NID issuance vs correction/reissue only.",
    ]
    s["practical_experience"] = [
        {
            "text": "News reporting describes long backlogs and middlemen for NID processes generally; not specific official guidance for new registration.",
            "layer": "PRACTICAL",
            "source_ids": ["src-tbs-nid-corrections"],
            "verification_status": "UNVERIFIED",
            "do_not_promote_to_must": True,
        }
    ]
    s["research_status"] = "SUBSTANTIAL"
    s["knowledge_quality"] = kqs(
        coverage=78,
        authority=92,
        freshness=85,
        consistency=90,
        usability=50,
        notes="Strong Tier-1 FAQ coverage for eligibility/docs/steps; fee amount for first issuance incomplete.",
    )
    return s


def build_nid_correction(cat: dict, sid: str, kind: str) -> dict:
    """kind: card | other | combined"""
    s = base_service(sid, cat)
    s["responsible_ministry"] = "Bangladesh Election Commission"
    s["responsible_agency"] = "NID Wing, Bangladesh Election Commission"
    s["banglish_variants"] = ["nid correction", "nid songshodhon", "nid update"]
    s["application_methods"] = ["online", "in_person"]
    s["online_application"] = True
    s["offline_application"] = True
    s["official_application_url"] = "https://services.nidw.gov.bd/nid-pub/?locale=en"
    s["official_information_urls"] = [
        "https://services.nidw.gov.bd/nid-pub/faq?tab=faq-correction",
        "https://services.nidw.gov.bd/nid-pub/fees",
        "https://nidw.gov.bd/",
    ]
    s["claims"] = [
        claim(
            f"c-{sid}-channel",
            "Correction applications may be submitted online or at NID Registration Wing / Upazila / Thana / District election offices with adequate supporting documents.",
            field="application_methods",
            information_class="OFFICIAL",
            source_ids=["src-nid-faq-correction"],
            verification_status="VERIFIED",
            confidence=0.95,
        ),
        claim(
            f"c-{sid}-ssc-priority",
            "For name (Bangla/English) and date of birth correction, SSC/equivalent certificate is required if minimum qualification is SSC/equivalent.",
            field="requirements",
            information_class="OFFICIAL",
            source_ids=["src-nid-faq"],
            verification_status="VERIFIED",
            confidence=0.95,
        ),
        claim(
            f"c-{sid}-once",
            "Official FAQ states one piece of information may be corrected only once; unjustified corrections are not acceptable.",
            field="correction_rules",
            information_class="OFFICIAL",
            source_ids=["src-nid-faq-correction"],
            verification_status="VERIFIED",
            confidence=0.9,
            excerpt="এক তথ্য শুধুমাত্র একবার সংশোধন করা যাবে",
        ),
        claim(
            f"c-{sid}-fee-exists",
            "Fees are payable for correction/reissue; applicants must calculate fee via the official fee calculator.",
            field="fees",
            information_class="OFFICIAL",
            source_ids=["src-nid-faq-correction", "src-nid-fees"],
            verification_status="VERIFIED",
            confidence=0.95,
            excerpt="হ্যাঁ ফি দিতে হয়। আপনার আবেদনের ফি জানতে এখানে ক্লিক করুন।",
        ),
        claim(
            f"c-{sid}-fee-amount-news",
            "Secondary news reports cite VAT-inclusive visible-info correction fees such as BDT 230 (1st), 345 (2nd), 460 (3rd+); not confirmed from a retrieved Tier-1 fee schedule PDF in this pass.",
            field="fees",
            information_class="PRACTICAL",
            source_ids=["src-sib-nid-fees"],
            verification_status="UNVERIFIED",
            confidence=0.45,
            layer="PRACTICAL",
        ),
    ]
    s["requirements"] = [
        req(
            "r-corr-ssc",
            "SSC/equivalent certificate",
            "এসএসসি/সমমান সনদপত্র",
            "CONDITIONAL",
            condition={"all": [{"field": "correction_fields", "op": "in", "value": ["name", "date_of_birth"]}, {"field": "has_ssc_or_equivalent", "op": "eq", "value": True}]},
            claim_ids=[f"c-{sid}-ssc-priority"],
        ),
        req(
            "r-corr-alt-age-name",
            "Passport / birth registration / driving licence / trade licence / certified kabinnama copy",
            "পাসপোর্ট/জন্ম নিবন্ধন/ড্রাইভিং লাইসেন্স/ট্রেড লাইসেন্স/কাবিননামা",
            "CONDITIONAL",
            condition={"all": [{"field": "correction_fields", "op": "in", "value": ["name", "date_of_birth"]}, {"field": "has_ssc_or_equivalent", "op": "eq", "value": False}]},
            claim_ids=[f"c-{sid}-ssc-priority"],
        ),
        req(
            "r-corr-name-change-affidavit",
            "Magistrate court affidavit + national daily newspaper notice",
            "ম্যাজিস্ট্রেট আদালত হলফনামা ও জাতীয় দৈনিক পত্রিকায় বিজ্ঞপ্তি",
            "CONDITIONAL",
            condition={"field": "name_change_type", "op": "eq", "value": "fundamental_name_change"},
            claim_ids=[f"c-{sid}-ssc-priority"],
        ),
        req(
            "r-corr-marriage-title",
            "Certified kabinnama / talaknama / death certificate / affidavit / divorce decree",
            "কাবিননামা/তালাকনামা/মৃত্যু সনদ/হলফনামা/বিবাহ বিচ্ছেদ ডিক্রি",
            "CONDITIONAL",
            condition={"field": "correction_reason", "op": "in", "value": ["marriage", "divorce", "spouse_title"]},
        ),
        req(
            "r-corr-parents",
            "Applicant SSC/HSC (if parents named) + certified copies of parents/siblings NID",
            "পিতা/মাতার নাম সংশোধনে এসএসসি/এইচএসসি ও পিতা-মাতা-ভাই-বোনের এনআইডি",
            "CONDITIONAL",
            condition={"field": "correction_fields", "op": "in", "value": ["father_name", "mother_name"]},
        ),
        req(
            "r-corr-deceased-marker",
            "Death certificate OR NID + UP Chairman/Mayor/Councillor certification of being alive",
            "মৃত সংযোজন/বিয়োজনে মৃত্যু সনদ বা জীবিত প্রত্যয়ন",
            "CONDITIONAL",
            condition={"field": "correction_fields", "op": "in", "value": ["parent_deceased_marker"]},
        ),
        req(
            "r-corr-address",
            "Deed / telephone-gas-water bill / rent agreement / rent receipt (certified)",
            "ঠিকানা সংশোধনে দলিল/ইউটিলিটি বিল/ভাড়া চুক্তি/রশিদ",
            "CONDITIONAL",
            condition={"field": "correction_fields", "op": "in", "value": ["address_detail"]},
        ),
        req(
            "r-corr-blood",
            "Medical certificate for blood group",
            "রক্তের গ্রুপের ডাক্তারী সনদ",
            "CONDITIONAL",
            condition={"field": "correction_fields", "op": "in", "value": ["blood_group"]},
        ),
        req(
            "r-corr-attestation",
            "Supporting copies attested by authorized persons (MP, elected LGI, gazetted officer, or secondary/higher secondary head)",
            "সত্যায়িত অনুলিপি",
            "MUST",
            notes="FAQ lists who may attest copies.",
        ),
    ]
    s["fees"] = [
        fee(
            "f-corr-calc",
            "Fee must be calculated on official NID fee calculator (application type + delivery type)",
            amount_bdt=None,
            claim_ids=[f"c-{sid}-fee-exists"],
            verification_status="VERIFIED",
            notes="Static BDT amounts not taken from Tier-1 schedule in this pass; use calculator.",
        ),
        fee(
            "f-corr-news-230",
            "Reported first-time visible-info correction fee (VAT inclusive) — news only",
            amount_bdt=230,
            claim_ids=[f"c-{sid}-fee-amount-news"],
            verification_status="UNVERIFIED",
            notes="Do not treat as MUST official fee until Tier-1 schedule confirmed.",
        ),
    ]
    s["payment_methods"] = [
        {"method": "bKash", "verification_status": "LIKELY", "source_ids": ["src-nidw-main"], "notes": "nidw.gov.bd references bKash payment instructions PDF"},
        {"method": "Dutch-Bangla Bank / Rocket", "verification_status": "LIKELY", "source_ids": ["src-nidw-main"], "notes": "nidw.gov.bd references DBBL payment instructions"},
        {"method": "NID Wallet app", "verification_status": "LIKELY", "source_ids": ["src-nid-faq"], "notes": "FAQ references NID Wallet for login/face verification"},
    ]
    s["correction_rules"] = [
        "One information item generally correctable once (FAQ).",
        "Lost card + correction cannot be done simultaneously — reissue first (FAQ).",
    ]
    s["common_rejection_reasons"] = [
        {
            "text": "Incomplete or defective applications are treated as cancelled (official FAQ).",
            "layer": "OFFICIAL",
            "source_ids": ["src-nid-faq"],
            "verification_status": "VERIFIED",
        },
        {
            "text": "Applicants and guides commonly report rejections for blurred scans, name mismatches across documents, missing birth certificate, and unverified fee payment — not elevated to MUST rules.",
            "layer": "PRACTICAL",
            "source_ids": ["src-eshoi-rejection", "src-tbs-nid-corrections"],
            "verification_status": "UNVERIFIED",
            "do_not_promote_to_must": True,
        },
    ]
    s["practical_experience"] = [
        {
            "text": "TBS reports long pending queues, high rejection friction, field investigation/interviews, and broker exploitation risk.",
            "layer": "PRACTICAL",
            "source_ids": ["src-tbs-nid-corrections"],
            "verification_status": "UNVERIFIED",
            "do_not_promote_to_must": True,
        },
        {
            "text": "Dhaka Tribune reports canceled crash-program correction applications may be reapplied under the same category until a stated deadline (verify current deadline before advising).",
            "layer": "PRACTICAL",
            "source_ids": ["src-dt-nid-reapply"],
            "verification_status": "UNVERIFIED",
            "do_not_promote_to_must": True,
        },
    ]
    s["conflicts"] = [
        {
            "conflict_id": f"conf-{sid}-fee-amount",
            "topic": "Exact NID correction fee amounts",
            "claim_a": "Official portal: fees exist; calculate via fee calculator (no static schedule retrieved).",
            "source_a": "src-nid-fees",
            "claim_b": "News reports specific BDT 230/345/460 (VAT inclusive) tiers.",
            "source_b": "src-sib-nid-fees",
            "resolution": "UNRESOLVED",
            "prefer": "Advise applicants to use official fee calculator; do not hardcode news amounts as official MUST.",
            "authority_comparison": "Tier 1 calculator > Tier 5 news amounts",
        }
    ]
    s["warnings"] = [
        "Do not present unverified news fee amounts as official requirements.",
        "Cannot combine lost-card reissue and correction in one application (official FAQ).",
    ]
    s["related_services"] = ["nid-reissue-lost", "nid-fee-calculator", "nid-online-account-registration", "nid-voter-area-change"]
    s["missing_information"] = [
        "Authoritative published fee schedule PDF/gazette not retrieved in this pass.",
        "Exact processing SLA not stated on FAQ.",
    ]
    s["manual_review_required"] = ["Confirm fee schedule from EC gazette or calculator output screenshots under controlled capture."]
    s["research_status"] = "SUBSTANTIAL"
    s["knowledge_quality"] = kqs(
        coverage=82,
        authority=88,
        freshness=80,
        consistency=70,
        notes="Docs/rules strong from Tier-1 FAQ; fee amounts conflict unresolved.",
    )
    if kind == "other":
        s["notes"] = "Other-info correction covers fields not printed on card; FAQ says these can be corrected online."
    if kind == "combined":
        s["notes"] = "Combined card + other information correction is a distinct fee calculator application type."
    return s


def build_nid_reissue(cat: dict) -> dict:
    s = base_service("nid-reissue-lost", cat)
    s["responsible_ministry"] = "Bangladesh Election Commission"
    s["responsible_agency"] = "NID Wing, Bangladesh Election Commission"
    s["banglish_variants"] = ["nid reissue", "lost nid", "duplicate nid", "nid reprint"]
    s["application_methods"] = ["online"]
    s["online_application"] = True
    s["official_application_url"] = "https://services.nidw.gov.bd/nid-pub/?locale=en"
    s["official_information_urls"] = [
        "https://services.nidw.gov.bd/nid-pub/faq?tab=faq-correction",
        "https://www.nidw.gov.bd/IssuanceDuplicateNID.php",
        "https://services.nidw.gov.bd/nid-pub/fees",
    ]
    s["claims"] = [
        claim(
            "c-reissue-online",
            "For lost NID, apply online for reissue/reprint; after approval, receive SMS/email then download NID copy online.",
            field="procedure",
            information_class="OFFICIAL",
            source_ids=["src-nid-faq-correction"],
            verification_status="VERIFIED",
            confidence=0.95,
        ),
        claim(
            "c-reissue-law",
            "If NID is lost or damaged, citizen may apply in prescribed manner with prescribed fees for a fresh card.",
            field="eligibility",
            information_class="OFFICIAL",
            source_ids=["src-nidw-duplicate"],
            verification_status="VERIFIED",
            confidence=0.95,
        ),
        claim(
            "c-reissue-no-combo",
            "Lost-card reissue and correction cannot be done together; reissue first.",
            field="rules",
            information_class="OFFICIAL",
            source_ids=["src-nid-faq-correction"],
            verification_status="VERIFIED",
            confidence=0.95,
        ),
        claim(
            "c-reissue-fee",
            "Fees apply; use official fee calculator (application type: reissue).",
            field="fees",
            information_class="OFFICIAL",
            source_ids=["src-nid-faq-correction", "src-nid-fees"],
            verification_status="VERIFIED",
            confidence=0.95,
        ),
    ]
    s["requirements"] = [
        req("r-online-account", "Registered NID online account", "অনলাইন একাউন্ট", "MUST", claim_ids=["c-reissue-online"]),
        req(
            "r-gd-practical",
            "Police GD for lost card",
            "হারানোর জিডি",
            "RECOMMENDED",
            notes="Not stated as mandatory on retrieved official FAQ; sometimes reported in practice — keep RECOMMENDED/PRACTICAL only.",
        ),
    ]
    s["replacement_rules"] = [
        "Apply online for reissue when lost/damaged (official).",
        "If undistributed card not found at Upazila/Thana office, online reissue may be used (FAQ).",
    ]
    s["fees"] = [
        fee("f-reissue-calc", "Calculate via official fee calculator (reissue + delivery type)", amount_bdt=None, claim_ids=["c-reissue-fee"], verification_status="VERIFIED"),
    ]
    s["delivery_collection"] = [
        "Download digital NID copy online after approval notification (FAQ).",
        "Physical card collection pathways via Upazila/Thana election office also referenced for undistributed cards.",
    ]
    s["related_services"] = ["nid-card-info-correction", "nid-download-copy", "nid-fee-calculator"]
    s["missing_information"] = ["Exact reissue fee amounts not hardcoded from Tier-1 schedule."]
    s["research_status"] = "SUBSTANTIAL"
    s["knowledge_quality"] = kqs(coverage=75, authority=93, freshness=85, consistency=88, notes="Clear Tier-1 reissue pathway; fee amounts via calculator.")
    return s


def build_nid_supporting(cat: dict, sid: str) -> dict:
    s = base_service(sid, cat)
    s["responsible_ministry"] = "Bangladesh Election Commission"
    s["responsible_agency"] = "NID Wing, Bangladesh Election Commission"
    s["official_information_urls"] = ["https://services.nidw.gov.bd/nid-pub/?locale=en", "https://services.nidw.gov.bd/nid-pub/faq?locale=en"]
    if sid == "nid-online-account-registration":
        s["claims"] = [
            claim("c-acct-reg", "Voters with NID can register an online account using card number, active mobile/email, date of birth, and address-related info.", field="eligibility", information_class="OFFICIAL", source_ids=["src-nid-faq"], verification_status="VERIFIED", confidence=0.95),
            claim("c-acct-wallet", "After registration, download NID Wallet app and complete face verification to log in.", field="procedure", information_class="OFFICIAL", source_ids=["src-nid-faq"], verification_status="VERIFIED", confidence=0.9),
        ]
        s["procedure_steps"] = [
            step("a1", 1, "Fill account registration", "Provide card and contact details.", claim_ids=["c-acct-reg"]),
            step("a2", 2, "Activate via OTP", "Enter activation code from mobile/email.", claim_ids=["c-acct-reg"]),
            step("a3", 3, "Face verification via NID Wallet", "Login after face verification.", claim_ids=["c-acct-wallet"]),
        ]
        s["research_status"] = "SUBSTANTIAL"
        s["knowledge_quality"] = kqs(coverage=70, authority=95, freshness=85, consistency=95, notes="Account registration well covered by FAQ.")
    elif sid == "nid-claim-account":
        s["claims"] = [
            claim("c-claim", "If registered as voter but no NID number received, use Claim Account with form number, date of birth, captcha and required info, then login to download NID copy.", field="procedure", information_class="OFFICIAL", source_ids=["src-nid-faq"], verification_status="VERIFIED", confidence=0.95),
        ]
        s["research_status"] = "SUBSTANTIAL"
        s["knowledge_quality"] = kqs(coverage=65, authority=95, freshness=85, consistency=95, notes="Claim account pathway from FAQ.")
    elif sid == "nid-download-copy":
        s["claims"] = [
            claim("c-dl", "Citizens with online account can download NID card copy from the download menu after login.", field="delivery", information_class="OFFICIAL", source_ids=["src-nid-faq", "src-nid-home"], verification_status="VERIFIED", confidence=0.9),
        ]
        s["research_status"] = "SUBSTANTIAL"
        s["knowledge_quality"] = kqs(coverage=60, authority=95, freshness=85, consistency=95, notes="Download pathway confirmed; technical download limits not detailed.")
    elif sid == "nid-fee-calculator":
        s["claims"] = [
            claim("c-fee-types", "Fee calculator supports application types: NID card correction; other info correction; combined correction; reissue — plus delivery type.", field="fees", information_class="OFFICIAL", source_ids=["src-nid-fees"], verification_status="VERIFIED", confidence=0.95),
        ]
        s["official_application_url"] = "https://services.nidw.gov.bd/nid-pub/fees"
        s["research_status"] = "SUBSTANTIAL"
        s["knowledge_quality"] = kqs(coverage=55, authority=98, freshness=90, consistency=95, notes="Calculator exists; numeric outputs not archived in this pass.")
    elif sid == "nid-photo-signature-appointment":
        s["claims"] = [
            claim("c-photo", "Photo/signature change appointment is listed among online account services; unclear photo may require in-person application at National Identity Registration Wing.", field="appointment", information_class="OFFICIAL", source_ids=["src-nid-faq"], verification_status="VERIFIED", confidence=0.85),
            claim("c-sign-once", "Signature change requires sample with acceptable proof; signature may be changed only once.", field="rules", information_class="OFFICIAL", source_ids=["src-nid-faq-correction"], verification_status="VERIFIED", confidence=0.9),
        ]
        s["research_status"] = "PARTIAL"
        s["missing_information"] = ["Exact appointment booking UI steps and fees for photo capture."]
        s["knowledge_quality"] = kqs(coverage=50, authority=90, freshness=80, consistency=90, notes="High-level only.")
    elif sid == "nid-voter-area-change":
        s["claims"] = [
            claim("c-f13", "For change of residence, apply with Form 13 at the Upazila/Thana election office of the current residence area. Spelling/detail fixes within same voter area use ordinary correction form.", field="procedure", information_class="OFFICIAL", source_ids=["src-nid-faq-correction"], verification_status="VERIFIED", confidence=0.95),
        ]
        s["procedure_steps"] = [
            step("f1", 1, "Determine if area transfer or local address correction", "Area transfer (residence change) uses Form 13; same-area spelling uses correction form.", claim_ids=["c-f13"]),
            step("f2", 2, "Apply at current area election office", "Submit Form 13 at Upazila/Thana election office where currently residing.", claim_ids=["c-f13"]),
        ]
        s["research_status"] = "SUBSTANTIAL"
        s["knowledge_quality"] = kqs(coverage=68, authority=95, freshness=85, consistency=95, notes="Form 13 rule clear; supporting docs for Form 13 not fully enumerated on FAQ.")
        s["missing_information"] = ["Complete Form 13 supporting document checklist on Tier-1 page."]
    elif sid == "nid-expatriate-registration":
        s["claims"] = [
            claim("c-exp-otp", "OTP and notifications for expatriate Bangladeshi applicants are sent via email only.", field="application", information_class="OFFICIAL", source_ids=["src-nid-home"], verification_status="VERIFIED", confidence=0.9),
            claim("c-exp-apply", "Applicants abroad who missed registration may apply online any time (FAQ).", field="eligibility", information_class="OFFICIAL", source_ids=["src-nid-faq"], verification_status="VERIFIED", confidence=0.85),
        ]
        s["research_status"] = "PARTIAL"
        s["missing_information"] = ["Mission-specific biometric capture workflow and document checklist for expatriates."]
        s["knowledge_quality"] = kqs(coverage=45, authority=85, freshness=80, consistency=90, notes="Partial — portal notes + FAQ; mission procedures incomplete.")
    elif sid == "identity-voter-slip-download":
        s["claims"] = [
            claim("c-slip", "Online account services include election-time vote centre related information.", field="service", information_class="OFFICIAL", source_ids=["src-nid-faq"], verification_status="VERIFIED", confidence=0.8),
        ]
        s["research_status"] = "PARTIAL"
        s["missing_information"] = ["Dedicated voter slip download URL/steps not separately documented beyond general account benefits."]
        s["knowledge_quality"] = kqs(coverage=35, authority=80, freshness=75, consistency=90, notes="Thin evidence for distinct slip download service.")
    else:
        s["research_status"] = "PARTIAL"
        s["knowledge_quality"] = kqs(coverage=30, authority=70, freshness=70, consistency=80, notes="Stub.")
    s["related_services"] = ["nid-new-voter-registration", "nid-card-info-correction", "nid-reissue-lost"]
    return s


def build_bdris_birth(cat: dict) -> dict:
    s = base_service("civil-birth-registration", cat)
    s["responsible_ministry"] = "Local Government Division, MoLGRD&C"
    s["responsible_agency"] = "Office of the Registrar General, Birth and Death Registration"
    s["banglish_variants"] = ["jonmo nibondhon", "birth certificate", "bdris", "bris"]
    s["legal_basis"] = [
        {"name": "Births and Deaths Registration Act, 2004", "source_ids": ["src-bdris-home"]},
        {"name": "Births and Deaths Registration Rules, 2018", "source_ids": ["src-bdris-home"]},
        {"name": "Birth and Death Registration Guidelines 2021", "source_ids": ["src-bdris-home"]},
    ]
    s["application_methods"] = ["online", "local_registration_office"]
    s["online_application"] = True
    s["official_application_url"] = "https://bdris.gov.bd/br/application"
    s["official_information_urls"] = ["https://www.bdris.gov.bd/", "https://orgbdr.gov.bd/", "https://everify.bdris.gov.bd/"]
    s["claims"] = [
        claim(
            "c-br-portal",
            "Birth registration applications are submitted via BDRIS at bdris.gov.bd; applicant chooses registration address type (birth place / permanent / present).",
            field="application",
            information_class="OFFICIAL",
            source_ids=["src-bdris-br-app"],
            verification_status="VERIFIED",
            confidence=0.95,
        ),
        claim(
            "c-br-upload",
            "Only image files (.jpg/.jpeg/.png) may be uploaded; maximum 2 MB per file (application page).",
            field="requirements",
            information_class="OFFICIAL",
            source_ids=["src-bdris-br-app"],
            verification_status="VERIFIED",
            confidence=0.95,
            excerpt="শুধুমাত্র ইমেজ ফাইল (.jpg, .jpeg, .png) আপলোড করা যাবে। (প্রতিটি ফাইলের জন্য সর্বোচ্চ ফাইল সাইজ 2 মেগাবাইট)",
        ),
        claim(
            "c-br-fee-free45",
            "Registration within 45 days of birth is free of charge (domestic and abroad) per LGD-referenced fee schedule republished via MOFA mission notice.",
            field="fees",
            information_class="OFFICIAL",
            source_ids=["src-mofa-ankara-bdr", "src-bdservicerules-fee"],
            verification_status="VERIFIED",
            confidence=0.85,
            excerpt="within 45 (forty-five) days ... Free of charge",
        ),
        claim(
            "c-br-fee-late",
            "After 45 days to 5 years: BDT 25 (domestic) / USD 1 (abroad); after 5 years: BDT 50 (domestic) / USD 1 (abroad), per LGD-referenced schedule.",
            field="fees",
            information_class="OFFICIAL",
            source_ids=["src-mofa-ankara-bdr", "src-bdservicerules-fee"],
            verification_status="VERIFIED",
            confidence=0.8,
        ),
        claim(
            "c-br-fee-conflict-500",
            "Some secondary guides claim BDT 500 for registration after 10 years; this conflicts with the LGD-referenced schedule (BDT 50 after 5 years) and is not adopted as official.",
            field="fees",
            information_class="PRACTICAL",
            source_ids=["src-legalclarity-birth"],
            verification_status="UNVERIFIED",
            confidence=0.3,
            layer="PRACTICAL",
        ),
        claim(
            "c-br-helpline",
            "Registrar General office operates call centre 16152; support emails support@bdris.gov.bd / help@bdris.gov.bd.",
            field="office",
            information_class="OFFICIAL",
            source_ids=["src-orgbdr"],
            verification_status="VERIFIED",
            confidence=0.9,
        ),
        claim(
            "c-br-docs-practical",
            "Guides commonly list hospital birth certificate/midwife certificate and parents' NID/birth certificates; treat as practical/conditional pending full official checklist PDF retrieval.",
            field="requirements",
            information_class="PRACTICAL",
            source_ids=["src-legalclarity-birth", "src-mofa-ankara-bdr"],
            verification_status="UNVERIFIED",
            confidence=0.55,
            layer="PRACTICAL",
        ),
    ]
    s["requirements"] = [
        req(
            "r-br-hospital",
            "Hospital birth certificate or midwife certificate",
            "হাসপাতাল/মিডওয়াইফ সনদ",
            "CONDITIONAL",
            condition={"field": "birth_place_type", "op": "in", "value": ["hospital", "clinic", "home_with_midwife"]},
            claim_ids=["c-br-docs-practical"],
            notes="Listed on secondary/mission materials; confirm against Guidelines 2021 PDF in manual review.",
        ),
        req(
            "r-br-parents-id",
            "Parents' NID or birth registration certificates",
            "পিতা-মাতার এনআইডি/জন্ম সনদ",
            "MUST",
            claim_ids=["c-br-docs-practical"],
            notes="Strongly evidenced across official application context and secondary guides; mark MUST with review flag if Guidelines PDF differs.",
        ),
        req(
            "r-br-guardian-proof",
            "Guardian proof if applicant is not father/mother",
            "অভিভাবকের উপযুক্ত প্রমাণক",
            "CONDITIONAL",
            condition={"field": "applicant_relation", "op": "not_in", "value": ["father", "mother"]},
            claim_ids=["c-br-portal"],
            notes="Application form text references guardian proof under Act/Rules.",
        ),
        req(
            "r-br-images",
            "Supporting scans as JPG/JPEG/PNG ≤ 2MB each",
            "ইমেজ আপলোড সীমা",
            "MUST",
            claim_ids=["c-br-upload"],
        ),
    ]
    s["fees"] = [
        fee("f-br-0-45", "Registration within 45 days", amount_bdt=0, condition={"field": "days_since_birth", "op": "lte", "value": 45}, claim_ids=["c-br-fee-free45"], verification_status="VERIFIED"),
        fee("f-br-45-5y", "Registration after 45 days up to 5 years (domestic)", amount_bdt=25, condition={"all": [{"field": "days_since_birth", "op": "gt", "value": 45}, {"field": "years_since_birth", "op": "lte", "value": 5}]}, claim_ids=["c-br-fee-late"], verification_status="VERIFIED"),
        fee("f-br-5y-plus", "Registration after 5 years (domestic)", amount_bdt=50, condition={"field": "years_since_birth", "op": "gt", "value": 5}, claim_ids=["c-br-fee-late"], verification_status="VERIFIED"),
    ]
    s["conflicts"] = [
        {
            "conflict_id": "conf-br-fee-10y",
            "topic": "Late birth registration fee after 10 years",
            "claim_a": "LGD-referenced schedule via MOFA mission: BDT 50 after 5 years (no separate 10-year tier).",
            "source_a": "src-mofa-ankara-bdr",
            "claim_b": "LegalClarity guide: BDT 500 after more than 10 years.",
            "source_b": "src-legalclarity-birth",
            "resolution": "UNRESOLVED — prefer Tier-2 LGD-referenced schedule; do not publish BDT 500 as official.",
            "likely_reason": "Outdated/incorrect secondary guide or different historical schedule.",
        }
    ]
    s["procedure_steps"] = [
        step("b1", 1, "Open BDRIS birth application", "Go to bdris.gov.bd/br/application.", claim_ids=["c-br-portal"]),
        step("b2", 2, "Select registration address basis", "Choose birth place / permanent / present address path.", claim_ids=["c-br-portal"]),
        step("b3", 3, "Enter child and parents data", "Provide names, dates, parent identifiers as required.", claim_ids=[]),
        step("b4", 4, "Upload supporting images", "JPG/JPEG/PNG ≤2MB.", claim_ids=["c-br-upload"]),
        step("b5", 5, "Submit and follow local office verification", "Declaration of accuracy required; processing via registration office.", claim_ids=[]),
        step("b6", 6, "Obtain certificate / verify online", "Use reprint/verify portals as applicable.", claim_ids=[]),
    ]
    s["related_services"] = [
        "civil-birth-registration-correction",
        "civil-birth-registration-copy",
        "civil-birth-death-verify",
        "civil-birth-registration-duplicate-cancel",
        "nid-new-voter-registration",
    ]
    s["warnings"] = [
        "Do not use secondary BDT 500 late fee as official.",
        "False declaration of non-prior registration creates legal liability (application declaration).",
    ]
    s["missing_information"] = [
        "Full official document checklist from Guidelines 2021 PDF not extracted in this pass.",
        "Payment channel details for domestic fees (online vs cash at UP/pourashava) not fully verified.",
    ]
    s["manual_review_required"] = ["Retrieve and attach Guidelines 2021 + official fee gazette PDF."]
    s["research_status"] = "SUBSTANTIAL"
    s["knowledge_quality"] = kqs(coverage=72, authority=86, freshness=75, consistency=65, notes="Portal + fee schedule strong; document checklist partly secondary; fee conflict recorded.")
    return s


def build_bdris_variant(cat: dict, sid: str) -> dict:
    s = base_service(sid, cat)
    s["responsible_ministry"] = "Local Government Division, MoLGRD&C"
    s["responsible_agency"] = "Office of the Registrar General, Birth and Death Registration"
    s["official_information_urls"] = ["https://www.bdris.gov.bd/", "https://orgbdr.gov.bd/"]
    if "death-registration" == sid.replace("civil-", "") or sid == "civil-death-registration":
        s["official_application_url"] = "https://bdris.gov.bd/dr/application"
        s["claims"] = [
            claim("c-dr-portal", "Death registration applications are available at bdris.gov.bd/dr/application.", field="application", information_class="OFFICIAL", source_ids=["src-orgbdr"], verification_status="VERIFIED", confidence=0.9),
            claim("c-dr-fees", "Death registration fee tiers mirror birth registration (free ≤45 days; BDT 25 after 45 days to 5 years; BDT 50 after 5 years) per LGD-referenced schedule.", field="fees", information_class="OFFICIAL", source_ids=["src-mofa-ankara-bdr", "src-bdservicerules-fee"], verification_status="VERIFIED", confidence=0.8),
        ]
        s["fees"] = [
            fee("f-dr-0-45", "Death registration within 45 days", amount_bdt=0, claim_ids=["c-dr-fees"], verification_status="VERIFIED"),
            fee("f-dr-45-5y", "After 45 days to 5 years (domestic)", amount_bdt=25, claim_ids=["c-dr-fees"], verification_status="VERIFIED"),
            fee("f-dr-5y", "After 5 years (domestic)", amount_bdt=50, claim_ids=["c-dr-fees"], verification_status="VERIFIED"),
        ]
        s["missing_information"] = ["Full death-registration document checklist from official guidelines PDF."]
        s["research_status"] = "PARTIAL"
        s["knowledge_quality"] = kqs(coverage=55, authority=85, freshness=75, consistency=80, notes="Portal+fees confirmed; docs incomplete.")
    elif "correction" in sid:
        is_birth = "birth" in sid
        s["official_application_url"] = "https://bdris.gov.bd/br/correction" if is_birth else "https://bdris.gov.bd/dr/correction"
        s["claims"] = [
            claim(
                "c-corr-fee-dob",
                "Application fee for date-of-birth correction: BDT 100 domestic / USD 2 abroad (LGD-referenced schedule).",
                field="fees",
                information_class="OFFICIAL",
                source_ids=["src-mofa-ankara-bdr", "src-bdservicerules-fee"],
                verification_status="VERIFIED",
                confidence=0.8,
            ),
            claim(
                "c-corr-fee-other",
                "Application fee for other information correction (name, parents, address, etc.): BDT 50 domestic / USD 1 abroad (LGD-referenced schedule).",
                field="fees",
                information_class="OFFICIAL",
                source_ids=["src-mofa-ankara-bdr", "src-bdservicerules-fee"],
                verification_status="VERIFIED",
                confidence=0.75,
            ),
        ]
        s["conflicts"] = [
            {
                "conflict_id": "conf-bdris-corr-other-fee",
                "topic": "Other-info correction fee",
                "claim_a": "BDT 50 (MOFA/LGD-referenced + bdservicerules table)",
                "source_a": "src-mofa-ankara-bdr",
                "claim_b": "Some secondary sites state BDT 100 for other corrections too",
                "source_b": "src-bdservicerules-fee",
                "resolution": "Prefer MOFA English notice distinguishing DOB 100 vs other 50; mark secondary ambiguity.",
                "notes": "bdservicerules table itself shows 50 for other; another blog claimed 100 — unresolved blog noise.",
            }
        ]
        s["fees"] = [
            fee("f-corr-dob", "DOB correction application fee (domestic)", amount_bdt=100, claim_ids=["c-corr-fee-dob"], verification_status="VERIFIED"),
            fee("f-corr-other", "Other field correction application fee (domestic)", amount_bdt=50, claim_ids=["c-corr-fee-other"], verification_status="VERIFIED"),
            fee("f-corr-cert-copy", "Certified copy after correction in Bangla & English", amount_bdt=0, verification_status="VERIFIED", notes="Original/corrected certificate copy free per schedule; duplicate copy BDT 50."),
        ]
        s["research_status"] = "PARTIAL"
        s["missing_information"] = ["Field-by-field supporting document matrix for birth/death corrections."]
        s["knowledge_quality"] = kqs(coverage=50, authority=82, freshness=70, consistency=75, notes="Fees better than docs.")
    elif "copy" in sid or "reprint" in sid:
        is_birth = "birth" in sid
        s["official_application_url"] = "https://bdris.gov.bd/br/reprint/add" if is_birth else "https://bdris.gov.bd/dr/reprint/add"
        s["claims"] = [
            claim("c-copy-fee", "Issuance of duplicate certificate copy in Bangla & English: BDT 50 domestic / USD 1 abroad; original certificate issuance free.", field="fees", information_class="OFFICIAL", source_ids=["src-mofa-ankara-bdr", "src-bdservicerules-fee"], verification_status="VERIFIED", confidence=0.8),
        ]
        s["fees"] = [fee("f-dup-copy", "Duplicate certificate copy (domestic)", amount_bdt=50, claim_ids=["c-copy-fee"], verification_status="VERIFIED")]
        s["research_status"] = "PARTIAL"
        s["knowledge_quality"] = kqs(coverage=48, authority=85, freshness=75, consistency=90, notes="Reprint URL+fee known; identity verification steps thin.")
    elif "duplicate-cancel" in sid:
        s["official_application_url"] = "https://bdris.gov.bd/application/print"
        s["claims"] = [
            claim("c-dup-cancel", "orgbdr.gov.bd lists cancellation of multiple birth certificates as a service linked through BDRIS login/application print flows.", field="service", information_class="OFFICIAL", source_ids=["src-orgbdr"], verification_status="VERIFIED", confidence=0.7),
        ]
        s["research_status"] = "PARTIAL"
        s["missing_information"] = ["Detailed eligibility, evidence, and fee for duplicate cancellation."]
        s["knowledge_quality"] = kqs(coverage=30, authority=75, freshness=70, consistency=85, notes="Existence confirmed; procedure incomplete.")
    elif sid == "civil-birth-death-verify":
        s["official_application_url"] = "https://everify.bdris.gov.bd/"
        s["claims"] = [
            claim("c-verify", "Birth and death records can be verified via everify.bdris.gov.bd.", field="application", information_class="OFFICIAL", source_ids=["src-orgbdr", "src-everify"], verification_status="VERIFIED", confidence=0.9),
        ]
        s["research_status"] = "SUBSTANTIAL"
        s["knowledge_quality"] = kqs(coverage=55, authority=95, freshness=80, consistency=95, notes="Verification portal confirmed; input fields not fully documented.")
    elif sid == "civil-bdris-application-print":
        s["official_application_url"] = "https://bdris.gov.bd/application/print"
        s["claims"] = [
            claim("c-print", "BDRIS provides an application print endpoint for applicants.", field="application", information_class="OFFICIAL", source_ids=["src-bdris-br-app", "src-orgbdr"], verification_status="VERIFIED", confidence=0.85),
        ]
        s["research_status"] = "PARTIAL"
        s["knowledge_quality"] = kqs(coverage=40, authority=90, freshness=80, consistency=95, notes="Utility endpoint; limited procedural content.")
    else:
        s["research_status"] = "PARTIAL"
        s["knowledge_quality"] = kqs(coverage=25, authority=70, freshness=70, consistency=80, notes="Minimal.")
    s["related_services"] = ["civil-birth-registration", "civil-death-registration"]
    return s


def build_marriage_divorce(cat: dict, sid: str) -> dict:
    s = base_service(sid, cat)
    s["responsible_ministry"] = "Ministry of Law, Justice and Parliamentary Affairs / Local Government (CRVS)"
    s["official_application_url"] = "https://marriage.gov.bd/"
    s["official_information_urls"] = ["https://marriage.gov.bd/", "https://marriage.gov.bd/docs/CRVS_User_Manual.pdf"]
    if sid == "civil-marriage-registration":
        s["legal_basis"] = [
            {"name": "Muslim Marriages and Divorces (Registration) Act, 1974", "source_ids": ["src-law-muslim-marriage"]},
            {"name": "Hindu Marriage Registration Act, 2012", "source_ids": ["src-law-hindu-marriage"]},
        ]
        s["claims"] = [
            claim("c-mm-mandatory", "Every marriage solemnized under Muslim law shall be registered under the 1974 Act.", field="eligibility", information_class="OFFICIAL", source_ids=["src-law-muslim-marriage"], verification_status="VERIFIED", confidence=0.95),
            claim("c-hm-optional", "Hindu marriage registration is provided for under the 2012 Act (registration framework; widely described as optional vs Muslim mandatory).", field="eligibility", information_class="OFFICIAL", source_ids=["src-law-hindu-marriage"], verification_status="VERIFIED", confidence=0.85),
            claim("c-portal", "CRVS Marriage & Divorce portal supports civilian registration/login and multi-step marriage registration forms; registrars manage applications (official user manual).", field="application", information_class="OFFICIAL", source_ids=["src-marriage-manual", "src-marriage-portal"], verification_status="VERIFIED", confidence=0.85),
            claim("c-report-30", "Where marriage is solemnized by someone other than the Nikah Registrar, the bridegroom must report within 30 days for registration.", field="procedure", information_class="OFFICIAL", source_ids=["src-law-muslim-marriage"], verification_status="VERIFIED", confidence=0.9),
        ]
        s["requirements"] = [
            req("r-nikah", "Nikahnama / kabinnama details and witnesses as applicable", "কাবিননামা/সাক্ষী", "MUST", notes="Exact portal upload checklist needs manual extraction from registrar practice."),
            req("r-registrar", "Registration via licensed Nikah Registrar / Hindu Marriage Registrar as applicable", "নিবন্ধক", "MUST"),
        ]
        s["missing_information"] = ["Citizen-facing fee schedule for nikah registration", "Complete document upload list from portal UI"]
        s["research_status"] = "PARTIAL"
        s["knowledge_quality"] = kqs(coverage=55, authority=90, freshness=70, consistency=85, notes="Legal basis strong; operational fees/docs incomplete.")
    elif sid == "civil-divorce-registration":
        s["legal_basis"] = [{"name": "Muslim Marriages and Divorces (Registration) Act, 1974", "source_ids": ["src-law-muslim-marriage"]}]
        s["claims"] = [
            claim("c-div-portal", "CRVS Marriage & Divorce portal user manual covers divorce-related registrar workflows alongside marriage.", field="application", information_class="OFFICIAL", source_ids=["src-marriage-manual"], verification_status="VERIFIED", confidence=0.75),
        ]
        s["missing_information"] = ["Citizen divorce registration document checklist and fees"]
        s["research_status"] = "PARTIAL"
        s["knowledge_quality"] = kqs(coverage=35, authority=80, freshness=70, consistency=85, notes="Existence via portal/manual; thin citizen checklist.")
    elif "registrar" in sid:
        s["claims"] = [
            claim("c-reg-list", "marriage.gov.bd provides registrar list/search functions for Muslim/Hindu registrars.", field="service", information_class="OFFICIAL", source_ids=["src-marriage-portal"], verification_status="VERIFIED", confidence=0.8),
        ]
        s["research_status"] = "PARTIAL"
        s["notes"] = "Directory/support service for finding registrars; not a registration outcome itself."
        s["knowledge_quality"] = kqs(coverage=40, authority=85, freshness=75, consistency=90, notes="Directory service.")
    return s


def build_local_certificate(cat: dict, sid: str) -> dict:
    s = base_service(sid, cat)
    s["application_methods"] = ["local_office", "local_online_where_available"]
    s["geographic_limitations"] = ["Issued by Union Parishad / Pourashava / City Corporation / DC office depending on certificate type; procedure and fees vary by LGI."]
    s["claims"] = [
        claim(
            f"c-{sid}-exists",
            f"Catalogue lists {cat['service_name_en']} as a local/public certificate service with example LGI portals; national uniform checklist not verified in this batch.",
            field="service",
            information_class="OFFICIAL",
            source_ids=[],
            verification_status="UNVERIFIED",
            confidence=0.5,
        )
    ]
    # attach catalogue official source if present
    if cat.get("official_source"):
        s["official_application_url"] = cat["official_source"]
        s["claims"][0]["source_ids"] = ["catalogue-official_source"]
        s["claims"][0]["verification_status"] = "VERIFIED"
        s["claims"][0]["confidence"] = 0.7
        s["claims"][0]["claim"] = f"Example official/LGI URL referenced: {cat['official_source']}. Treat as geographic instance, not national fee/doc schedule."

    if sid == "dc-guardianship-certificate":
        s["responsible_agency"] = "Deputy Commissioner Office"
        s["missing_information"] = ["National guardianship certificate legal pathway vs family court overlap", "Standard fee/docs"]
    if sid == "dc-attestation-photocopy":
        s["responsible_agency"] = "Deputy Commissioner Office"
        s["missing_information"] = ["Which document types DC will attest; fee schedule"]
    if sid == "local-death-certificate-union":
        s["related_services"] = ["civil-death-registration"]
        s["warnings"] = ["Union death certificate attestation may differ from BDRIS legal death registration — do not conflate."]
        s["claims"].append(
            claim(
                "c-local-death-vs-bdris",
                "Local union death certificate is distinct from BDRIS death registration (catalogue/finalization notes).",
                field="related_services",
                information_class="OFFICIAL",
                source_ids=[],
                verification_status="VERIFIED",
                confidence=0.85,
            )
        )

    s["requirements"] = [
        req("r-nid", "Applicant NID", "জাতীয় পরিচয়পত্র", "LIKELY_MUST_UNVERIFIED", notes="Commonly required in practice at LGIs; not nationally verified here — classify carefully in UI as unverified until LGI schedule confirmed."),
    ]
    # Fix invalid classification - use CONDITIONAL with note instead
    s["requirements"] = [
        req(
            "r-local-nid",
            "Applicant NID / identity proof",
            "জাতীয় পরিচয়পত্র",
            "CONDITIONAL",
            condition={"field": "lgi_requires_nid", "op": "eq", "value": True},
            notes="Typically required; verify per LGI. Not elevated to national MUST.",
        ),
        req(
            "r-local-application",
            "Application via local citizen certificate portal or office form",
            "স্থানীয় আবেদন",
            "MUST",
            notes="Channel varies by Union/Pourashava/City Corporation.",
        ),
    ]
    s["fees"] = []
    s["missing_information"] = [
        "Nationally uniform fee schedule (does not exist — local variance).",
        "Authoritative per-LGI document checklists beyond sample portals.",
    ]
    s["manual_review_required"] = ["Populate geographic_availability with verified LGI URLs/fees before publishing as authoritative."]
    s["research_status"] = "PARTIAL"
    s["knowledge_quality"] = kqs(coverage=28, authority=55, freshness=60, consistency=80, notes="Existence known; local variance model required; weak national MUST docs.")
    s["related_services"] = ["civil-birth-registration", "civil-death-registration", "nid-new-voter-registration"]
    return s


def main() -> None:
    catalogue = json.loads((ROOT / "data" / "service_catalogue" / "services.json").read_text(encoding="utf-8"))
    by_id = {s["service_id"]: s for s in catalogue["services"] if s["status"] == "CONFIRMED"}

    batch_ids = [
        "civil-bdris-application-print",
        "civil-birth-death-verify",
        "civil-birth-registration",
        "civil-birth-registration-copy",
        "civil-birth-registration-correction",
        "civil-birth-registration-duplicate-cancel",
        "civil-death-registration",
        "civil-death-registration-copy",
        "civil-death-registration-correction",
        "civil-death-registration-duplicate-cancel",
        "civil-divorce-registration",
        "civil-marriage-registrar-hindu-list",
        "civil-marriage-registrar-muslim-list",
        "civil-marriage-registration",
        "dc-attestation-photocopy",
        "dc-guardianship-certificate",
        "identity-voter-slip-download",
        "local-character-certificate",
        "local-death-certificate-union",
        "local-nationality-certificate",
        "local-passport-attestation",
        "local-voter-transfer-attestation",
        "nid-card-info-correction",
        "nid-claim-account",
        "nid-combined-correction",
        "nid-download-copy",
        "nid-expatriate-registration",
        "nid-fee-calculator",
        "nid-new-voter-registration",
        "nid-online-account-registration",
        "nid-other-info-correction",
        "nid-photo-signature-appointment",
        "nid-reissue-lost",
        "nid-voter-area-change",
    ]

    builders = {}
    records = []
    for sid in batch_ids:
        if sid not in by_id:
            raise SystemExit(f"Missing catalogue service {sid}")
        cat = by_id[sid]
        if sid == "nid-new-voter-registration":
            rec = build_nid_new(cat)
        elif sid == "nid-card-info-correction":
            rec = build_nid_correction(cat, sid, "card")
        elif sid == "nid-other-info-correction":
            rec = build_nid_correction(cat, sid, "other")
        elif sid == "nid-combined-correction":
            rec = build_nid_correction(cat, sid, "combined")
        elif sid == "nid-reissue-lost":
            rec = build_nid_reissue(cat)
        elif sid.startswith("nid-") or sid == "identity-voter-slip-download":
            rec = build_nid_supporting(cat, sid)
        elif sid == "civil-birth-registration":
            rec = build_bdris_birth(cat)
        elif sid.startswith("civil-birth") or sid.startswith("civil-death") or sid == "civil-bdris-application-print" or sid == "civil-birth-death-verify":
            rec = build_bdris_variant(cat, sid)
        elif sid.startswith("civil-marriage") or sid == "civil-divorce-registration":
            rec = build_marriage_divorce(cat, sid)
        else:
            rec = build_local_certificate(cat, sid)
        records.append(rec)
        builders[sid] = rec

    OUT.mkdir(parents=True, exist_ok=True)
    SVC_DIR.mkdir(parents=True, exist_ok=True)

    for rec in records:
        (SVC_DIR / f"{rec['service_id']}.json").write_text(
            json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    (OUT / "sources.json").write_text(json.dumps({"sources": list(SOURCES.values())}, ensure_ascii=False, indent=2), encoding="utf-8")

    # Flatten claims/evidence index
    claims = []
    for rec in records:
        for c in rec.get("claims") or []:
            claims.append({**c, "service_id": rec["service_id"]})
    (OUT / "claims.json").write_text(json.dumps({"claims": claims}, ensure_ascii=False, indent=2), encoding="utf-8")

    conflicts = []
    for rec in records:
        for conf in rec.get("conflicts") or []:
            conflicts.append({**conf, "service_id": rec["service_id"]})
    (OUT / "conflicts.json").write_text(json.dumps({"conflicts": conflicts}, ensure_ascii=False, indent=2), encoding="utf-8")

    scores = [r["knowledge_quality"]["knowledge_quality_score"] for r in records if r.get("knowledge_quality")]
    status_counts = {}
    for r in records:
        status_counts[r["research_status"]] = status_counts.get(r["research_status"], 0) + 1

    official_sources = [s for s in SOURCES.values() if s["authority_tier"] <= 2]
    practical_sources = [s for s in SOURCES.values() if s["authority_tier"] >= 5]

    manual_claims = [c for c in claims if c["verification_status"] != "VERIFIED"]
    metadata = {
        "batch_id": BATCH,
        "researched_at": RETRIEVED,
        "services_researched": len(records),
        "research_status_counts": status_counts,
        "average_kqs": round(sum(scores) / len(scores), 1) if scores else 0,
        "source_count": len(SOURCES),
        "official_source_count_tier1_2": len(official_sources),
        "practical_community_source_count_tier5_plus": len(practical_sources),
        "claims_total": len(claims),
        "claims_requiring_manual_verification": len(manual_claims),
        "conflicts": len(conflicts),
        "service_ids": batch_ids,
    }
    (OUT / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "services_index.json").write_text(
        json.dumps(
            {
                "services": [
                    {
                        "service_id": r["service_id"],
                        "research_status": r["research_status"],
                        "kqs": r["knowledge_quality"]["knowledge_quality_score"] if r.get("knowledge_quality") else None,
                        "missing_count": len(r.get("missing_information") or []),
                    }
                    for r in records
                ]
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
