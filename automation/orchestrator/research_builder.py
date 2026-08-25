"""Generic research artifact builder — SCAFFOLDING ONLY, not authoritative research."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx

from automation.orchestrator.batch_manager import BatchManager
from automation.orchestrator.phase_completion import batch_slug, check_research_complete


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


class ResearchBuilder:
    """Build raw research artifacts from catalogue + authoritative source probes."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.batch_manager = BatchManager(repo_root)

    def _today(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def _fetch_probe(self, url: str, timeout: float = 15.0) -> dict[str, Any]:
        try:
            with httpx.Client(follow_redirects=True, timeout=timeout) as client:
                response = client.get(url, headers={"User-Agent": "BDA-ResearchBot/1.0"})
                title = ""
                if "text/html" in (response.headers.get("content-type") or ""):
                    match = re.search(r"<title[^>]*>([^<]+)</title>", response.text[:8000], re.I)
                    if match:
                        title = re.sub(r"\s+", " ", match.group(1)).strip()
                return {
                    "url": str(response.url),
                    "status_code": response.status_code,
                    "reachable": response.status_code < 400,
                    "title": title,
                    "content_type": response.headers.get("content-type"),
                }
        except Exception as exc:
            return {"url": url, "reachable": False, "error": str(exc)}

    def build_batch_research(self, batch: dict[str, Any]) -> dict[str, Any]:
        slug = batch_slug(batch)
        raw_dir = self.repo_root / "data" / "research" / "raw" / slug
        services_dir = raw_dir / "services"
        snapshots_dir = raw_dir / "source_snapshots"
        raw_dir.mkdir(parents=True, exist_ok=True)
        services_dir.mkdir(exist_ok=True)
        snapshots_dir.mkdir(exist_ok=True)

        catalogue = {s.get("service_id") or s.get("id"): s for s in self.batch_manager.load_catalogue()}
        service_ids: list[str] = list(batch.get("service_ids") or [])
        sources: list[dict[str, Any]] = []
        all_claims: list[dict[str, Any]] = []
        gaps: list[dict[str, Any]] = []
        conflicts: list[dict[str, Any]] = []
        probed_urls: dict[str, dict[str, Any]] = {}

        for sid in service_ids:
            entry = catalogue.get(sid) or {}
            official = entry.get("official_source") or entry.get("official_url") or ""
            # NBR portals only for tax/vat/customs — never bleed to land/education/etc.
            category_id = entry.get("category_id") or ""
            if sid in NBR_PORTALS:
                portal = NBR_PORTALS[sid]
            elif category_id in {"tax", "vat", "customs"}:
                portal = official or NBR_PORTALS.get(sid, "")
            else:
                portal = official
            source_id = f"src-{sid}"
            probe_key = portal or official
            if probe_key and probe_key not in probed_urls:
                probed_urls[probe_key] = self._fetch_probe(probe_key)

            probe = probed_urls.get(probe_key) or {}
            tier = 1 if probe.get("reachable") else 2 if official else 3
            sources.append(
                {
                    "source_id": source_id,
                    "service_id": sid,
                    "url": official or portal,
                    "portal_url": portal if portal != official else None,
                    "title": probe.get("title") or entry.get("service_name_en") or sid,
                    "authority_id": entry.get("authority_id"),
                    "tier": tier,
                    "source_type": "OFFICIAL" if tier <= 2 else "DISCOVERY",
                    "retrieved_at": self._today(),
                    "probe": probe,
                }
            )

            claims: list[dict[str, Any]] = []
            name_en = entry.get("service_name_en") or sid
            name_bn = entry.get("service_name_bn") or ""

            if portal:
                portal_label = "NBR e-service portal" if category_id in {"tax", "vat", "customs"} else "official portal"
                claims.append(
                    {
                        "claim_id": f"{sid}::c-application-portal",
                        "service_id": sid,
                        "claim_type": "application_url",
                        "claim_text": f"Catalogue associates {name_en} with {portal_label} {portal}.",
                        "information_class": "CATALOGUE_METADATA",
                        "claim_class": "CATALOGUE_METADATA",
                        "authoritative_for_completeness": False,
                        "pipeline_status": "DISCOVERED",
                        "verification_status": "PENDING_INDEPENDENT_VERIFICATION",
                        "source_ids": [source_id, "src-catalogue"],
                        "retrieved_at": self._today(),
                    }
                )
            if official and official != portal:
                claims.append(
                    {
                        "claim_id": f"{sid}::c-official-source",
                        "service_id": sid,
                        "claim_type": "application_url",
                        "claim_text": f"Catalogue official source documented for {name_en}.",
                        "information_class": "CATALOGUE_METADATA",
                        "claim_class": "CATALOGUE_METADATA",
                        "authoritative_for_completeness": False,
                        "pipeline_status": "DISCOVERED",
                        "verification_status": "PENDING_INDEPENDENT_VERIFICATION",
                        "source_ids": [source_id, "src-catalogue"],
                        "structured_value": {"url": official},
                        "retrieved_at": self._today(),
                    }
                )

            claims.append(
                {
                    "claim_id": f"{sid}::c-responsible-authority",
                    "service_id": sid,
                    "claim_type": "eligibility",
                    "claim_text": f"Catalogue responsible authority: {entry.get('responsible_authority', entry.get('authority_id', 'unknown'))}.",
                    "information_class": "CATALOGUE_METADATA",
                    "claim_class": "CATALOGUE_METADATA",
                    "authoritative_for_completeness": False,
                    "pipeline_status": "DISCOVERED",
                    "verification_status": "PENDING_INDEPENDENT_VERIFICATION",
                    "source_ids": ["src-catalogue"],
                    "retrieved_at": self._today(),
                }
            )

            if not probe.get("reachable") and not official:
                gaps.append(
                    {
                        "gap_id": f"gap-{sid}-official-url",
                        "service_id": sid,
                        "gap_type": "OFFICIAL_URL_MISSING",
                        "description": f"No reachable official URL confirmed for {name_en}.",
                        "severity": "HIGH",
                    }
                )
            elif not probe.get("reachable"):
                gaps.append(
                    {
                        "gap_id": f"gap-{sid}-portal-unreachable",
                        "service_id": sid,
                        "gap_type": "CURRENT_URL_MISSING",
                        "description": f"Catalogue/portal URL not reachable at research time for {name_en}.",
                        "severity": "MEDIUM",
                        "url": probe_key,
                    }
                )

            gaps.append(
                {
                    "gap_id": f"gap-{sid}-fee-unverified",
                    "service_id": sid,
                    "gap_type": "CURRENT_FEE_MISSING",
                    "description": f"Fee schedule not independently verified for {name_en}.",
                    "severity": "HIGH",
                }
            )
            gaps.append(
                {
                    "gap_id": f"gap-{sid}-documents-unverified",
                    "service_id": sid,
                    "gap_type": "LOCAL_RULE_MISSING",
                    "description": f"Mandatory document checklist not fully verified for {name_en}.",
                    "severity": "MEDIUM",
                }
            )

            service_doc = {
                "service_id": sid,
                "batch_id": slug,
                "catalogue_version": "1.0.0-finalized",
                "service_name_en": name_en,
                "service_name_bn": name_bn,
                "aliases": entry.get("aliases") or [],
                "category_id": entry.get("category_id"),
                "responsible_agency": entry.get("responsible_authority") or entry.get("authority_id"),
                "official_application_url": portal or official or None,
                "research_status": "SCAFFOLDING_ONLY",
                "authoritative_research": False,
                "claims": claims,
            }
            (services_dir / f"{sid}.json").write_text(
                json.dumps(service_doc, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            all_claims.extend(claims)

        sources.append(
            {
                "source_id": "src-catalogue",
                "url": str(self.repo_root / "data" / "service_catalogue" / "services.json"),
                "title": "National Service Catalogue",
                "tier": 1,
                "source_type": "OFFICIAL",
                "retrieved_at": self._today(),
            }
        )

        scope = {
            "batch_id": batch["batch_id"],
            "slug": slug,
            "name": batch.get("name", slug),
            "in_scope": service_ids,
            "out_of_scope_noted": [],
            "generated_by": "automation.orchestrator.research_builder",
        }
        services_index = {
            "batch_id": batch["batch_id"],
            "services": [
                {
                    "service_id": sid,
                    "catalogue_status": (catalogue.get(sid) or {}).get("status", "CONFIRMED"),
                    "authority_id": (catalogue.get(sid) or {}).get("authority_id"),
                    "category_id": (catalogue.get(sid) or {}).get("category_id"),
                    "official_source": (catalogue.get(sid) or {}).get("official_source"),
                }
                for sid in service_ids
            ],
        }
        metadata = {
            "batch_id": slug,
            "phase": "RESEARCH_ONLY",
            "researched_at": self._today(),
            "catalogue_version": "1.0.0-finalized",
            "services_in_scope": len(service_ids),
            "services_researched": len(service_ids),
            "source_count": len(sources),
            "official_source_count_tier1_2": sum(1 for s in sources if s.get("tier", 3) <= 2),
            "claims_total": len(all_claims),
            "claims_official": sum(1 for c in all_claims if c.get("information_class") == "OFFICIAL"),
            "claims_practical": 0,
            "claims_discovery": sum(1 for c in all_claims if c.get("information_class") == "DISCOVERY"),
            "conflicts": len(conflicts),
            "knowledge_gaps": len(gaps),
            "verification_status": "NOT_STARTED",
            "publication_status": "NOT_STARTED",
            "builder": "generic_research_builder",
            "authoritative_research": False,
            "scaffolding_only": True,
        }

        for name, payload in [
            ("scope.json", scope),
            ("services_index.json", services_index),
            ("claims.json", {"batch_id": slug, "claims": all_claims}),
            ("sources.json", {"batch_id": slug, "sources": sources}),
            ("conflicts.json", {"batch_id": slug, "conflicts": conflicts}),
            ("knowledge_gaps.json", {"batch_id": slug, "gaps": gaps}),
            ("metadata.json", metadata),
        ]:
            (raw_dir / name).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        report_path = self.repo_root / "docs" / "research" / f"{slug}-research.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            f"# {batch.get('name', slug)} — Research Report\n\n"
            f"Generated by generic research builder on {self._today()}.\n\n"
            f"- Services in scope: {len(service_ids)}\n"
            f"- Claims: {len(all_claims)}\n"
            f"- Knowledge gaps: {len(gaps)}\n"
            f"- Conflicts: {len(conflicts)}\n\n"
            f"Fees and mandatory documents remain **unverified** pending gap closure.\n",
            encoding="utf-8",
        )

        completion = check_research_complete(self.repo_root, batch)
        return {
            "complete": completion.complete,
            "missing": completion.missing,
            "metadata": metadata,
            "artifacts_dir": str(raw_dir),
        }
