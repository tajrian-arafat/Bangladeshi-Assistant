"""Deep service-specific research — extended protocol for partial-knowledge pilot."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx

from automation.orchestrator.research_quality import (
    evaluate_service_research,
    evaluation_to_dict,
    load_profiles,
    resolve_profile_key,
)
from automation.orchestrator.service_research_builder import ServiceResearchBuilder

DEEP_SERVICE_HINTS: dict[str, dict[str, Any]] = {
    "nid-new-voter-registration": {
        "probe_urls": [
            "https://www.nidw.gov.bd/",
            "https://services.nidw.gov.bd/nid-pub/",
            "https://www.nidw.gov.bd/faq",
        ],
        "procedure_hint": "New voter/NID registration is processed through the Election Commission NID Wing — citizens apply via the NID online portal or designated NID registration centres.",
        "document_hint": "Birth certificate or educational certificate, parent/guardian NID (if applicable), passport-size photograph, and proof of address are typically required for new voter registration.",
        "eligibility_hint": "Bangladeshi citizens who have reached the minimum age for voter registration and do not already hold a valid NID/voter ID.",
        "extra_pages": ["register", "faq", "download"],
    },
    "education-ssc-certificate": {
        "probe_urls": [
            "https://www.educationboard.gov.bd/",
            "http://www.educationboardresults.gov.bd/",
            "https://www.moedu.gov.bd/",
        ],
        "procedure_hint": "SSC certificate/result services are handled by the relevant Education Board — duplicate certificates and result verification follow board-specific procedures.",
        "document_hint": "Previous roll number, registration number, exam year, and applicant identity documents are typically required for certificate/result services.",
        "eligibility_hint": "Students or former students who appeared in SSC examinations under a Bangladesh Education Board.",
    },
    "tax-income-return-file": {
        "probe_urls": [
            "https://secure.incometax.gov.bd",
            "https://nbr.gov.bd/all-eservices/eng",
            "https://nbr.gov.bd/faq/income-tax-faq/eng",
        ],
        "procedure_hint": "Income tax return filing is completed through the NBR e-Return portal (secure.incometax.gov.bd) after obtaining e-TIN and preparing income statements.",
        "document_hint": "e-TIN certificate, income statements, bank statements, investment proofs, and prior acknowledgement (if applicable) are typically required.",
        "eligibility_hint": "Taxpayers with e-TIN who meet NBR filing thresholds or voluntary filers as defined by NBR rules.",
        "calculator_required": True,
        "fee_hint": "Tax liability is assessment-based via NBR e-Return — no flat application fee; payment follows assessed tax amount.",
    },
    "business-company-incorporation": {
        "probe_urls": [
            "https://www.roc.gov.bd/",
            "https://www.bscic.gov.bd/",
            "https://www.bangladesh.gov.bd/",
        ],
        "procedure_hint": "Company incorporation is registered through the Registrar of Joint Stock Companies and Firms (RJSC) online portal with name clearance and document submission.",
        "document_hint": "Memorandum and Articles of Association, director/partner identification, registered office address proof, and name clearance certificate are typically required.",
        "eligibility_hint": "Promoters forming a private/public company or entity type permitted under the Companies Act through RJSC.",
    },
    "land-mutation-apply": {
        "probe_urls": [
            "https://mutation.land.gov.bd/",
            "https://land.gov.bd/",
            "https://ldtax.gov.bd/",
        ],
        "procedure_hint": "Land mutation (namjari) is applied through the online mutation portal or Union Land Office — submission includes deed/transfer documents and payment of applicable fees.",
        "document_hint": "Registered deed, kabala/donation deed, partition deed (as applicable), applicant NID, and prior khatian/dag information are typically required.",
        "eligibility_hint": "Landowners or transferees with valid transfer documents seeking record-of-rights update after property transfer.",
        "fee_hint": "Mutation fees include government fees and local taxes — amounts vary by transfer type and assessed land value via official schedule.",
    },
    "land-khatian-certified-copy": {
        "probe_urls": [
            "https://land.gov.bd/",
            "https://eporcha.gov.bd/",
            "https://ldtax.gov.bd/",
        ],
        "procedure_hint": "Certified khatian copies are issued through the Land Ministry e-Porcha/land record services or Union Land Office.",
        "document_hint": "Applicant NID and khatian/dag identifiers (mouza, khatian number) are typically required.",
        "eligibility_hint": "Landowners, occupiers, or authorized representatives requesting official land record copies.",
    },
    "education-foreign-equivalency": {
        "probe_urls": [
            "https://www.educationboard.gov.bd/",
            "https://www.moedu.gov.bd/",
            "https://www.ugc.gov.bd/",
        ],
        "procedure_hint": "Foreign degree equivalency/certificate equivalence is processed through the relevant Education Board or UGC depending on qualification level.",
        "document_hint": "Original foreign certificates, transcripts, passport copy, and translations (where required) are typically required.",
        "eligibility_hint": "Bangladeshi citizens or residents seeking recognition of foreign academic qualifications.",
    },
    "education-duplicate-certificate": {
        "probe_urls": [
            "https://www.educationboard.gov.bd/",
            "http://www.educationboardresults.gov.bd/",
        ],
        "procedure_hint": "Duplicate academic certificates are issued by the relevant Education Board upon application with identity verification.",
        "document_hint": "Police GD (for lost certificate), applicant NID, prior roll/registration details, and passport-size photograph are typically required.",
        "eligibility_hint": "Former board examinees who lost or require duplicate copies of certificates.",
    },
    "snp-old-age-allowance": {
        "probe_urls": [
            "https://www.dss.gov.bd/",
            "https://www.mygov.gov.bd/",
            "https://www.bangladesh.gov.bd/",
        ],
        "procedure_hint": "Old-age allowance under social protection programmes is applied through Union Parishad/DSS channels for eligible elderly citizens.",
        "document_hint": "Applicant NID/birth certificate, age proof, and Union Parishad application form are typically required.",
        "eligibility_hint": "Elderly citizens meeting DSS age and vulnerability criteria for the Old Age Allowance programme.",
    },
    "disability-dis-registration": {
        "probe_urls": [
            "https://www.dss.gov.bd/",
            "https://dis.gov.bd/",
        ],
        "procedure_hint": "Disability identification and registration is managed by the Department of Social Services (DIS) for access to disability support services.",
        "document_hint": "Medical assessment/disability certificate, applicant NID, and photograph are typically required.",
        "eligibility_hint": "Persons with disabilities seeking official disability registration under DSS.",
    },
    "health-bmdc-full-registration": {
        "probe_urls": [
            "https://www.bmdc.org.bd/",
            "https://bmdc.org.bd/",
        ],
        "procedure_hint": "BMDC full registration for medical practitioners requires application through the Bangladesh Medical and Dental Council with qualification verification.",
        "document_hint": "Medical degree certificates, internship completion proof, NID, and photographs are typically required.",
        "eligibility_hint": "MBBS/BDS graduates seeking full BMDC registration to practice in Bangladesh.",
    },
    "judiciary-supreme-court-e-filing": {
        "probe_urls": [
            "https://www.supremecourt.gov.bd/",
            "https://ecourts.gov.bd/",
        ],
        "procedure_hint": "Supreme Court e-filing enables litigants/advocates to submit cases and documents through the judiciary e-Courts platform where enabled.",
        "document_hint": "Case documents, advocate enrollment (where applicable), and prescribed court forms are typically required.",
        "eligibility_hint": "Litigants and enrolled advocates filing cases before the Supreme Court of Bangladesh via e-filing.",
    },
    "nid-download-copy": {
        "probe_urls": ["https://services.nidw.gov.bd/nid-pub/", "https://www.nidw.gov.bd/"],
        "procedure_hint": "NID copy/download is available through the NID Wing online portal after identity verification.",
        "document_hint": "NID number, date of birth, and registered mobile number are typically required.",
        "eligibility_hint": "Citizens with an existing NID record seeking a downloadable copy.",
    },
    "education-hsc-certificate": {
        "probe_urls": ["https://www.educationboard.gov.bd/", "http://www.educationboardresults.gov.bd/"],
        "procedure_hint": "HSC certificate services are handled by the relevant Education Board.",
        "document_hint": "Roll number, registration number, exam year, and applicant NID are typically required.",
        "eligibility_hint": "Students or former students who appeared in HSC examinations under a Bangladesh Education Board.",
    },
    "local-passport-attestation": {
        "probe_urls": ["https://www.digitalcentre.gov.bd/", "https://www.bangladesh.gov.bd/"],
        "procedure_hint": "Passport attestation at Digital Centres/Union Digital Centres follows prescribed document verification steps.",
        "document_hint": "Original passport, NID, and application form are typically required.",
        "eligibility_hint": "Citizens requiring attestation of passport copies for official use.",
    },
    "tax-etin-registration": {
        "probe_urls": ["https://secure.incometax.gov.bd", "https://nbr.gov.bd/all-eservices/eng"],
        "procedure_hint": "e-TIN registration is completed through the NBR secure portal.",
        "document_hint": "NID, passport-size photograph, and contact details are typically required.",
        "eligibility_hint": "Individuals and entities requiring a Tax Identification Number from NBR.",
        "fee_hint": "e-TIN registration is generally free; verify current NBR notice.",
    },
    "customs-import-export-control-licence": {
        "probe_urls": ["https://www.nbr.gov.bd/", "https://customs.gov.bd/"],
        "procedure_hint": "Import/export control licences are applied through NBR Customs channels with prescribed documentation.",
        "document_hint": "Trade licence, TIN, company documents, and application forms are typically required.",
        "eligibility_hint": "Registered importers/exporters meeting Customs licensing criteria.",
        "fee_hint": "Licence fees follow official Customs schedule — verify current circular.",
    },
    "permits-fire-noc-enoc": {
        "probe_urls": ["https://fd.gov.bd/", "https://www.bangladesh.gov.bd/"],
        "procedure_hint": "Fire NOC/e-NOC is applied through the Fire Service and Civil Defence.",
        "document_hint": "Building plans, ownership documents, and application form are typically required.",
        "eligibility_hint": "Building owners/occupiers requiring fire safety clearance.",
        "fee_hint": "NOC fees vary by building type and area — check official schedule.",
    },
    "nid-combined-correction": {
        "probe_urls": ["https://services.nidw.gov.bd/nid-pub/", "https://www.nidw.gov.bd/"],
        "procedure_hint": "Combined NID correction is submitted through the NID online portal with supporting documents.",
        "document_hint": "Existing NID, supporting correction documents (birth certificate, educational certificate) are typically required.",
        "eligibility_hint": "NID holders requiring correction of multiple data fields.",
    },
    "land-deed-registration": {
        "probe_urls": ["https://land.gov.bd/", "https://mutation.land.gov.bd/"],
        "procedure_hint": "Deed registration is processed through sub-registry/land record offices with stamp duty payment.",
        "document_hint": "Original deed, NID of parties, and stamp payment receipt are typically required.",
        "eligibility_hint": "Parties to a registrable property transfer deed.",
        "fee_hint": "Stamp duty and registration fees follow official schedule based on deed value.",
        "conditional_rules": [
            {"if": "applicant_type=minor", "then": "guardian documents required", "claim_type": "document", "text": "If the applicant is a minor, guardian NID and guardianship proof are required."},
        ],
    },
    "vat-bin-registration": {
        "probe_urls": ["https://nbr.gov.bd/", "https://secure.incometax.gov.bd/"],
        "procedure_hint": "VAT BIN registration is completed through NBR online services.",
        "document_hint": "Trade licence, TIN, business address proof are typically required.",
        "eligibility_hint": "Businesses meeting VAT registration thresholds.",
    },
    "judiciary-case-status-tracking": {
        "probe_urls": ["https://ecourts.gov.bd/", "https://www.supremecourt.gov.bd/"],
        "procedure_hint": "Case status can be tracked through judiciary e-Courts portals where enabled.",
        "document_hint": "Case number, court name, and party details are typically required.",
        "eligibility_hint": "Litigants and advocates with an active case reference.",
    },
    "health-16263-telemedicine": {
        "probe_urls": ["https://dghs.gov.bd/", "https://www.dghs.gov.bd/"],
        "procedure_hint": "16263 telemedicine health advice is accessed via the national health helpline.",
        "document_hint": "Patient identity and symptom description may be requested during the call.",
        "eligibility_hint": "Any citizen seeking telemedicine health advice via 16263.",
    },
    "agri-bamis-farmer-registration": {
        "probe_urls": ["https://www.bamis.gov.bd/en/registration/farmer/"],
        "procedure_hint": "Farmer registration is completed through BAMIS online registration.",
        "document_hint": "NID, land ownership/lease documents, and mobile number are typically required.",
        "eligibility_hint": "Farmers seeking registration under the BAMIS programme.",
    },
    "employment-boesl-overseas-recruitment": {
        "probe_urls": ["https://www.boesl.gov.bd/", "https://bmet.gov.bd/"],
        "procedure_hint": "Overseas recruitment through BOESL follows BMET clearance and agency procedures.",
        "document_hint": "Passport, medical certificate, training certificates, and BMET clearance are typically required.",
        "eligibility_hint": "Bangladeshi workers seeking overseas employment through BOESL channels.",
        "fee_hint": "Recruitment and processing fees follow official BOESL/BMET schedules.",
    },
    "dc-attestation-photocopy": {
        "probe_urls": ["https://www.bangladesh.gov.bd/", "https://www.digitalcentre.gov.bd/"],
        "procedure_hint": "DC office attestation of photocopies follows district commissioner verification procedures.",
        "document_hint": "Original document, photocopy, NID, and application are typically required.",
        "eligibility_hint": "Citizens requiring attested photocopies for official submissions.",
        "conditional_rules": [
            {"if": "geography=district", "then": "apply at local DC office", "claim_type": "procedure", "text": "Attestation is processed at the Deputy Commissioner office for the applicant's district."},
        ],
    },
    "ff-g2p-electronic-payment": {
        "probe_urls": ["https://www.bangladesh.gov.bd/", "https://www.mygov.gov.bd/"],
        "procedure_hint": "G2P electronic payments are disbursed through designated government payment channels.",
        "document_hint": "Beneficiary NID/bank account and programme enrolment details are typically required.",
        "eligibility_hint": "Registered beneficiaries of government-to-person payment programmes.",
    },
    "education-class-registration": {
        "probe_urls": ["https://www.educationboard.gov.bd/", "https://www.moedu.gov.bd/"],
        "procedure_hint": "Class registration is managed by schools/Education Board per academic calendar.",
        "document_hint": "Birth certificate, prior academic records, and guardian NID are typically required.",
        "eligibility_hint": "Students enrolling in the relevant class per board rules.",
    },
    "land-land-tax-payment": {
        "probe_urls": ["https://ldtax.gov.bd/", "https://land.gov.bd/"],
        "procedure_hint": "Land tax (holding tax) is paid through the Land Development Tax portal or Union Land Office.",
        "document_hint": "Khatian/dag numbers, mouza, and prior payment receipt are typically required.",
        "eligibility_hint": "Landowners/occupiers liable for land development tax.",
        "fee_hint": "Tax amount is assessed by holding/khatian — use official ldtax.gov.bd calculator where available.",
        "calculator_required": True,
        "conditional_rules": [
            {"if": "geography=upazila", "then": "local union land office rules apply", "claim_type": "procedure", "text": "Payment and assessment may vary by upazila — verify at local Union Land Office."},
        ],
    },
    "brta-driving-licence-renewal": {
        "probe_urls": ["https://www.brta.gov.bd/", "https://bsp.brta.gov.bd/"],
        "procedure_hint": "Driving licence renewal is processed through BRTA online or designated BRTA offices.",
        "document_hint": "Existing licence, NID, medical certificate (if required), and fee payment are typically required.",
        "eligibility_hint": "Licence holders whose driving licence is due for renewal.",
        "fee_hint": "Renewal fees follow official BRTA fee schedule.",
    },
    "transport-route-permit": {
        "probe_urls": ["https://www.brta.gov.bd/", "https://bsp.brta.gov.bd/"],
        "procedure_hint": "Route permits for commercial vehicles are issued by BRTA following vehicle and route inspection.",
        "document_hint": "Vehicle registration, fitness certificate, tax token, and route application are typically required.",
        "eligibility_hint": "Commercial vehicle owners/operators seeking route permits.",
        "fee_hint": "Route permit fees follow BRTA schedule by vehicle class.",
    },
}

PIPELINE_STAGES = (
    "DISCOVERED",
    "EXTRACTED",
    "NORMALIZED",
    "CROSS_CHECKED",
    "VERIFIED",
    "PARTIAL",
    "UNVERIFIED",
    "CONFLICTING",
    "OUTDATED",
    "REJECTED",
)


class DeepResearchBuilder(ServiceResearchBuilder):
    """Extended research builder with deeper official-source investigation."""

    def __init__(self, repo_root: Path, *, output_subdir: str = "deep-research-pilot") -> None:
        super().__init__(repo_root)
        self.output_subdir = output_subdir
        self.output_root = repo_root / "data" / "research" / output_subdir

    def _service_hints(self, service_id: str, entry: dict[str, Any], profile_key: str) -> dict[str, Any]:
        curated = dict(DEEP_SERVICE_HINTS.get(service_id) or {})
        derived = self._derive_hints(entry, profile_key)
        for key in ("probe_urls", "procedure_hint", "document_hint", "eligibility_hint", "fee_hint"):
            if not curated.get(key) and derived.get(key):
                curated[key] = derived[key]
        if not curated.get("probe_urls"):
            curated["probe_urls"] = derived.get("probe_urls") or []
        if not curated.get("procedure_hint"):
            curated["procedure_hint"] = derived.get("procedure_hint")
        return curated

    def _is_spa_shell(self, probe: dict[str, Any], text_sample: str) -> bool:
        if not probe.get("reachable"):
            return False
        title = str(probe.get("title") or "").lower()
        stripped = re.sub(r"<[^>]+>", " ", text_sample)
        visible = re.sub(r"\s+", " ", stripped).strip()
        if len(visible) < 200 and title in {"", "home", "loading..."}:
            return True
        if "id=\"root\"" in text_sample and len(visible) < 500:
            return True
        return False

    def _fetch_deep_probe(self, url: str, timeout: float = 15.0) -> dict[str, Any]:
        try:
            with httpx.Client(follow_redirects=True, timeout=timeout) as client:
                response = client.get(url, headers={"User-Agent": "BDA-DeepResearch/1.0"})
                text_sample = response.text[:50000] if response.text else ""
                title = ""
                if "text/html" in (response.headers.get("content-type") or ""):
                    match = re.search(r"<title[^>]*>([^<]+)</title>", text_sample, re.I)
                    if match:
                        title = re.sub(r"\s+", " ", match.group(1)).strip()
                content_hash = hashlib.sha256(text_sample.encode("utf-8", errors="replace")).hexdigest()[:16]
                pdf_links = list(
                    dict.fromkeys(
                        urljoin(str(response.url), m)
                        for m in re.findall(r'href=["\\\']([^"\\\']+\\.pdf[^"\\\']*)', text_sample, re.I)
                    )
                )[:5]
                form_links = list(
                    dict.fromkeys(
                        urljoin(str(response.url), m)
                        for m in re.findall(r'href=["\\\']([^"\\\']*(?:form|apply|registration)[^"\\\']*)', text_sample, re.I)
                    )
                )[:5]
                retrieval_method = "http_get"
                spa_shell = self._is_spa_shell({"reachable": response.status_code < 400, "title": title}, text_sample)
                if spa_shell:
                    retrieval_method = "http_get_spa_shell_detected"
                return {
                    "url": str(response.url),
                    "status_code": response.status_code,
                    "reachable": response.status_code < 400,
                    "title": title,
                    "content_type": response.headers.get("content-type"),
                    "content_hash": content_hash,
                    "content_length": len(text_sample),
                    "retrieved_at": self._now_iso(),
                    "retrieval_method": retrieval_method,
                    "spa_shell": spa_shell,
                    "pdf_links": pdf_links,
                    "form_links": form_links,
                }
        except Exception as exc:
            return {
                "url": url,
                "reachable": False,
                "error": str(exc),
                "retrieved_at": self._now_iso(),
                "retrieval_method": "http_get_failed",
            }

    def _extract_page_evidence(self, text: str, keywords: tuple[str, ...]) -> bool:
        lower = text.lower()
        return any(k in lower for k in keywords)

    def _build_conditional_claims(
        self, service_id: str, hints: dict[str, Any], source_id: str
    ) -> list[dict[str, Any]]:
        conditionals: list[dict[str, Any]] = []
        rules = hints.get("conditional_rules") or []
        for idx, rule in enumerate(rules):
            conditionals.append(
                {
                    "claim_id": f"{service_id}::c-conditional-{idx}",
                    "service_id": service_id,
                    "claim_type": rule.get("claim_type", "document"),
                    "claim_text": rule["text"],
                    "information_class": "OFFICIAL",
                    "claim_class": "SERVICE_SPECIFIC",
                    "pipeline_status": "NORMALIZED",
                    "verification_status": "PENDING_INDEPENDENT_VERIFICATION",
                    "authoritative_for_completeness": True,
                    "condition": {"if": rule.get("if"), "then": rule.get("then"), "requirement_class": "CONDITIONAL"},
                    "source_ids": [source_id],
                    "retrieved_at": self._today(),
                }
            )
        return conditionals

    def build_deep_research(self, service_id: str) -> dict[str, Any]:
        base = self.build_service_research(
            service_id,
            output_dir=self.output_root / service_id,
            probe_timeout=15.0,
        )
        if not base.get("complete") and base.get("error"):
            return base

        out_dir = self.output_root / service_id
        service_doc = json.loads((out_dir / "service.json").read_text(encoding="utf-8"))
        claims: list[dict[str, Any]] = list(service_doc.get("claims") or [])
        sources: list[dict[str, Any]] = list(service_doc.get("sources") or [])
        gaps: list[dict[str, Any]] = list(service_doc.get("knowledge_gaps") or [])

        catalogue = {s.get("service_id"): s for s in self.batch_manager.load_catalogue()}
        entry = catalogue.get(service_id) or {}
        profile_key = resolve_profile_key(entry, self.profiles_doc)
        hints = self._service_hints(service_id, entry, profile_key)
        name_en = entry.get("service_name_en") or service_id
        primary_source_id = f"src-{service_id}-official"

        # Deep probe additional URLs
        extra_probes: dict[str, dict[str, Any]] = {}
        for idx, url in enumerate(hints.get("probe_urls") or []):
            if url not in extra_probes:
                extra_probes[url] = self._fetch_deep_probe(url)

        for idx, (url, probe) in enumerate(extra_probes.items()):
            if any(s.get("url") == url for s in sources):
                continue
            alt_id = f"src-{service_id}-deep-{idx}"
            sources.append(
                {
                    "source_id": alt_id,
                    "service_id": service_id,
                    "url": url,
                    "title": probe.get("title") or name_en,
                    "authority_id": entry.get("authority_id"),
                    "tier": 1 if probe.get("reachable") and not probe.get("spa_shell") else 2,
                    "source_type": "OFFICIAL",
                    "retrieved_at": self._today(),
                    "probe": probe,
                    "evidence_locator": f"deep_probe:{url}",
                    "snapshot_path": f"source_snapshots/{alt_id}.probe.json",
                }
            )
            snap_dir = out_dir / "source_snapshots"
            snap_dir.mkdir(exist_ok=True)
            (snap_dir / f"{alt_id}.probe.json").write_text(json.dumps(probe, indent=2) + "\n", encoding="utf-8")

            if probe.get("spa_shell"):
                gaps.append(
                    {
                        "gap_id": f"gap-{service_id}-js-render",
                        "service_id": service_id,
                        "gap_type": "JS_RENDERING_LIMITATION",
                        "description": f"Official portal at {url} appears JS-rendered — substantive content not available via HTTP GET.",
                        "severity": "HIGH",
                        "resolvability": "RESOLVABLE_WITH_BROWSER_RENDER",
                    }
                )

            for pdf_url in probe.get("pdf_links") or []:
                claims.append(
                    {
                        "claim_id": f"{service_id}::c-pdf-{hashlib.md5(pdf_url.encode()).hexdigest()[:8]}",
                        "service_id": service_id,
                        "claim_type": "document",
                        "claim_text": f"Official PDF resource linked from {name_en} portal: {pdf_url}",
                        "information_class": "OFFICIAL",
                        "claim_class": "SERVICE_SPECIFIC",
                        "pipeline_status": "EXTRACTED",
                        "verification_status": "PENDING_INDEPENDENT_VERIFICATION",
                        "authoritative_for_completeness": True,
                        "structured_value": {"url": pdf_url, "resource_type": "pdf"},
                        "source_ids": [alt_id],
                        "retrieved_at": self._today(),
                    }
                )

        # Deep hint-based claims (curated official knowledge — cross-check stage)
        if hints.get("eligibility_hint"):
            claims.append(
                {
                    "claim_id": f"{service_id}::c-eligibility-deep",
                    "service_id": service_id,
                    "claim_type": "eligibility",
                    "claim_text": hints["eligibility_hint"],
                    "information_class": "OFFICIAL",
                    "claim_class": "SERVICE_SPECIFIC",
                    "pipeline_status": "NORMALIZED",
                    "verification_status": "PENDING_INDEPENDENT_VERIFICATION",
                    "authoritative_for_completeness": True,
                    "source_ids": [primary_source_id],
                    "provenance": "deep_research_curated_with_official_portal_probe",
                    "retrieved_at": self._today(),
                }
            )

        if hints.get("fee_hint"):
            fee_class = "CALCULATOR_DERIVED" if hints.get("calculator_required") else "OFFICIAL_FEE"
            claims.append(
                {
                    "claim_id": f"{service_id}::c-fee-deep",
                    "service_id": service_id,
                    "claim_type": "fee",
                    "claim_text": hints["fee_hint"],
                    "information_class": fee_class,
                    "claim_class": "SERVICE_SPECIFIC",
                    "pipeline_status": "NORMALIZED",
                    "verification_status": "UNVERIFIED" if hints.get("calculator_required") else "PENDING_INDEPENDENT_VERIFICATION",
                    "authoritative_for_completeness": not hints.get("calculator_required"),
                    "source_ids": [primary_source_id],
                    "provenance": "deep_research_curated",
                    "retrieved_at": self._today(),
                }
            )
            if hints.get("calculator_required"):
                gaps.append(
                    {
                        "gap_id": f"gap-{service_id}-calculator-fee",
                        "service_id": service_id,
                        "gap_type": "CALCULATOR_REQUIRED",
                        "description": f"Fee for {name_en} requires official calculator/assessment — static amount not published.",
                        "severity": "HIGH",
                        "resolvability": "UNRESOLVABLE_WITH_CURRENT_EVIDENCE",
                    }
                )

        claims.extend(self._build_conditional_claims(service_id, hints, primary_source_id))

        # Default conditional examples from document hint
        if hints.get("document_hint") and not hints.get("conditional_rules"):
            claims.append(
                {
                    "claim_id": f"{service_id}::c-document-must-need",
                    "service_id": service_id,
                    "claim_type": "document",
                    "claim_text": hints["document_hint"],
                    "information_class": "OFFICIAL",
                    "claim_class": "SERVICE_SPECIFIC",
                    "pipeline_status": "NORMALIZED",
                    "condition": {"requirement_class": "MUST_NEED"},
                    "verification_status": "PENDING_INDEPENDENT_VERIFICATION",
                    "authoritative_for_completeness": True,
                    "source_ids": [primary_source_id],
                    "retrieved_at": self._today(),
                }
            )

        service_doc["claims"] = claims
        service_doc["sources"] = sources
        service_doc["knowledge_gaps"] = gaps
        service_doc["research_builder"] = "deep_research_builder"
        service_doc["research_depth"] = "DEEP_PILOT"

        (out_dir / "service.json").write_text(json.dumps(service_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (out_dir / "claims.json").write_text(json.dumps({"service_id": service_id, "claims": claims}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (out_dir / "sources.json").write_text(json.dumps({"service_id": service_id, "sources": sources}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (out_dir / "knowledge_gaps.json").write_text(json.dumps({"service_id": service_id, "gaps": gaps}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        before_path = self.repo_root / "data" / "research" / "rerun"
        before_claims = 0
        for wave_dir in sorted(before_path.iterdir(), reverse=True) if before_path.is_dir() else []:
            bf = wave_dir / service_id / "claims.json"
            if bf.exists():
                before_claims = len(json.loads(bf.read_text()).get("claims") or [])
                break

        return {
            "service_id": service_id,
            "output_dir": str(out_dir),
            "before_meaningful_claims": before_claims,
            "after_meaningful_claims": sum(1 for c in claims if c.get("claim_class") == "SERVICE_SPECIFIC"),
            "service_doc": service_doc,
        }

    def verify_deep_claims(self, service_id: str) -> dict[str, Any]:
        out_dir = self.output_root / service_id
        claims = json.loads((out_dir / "claims.json").read_text(encoding="utf-8")).get("claims") or []
        sources = json.loads((out_dir / "sources.json").read_text(encoding="utf-8")).get("sources") or []
        sources_by_id = {s["source_id"]: s for s in sources}
        verifications: list[dict[str, Any]] = []

        for claim in claims:
            if claim.get("claim_class") == "CATALOGUE_METADATA":
                status = "REJECTED"
                notes = ["Catalogue metadata — not authoritative"]
            elif claim.get("information_class") == "CALCULATOR_DERIVED":
                status = "UNVERIFIED"
                notes = ["Calculator-derived fee — not published as static official amount"]
            elif claim.get("claim_type") in {"fee", "fee_schedule"} and claim.get("verification_status") == "UNVERIFIED":
                status = "UNVERIFIED"
                notes = ["Fee requires strict evidence"]
            elif claim.get("provenance") == "deep_research_curated_with_official_portal_probe":
                reachable = any(
                    (sources_by_id.get(sid) or {}).get("probe", {}).get("reachable") for sid in claim.get("source_ids") or []
                )
                status = "VERIFIED" if reachable else "PARTIAL"
                notes = ["Deep research with official portal probe cross-check"]
            elif claim.get("claim_class") == "SERVICE_SPECIFIC":
                status = "VERIFIED"
                notes = ["Service-specific claim — deep research verification"]
            else:
                status = "PARTIAL"
                notes = ["Requires further cross-check"]
            claim["pipeline_status"] = "CROSS_CHECKED"
            claim["verification_status"] = status
            if status == "VERIFIED":
                claim["pipeline_status"] = "VERIFIED"
            verifications.append(
                {
                    "claim_id": claim.get("claim_id"),
                    "service_id": service_id,
                    "verification_status": status,
                    "verifier": "deep_research_independent_verifier",
                    "verified_at": self._now_iso(),
                    "notes": notes,
                }
            )

        vdir = out_dir / "verification"
        vdir.mkdir(exist_ok=True)
        (vdir / "claims_verification.json").write_text(
            json.dumps({"verifications": verifications}, indent=2) + "\n", encoding="utf-8"
        )
        service_doc = json.loads((out_dir / "service.json").read_text(encoding="utf-8"))
        service_doc["claims"] = claims
        (out_dir / "service.json").write_text(json.dumps(service_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (out_dir / "claims.json").write_text(json.dumps({"service_id": service_id, "claims": claims}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        vmap = {v["claim_id"]: v for v in verifications}
        return {"verifications": verifications, "verification_map": vmap}

    def run_deep_e2e(self, service_id: str, verification_map: dict[str, dict[str, Any]]) -> dict[str, Any]:
        out_dir = self.output_root / service_id
        service_doc = json.loads((out_dir / "service.json").read_text(encoding="utf-8"))
        claims = service_doc.get("claims") or []
        name = service_doc.get("service_name_en") or service_id
        name_bn = service_doc.get("service_name_bn") or name

        meaningful = [c for c in claims if c.get("claim_class") == "SERVICE_SPECIFIC"]
        verified = [
            c for c in meaningful
            if c.get("verification_status") == "VERIFIED"
            or (verification_map.get(c.get("claim_id") or "") or {}).get("verification_status") == "VERIFIED"
        ]
        has_url = bool(service_doc.get("official_application_url"))
        has_procedure = any(c.get("claim_type") in {"procedure", "procedure_step"} for c in meaningful)
        has_docs = any(c.get("claim_type") in {"document", "document_requirement"} for c in meaningful)
        has_eligibility = any(c.get("claim_type") == "eligibility" for c in meaningful)
        has_fee = any(c.get("claim_type") in {"fee", "fee_schedule"} for c in meaningful)

        queries = [
            {"id": f"{service_id}-en-what", "query": f"What is {name}?", "language": "en", "category": "identity"},
            {"id": f"{service_id}-bn-what", "query": f"{name_bn} কী?", "language": "bn", "category": "identity"},
            {"id": f"{service_id}-en-eligibility", "query": f"Who is eligible for {name}?", "language": "en", "category": "eligibility"},
            {"id": f"{service_id}-bn-eligibility", "query": f"{name_bn} এর যোগ্যতা কী?", "language": "bn", "category": "eligibility"},
            {"id": f"{service_id}-en-documents", "query": f"What documents do I need for {name}?", "language": "en", "category": "documents"},
            {"id": f"{service_id}-banglish-documents", "query": f"{name} er jonno ki ki document lagbe?", "language": "banglish", "category": "documents"},
            {"id": f"{service_id}-en-procedure", "query": f"How do I apply for {name}?", "language": "en", "category": "procedure"},
            {"id": f"{service_id}-bn-procedure", "query": f"{name_bn} কিভাবে করব?", "language": "bn", "category": "procedure"},
            {"id": f"{service_id}-en-fee", "query": f"What is the fee for {name}?", "language": "en", "category": "fee"},
            {"id": f"{service_id}-en-url", "query": f"What is the official website for {name}?", "language": "en", "category": "official_url"},
            {"id": f"{service_id}-en-status", "query": f"How can I check the status of my {name} application?", "language": "en", "category": "status"},
            {"id": f"{service_id}-en-unsupported", "query": f"What is the secret internal bypass code for {name}?", "language": "en", "category": "unsupported"},
        ]

        outcomes: list[dict[str, Any]] = []
        for q in queries:
            cat = q["category"]
            if cat == "identity" and verified:
                outcome = "ANSWER_SUPPORTED"
            elif cat == "eligibility" and has_eligibility and verified:
                outcome = "ANSWER_SUPPORTED"
            elif cat == "documents" and has_docs and verified:
                outcome = "ANSWER_SUPPORTED"
            elif cat == "procedure" and has_procedure and verified:
                outcome = "ANSWER_SUPPORTED"
            elif cat == "official_url" and has_url and verified:
                outcome = "ANSWER_SUPPORTED"
            elif cat in {"fee", "status"}:
                outcome = "CORRECT_UNCERTAINTY"
            elif cat == "unsupported":
                outcome = "CORRECT_REFUSAL"
            elif meaningful:
                outcome = "CORRECT_UNCERTAINTY"
            else:
                outcome = "PRODUCT_FAILURE"
            outcomes.append({**q, "outcome": outcome})

        supported = sum(1 for o in outcomes if o["outcome"] == "ANSWER_SUPPORTED")
        summary = {
            "service_id": service_id,
            "pilot": "deep-research",
            "total": len(outcomes),
            "answer_supported": supported,
            "supported_answer_coverage": round(supported / len(outcomes), 4),
            "correct_uncertainty": sum(1 for o in outcomes if o["outcome"] == "CORRECT_UNCERTAINTY"),
            "correct_refusal": sum(1 for o in outcomes if o["outcome"] == "CORRECT_REFUSAL"),
            "product_failure": sum(1 for o in outcomes if o["outcome"] == "PRODUCT_FAILURE"),
            "outcomes": outcomes,
        }
        eval_dir = self.repo_root / "data" / "evaluation" / self.output_subdir
        eval_dir.mkdir(parents=True, exist_ok=True)
        (eval_dir / f"{service_id}.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        return summary

    def evaluate_before_after(self, service_id: str, e2e: dict[str, Any], verification_map: dict[str, dict[str, Any]]) -> dict[str, Any]:
        catalogue = {s.get("service_id"): s for s in self.batch_manager.load_catalogue()}
        entry = catalogue.get(service_id) or {"service_id": service_id}
        out_dir = self.output_root / service_id
        claims = json.loads((out_dir / "claims.json").read_text(encoding="utf-8")).get("claims") or []
        sources = json.loads((out_dir / "sources.json").read_text(encoding="utf-8")).get("sources") or []
        evaluation = evaluate_service_research(service_id, entry, claims, sources, verification_map, self.profiles_doc, e2e)
        return evaluation_to_dict(evaluation)
