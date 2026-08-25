"""Normalize verified research into publication staging — no batch-specific script required."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from automation.orchestrator.phase_completion import batch_slug, raw_research_dir


class StagingBuilder:
    """Build staging artifacts from raw research + verification results."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def build_staging(self, batch: dict[str, Any]) -> dict[str, Any]:
        slug = batch_slug(batch)
        raw = raw_research_dir(self.repo_root, batch)
        verify_dir = self.repo_root / "data" / "research" / "verification" / slug
        staging = self.repo_root / "data" / "research" / "staging" / slug
        staging.mkdir(parents=True, exist_ok=True)

        claims_doc = json.loads((raw / "claims.json").read_text(encoding="utf-8"))
        sources_doc = json.loads((raw / "sources.json").read_text(encoding="utf-8")) if (raw / "sources.json").exists() else {"sources": []}
        verify_doc = json.loads((verify_dir / "claims_verification.json").read_text(encoding="utf-8")) if (verify_dir / "claims_verification.json").exists() else {"verifications": []}

        verify_by_id = {v["claim_id"]: v for v in verify_doc.get("verifications") or []}
        publishable_statuses = {"VERIFIED", "PARTIALLY_VERIFIED"}
        staging_claims: list[dict[str, Any]] = []
        evidence: list[dict[str, Any]] = []
        today = date.today().isoformat()

        for claim in claims_doc.get("claims") or []:
            claim_id = claim.get("claim_id") or ""
            v = verify_by_id.get(claim_id) or {}
            vstatus = v.get("verification_status") or "UNVERIFIED"
            if vstatus not in publishable_statuses:
                continue
            pipeline = vstatus
            staging_claims.append(
                {
                    **claim,
                    "pipeline_status": pipeline,
                    "provenance": {
                        "batch_id": slug,
                        "normalized_at": today,
                        "verification_status": vstatus,
                        "publication_status": "STAGING_ONLY",
                    },
                    "independent_verification": {
                        "verifier": v.get("verifier", "generic_verification_builder"),
                        "verified_at": v.get("verified_at"),
                        "reasoning": "; ".join(v.get("notes") or []),
                    },
                }
            )
            for sid in claim.get("source_ids") or []:
                evidence.append(
                    {
                        "evidence_id": f"ev-{claim_id}-{sid}",
                        "claim_id": claim_id,
                        "source_id": sid,
                    }
                )

        services = []
        services_dir = raw / "services"
        if services_dir.is_dir():
            for path in sorted(services_dir.glob("*.json")):
                services.append(json.loads(path.read_text(encoding="utf-8")))

        manifest = {
            "batch_id": slug,
            "normalized_at": today,
            "builder": "generic_staging_builder",
            "claims_count": len(staging_claims),
            "services_count": len(services),
        }

        for name, payload in [
            ("claims.json", {"claims": staging_claims}),
            ("sources.json", sources_doc),
            ("services.json", {"services": services}),
            ("evidence.json", {"evidence": evidence}),
            ("fees.json", {"fees": []}),
            ("source_versions.json", {"versions": []}),
            ("MANIFEST.json", manifest),
        ]:
            (staging / name).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        return {"complete": True, "staging_dir": str(staging), "claims_count": len(staging_claims)}
