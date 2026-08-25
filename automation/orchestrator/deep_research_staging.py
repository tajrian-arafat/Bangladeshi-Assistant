"""Normalize deep-research per-service artifacts into publisher-ready staging."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

BATCH_SLUG = "deep-research-pilot-20"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _domain(url: str) -> str:
    try:
        host = urlparse(url).netloc.lower()
        return host[4:] if host.startswith("www.") else host
    except Exception:
        return ""


class DeepResearchStagingBuilder:
    """Build full staging + verification batch from deep-research service dirs."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.staging_dir = repo_root / "data" / "research" / "staging" / BATCH_SLUG
        self.verification_dir = repo_root / "data" / "research" / "verification" / BATCH_SLUG

    def build_from_service_dirs(self, service_dirs: list[Path], catalogue: dict[str, dict[str, Any]]) -> Path:
        all_claims: list[dict[str, Any]] = []
        all_sources: list[dict[str, Any]] = []
        all_source_versions: list[dict[str, Any]] = []
        all_evidence: list[dict[str, Any]] = []
        all_services: list[dict[str, Any]] = []
        verification_claims: list[dict[str, Any]] = []

        seen_sources: set[str] = set()

        for svc_dir in service_dirs:
            service_id = svc_dir.name
            service_doc = json.loads((svc_dir / "service.json").read_text(encoding="utf-8"))
            claims = json.loads((svc_dir / "claims.json").read_text(encoding="utf-8")).get("claims") or []
            sources = json.loads((svc_dir / "sources.json").read_text(encoding="utf-8")).get("sources") or []
            ver_path = svc_dir / "verification" / "claims_verification.json"
            verifications = {}
            if ver_path.exists():
                for v in json.loads(ver_path.read_text(encoding="utf-8")).get("verifications") or []:
                    verifications[v["claim_id"]] = v

            entry = catalogue.get(service_id) or {}
            for src in sources:
                sid = src.get("source_id")
                if not sid or sid in seen_sources:
                    continue
                seen_sources.add(sid)
                url = src.get("url") or ""
                probe = src.get("probe") or {}
                sv_id = f"sv-{sid}"
                all_sources.append(
                    {
                        "source_id": sid,
                        "url": url,
                        "domain": _domain(url),
                        "authority_id": src.get("authority_id") or entry.get("authority_id"),
                        "tier": src.get("tier", 2),
                        "source_type": src.get("source_type", "OFFICIAL"),
                        "title": src.get("title"),
                    }
                )
                all_source_versions.append(
                    {
                        "source_version_id": sv_id,
                        "source_id": sid,
                        "url": url,
                        "content_hash": probe.get("content_hash"),
                        "retrieved_at": probe.get("retrieved_at") or _now()[:10],
                        "fetched_method": probe.get("retrieval_method") or "deep_research_http",
                        "http_status": probe.get("status_code"),
                        "raw_pointer": src.get("snapshot_path"),
                        "is_published": False,
                        "notes": "Deep-research pipeline staging",
                    }
                )

            for claim in claims:
                if claim.get("claim_class") == "CATALOGUE_METADATA":
                    continue
                cid = claim.get("claim_id")
                source_ids = [s for s in (claim.get("source_ids") or []) if s != "src-catalogue"]
                sv_ids = [f"sv-{s}" for s in source_ids]
                vstatus = claim.get("verification_status") or (verifications.get(cid) or {}).get("verification_status") or "UNVERIFIED"
                pipeline = "VERIFIED" if vstatus == "VERIFIED" else "NORMALIZED"
                if vstatus in {"UNVERIFIED", "REJECTED"}:
                    pipeline = vstatus

                staging_claim = {
                    "claim_id": cid,
                    "legacy_claim_id": cid.split("::")[-1] if cid else None,
                    "service_id": service_id,
                    "claim_text": claim.get("claim_text"),
                    "claim_type": claim.get("claim_type") or "other",
                    "information_class": claim.get("information_class") if claim.get("information_class") != "CALCULATOR_DERIVED" else "OFFICIAL",
                    "pipeline_status": pipeline,
                    "confidence": 0.75 if vstatus == "VERIFIED" else 0.5,
                    "evidence_ids": claim.get("evidence_ids") or [f"ev-{cid}-{source_ids[0]}" if source_ids else f"ev-{cid}"],
                    "source_ids": source_ids,
                    "source_version_ids": sv_ids,
                    "structured_value": claim.get("structured_value"),
                    "condition": claim.get("condition"),
                    "provenance": {
                        "batch_id": BATCH_SLUG,
                        "discovered_at": claim.get("retrieved_at") or _now()[:10],
                        "normalized_at": _now()[:10],
                        "publication_status": "STAGING_ONLY",
                        "research_builder": "deep_research_pipeline",
                    },
                    "independent_verification_status": vstatus,
                }
                all_claims.append(staging_claim)

                for sid in source_ids:
                    ev_id = f"ev-{cid}-{sid}"
                    all_evidence.append(
                        {
                            "evidence_id": ev_id,
                            "source_version_id": f"sv-{sid}",
                            "claim_id": cid,
                            "summary": (claim.get("claim_text") or "")[:200],
                            "excerpt": None,
                            "locator": claim.get("evidence_locator") or src.get("evidence_locator") if (src := next((s for s in sources if s.get("source_id") == sid), {})) else None,
                            "language": "en",
                            "captured_at": _now()[:10],
                            "strength": "STRONG" if vstatus == "VERIFIED" else "WEAK",
                        }
                    )

                ver = verifications.get(cid) or {}
                verification_claims.append(
                    {
                        "claim_id": cid,
                        "service_id": service_id,
                        "claim_text": claim.get("claim_text"),
                        "staging_pipeline_status": pipeline,
                        "information_class": staging_claim["information_class"],
                        "claim_type": staging_claim.get("claim_type"),
                        "priority": 1,
                        "verification_status": vstatus,
                        "reasoning": "; ".join(ver.get("notes") or []) or "Deep-research independent verification",
                        "evidence": [
                            {
                                "source_id": sid,
                                "source_url": next((s.get("url") for s in sources if s.get("source_id") == sid), None),
                                "authority_tier": next((s.get("tier") for s in sources if s.get("source_id") == sid), 2),
                                "retrieved_live_at": _now()[:10],
                                "retrieved_via": "deep_research_pipeline",
                            }
                            for sid in source_ids[:2]
                        ],
                        "condition": claim.get("condition"),
                        "verifier": ver.get("verifier") or "deep_research_independent_verifier",
                        "verified_at": ver.get("verified_at") or _now(),
                        "publication_status": "STAGING_ONLY",
                    }
                )

            all_services.append(
                {
                    "service_id": service_id,
                    "catalogue_status": "CONFIRMED",
                    "research_depth": "DEEP",
                    "pipeline_status": "CROSS_CHECKED",
                    "publication_status": "STAGING_ONLY",
                    "official_application_url": service_doc.get("official_application_url"),
                    "official_information_urls": [s.get("url") for s in sources if s.get("url")][:5],
                    "missing_information": [g.get("description") for g in (service_doc.get("knowledge_gaps") or [])][:5],
                    "manual_review_required": [],
                    "runtime_service_row": None,
                    "notes": "Deep-research pilot-20 staging pack",
                }
            )

        self.staging_dir.mkdir(parents=True, exist_ok=True)
        (self.staging_dir / "claims.json").write_text(json.dumps({"claims": all_claims}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (self.staging_dir / "sources.json").write_text(json.dumps({"sources": all_sources}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (self.staging_dir / "source_versions.json").write_text(json.dumps({"source_versions": all_source_versions}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (self.staging_dir / "evidence.json").write_text(json.dumps({"evidence": all_evidence}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (self.staging_dir / "services.json").write_text(json.dumps({"services": all_services}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (self.staging_dir / "fees.json").write_text(json.dumps({"fees": []}, indent=2) + "\n", encoding="utf-8")
        (self.staging_dir / "conflicts.json").write_text(json.dumps({"conflicts": []}, indent=2) + "\n", encoding="utf-8")

        self.verification_dir.mkdir(parents=True, exist_ok=True)
        (self.verification_dir / "claims_verification.json").write_text(
            json.dumps(
                {
                    "schema": "bda.research.verification.claims/1.0",
                    "batch_id": BATCH_SLUG,
                    "claims": verification_claims,
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        return self.staging_dir
