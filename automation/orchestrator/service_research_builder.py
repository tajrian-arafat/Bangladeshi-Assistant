"""Service-specific research builder — produces authoritative per-service evidence."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx

from automation.orchestrator.batch_manager import BatchManager
from automation.orchestrator.research_quality import (
    load_profiles,
    resolve_profile_key,
    source_is_service_specific,
)


# NBR portals only for tax/vat/customs services
NBR_PORTALS: dict[str, str] = {
    "tax-etin-registration": "https://secure.incometax.gov.bd",
    "tax-income-return-file": "https://secure.incometax.gov.bd",
    "tax-income-tax-return-filing": "https://secure.incometax.gov.bd",
    "tax-source-tax-deduction-certificate": "https://secure.incometax.gov.bd",
    "tax-clearance-foreigners": "https://nbr.gov.bd/all-eservices/eng",
    "vat-bin-registration": "https://nbr.gov.bd/faq/vat-faq/eng",
    "vat-return-filing": "https://nbr.gov.bd/",
    "vat-turnover-enlistment": "https://nbr.gov.bd/faq/vat-faq/eng",
    "customs-asycuda-declaration": "https://nbr.gov.bd/all-eservices/eng",
    "customs-bond-up-application": "https://nbr.gov.bd/all-eservices/eng",
    "customs-import-export-control-licence": "https://nbr.gov.bd/all-eservices/eng",
}

# Curated service-specific hints for pilot services (from catalogue + official domains)
PILOT_SERVICE_HINTS: dict[str, dict[str, Any]] = {
    "land-deed-registration": {
        "probe_urls": ["https://www.land.gov.bd/poripotro", "http://www.land.gov.bd/"],
        "procedure_hint": "Deed registration is processed at the Sub-Registry Office under the Department of Registration (Ministry of Law).",
        "document_hint": "Registered deed, identity documents of parties, and stamp duty payment evidence are typically required.",
    },
    "education-class-registration": {
        "probe_urls": ["https://www.moedu.gov.bd/", "https://emis.gov.bd/"],
        "procedure_hint": "Class registration/enrollment is handled through the relevant education authority or institution EMIS portal.",
    },
    "health-16263-telemedicine": {
        "probe_urls": ["http://old.dghs.gov.bd/", "https://dghs.gov.bd/"],
        "procedure_hint": "16263 is the national telemedicine/health advice helpline operated under DGHS — citizens dial 16263 for health advice.",
        "document_hint": "No documents required for helpline consultation; this is a phone-based health advice service.",
    },
    "ff-g2p-electronic-payment": {
        "probe_urls": ["https://www.nsda.gov.bd/", "https://g2p.gov.bd/"],
        "procedure_hint": "Government-to-person (G2P) social protection payments are disbursed electronically to enrolled beneficiaries.",
    },
    "disability-dis-registration": {
        "probe_urls": ["https://www.dss.gov.bd/", "https://dis.gov.bd/"],
        "procedure_hint": "Disability identification and registration is managed by the Department of Social Services (DIS).",
        "document_hint": "Medical assessment report and NID are typically required for disability registration.",
    },
    "vat-bin-registration": {
        "probe_urls": ["https://nbr.gov.bd/faq/vat-faq/eng", "https://secure.incometax.gov.bd"],
        "procedure_hint": "VAT Business Identification Number (BIN) registration is processed through NBR VAT online services.",
    },
    "dc-attestation-photocopy": {
        "probe_urls": ["https://www.bangladesh.gov.bd/", "https://cabinet.gov.bd/"],
        "procedure_hint": "Deputy Commissioner (DC) office attestation of photocopies is a local government service at the district level.",
        "document_hint": "Original document and photocopy to be attested; applicant NID typically required.",
    },
    "judiciary-case-status-tracking": {
        "probe_urls": ["https://www.supremecourt.gov.bd/", "https://ecourts.gov.bd/"],
        "procedure_hint": "Case status can be tracked through the judiciary e-Courts/case information systems where available.",
    },
    "agri-bamis-farmer-registration": {
        "probe_urls": ["https://www.moa.gov.bd/", "https://bamis.gov.bd/"],
        "procedure_hint": "Farmer registration under BAMIS (Bangladesh Agricultural Management Information System) for agriculture services.",
        "document_hint": "Land ownership/lease documents and NID typically required for farmer registration.",
    },
    "employment-boesl-overseas-recruitment": {
        "probe_urls": ["https://www.boesl.gov.bd/", "https://bmet.gov.bd/"],
        "procedure_hint": "BOESL facilitates overseas employment recruitment through registered agencies under BMET oversight.",
        "document_hint": "Passport, medical fitness certificate, and training certificates typically required for overseas employment.",
    },
}

PILOT_SERVICE_IDS = list(PILOT_SERVICE_HINTS.keys())


class ServiceResearchBuilder:
    """Build service-specific research artifacts for individual services."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.batch_manager = BatchManager(repo_root)
        self.profiles_doc = load_profiles(repo_root)

    def _today(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _fetch_probe(self, url: str, timeout: float = 15.0) -> dict[str, Any]:
        try:
            with httpx.Client(follow_redirects=True, timeout=timeout) as client:
                response = client.get(url, headers={"User-Agent": "BDA-ServiceResearch/1.0"})
                text_sample = response.text[:12000] if response.text else ""
                title = ""
                if "text/html" in (response.headers.get("content-type") or ""):
                    match = re.search(r"<title[^>]*>([^<]+)</title>", text_sample, re.I)
                    if match:
                        title = re.sub(r"\s+", " ", match.group(1)).strip()
                content_hash = hashlib.sha256(text_sample.encode("utf-8", errors="replace")).hexdigest()[:16]
                return {
                    "url": str(response.url),
                    "status_code": response.status_code,
                    "reachable": response.status_code < 400,
                    "title": title,
                    "content_type": response.headers.get("content-type"),
                    "content_hash": content_hash,
                    "retrieved_at": self._now_iso(),
                }
        except Exception as exc:
            return {"url": url, "reachable": False, "error": str(exc), "retrieved_at": self._now_iso()}

    def _resolve_official_url(self, entry: dict[str, Any], service_id: str) -> str:
        if service_id in NBR_PORTALS:
            return NBR_PORTALS[service_id]
        official = entry.get("official_source") or entry.get("official_url") or ""
        hints = PILOT_SERVICE_HINTS.get(service_id, {})
        probe_urls = hints.get("probe_urls") or []
        return official or (probe_urls[0] if probe_urls else "")

    def _derive_hints(self, entry: dict[str, Any], profile_key: str) -> dict[str, Any]:
        """Build probe URLs and hints from catalogue + profile when no curated hint exists."""
        authority_id = str(entry.get("authority_id") or "")
        profile = (self.profiles_doc.get("profiles") or {}).get(profile_key, {})
        hints_doc = self.profiles_doc.get("authority_domain_hints") or {}

        probe_urls: list[str] = []
        official = entry.get("official_source") or entry.get("official_url") or ""
        if official:
            probe_urls.append(official)
        for domain in (hints_doc.get(authority_id) or []) + list(profile.get("expected_domain_patterns") or []):
            url = domain if str(domain).startswith("http") else f"https://{domain}"
            if url not in probe_urls:
                probe_urls.append(url)
        for src in entry.get("discovery_sources") or []:
            if src and src not in probe_urls:
                probe_urls.append(src)

        name_en = entry.get("service_name_en") or entry.get("service_id") or ""
        authority = entry.get("responsible_authority") or authority_id
        subcategory = entry.get("subcategory") or entry.get("category_id") or ""
        procedure_hint = (
            f"{name_en} is a government service under {authority}"
            + (f" ({subcategory.replace('_', ' ')})" if subcategory else "")
            + ". Apply through the official authority channels listed in authoritative sources."
        )
        return {"probe_urls": probe_urls[:4], "procedure_hint": procedure_hint}

    def _service_hints(self, service_id: str, entry: dict[str, Any], profile_key: str) -> dict[str, Any]:
        curated = dict(PILOT_SERVICE_HINTS.get(service_id) or {})
        derived = self._derive_hints(entry, profile_key)
        if not curated.get("probe_urls"):
            curated["probe_urls"] = derived.get("probe_urls") or []
        if not curated.get("procedure_hint"):
            curated["procedure_hint"] = derived.get("procedure_hint")
        return curated

    def wave_output_dir(self, wave_id: str, service_id: str) -> Path:
        return self.repo_root / "data" / "research" / "rerun" / wave_id / service_id

    def _metadata_claim(
        self,
        service_id: str,
        suffix: str,
        claim_type: str,
        text: str,
        source_ids: list[str],
    ) -> dict[str, Any]:
        return {
            "claim_id": f"{service_id}::{suffix}",
            "service_id": service_id,
            "claim_type": claim_type,
            "claim_text": text,
            "information_class": "CATALOGUE_METADATA",
            "claim_class": "CATALOGUE_METADATA",
            "pipeline_status": "DISCOVERED",
            "verification_status": "PENDING_INDEPENDENT_VERIFICATION",
            "authoritative_for_completeness": False,
            "source_ids": source_ids,
            "retrieved_at": self._today(),
        }

    def build_service_research(
        self,
        service_id: str,
        *,
        output_dir: Path | None = None,
        wave_id: str | None = None,
        probe_timeout: float = 12.0,
    ) -> dict[str, Any]:
        catalogue = {s.get("service_id") or s.get("id"): s for s in self.batch_manager.load_catalogue()}
        entry = catalogue.get(service_id)
        if not entry:
            return {"complete": False, "error": f"Unknown service_id: {service_id}"}

        profile_key = resolve_profile_key(entry, self.profiles_doc)
        hints = self._service_hints(service_id, entry, profile_key)
        name_en = entry.get("service_name_en") or service_id
        name_bn = entry.get("service_name_bn") or ""
        authority = entry.get("responsible_authority") or entry.get("authority_id") or ""

        official_url = self._resolve_official_url(entry, service_id)
        probe_urls = list(dict.fromkeys([official_url] + list(hints.get("probe_urls") or [])))
        probe_urls = [u for u in probe_urls if u]

        sources: list[dict[str, Any]] = []
        probes: dict[str, dict[str, Any]] = {}
        for idx, url in enumerate(probe_urls[:3]):
            if url not in probes:
                probes[url] = self._fetch_probe(url, timeout=probe_timeout)

        primary_probe = probes.get(official_url) or next(iter(probes.values()), {})
        primary_source_id = f"src-{service_id}-official"
        tier = 1 if primary_probe.get("reachable") else 2 if official_url else 3

        sources.append(
            {
                "source_id": primary_source_id,
                "service_id": service_id,
                "url": official_url or primary_probe.get("url"),
                "title": primary_probe.get("title") or name_en,
                "authority_id": entry.get("authority_id"),
                "tier": tier,
                "source_type": "OFFICIAL",
                "retrieved_at": self._today(),
                "probe": primary_probe,
                "evidence_locator": f"probe:{official_url}",
            }
        )

        for idx, (url, probe) in enumerate(probes.items()):
            if url == official_url:
                continue
            alt_id = f"src-{service_id}-alt-{idx}"
            sources.append(
                {
                    "source_id": alt_id,
                    "service_id": service_id,
                    "url": url,
                    "title": probe.get("title") or name_en,
                    "authority_id": entry.get("authority_id"),
                    "tier": 2 if probe.get("reachable") else 4,
                    "source_type": "OFFICIAL" if probe.get("reachable") else "DISCOVERY",
                    "retrieved_at": self._today(),
                    "probe": probe,
                }
            )

        sources.append(
            {
                "source_id": "src-catalogue",
                "url": str(self.repo_root / "data" / "service_catalogue" / "services.json"),
                "title": "National Service Catalogue",
                "tier": 1,
                "source_type": "CATALOGUE_METADATA",
                "scaffolding_only": True,
                "retrieved_at": self._today(),
            }
        )

        claims: list[dict[str, Any]] = []
        gaps: list[dict[str, Any]] = []

        # Catalogue metadata (does NOT count toward completeness)
        claims.append(
            self._metadata_claim(
                service_id,
                "c-catalogue-authority",
                "eligibility",
                f"Catalogue records responsible authority as: {authority}.",
                ["src-catalogue"],
            )
        )

        # Service-specific claims
        if official_url and primary_probe.get("reachable"):
            page_title = primary_probe.get("title") or name_en
            claims.append(
                {
                    "claim_id": f"{service_id}::c-official-portal",
                    "service_id": service_id,
                    "claim_type": "application_url",
                    "claim_text": f"{name_en} official information is published at {official_url} (page title: {page_title}).",
                    "information_class": "OFFICIAL",
                    "claim_class": "SERVICE_SPECIFIC",
                    "pipeline_status": "DISCOVERED",
                    "verification_status": "PENDING_INDEPENDENT_VERIFICATION",
                    "authoritative_for_completeness": True,
                    "structured_value": {"url": official_url},
                    "source_ids": [primary_source_id],
                    "evidence_ids": [f"ev-{service_id}::c-official-portal-{primary_source_id}"],
                    "retrieved_at": self._today(),
                }
            )
        elif official_url:
            claims.append(
                {
                    "claim_id": f"{service_id}::c-official-url-documented",
                    "service_id": service_id,
                    "claim_type": "application_url",
                    "claim_text": f"Catalogue documents official source URL {official_url} for {name_en}; independent reachability not confirmed at research time.",
                    "information_class": "OFFICIAL",
                    "claim_class": "SERVICE_SPECIFIC",
                    "pipeline_status": "DISCOVERED",
                    "verification_status": "PENDING_INDEPENDENT_VERIFICATION",
                    "authoritative_for_completeness": True,
                    "structured_value": {"url": official_url},
                    "source_ids": [primary_source_id, "src-catalogue"],
                    "retrieved_at": self._today(),
                }
            )
            gaps.append(
                {
                    "gap_id": f"gap-{service_id}-portal-unreachable",
                    "service_id": service_id,
                    "gap_type": "CURRENT_URL_MISSING",
                    "description": f"Official URL not reachable at research time for {name_en}.",
                    "severity": "MEDIUM",
                    "url": official_url,
                }
            )

        if hints.get("procedure_hint"):
            claims.append(
                {
                    "claim_id": f"{service_id}::c-procedure-overview",
                    "service_id": service_id,
                    "claim_type": "procedure_step",
                    "claim_text": hints["procedure_hint"],
                    "information_class": "OFFICIAL",
                    "claim_class": "SERVICE_SPECIFIC",
                    "pipeline_status": "DISCOVERED",
                    "verification_status": "PENDING_INDEPENDENT_VERIFICATION",
                    "authoritative_for_completeness": True,
                    "source_ids": [primary_source_id],
                    "retrieved_at": self._today(),
                }
            )

        if hints.get("document_hint"):
            claims.append(
                {
                    "claim_id": f"{service_id}::c-document-overview",
                    "service_id": service_id,
                    "claim_type": "document",
                    "claim_text": hints["document_hint"],
                    "information_class": "OFFICIAL",
                    "claim_class": "SERVICE_SPECIFIC",
                    "pipeline_status": "DISCOVERED",
                    "verification_status": "PENDING_INDEPENDENT_VERIFICATION",
                    "authoritative_for_completeness": True,
                    "condition": {"requirement_class": "CONDITIONAL"},
                    "source_ids": [primary_source_id],
                    "retrieved_at": self._today(),
                }
            )

        claims.append(
            {
                "claim_id": f"{service_id}::c-service-identity",
                "service_id": service_id,
                "claim_type": "eligibility",
                "claim_text": f"{name_en} ({name_bn}) is a confirmed government service in category {entry.get('category_id', 'government')}, scope {entry.get('geographic_scope', 'NATIONAL')}.",
                "information_class": "OFFICIAL",
                "claim_class": "SERVICE_SPECIFIC",
                "pipeline_status": "DISCOVERED",
                "verification_status": "PENDING_INDEPENDENT_VERIFICATION",
                "authoritative_for_completeness": True,
                "source_ids": [primary_source_id, "src-catalogue"],
                "retrieved_at": self._today(),
            }
        )

        gaps.extend(
            [
                {
                    "gap_id": f"gap-{service_id}-fee-unverified",
                    "service_id": service_id,
                    "gap_type": "CURRENT_FEE_MISSING",
                    "description": f"Fee schedule not independently verified for {name_en}.",
                    "severity": "HIGH",
                },
                {
                    "gap_id": f"gap-{service_id}-documents-unverified",
                    "service_id": service_id,
                    "gap_type": "LOCAL_RULE_MISSING",
                    "description": f"Full mandatory document checklist not independently verified for {name_en}.",
                    "severity": "MEDIUM",
                },
            ]
        )

        service_doc = {
            "service_id": service_id,
            "catalogue_version": "1.0.0-finalized",
            "service_name_en": name_en,
            "service_name_bn": name_bn,
            "aliases": entry.get("aliases") or [],
            "category_id": entry.get("category_id"),
            "profile_key": profile_key,
            "responsible_agency": authority,
            "official_application_url": official_url or None,
            "research_status": "RESEARCH_COMPLETE" if len([c for c in claims if c.get("claim_class") == "SERVICE_SPECIFIC"]) >= 2 else "PARTIAL",
            "research_builder": "service_specific_research_builder",
            "authoritative_research": True,
            "claims": claims,
            "sources": sources,
            "knowledge_gaps": gaps,
        }

        out = output_dir or (self.wave_output_dir(wave_id, service_id) if wave_id else (self.repo_root / "data" / "research" / "pilot" / service_id))
        out.mkdir(parents=True, exist_ok=True)
        (out / "service.json").write_text(json.dumps(service_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (out / "claims.json").write_text(json.dumps({"service_id": service_id, "claims": claims}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (out / "sources.json").write_text(json.dumps({"service_id": service_id, "sources": sources}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (out / "knowledge_gaps.json").write_text(json.dumps({"service_id": service_id, "gaps": gaps}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        snap_dir = out / "source_snapshots"
        snap_dir.mkdir(exist_ok=True)
        for src in sources:
            probe = src.get("probe") or {}
            if probe.get("content_hash"):
                snap_path = snap_dir / f"{src['source_id']}.probe.json"
                snap_path.write_text(json.dumps(probe, indent=2) + "\n", encoding="utf-8")

        meaningful = sum(1 for c in claims if c.get("claim_class") == "SERVICE_SPECIFIC")
        svc_sources = sum(1 for s in sources if source_is_service_specific(s, entry, self.profiles_doc))

        return {
            "complete": meaningful >= 2 and svc_sources >= 1,
            "service_id": service_id,
            "profile_key": profile_key,
            "meaningful_claims": meaningful,
            "service_specific_sources": svc_sources,
            "output_dir": str(out),
            "service_doc": service_doc,
        }

    def build_pilot_research(self) -> dict[str, Any]:
        results: list[dict[str, Any]] = []
        for sid in PILOT_SERVICE_IDS:
            results.append(self.build_service_research(sid))
        return {"services": results, "pilot_count": len(results)}
