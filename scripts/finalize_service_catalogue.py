#!/usr/bin/env python3
"""Finalize and normalize the master service catalogue.

Applies verification decisions, merges, taxonomy, lifecycle metadata,
local-government geographic availability, and myGov mapping scaffold.

Does NOT collect requirements, fees, or procedures.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CATALOGUE_DIR = REPO_ROOT / "data" / "service_catalogue"
FINAL_DIR = CATALOGUE_DIR / "final"
BY_CATEGORY_DIR = CATALOGUE_DIR / "by_category"

TODAY = "2026-08-24"
CATALOGUE_VERSION = "1.0.0-finalized"

# ---------------------------------------------------------------------------
# Verification decisions for every LIKELY / NEEDS_VERIFICATION entry
# disposition: CONFIRMED | MERGED | DUPLICATE | DEPRECATED | NOT_A_SERVICE | UNVERIFIED
# ---------------------------------------------------------------------------

UNCERTAIN_DECISIONS: dict[str, dict] = {
    # --- CONFIRMED (credible official citizen/public service) ---
    "digital-ekpay-government-payment": {
        "disposition": "CONFIRMED",
        "official_source": "https://ekpay.gov.bd/",
        "reason": "Official a2i national P2G payment gateway (ekpay.gov.bd / support.ekpay.gov.bd).",
    },
    "police-general-diary-online": {
        "disposition": "CONFIRMED",
        "official_source": "https://gd.police.gov.bd/",
        "reason": "Official Bangladesh Police Online GD portal gd.police.gov.bd.",
    },
    "migration-e-apostille": {
        "disposition": "CONFIRMED",
        "reason": "Already had official apostille.mygov.bd; retained CONFIRMED.",
    },
    "disability-dis-registration": {
        "disposition": "CONFIRMED",
        "reason": "Official DIS portal dis.gov.bd; Rights of Persons with Disabilities Act pathway.",
    },
    "employment-boesl-overseas-recruitment": {
        "disposition": "CONFIRMED",
        "reason": "Official BOESL BRMS portal brms.boesl.gov.bd.",
    },
    "business-cooperative-society-registration": {
        "disposition": "CONFIRMED",
        "reason": "Official RDCD/Department of Cooperatives IDSDP service.rdcd.gov.bd.",
    },
    "permits-fire-e-license": {
        "disposition": "CONFIRMED",
        "reason": "Official Fire Service e-license elicense.fireservice.gov.bd.",
    },
    "permits-fire-noc-enoc": {
        "disposition": "CONFIRMED",
        "reason": "Official Fire Service e-NOC enoc.fireservice.gov.bd.",
    },
    "permits-fire-safety-firm-registration": {
        "disposition": "CONFIRMED",
        "reason": "Official Fire Service safety firm registration on enoc portal.",
    },
    "digital-mygov-citizen-registration": {
        "disposition": "CONFIRMED",
        "reason": "Official myGov.bd citizen account registration.",
    },
    "judiciary-supreme-court-e-filing": {
        "disposition": "CONFIRMED",
        "reason": "Official Supreme Court lawyers panel / mycase e-filing tutorial.",
    },
    "social-allowance-online-application": {
        "disposition": "CONFIRMED",
        "official_source": "https://mis.bhata.gov.bd/online-application",
        "reason": "DSS social allowance application portal mis.bhata.gov.bd used for OAA/widow/disability.",
    },
    "trade-erc-registration": {
        "disposition": "CONFIRMED",
        "reason": "CCIE OLM portal olm.ccie.gov.bd for ERC.",
    },
    "land-deed-registration": {
        "disposition": "CONFIRMED",
        "reason": "Registration Act / Sub-Registrar deed registration is a core citizen service; land.gov.bd references.",
    },
    "civil-divorce-registration": {
        "disposition": "CONFIRMED",
        "reason": "CRVS/marriage.gov.bd documentation references divorce registration pathway.",
    },
    "dc-district-e-application": {
        "disposition": "CONFIRMED",
        "official_source": "http://online.forms.gov.bd/",
        "reason": "District online forms portal online.forms.gov.bd is a real citizen application channel.",
    },
    "dc-attestation-photocopy": {
        "disposition": "CONFIRMED",
        "reason": "DC office document attestation is a standard district citizen service.",
    },
    "dc-guardianship-certificate": {
        "disposition": "CONFIRMED",
        "reason": "Guardianship certificate via DC office is a documented district citizen service.",
    },
    "health-16263-telemedicine": {
        "disposition": "CONFIRMED",
        "reason": "DGHS national telemedicine helpline 16263 is a known citizen health service.",
    },
    "health-private-clinic-license": {
        "disposition": "CONFIRMED",
        "reason": "DGHS hospitaldghs.gov.bd private clinic licensing.",
    },
    "health-private-hospital-license": {
        "disposition": "CONFIRMED",
        "reason": "DGHS hospitaldghs.gov.bd private hospital licensing.",
    },
    "education-duplicate-certificate": {
        "disposition": "CONFIRMED",
        "reason": "Education board Controllers issue duplicate certificates; board rules document the service.",
    },
    "hajj-call-center": {
        "disposition": "CONFIRMED",
        "reason": "Already CONFIRMED in prior pass; helpline is a citizen service channel.",
    },
    "women-child-helpline-1098": {
        "disposition": "CONFIRMED",
        "reason": "National child helpline 1098 is an established MoWCA citizen service.",
    },
    "women-one-stop-crisis-centre": {
        "disposition": "CONFIRMED",
        "reason": "OCC network under MoWCA is an established G2C support service.",
    },
    "women-lactating-mothers-allowance": {
        "disposition": "CONFIRMED",
        "reason": "DWA Working Lactating Mothers Allowance is a documented programme/service.",
    },
    "women-ngo-registration": {
        "disposition": "CONFIRMED",
        "reason": "DWA voluntary women organization registration is documented on dwa.portal.gov.bd.",
    },
    "customs-asycuda-declaration": {
        "disposition": "CONFIRMED",
        "reason": "ASYCUDA World customs declaration is the national customs filing system.",
    },
    "customs-bond-up-application": {
        "disposition": "CONFIRMED",
        "reason": "NBR customs UP user manual confirms Bond Utilization Permit application.",
    },
    "customs-import-export-control-licence": {
        "disposition": "CONFIRMED",
        "reason": "Import/Export Control Act licence pathway documented via NBR/CCIE materials.",
    },
    "titas-industry-gas-connection": {
        "disposition": "CONFIRMED",
        "reason": "Titas online application portal for industry/captive power connections.",
    },
    "bpdb-high-tension-connection": {
        "disposition": "CONFIRMED",
        "reason": "BPDB high-tension connection is a standard utility application service.",
    },
    "police-character-certificate": {
        "disposition": "CONFIRMED",
        "reason": "Police clearance / character certificate is an established police citizen service.",
    },
    "police-passport-police-verification": {
        "disposition": "CONFIRMED",
        "reason": "Passport police verification is a required DIP/police pathway for e-passport.",
    },
    "police-nid-address-verification": {
        "disposition": "CONFIRMED",
        "reason": "Address/NID-based police verification is a documented police citizen verification service.",
    },
    "professional-bar-council-enrolment": {
        "disposition": "CONFIRMED",
        "reason": "Bangladesh Bar Council advocate enrolment is the statutory professional pathway.",
    },
    "professional-bmdc-doctor-registration": {
        "disposition": "CONFIRMED",
        "reason": "BMDC doctor registration is the statutory medical licensing service.",
    },
    "professional-nursing-council-registration": {
        "disposition": "CONFIRMED",
        "reason": "BNMC registration is the statutory nursing/midwifery licensing service.",
    },
    "professional-pharmacy-council-registration": {
        "disposition": "CONFIRMED",
        "reason": "Pharmacy Council registration is the statutory pharmacist licensing service.",
    },
    "tax-income-tax-return-filing": {
        "disposition": "CONFIRMED",
        "reason": "NBR income tax return filing is a core citizen/business tax service.",
    },
    "tax-source-tax-deduction-certificate": {
        "disposition": "CONFIRMED",
        "reason": "TDS/AIT certificate issuance is a standard NBR tax service.",
    },
    "vat-return-filing": {
        "disposition": "CONFIRMED",
        "reason": "VAT Mushak return filing is a core NBR business tax service.",
    },
    "trade-bsti-standard-certification": {
        "disposition": "CONFIRMED",
        "reason": "BSTI product/CM mark certification is a statutory business service.",
    },
    "trade-dpd-trademark-registration": {
        "disposition": "CONFIRMED",
        "reason": "DPDT trademark registration is a statutory IP service.",
    },
    "trade-dpd-patent-registration": {
        "disposition": "CONFIRMED",
        "reason": "DPDT patent registration is a statutory IP service.",
    },
    "business-ngoab-ngo-registration": {
        "disposition": "CONFIRMED",
        "reason": "NGO Affairs Bureau NGO registration is a statutory organization service.",
    },
    "housing-cda-building-permit": {
        "disposition": "CONFIRMED",
        "reason": "CDA building plan approval is a real development-authority permit service.",
    },
    "housing-nha-allotment-application": {
        "disposition": "CONFIRMED",
        "reason": "NHA flat allotment applications are periodic but real public housing services.",
    },
    "transport-route-permit": {
        "disposition": "CONFIRMED",
        "reason": "BRTA route permit is a standard operator licensing service on BSP.",
    },
    "transport-driving-school-licence": {
        "disposition": "CONFIRMED",
        "reason": "BRTA driving school/training centre licence is a BSP licensing service.",
    },
    "migration-visa-application-dip": {
        "disposition": "CONFIRMED",
        "reason": "DIP visa services at Divisional Passport and Visa offices are real.",
    },
    "judiciary-supreme-court-certified-copy": {
        "disposition": "CONFIRMED",
        "reason": "Supreme Court certified copy applications are a documented registry service.",
    },
    "judiciary-case-status-tracking": {
        "disposition": "CONFIRMED",
        "reason": "Case status / tracking via Supreme Court digital systems is a citizen/lawyer service.",
    },
    "identity-voter-slip-download": {
        "disposition": "CONFIRMED",
        "reason": "EC NID services include voter information slip retrieval.",
    },
    "election-candidate-nomination": {
        "disposition": "CONFIRMED",
        "reason": "EC candidate nomination is a statutory electoral service (periodic).",
    },
    "health-immunization-card-mcv": {
        "disposition": "CONFIRMED",
        "reason": "EPI immunization card issuance is a core DGHS/EPI childhood health service.",
    },
    "health-hospital-birth-notification": {
        "disposition": "CONFIRMED",
        "reason": "Hospital birth notification feeds BDRIS; real institutional G2C pathway.",
    },
    "education-ugc-university-recognition": {
        "disposition": "CONFIRMED",
        "reason": "UGC publishes and verifies recognized university/institution lists.",
    },
    "agriculture-livestock-farm-registration": {
        "disposition": "CONFIRMED",
        "reason": "DLS livestock farm registration is a departmental citizen/business service.",
    },
    "agriculture-fisheries-fish-farm-registration": {
        "disposition": "CONFIRMED",
        "reason": "DoF fish farm registration is a departmental citizen/business service.",
    },
    "environment-forest-clearance": {
        "disposition": "CONFIRMED",
        "reason": "Forest Department clearance/permits are real environmental authorizations.",
    },
    "permits-forest-timber-transit": {
        "disposition": "CONFIRMED",
        "reason": "Forest timber transit permits are established Forest Department services.",
    },
    "food-ministry-vgf-card": {
        "disposition": "CONFIRMED",
        "reason": "VGF/food assistance card distribution is a Ministry of Food safety-net service.",
    },
    "bida-aftercare-services": {
        "disposition": "CONFIRMED",
        "reason": "BIDA aftercare is a documented investor-facing service under BIDA OSS.",
    },
    "bida-commercial-office-services": {
        "disposition": "CONFIRMED",
        "reason": "BIDA branch/liaison/representative office services are OSS investment services.",
    },
    "expatriate-bmet-training": {
        "disposition": "CONFIRMED",
        "reason": "BMET skill development training is a documented expatriate labour service.",
    },
    "expatriate-worker-registration": {
        "disposition": "CONFIRMED",
        "reason": "BMET overseas worker registration is a core emigration service.",
    },
    "land-partition-consolidation": {
        "disposition": "CONFIRMED",
        "reason": "Land partition/consolidation via Ministry of Land is a citizen land service.",
    },
    "local-upazila-land-tax-payment": {
        "disposition": "CONFIRMED",
        "reason": "Land development tax payment at upazila/union land offices is a core local service.",
    },
    "local-unno-digital-upazila-services": {
        "disposition": "CONFIRMED",
        "reason": "UNO office provides multiple citizen charter services; retained as umbrella local channel.",
    },
    "digital-centre-assisted-services": {
        "disposition": "CONFIRMED",
        "reason": "Digital centres deliver assisted e-services; real G2C access channel.",
    },
    "legal-aid-panel-lawyer-list": {
        "disposition": "CONFIRMED",
        "reason": "NLASO panel lawyer lists support legal aid application; retained as supporting service.",
    },
    "health-blood-bank-license": {
        "disposition": "CONFIRMED",
        "reason": "DGHS blood bank licensing is a regulated health facility service.",
    },
    "health-diagnostic-center-license": {
        "disposition": "CONFIRMED",
        "reason": "DGHS diagnostic/pathology centre licensing is a regulated health facility service.",
    },
    "agri-e-pesticide-prescription": {
        "disposition": "CONFIRMED",
        "reason": "DAE e-pesticide prescription referenced on DAE district portals.",
    },
    "agri-farmer-digital-address": {
        "disposition": "CONFIRMED",
        "reason": "Farmer digital address service referenced on DAE district portals.",
    },
    "employment-trade-union-registration": {
        "disposition": "CONFIRMED",
        "reason": "Trade union registration under Department of Labour is a statutory labour service.",
    },
    "employment-labour-court-adr": {
        "disposition": "CONFIRMED",
        "reason": "Labour court ADR announced/implemented under MoLE; treated as real dispute pathway.",
    },
    "judiciary-virtual-court-services": {
        "disposition": "CONFIRMED",
        "reason": "Virtual court hearings are an established judiciary digital service channel.",
    },
    "professional-engineer-registration": {
        "disposition": "CONFIRMED",
        "reason": "IEB professional engineer membership/registration is the national engineering body pathway.",
    },
    "digital-challan-treasury-payment": {
        "disposition": "CONFIRMED",
        "official_source": "https://www.achallan.gov.bd/",
        "reason": "A-challan / automated treasury challan is the government payment channel for duties/fees.",
    },
    # --- MERGED (geographic variants → canonical) ---
    "local-dncc-holding-tax": {
        "disposition": "MERGED",
        "canonical_service_id": "local-holding-tax-payment",
        "geo": {
            "tier": "CITY_CORPORATION",
            "name_en": "Dhaka North City Corporation",
            "name_bn": "ঢাকা উত্তর সিটি কর্পোরেশন",
            "availability": "AVAILABLE",
            "url": "https://dncc.gov.bd/",
        },
        "reason": "Geographic delivery of holding tax, not a distinct service type.",
    },
    "local-dscc-holding-tax": {
        "disposition": "MERGED",
        "canonical_service_id": "local-holding-tax-payment",
        "geo": {
            "tier": "CITY_CORPORATION",
            "name_en": "Dhaka South City Corporation",
            "name_bn": "ঢাকা দক্ষিণ সিটি কর্পোরেশন",
            "availability": "AVAILABLE",
            "url": "https://dscc.gov.bd/",
        },
        "reason": "Geographic delivery of holding tax.",
    },
    "local-ccc-holding-tax": {
        "disposition": "MERGED",
        "canonical_service_id": "local-holding-tax-payment",
        "geo": {
            "tier": "CITY_CORPORATION",
            "name_en": "Chattogram City Corporation",
            "name_bn": "চট্টগ্রাম সিটি কর্পোরেশন",
            "availability": "AVAILABLE",
            "url": None,
            "notes": "Amader Chattogram / Shapla OSS references holding tax.",
        },
        "reason": "Geographic delivery of holding tax.",
    },
    "local-pourashava-holding-tax": {
        "disposition": "MERGED",
        "canonical_service_id": "local-holding-tax-payment",
        "geo": {
            "tier": "MUNICIPALITY",
            "name_en": "Municipality / Pourashava (generic)",
            "name_bn": "পৌরসভা",
            "availability": "AVAILABLE",
            "url": None,
        },
        "reason": "Geographic delivery of holding tax at pourashava tier.",
    },
    "local-ccc-trade-licence": {
        "disposition": "MERGED",
        "canonical_service_id": "licence-trade-local-government",
        "geo": {
            "tier": "CITY_CORPORATION",
            "name_en": "Chattogram City Corporation",
            "name_bn": "চট্টগ্রাম সিটি কর্পোরেশন",
            "availability": "AVAILABLE",
            "url": None,
        },
        "reason": "Same service type as other LGI trade licences; geography differs.",
    },
    # --- NOT_A_SERVICE ---
    "religious-mora-portal": {
        "disposition": "NOT_A_SERVICE",
        "reason": "Ministry portal/overview page, not a distinct citizen service outcome.",
    },
    "dm-knowledge-portal": {
        "disposition": "NOT_A_SERVICE",
        "reason": "Knowledge portal / information site, not a transactional citizen service.",
    },
    "education-madrasah-board-services": {
        "disposition": "NOT_A_SERVICE",
        "reason": "Agency/board umbrella label; individual board services should be separate.",
    },
    "education-technical-board-services": {
        "disposition": "NOT_A_SERVICE",
        "reason": "Agency/board umbrella label; not a single service outcome.",
    },
    "mygov-national-portal": {
        "disposition": "NOT_A_SERVICE",
        "reason": "myGov is an access channel/portal, not a service outcome. Account registration retained separately.",
    },
    # --- UNVERIFIED (keep but do not promote) ---
    "agri-seed-certification": {
        "disposition": "UNVERIFIED",
        "reason": "BADC portal exists but specific seed certification e-service URL not individually verified.",
    },
    "certificates-freedom-fighter-certificate": {
        "disposition": "UNVERIFIED",
        "reason": "Issuance/correction pathway distinct from MIS/allowance not confirmed with primary URL.",
    },
    "dc-armed-forces-property-noc": {
        "disposition": "UNVERIFIED",
        "reason": "Niche DC NOC; circular-level evidence only.",
    },
    "education-public-university-admission": {
        "disposition": "UNVERIFIED",
        "reason": "No single national admission service; university-specific portals vary annually.",
    },
    "employment-district-employment-exchange": {
        "disposition": "UNVERIFIED",
        "reason": "2026 MoLE rollout announced; nationwide operational status not confirmed.",
    },
    "expatriate-bmet-demand-verification": {
        "disposition": "UNVERIFIED",
        "reason": "Service name inferred; dedicated public application URL not confirmed.",
    },
    "judiciary-artha-rin-salish": {
        "disposition": "UNVERIFIED",
        "reason": "Artha Rin Adalat exists in law; citizen-facing digital service entry not confirmed.",
    },
    "judiciary-family-court-services": {
        "disposition": "UNVERIFIED",
        "reason": "Family courts exist; catalogue entry is too broad without a concrete application path.",
    },
    "land-e-stamp-payment": {
        "disposition": "UNVERIFIED",
        "reason": "Stamp duty / A-challan transition underway; dedicated e-stamp citizen portal URL not verified.",
    },
    "religious-waqf-services": {
        "disposition": "UNVERIFIED",
        "reason": "Waqf administration exists; specific citizen service endpoints not verified.",
    },
}

# CONFIRMED services that should be reclassified as NOT_A_SERVICE or MERGED
CONFIRMED_CLEANUP: dict[str, dict] = {
    "bida-oss-portal": {
        "disposition": "MERGED",
        "canonical_service_id": "bida-invest-bangladesh-oss",
        "reason": "Duplicate OSS portal entry; merge into Invest Bangladesh OSS.",
    },
    "bida-oss-available-services": {
        "disposition": "NOT_A_SERVICE",
        "reason": "Catalogue/list page of services, not a service outcome.",
    },
    "env-ecc-how-to-apply": {
        "disposition": "NOT_A_SERVICE",
        "reason": "Application guide/information page for ECC, not a separate service.",
    },
    "env-ecc-portal-info": {
        "disposition": "NOT_A_SERVICE",
        "reason": "Information page for DoE online clearance.",
    },
    "env-eia-guidelines": {
        "disposition": "NOT_A_SERVICE",
        "reason": "Guidelines document, not a citizen application service.",
    },
    "mofa-attestation-application-form": {
        "disposition": "MERGED",
        "canonical_service_id": "mofa-document-attestation",
        "reason": "Form artifact for MOFA attestation; merge into attestation service.",
    },
    "mofa-document-attestation-requirements": {
        "disposition": "MERGED",
        "canonical_service_id": "mofa-document-attestation",
        "reason": "Requirements page for MOFA attestation.",
    },
    "mofa-mygov-services": {
        "disposition": "NOT_A_SERVICE",
        "reason": "myGov directory listing for MOFA, not a service outcome.",
    },
    "mofa-citizen-eservices": {
        "disposition": "NOT_A_SERVICE",
        "reason": "Ministry e-services landing/overview, not a single service.",
    },
    "hajj-registration-portal": {
        "disposition": "MERGED",
        "canonical_service_id": "hajj-pre-registration",
        "reason": "Portal access for Hajj registration; canonical outcome is pre-registration/registration.",
    },
    "ff-welfare-trust-portal": {
        "disposition": "NOT_A_SERVICE",
        "reason": "Trust portal homepage, not a distinct enrollment service (enrollment kept).",
    },
    "ff-mis-login": {
        "disposition": "MERGED",
        "canonical_service_id": "ff-mis-freedom-fighter-list",
        "reason": "MIS login is access method for freedom fighter list/verification.",
    },
    "digital-centre-list": {
        "disposition": "NOT_A_SERVICE",
        "reason": "Directory of centres, not a service outcome.",
    },
    "civil-marriage-registrar-directory": {
        "disposition": "NOT_A_SERVICE",
        "reason": "Registrar directory/lookup, not a registration service.",
    },
    "legal-aid-office-management": {
        "disposition": "NOT_A_SERVICE",
        "reason": "Internal office management portal; not citizen-facing outcome.",
    },
    "licence-trade-dncc": {
        "disposition": "MERGED",
        "canonical_service_id": "licence-trade-local-government",
        "geo": {
            "tier": "CITY_CORPORATION",
            "name_en": "Dhaka North City Corporation",
            "name_bn": "ঢাকা উত্তর সিটি কর্পোরেশন",
            "availability": "AVAILABLE",
            "url": "https://dncc.gov.bd/",
        },
        "reason": "Geographic variant of LGI trade licence.",
    },
    "licence-trade-dscc": {
        "disposition": "MERGED",
        "canonical_service_id": "licence-trade-local-government",
        "geo": {
            "tier": "CITY_CORPORATION",
            "name_en": "Dhaka South City Corporation",
            "name_bn": "ঢাকা দক্ষিণ সিটি কর্পোরেশন",
            "availability": "AVAILABLE",
            "url": "https://dscc.gov.bd/",
        },
        "reason": "Geographic variant of LGI trade licence.",
    },
    "licence-trade-municipality": {
        "disposition": "MERGED",
        "canonical_service_id": "licence-trade-local-government",
        "geo": {
            "tier": "MUNICIPALITY",
            "name_en": "Municipality / Pourashava (generic)",
            "name_bn": "পৌরসভা",
            "availability": "AVAILABLE",
            "url": None,
        },
        "reason": "Geographic variant of LGI trade licence.",
    },
    "licence-trade-union-parishad": {
        "disposition": "MERGED",
        "canonical_service_id": "licence-trade-local-government",
        "geo": {
            "tier": "UNION",
            "name_en": "Union Parishad (generic)",
            "name_bn": "ইউনিয়ন পরিষদ",
            "availability": "AVAILABLE",
            "url": None,
        },
        "reason": "Geographic variant of LGI trade licence.",
    },
    "business-trade-license-renewal": {
        "disposition": "MERGED",
        "canonical_service_id": "licence-trade-local-government",
        "reason": "Renewal is a procedure variant of the same trade licence service outcome.",
    },
    "business-startup-trade-licence-guidance": {
        "disposition": "NOT_A_SERVICE",
        "reason": "Guidance sequence across multiple services (trade licence, TIN, VAT), not one service.",
    },
}

# New canonical services created to absorb geographic merges
NEW_CANONICAL: list[dict] = [
    {
        "service_id": "local-holding-tax-payment",
        "service_name_bn": "স্থানীয় সরকার হোল্ডিং ট্যাক্স পরিশোধ",
        "service_name_en": "Local Government Holding Tax Payment",
        "aliases": [
            "holding tax",
            "হোল্ডিং ট্যাক্স",
            "municipal holding tax",
            "city corporation holding tax",
        ],
        "category": "LOCAL_GOVERNMENT",
        "subcategory": "holding_tax",
        "responsible_authority": "City Corporation / Municipality / Pourashava",
        "authority_id": "local-government-institutions",
        "target_user": ["citizen", "property_owner"],
        "geographic_scope": "LOCAL",
        "lifecycle_stage": ["property", "tax"],
        "official_source": "https://dncc.gov.bd/",
        "discovery_sources": [
            "https://dncc.gov.bd/",
            "https://dscc.gov.bd/",
        ],
        "status": "CONFIRMED",
        "notes": "Canonical holding-tax service. Delivery varies by LGI; see geographic_availability.",
        "geographic_availability": [],
    },
    {
        "service_id": "licence-trade-local-government",
        "service_name_bn": "স্থানীয় সরকার ট্রেড লাইসেন্স",
        "service_name_en": "Local Government Trade Licence",
        "aliases": [
            "trade licence",
            "trade license",
            "ট্রেড লাইসেন্স",
            "business licence LGI",
        ],
        "category": "LICENCES",
        "subcategory": "trade_licence",
        "responsible_authority": "City Corporation / Municipality / Union Parishad",
        "authority_id": "local-government-institutions",
        "target_user": ["business", "citizen"],
        "geographic_scope": "LOCAL",
        "lifecycle_stage": ["business"],
        "official_source": "https://dncc.gov.bd/",
        "discovery_sources": [
            "https://dncc.gov.bd/",
            "https://dscc.gov.bd/",
        ],
        "status": "CONFIRMED",
        "notes": "Canonical LGI trade licence (issue + renew). See geographic_availability for LGIs.",
        "geographic_availability": [],
    },
    {
        "service_id": "mofa-document-attestation",
        "service_name_bn": "পররাষ্ট্র মন্ত্রণালয় নথি সত্যায়ন",
        "service_name_en": "MOFA Document Attestation",
        "aliases": [
            "MOFA attestation",
            "consular attestation",
            "document legalization MOFA",
            "নথি সত্যায়ন",
        ],
        "category": "PASSPORT_IMMIGRATION",
        "subcategory": "attestation",
        "responsible_authority": "Ministry of Foreign Affairs (MOFA) - Consular Section",
        "authority_id": "mofa",
        "target_user": ["citizen", "student", "business"],
        "geographic_scope": "NATIONAL",
        "lifecycle_stage": ["education", "employment"],
        "official_source": "https://csat.mofa.gov.bd/",
        "discovery_sources": [
            "https://csat.mofa.gov.bd/",
            "https://file.mofa.gov.bd/media/ea12c69b-b861-499a-a54f-ff0fb0fd6539/Attestation/General-Requiremnts-for-Documents-Attestation.pdf",
        ],
        "status": "CONFIRMED",
        "notes": "Canonical MOFA attestation. e-Apostille is a related but distinct service.",
        "geographic_availability": [],
    },
]

TAXONOMY: list[dict] = [
    {"category_id": "identity", "name_en": "Identity & Elections", "name_bn": "পরিচয় ও নির্বাচন", "description": "NID, voter, election services", "parent_category": None},
    {"category_id": "civil_registration", "name_en": "Civil Registration", "name_bn": "নাগরিক নিবন্ধন", "description": "Birth, death, marriage, divorce registration", "parent_category": None},
    {"category_id": "passport_immigration", "name_en": "Passport & Immigration", "name_bn": "পাসপোর্ট ও অভিবাসন", "description": "Passport, visa, attestation, apostille", "parent_category": None},
    {"category_id": "expatriate", "name_en": "Expatriate Labour", "name_bn": "প্রবাসী শ্রম", "description": "Overseas employment and expatriate welfare", "parent_category": None},
    {"category_id": "employment", "name_en": "Employment & Labour", "name_bn": "কর্মসংস্থান ও শ্রম", "description": "Domestic employment, labour relations", "parent_category": None},
    {"category_id": "education", "name_en": "Education", "name_bn": "শিক্ষা", "description": "Boards, scholarships, higher education", "parent_category": None},
    {"category_id": "health", "name_en": "Health", "name_bn": "স্বাস্থ্য", "description": "Healthcare licensing, telemedicine, immunization", "parent_category": None},
    {"category_id": "disability", "name_en": "Disability Services", "name_bn": "প্রতিবন্ধী সেবা", "description": "Disability registration and related benefits access", "parent_category": "social_protection"},
    {"category_id": "social_protection", "name_en": "Social Protection", "name_bn": "সামাজিক সুরক্ষা", "description": "Allowances, stipends, safety-net programmes", "parent_category": None},
    {"category_id": "women_children", "name_en": "Women & Children", "name_bn": "নারী ও শিশু", "description": "Women and child protection and support services", "parent_category": None},
    {"category_id": "land", "name_en": "Land & Property Records", "name_bn": "ভূমি ও সম্পত্তি রেকর্ড", "description": "Mutation, khatian, deed registration, land tax", "parent_category": None},
    {"category_id": "housing", "name_en": "Housing & Development Control", "name_bn": "গৃহায়ন ও উন্নয়ন নিয়ন্ত্রণ", "description": "Building permits, housing allotments", "parent_category": None},
    {"category_id": "local_government", "name_en": "Local Government", "name_bn": "স্থানীয় সরকার", "description": "City corporation, pourashava, union, DC/UNO citizen services", "parent_category": None},
    {"category_id": "certificates", "name_en": "Public Certificates", "name_bn": "সনদ ও প্রত্যয়ন", "description": "Citizen certificates issued by government bodies", "parent_category": None},
    {"category_id": "licences", "name_en": "Licences", "name_bn": "লাইসেন্স", "description": "Trade and other operating licences", "parent_category": None},
    {"category_id": "permits", "name_en": "Permits & Clearances", "name_bn": "অনুমতি ও ছাড়পত্র", "description": "Fire, forest, and other permits/NOCs", "parent_category": None},
    {"category_id": "registrations", "name_en": "Registrations", "name_bn": "নিবন্ধন", "description": "Organization, IP, cooperative, and other registrations", "parent_category": None},
    {"category_id": "business", "name_en": "Business Formation", "name_bn": "ব্যবসা গঠন", "description": "Company and business startup services", "parent_category": None},
    {"category_id": "investment", "name_en": "Investment", "name_bn": "বিনিয়োগ", "description": "BIDA and related investment services", "parent_category": None},
    {"category_id": "trade", "name_en": "Trade & Standards", "name_bn": "বাণিজ্য ও মান", "description": "ERC/IRC, BSTI, trade facilitation", "parent_category": None},
    {"category_id": "tax", "name_en": "Income Tax", "name_bn": "আয়কর", "description": "e-TIN, returns, withholding certificates", "parent_category": None},
    {"category_id": "vat", "name_en": "VAT", "name_bn": "মূসক/ভ্যাট", "description": "VAT registration and returns", "parent_category": None},
    {"category_id": "customs", "name_en": "Customs", "name_bn": "শুল্ক", "description": "Customs declarations and related licences", "parent_category": None},
    {"category_id": "transport", "name_en": "Road Transport", "name_bn": "সড়ক পরিবহন", "description": "BRTA licensing and vehicle services", "parent_category": None},
    {"category_id": "railways", "name_en": "Railways", "name_bn": "রেলপথ", "description": "Bangladesh Railway citizen services", "parent_category": None},
    {"category_id": "utilities", "name_en": "Utilities", "name_bn": "ইউটিলিটি", "description": "Electricity, gas, water connections and billing", "parent_category": None},
    {"category_id": "post", "name_en": "Postal Services", "name_bn": "ডাক সেবা", "description": "Bangladesh Post Office services", "parent_category": None},
    {"category_id": "ict", "name_en": "ICT & Telecom", "name_bn": "আইসিটি ও টেলিকম", "description": "BTRC, digital centres, telecom regulation", "parent_category": None},
    {"category_id": "digital_government", "name_en": "Digital Government Access", "name_bn": "ডিজিটাল সরকারি প্রবেশাধিকার", "description": "myGov account and related digital access services", "parent_category": None},
    {"category_id": "government_payments", "name_en": "Government Payments", "name_bn": "সরকারি পেমেন্ট", "description": "Ekpay, challan, and fee payment gateways", "parent_category": None},
    {"category_id": "agriculture", "name_en": "Agriculture", "name_bn": "কৃষি", "description": "Farmer and agricultural extension services", "parent_category": None},
    {"category_id": "fisheries", "name_en": "Fisheries", "name_bn": "মৎস্য", "description": "Fisheries department citizen/business services", "parent_category": None},
    {"category_id": "livestock", "name_en": "Livestock", "name_bn": "প্রাণিসম্পদ", "description": "Livestock department citizen/business services", "parent_category": None},
    {"category_id": "environment", "name_en": "Environment", "name_bn": "পরিবেশ", "description": "Environmental clearances and related authorizations", "parent_category": None},
    {"category_id": "disaster_relief", "name_en": "Disaster Management", "name_bn": "দুর্যোগ ব্যবস্থাপনা", "description": "Relief, shelters, disaster information systems", "parent_category": None},
    {"category_id": "police", "name_en": "Police", "name_bn": "পুলিশ", "description": "Police certificates, GD, verification", "parent_category": None},
    {"category_id": "judiciary", "name_en": "Judiciary & Courts", "name_bn": "বিচার বিভাগ", "description": "Court filing, certified copies, case tracking", "parent_category": None},
    {"category_id": "legal_aid", "name_en": "Legal Aid", "name_bn": "আইন সহায়তা", "description": "NLASO and related free legal aid", "parent_category": None},
    {"category_id": "professional", "name_en": "Professional Licensing", "name_bn": "পেশাগত লাইসেন্সিং", "description": "Bar, medical, nursing, pharmacy, engineering councils", "parent_category": None},
    {"category_id": "religious_affairs", "name_en": "Religious Affairs", "name_bn": "ধর্ম বিষয়ক", "description": "Hajj and related religious affairs services", "parent_category": None},
]

CATEGORY_MAP = {
    "IDENTITY": "identity",
    "CIVIL_REGISTRATION": "civil_registration",
    "PASSPORT_IMMIGRATION": "passport_immigration",
    "EXPATRIATE": "expatriate",
    "EMPLOYMENT": "employment",
    "EDUCATION": "education",
    "HEALTH": "health",
    "DISABILITY": "disability",
    "SOCIAL_PROTECTION": "social_protection",
    "WOMEN_CHILDREN": "women_children",
    "LAND": "land",
    "HOUSING": "housing",
    "LOCAL_GOVERNMENT": "local_government",
    "CERTIFICATES": "certificates",
    "LICENCES": "licences",
    "PERMITS": "permits",
    "REGISTRATIONS": "registrations",
    "BUSINESS": "business",
    "INVESTMENT": "investment",
    "TRADE": "trade",
    "TAX": "tax",
    "VAT": "vat",
    "CUSTOMS": "customs",
    "TRANSPORT": "transport",
    "RAILWAYS": "railways",
    "UTILITIES": "utilities",
    "POST": "post",
    "ICT": "ict",
    "DIGITAL_GOVERNMENT": "digital_government",
    "GOVERNMENT_PAYMENTS": "government_payments",
    "AGRICULTURE": "agriculture",
    "FISHERIES": "fisheries",
    "LIVESTOCK": "livestock",
    "ENVIRONMENT": "environment",
    "DISASTER_RELIEF": "disaster_relief",
    "POLICE": "police",
    "JUDICIARY": "judiciary",
    "LEGAL_AID": "legal_aid",
    "PROFESSIONAL": "professional",
    "RELIGIOUS_AFFAIRS": "religious_affairs",
}


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:128]


def base_entry(raw: dict) -> dict:
    return {
        "service_id": raw["service_id"],
        "uuid": raw.get("uuid"),
        "service_name_bn": raw.get("service_name_bn"),
        "service_name_en": raw["service_name_en"],
        "aliases": list(dict.fromkeys(raw.get("aliases") or [])),
        "category": raw["category"],
        "category_id": CATEGORY_MAP.get(raw["category"], slugify(raw["category"])),
        "subcategory": raw.get("subcategory", "general"),
        "responsible_authority": raw["responsible_authority"],
        "authority_id": raw.get("authority_id") or slugify(raw["responsible_authority"])[:64],
        "target_user": raw.get("target_user") or ["citizen"],
        "geographic_scope": raw.get("geographic_scope", "NATIONAL"),
        "geographic_availability": raw.get("geographic_availability") or [],
        "lifecycle_stage": raw.get("lifecycle_stage") or [],
        "official_source": raw.get("official_source"),
        "discovery_sources": list(dict.fromkeys(raw.get("discovery_sources") or [])),
        "mygov_service_ids": raw.get("mygov_service_ids") or [],
        "status": raw["status"],
        "canonical_service_id": raw.get("canonical_service_id"),
        "relationship_type": raw.get("relationship_type"),
        "notes": raw.get("notes"),
        "discovered_at": raw.get("discovered_at", TODAY),
        "confirmed_at": raw.get("confirmed_at"),
        "last_checked_at": raw.get("last_checked_at"),
        "effective_from": raw.get("effective_from"),
        "effective_until": raw.get("effective_until"),
        "deprecated_at": raw.get("deprecated_at"),
        "catalogue_version": CATALOGUE_VERSION,
        "finalization_notes": raw.get("finalization_notes"),
    }


def apply_lifecycle(entry: dict, disposition: str) -> None:
    entry["last_checked_at"] = TODAY
    if disposition == "CONFIRMED":
        entry["status"] = "CONFIRMED"
        entry["confirmed_at"] = TODAY
    elif disposition == "UNVERIFIED":
        entry["status"] = "UNVERIFIED"
    elif disposition == "DEPRECATED":
        entry["status"] = "DEPRECATED"
        entry["deprecated_at"] = TODAY
    elif disposition == "NOT_A_SERVICE":
        entry["status"] = "NOT_A_SERVICE"
    elif disposition in {"MERGED", "DUPLICATE"}:
        entry["status"] = "DUPLICATE"
        entry["relationship_type"] = disposition


def main() -> None:
    original = json.loads((CATALOGUE_DIR / "services.json").read_text(encoding="utf-8"))
    original_services = original["services"]
    original_count = len(original_services)
    prior_dups = json.loads((CATALOGUE_DIR / "duplicates.json").read_text(encoding="utf-8")).get(
        "duplicates", []
    )

    # Deduplicate prior_dups by service_id (build script had duplicate alias rows)
    prior_dup_map: dict[str, dict] = {}
    for d in prior_dups:
        prior_dup_map[d["service_id"]] = d

    decisions_log: list[dict] = []
    by_id = {s["service_id"]: deepcopy(s) for s in original_services}

    # Inject new canonical parents first
    for nc in NEW_CANONICAL:
        if nc["service_id"] not in by_id:
            entry = base_entry(nc)
            entry["confirmed_at"] = TODAY
            entry["last_checked_at"] = TODAY
            entry["finalization_notes"] = "Created during finalization to absorb geographic/portal merges."
            by_id[nc["service_id"]] = entry

    all_decisions = {**UNCERTAIN_DECISIONS, **CONFIRMED_CLEANUP}

    # Ensure every previously uncertain service has a decision
    for s in original_services:
        if s["status"] in {"LIKELY", "NEEDS_VERIFICATION"} and s["service_id"] not in UNCERTAIN_DECISIONS:
            raise SystemExit(f"Missing decision for uncertain service: {s['service_id']}")

    removed_from_canonical: list[dict] = []
    geo_attachments: dict[str, list[dict]] = defaultdict(list)

    for sid, decision in all_decisions.items():
        if sid not in by_id and decision["disposition"] not in {"MERGED", "DUPLICATE"}:
            # already absent
            continue
        if sid not in by_id:
            continue

        src = by_id[sid]
        disposition = decision["disposition"]
        entry = base_entry(src)
        if decision.get("official_source"):
            entry["official_source"] = decision["official_source"]
            if decision["official_source"] not in entry["discovery_sources"]:
                entry["discovery_sources"].append(decision["official_source"])
        entry["finalization_notes"] = decision["reason"]
        apply_lifecycle(entry, disposition)

        decisions_log.append(
            {
                "service_id": sid,
                "previous_status": src.get("status"),
                "disposition": disposition,
                "canonical_service_id": decision.get("canonical_service_id"),
                "reason": decision["reason"],
            }
        )

        if disposition == "CONFIRMED":
            by_id[sid] = entry
            continue

        if disposition == "UNVERIFIED":
            by_id[sid] = entry
            continue

        # MERGED / DUPLICATE / NOT_A_SERVICE / DEPRECATED leave canonical set
        if disposition in {"MERGED", "DUPLICATE"}:
            canonical = decision.get("canonical_service_id")
            entry["canonical_service_id"] = canonical
            entry["relationship_type"] = disposition
            if canonical and canonical in by_id:
                parent = by_id[canonical]
                parent["aliases"] = list(
                    dict.fromkeys(
                        (parent.get("aliases") or [])
                        + (entry.get("aliases") or [])
                        + [entry["service_name_en"], entry["service_id"]]
                    )
                )
                parent["discovery_sources"] = list(
                    dict.fromkeys(
                        (parent.get("discovery_sources") or []) + (entry.get("discovery_sources") or [])
                    )
                )
                if decision.get("geo"):
                    geo = decision["geo"]
                    geo_attachments[canonical].append(geo)
            removed_from_canonical.append(entry)
            del by_id[sid]
        else:
            # NOT_A_SERVICE / DEPRECATED
            removed_from_canonical.append(entry)
            del by_id[sid]

    # Attach geographic availability
    for cid, geos in geo_attachments.items():
        if cid in by_id:
            existing = by_id[cid].get("geographic_availability") or []
            # dedupe by name_en+tier
            seen = {(g.get("tier"), g.get("name_en")) for g in existing}
            for g in geos:
                key = (g.get("tier"), g.get("name_en"))
                if key not in seen:
                    existing.append(g)
                    seen.add(key)
            by_id[cid]["geographic_availability"] = existing

    # Normalize remaining untouched CONFIRMED services with lifecycle defaults
    for sid, svc in list(by_id.items()):
        if "category_id" not in svc or "mygov_service_ids" not in svc:
            entry = base_entry(svc)
            if entry["status"] == "CONFIRMED" and not entry.get("confirmed_at"):
                # Preserve prior confirmed; set last_checked only if we didn't touch it
                entry["confirmed_at"] = entry.get("discovered_at", TODAY)
            if not entry.get("last_checked_at") and sid in all_decisions:
                entry["last_checked_at"] = TODAY
            by_id[sid] = entry

    # Include prior duplicate alias records (deduped) as redirects
    for sid, d in prior_dup_map.items():
        if sid in by_id:
            continue
        if any(x["service_id"] == sid for x in removed_from_canonical):
            continue
        entry = base_entry(d)
        entry["status"] = "DUPLICATE"
        entry["relationship_type"] = "DUPLICATE"
        entry["canonical_service_id"] = d.get("canonical_service_id")
        entry["finalization_notes"] = d.get("notes") or "Prior discovery-phase alias redirect."
        entry["last_checked_at"] = TODAY
        removed_from_canonical.append(entry)

    canonical = sorted(by_id.values(), key=lambda x: x["service_id"])
    redirects = sorted(removed_from_canonical, key=lambda x: x["service_id"])

    # Status counts
    status_counts = Counter(s["status"] for s in canonical)
    redirect_counts = Counter(s["status"] for s in redirects)
    disposition_counts = Counter(d["disposition"] for d in decisions_log)

    # Authorities
    auth_map: dict[str, dict] = {}
    for svc in canonical:
        name = svc["responsible_authority"]
        slug = svc.get("authority_id") or slugify(name)[:64]
        if slug not in auth_map:
            auth_map[slug] = {
                "authority_id": slug,
                "name_en": name,
                "name_bn": None,
                "service_count": 0,
                "categories": set(),
            }
        auth_map[slug]["service_count"] += 1
        auth_map[slug]["categories"].add(svc["category_id"])
    authorities = []
    for a in sorted(auth_map.values(), key=lambda x: x["authority_id"]):
        a["categories"] = sorted(a["categories"])
        authorities.append(a)

    # myGov mapping scaffold (no unverified IDs)
    mygov_map = {
        "mapping_version": "0.1.0",
        "notes": (
            "myGov.bd is an access/orchestration layer. Public pages list ministries and sectors "
            "but do not expose a stable machine-readable myGov service ID catalogue in this pass. "
            "Only store verified mygov_service_id values. Currently unresolved for all services."
        ),
        "verified_mappings": [],
        "unresolved_count": len(canonical),
        "relationship_model": {
            "fields": [
                "canonical_service_id",
                "mygov_service_id",
                "mygov_url",
                "verification_status",
                "verified_at",
                "notes",
            ],
            "rule": "Do not assume myGov entry count equals unique government services.",
        },
    }

    local_gov_model = {
        "model_version": "1.0.0",
        "principle": (
            "Do not create hundreds of duplicate canonical services for district/LGI delivery. "
            "Use geographic_availability on a single canonical service."
        ),
        "tiers": [
            "DIVISION",
            "DISTRICT",
            "CITY_CORPORATION",
            "MUNICIPALITY",
            "UPAZILA",
            "UNION",
            "WARD",
        ],
        "availability_values": [
            "AVAILABLE",
            "UNAVAILABLE",
            "PROCEDURE_DIFFERS",
            "OFFICE_DIFFERS",
            "URL_DIFFERS",
            "FEE_DIFFERS",
        ],
        "canonical_services_using_geo": [
            s["service_id"]
            for s in canonical
            if s.get("geographic_availability")
        ],
    }

    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    BY_CATEGORY_DIR.mkdir(parents=True, exist_ok=True)

    catalogue = {
        "catalogue_version": CATALOGUE_VERSION,
        "finalized_at": TODAY,
        "disclaimer": (
            "Finalized inventory for research readiness. Does NOT claim all Bangladesh government "
            "services. Does NOT include detailed requirements, fees, or procedures."
        ),
        "original_canonical_count": original_count,
        "canonical_services": len(canonical),
        "redirect_entries": len(redirects),
        "services": canonical,
    }

    (CATALOGUE_DIR / "services.json").write_text(
        json.dumps(catalogue, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (FINAL_DIR / "services.json").write_text(
        json.dumps(catalogue, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    (CATALOGUE_DIR / "redirects.json").write_text(
        json.dumps(
            {
                "redirects": redirects,
                "counts_by_status": dict(redirect_counts),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    # Keep duplicates.json as redirects for backward compatibility
    (CATALOGUE_DIR / "duplicates.json").write_text(
        json.dumps({"duplicates": [r for r in redirects if r["status"] == "DUPLICATE"]}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    (CATALOGUE_DIR / "categories.json").write_text(
        json.dumps({"categories": TAXONOMY}, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (CATALOGUE_DIR / "authorities.json").write_text(
        json.dumps({"authorities": authorities}, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (CATALOGUE_DIR / "mygov_mapping.json").write_text(
        json.dumps(mygov_map, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (CATALOGUE_DIR / "local_government_model.json").write_text(
        json.dumps(local_gov_model, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (CATALOGUE_DIR / "finalization_decisions.json").write_text(
        json.dumps(
            {
                "finalized_at": TODAY,
                "decisions": decisions_log,
                "disposition_counts": dict(disposition_counts),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    # by category
    by_cat: dict[str, list] = defaultdict(list)
    for svc in canonical:
        by_cat[svc["category_id"]].append(svc)
    # clear old category files that may use uppercase names
    for old in BY_CATEGORY_DIR.glob("*.json"):
        old.unlink()
    for cat, items in sorted(by_cat.items()):
        (BY_CATEGORY_DIR / f"{cat}.json").write_text(
            json.dumps(
                {"category_id": cat, "count": len(items), "services": items},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    metadata = {
        "catalogue_version": CATALOGUE_VERSION,
        "finalized_at": TODAY,
        "original_canonical_count": original_count,
        "canonical_services": len(canonical),
        "redirect_entries": len(redirects),
        "status_counts": dict(status_counts),
        "redirect_status_counts": dict(redirect_counts),
        "disposition_counts": dict(disposition_counts),
        "category_counts": dict(Counter(s["category_id"] for s in canonical)),
        "authority_count": len(authorities),
        "taxonomy_categories": len(TAXONOMY),
        "mygov_verified_mappings": 0,
        "ready_for_deep_research": True,
        "ready_notes": (
            "Canonical set normalized. Unverified entries remain and must not be used for "
            "requirement research without further confirmation."
        ),
    }
    (CATALOGUE_DIR / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(json.dumps(metadata, indent=2))
    print(f"Decisions applied: {len(decisions_log)}")
    print(f"Canonical: {len(canonical)}; Redirects: {len(redirects)}")


if __name__ == "__main__":
    main()
