"""Runtime DB + claim retrieval validation for deep-research publication."""

from __future__ import annotations

import json
import os
import sys
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "backend"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class RetrievalProbe:
    service_id: str
    catalogue_service_id: str
    runtime_service_id: str | None
    query: str
    intent: str
    claim_type: str | None
    claim_found: bool
    claim_id: str | None
    evidence_count: int
    classification: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class RuntimeConsistencyReport:
    generated_at: str
    batch_slug: str
    db_path: str
    services: list[dict[str, Any]]
    retrieval_probes: list[dict[str, Any]]
    aggregate: dict[str, Any]
    bottlenecks: list[dict[str, Any]]


class RuntimeValidator:
    """Validate deep-research claims survive publication and retrieval."""

    INTENT_QUERIES: dict[str, tuple[str, str]] = {
        "procedure_inquiry": ("How do I apply for {name}?", "procedure"),
        "document_list": ("What documents do I need for {name}?", "document"),
        "eligibility": ("Who is eligible for {name}?", "eligibility"),
        "fee_inquiry": ("What is the fee for {name}?", "fee"),
        "application_url": ("What is the official website for {name}?", "application_url"),
    }

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.db_path = repo_root / "backend" / "data" / "bda.db"
        self.mappings = self._load_mappings()

    def _load_mappings(self) -> dict[str, dict[str, Any]]:
        path = self.repo_root / "data" / "research" / "catalogue_runtime_mappings.json"
        if not path.exists():
            return {}
        doc = json.loads(path.read_text(encoding="utf-8"))
        return {m["catalogue_service_id"]: m for m in doc.get("mappings") or []}

    def _ensure_backend_path(self) -> None:
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

    async def _session_factory(self):
        self._ensure_backend_path()
        os.chdir(BACKEND_DIR)
        from app.core.database import get_session_factory

        return get_session_factory()

    async def validate_service(
        self,
        catalogue_service_id: str,
        *,
        service_name: str | None = None,
    ) -> dict[str, Any]:
        mapping = self.mappings.get(catalogue_service_id) or {}
        runtime_id = mapping.get("runtime_service_id")
        name = service_name or catalogue_service_id

        result: dict[str, Any] = {
            "catalogue_service_id": catalogue_service_id,
            "runtime_service_id": runtime_id,
            "runtime_exists": False,
            "published_claim_count": 0,
            "verified_published_claim_count": 0,
            "fee_links": 0,
            "provenance_preserved": False,
            "retrieval_probes": [],
            "issues": [],
        }

        if not self.db_path.exists():
            result["issues"].append("RUNTIME_DB_MISSING")
            return result

        if not runtime_id:
            result["issues"].append("NO_RUNTIME_MAPPING")
            return result

        self._ensure_backend_path()
        from sqlalchemy import select

        from app.ai.routing.claim_retrieval import ClaimRetrieval
        from app.ai.routing.intent_classifier import IntentResult, classify_intents
        from app.domain.enums import ClaimPipelineStatus, InformationClass
        from app.domain.models.claims import Claim
        from app.domain.models.knowledge import Service

        session_factory = await self._session_factory()
        async with session_factory() as session:
            try:
                runtime_uuid = uuid.UUID(str(runtime_id))
            except ValueError:
                result["issues"].append("INVALID_RUNTIME_UUID")
                return result

            svc = await session.get(Service, runtime_uuid)
            if not svc:
                result["issues"].append("SERVICE_NOT_IN_RUNTIME")
                return result
            result["runtime_exists"] = True
            result["runtime_slug"] = svc.slug

            claims_result = await session.execute(
                select(Claim).where(Claim.service_id == runtime_uuid)
            )
            claims = list(claims_result.scalars().all())
            published = [c for c in claims if c.is_published]
            verified_pub = [
                c
                for c in published
                if c.pipeline_status == ClaimPipelineStatus.VERIFIED.value
                and c.information_class == InformationClass.OFFICIAL.value
            ]
            synced_verified = [
                c
                for c in claims
                if c.pipeline_status == ClaimPipelineStatus.VERIFIED.value
                and c.information_class == InformationClass.OFFICIAL.value
            ]
            result["synced_claim_count"] = len(claims)
            result["synced_verified_count"] = len(synced_verified)
            result["published_claim_count"] = len(published)
            result["verified_published_claim_count"] = len(verified_pub)
            result["provenance_preserved"] = any(
                c.research_claim_key or c.evidence_links for c in synced_verified
            )
            if synced_verified and not published:
                result["issues"].append("PUBLICATION_GATE_BLOCKED")

            retrieval = ClaimRetrieval(session)
            probes: list[RetrievalProbe] = []
            for intent, (template, claim_type) in self.INTENT_QUERIES.items():
                query = template.format(name=name)
                intents = classify_intents(query)
                if intent not in intents.all_intents:
                    intents = IntentResult(primary=intent)
                found = await retrieval.published_claims(svc.id, intents, limit=5)
                matched = [c for c in found if c.claim_type == claim_type] if claim_type else found
                if not verified_pub and synced_verified:
                    classification = "PUBLICATION_GAP"
                elif matched:
                    classification = "OK"
                else:
                    classification = "RETRIEVAL_BUG" if verified_pub else "PUBLICATION_GAP"
                probe = RetrievalProbe(
                    service_id=catalogue_service_id,
                    catalogue_service_id=catalogue_service_id,
                    runtime_service_id=runtime_id,
                    query=query,
                    intent=intent,
                    claim_type=claim_type,
                    claim_found=bool(matched),
                    claim_id=str(matched[0].id) if matched else None,
                    evidence_count=len(matched[0].evidence_links) if matched else 0,
                    classification=classification,
                )
                probes.append(probe)

            result["retrieval_probes"] = [asdict(p) for p in probes]
            retrieval_ok = sum(1 for p in probes if p.claim_found)
            result["retrieval_accuracy"] = round(retrieval_ok / max(len(probes), 1), 4)
            if retrieval_ok < len(probes):
                result["issues"].append("RETRIEVAL_GAPS")

        return result

    async def validate_batch(
        self,
        service_ids: list[str],
        *,
        batch_slug: str,
        service_names: dict[str, str] | None = None,
    ) -> RuntimeConsistencyReport:
        service_names = service_names or {}
        services: list[dict[str, Any]] = []
        all_probes: list[dict[str, Any]] = []
        for sid in service_ids:
            svc_report = await self.validate_service(sid, service_name=service_names.get(sid))
            services.append(svc_report)
            all_probes.extend(svc_report.get("retrieval_probes") or [])

        total_probes = len(all_probes)
        ok_probes = sum(1 for p in all_probes if p.get("claim_found"))
        services_with_runtime = sum(1 for s in services if s.get("runtime_exists"))
        services_with_published = sum(1 for s in services if (s.get("published_claim_count") or 0) > 0)

        bottlenecks: list[dict[str, Any]] = []
        if services_with_runtime < len(service_ids):
            bottlenecks.append({"layer": "RUNTIME_STORAGE", "count": len(service_ids) - services_with_runtime})
        if services_with_published < services_with_runtime:
            bottlenecks.append(
                {"layer": "PUBLICATION", "count": services_with_runtime - services_with_published}
            )
        retrieval_bugs = sum(1 for p in all_probes if p.get("classification") == "RETRIEVAL_BUG")
        publication_gaps = sum(1 for p in all_probes if p.get("classification") == "PUBLICATION_GAP")
        if publication_gaps:
            bottlenecks.append({"layer": "PUBLICATION", "count": publication_gaps})
        if retrieval_bugs:
            bottlenecks.append({"layer": "RETRIEVAL", "count": retrieval_bugs})

        return RuntimeConsistencyReport(
            generated_at=_now(),
            batch_slug=batch_slug,
            db_path=str(self.db_path),
            services=services,
            retrieval_probes=all_probes,
            aggregate={
                "service_count": len(service_ids),
                "runtime_mapped": services_with_runtime,
                "published_services": services_with_published,
                "retrieval_accuracy": round(ok_probes / max(total_probes, 1), 4),
                "retrieval_correctness_pct": round(100 * ok_probes / max(total_probes, 1), 1),
            },
            bottlenecks=bottlenecks,
        )

    def write_audit(self, report: RuntimeConsistencyReport, path: Path | None = None) -> Path:
        out = path or self.repo_root / "data" / "audit" / "deep-research-runtime-consistency.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(asdict(report), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return out
