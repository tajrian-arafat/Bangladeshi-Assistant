"""Generic claim verification — no batch-specific verify script required."""

from __future__ import annotations

import json
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from automation.orchestrator.phase_completion import batch_slug, raw_research_dir
from automation.orchestrator.staging_builder import StagingBuilder


class VerificationBuilder:
    """Independently verify raw research claims using source probe evidence."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def build_batch_verification(self, batch: dict[str, Any]) -> dict[str, Any]:
        slug = batch_slug(batch)
        raw = raw_research_dir(self.repo_root, batch)
        out = self.repo_root / "data" / "research" / "verification" / slug
        snap = out / "source_snapshots"
        out.mkdir(parents=True, exist_ok=True)
        snap.mkdir(parents=True, exist_ok=True)

        claims_path = raw / "claims.json"
        sources_path = raw / "sources.json"
        gaps_path = raw / "knowledge_gaps.json"
        if not claims_path.exists():
            return {"complete": False, "error": "missing claims.json"}

        claims_doc = json.loads(claims_path.read_text(encoding="utf-8"))
        sources_doc = json.loads(sources_path.read_text(encoding="utf-8")) if sources_path.exists() else {"sources": []}
        gaps_doc = json.loads(gaps_path.read_text(encoding="utf-8")) if gaps_path.exists() else {"gaps": []}

        sources_by_id = {s["source_id"]: s for s in sources_doc.get("sources") or []}
        verifications: list[dict[str, Any]] = []
        status_counts: Counter[str] = Counter()

        for claim in claims_doc.get("claims") or []:
            claim_id = claim.get("claim_id") or ""
            claim_type = claim.get("claim_type") or ""
            source_ids = list(claim.get("source_ids") or [])
            status = "UNVERIFIED"
            notes: list[str] = []
            evidence: list[dict[str, Any]] = []

            for sid in source_ids:
                src = sources_by_id.get(sid)
                if not src:
                    continue
                probe = src.get("probe") or {}
                evidence.append(
                    {
                        "source_id": sid,
                        "url": src.get("url"),
                        "reachable": probe.get("reachable"),
                        "status_code": probe.get("status_code"),
                    }
                )

            if claim_type == "application_url":
                reachable = any(e.get("reachable") for e in evidence)
                if reachable:
                    status = "VERIFIED"
                    notes.append("Official portal URL reachable at verification time")
                elif evidence:
                    status = "PARTIALLY_VERIFIED"
                    notes.append("URL documented but not independently reachable")
                else:
                    status = "UNVERIFIED"
                    notes.append("No probe evidence for application URL")
            elif claim_type == "eligibility":
                if "src-catalogue" in source_ids:
                    status = "PARTIALLY_VERIFIED"
                    notes.append("Authority from catalogue only — not independently confirmed")
                else:
                    status = "UNVERIFIED"
            else:
                status = "UNVERIFIED"
                notes.append("Generic builder — requires dedicated verification")

            if "fee" in claim_id or "fee" in (claim.get("claim_text") or "").lower():
                status = "UNVERIFIED"
                notes.append("Fee claims require strict independent evidence — not verified")

            status_counts[status] += 1
            verifications.append(
                {
                    "claim_id": claim_id,
                    "service_id": claim.get("service_id"),
                    "verification_status": status,
                    "verifier": "generic_verification_builder",
                    "verified_at": self._now(),
                    "notes": notes,
                    "evidence": evidence,
                }
            )

        open_gaps = list(gaps_doc.get("gaps") or [])
        summary = {
            "batch_id": slug,
            "verified_at": self._now(),
            "verifier": "generic_verification_builder",
            "claims_total": len(verifications),
            "status_counts": dict(status_counts),
            "verified": status_counts.get("VERIFIED", 0),
            "partially_verified": status_counts.get("PARTIALLY_VERIFIED", 0),
            "unverified": status_counts.get("UNVERIFIED", 0),
            "conflicting": status_counts.get("CONFLICTING", 0),
            "critical_conflicts": 0,
            "knowledge_gaps": len(open_gaps),
            "knowledge_gaps_open": len(open_gaps),
        }

        claims_file = out / "claims_verification.json"
        claims_file.write_text(
            json.dumps({"batch_id": slug, "verifications": verifications}, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        raw_snap = raw / "source_snapshots"
        if raw_snap.is_dir():
            for item in raw_snap.iterdir():
                dest = snap / item.name
                if item.is_file() and not dest.exists():
                    shutil.copy2(item, dest)

        StagingBuilder(self.repo_root).build_staging(batch)

        return {"complete": True, "summary": summary, "output_dir": str(out)}
