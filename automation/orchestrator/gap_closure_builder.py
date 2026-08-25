"""Generic gap-closure pass — records deferrals without re-researching entire batch."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from automation.orchestrator.phase_completion import batch_slug, raw_research_dir


class GapClosureBuilder:
    """Target gap closure for independently researchable gaps; defer the rest."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def build_gap_closure(self, batch: dict[str, Any]) -> dict[str, Any]:
        slug = batch_slug(batch)
        raw = raw_research_dir(self.repo_root, batch)
        verify_dir = self.repo_root / "data" / "research" / "verification" / slug
        gap_dir = self.repo_root / "data" / "research" / "verification" / f"{slug}-gap-closure"
        gap_dir.mkdir(parents=True, exist_ok=True)

        gaps_path = raw / "knowledge_gaps.json"
        gaps = []
        if gaps_path.exists():
            doc = json.loads(gaps_path.read_text(encoding="utf-8"))
            gaps = list(doc.get("gaps") or [])

        investigations: list[dict[str, Any]] = []
        deferred: list[dict[str, Any]] = []
        resolved = 0

        for gap in gaps:
            gap_type = gap.get("gap_type") or ""
            if gap_type in {"CURRENT_FEE_MISSING", "LOCAL_RULE_MISSING", "SLA_MISSING"}:
                deferred.append(
                    {
                        **gap,
                        "resolution": "DEFERRED_HUMAN_REVIEW",
                        "reason": "Requires authoritative fee/document source — not guessed",
                    }
                )
                investigations.append(
                    {
                        "gap_id": gap.get("gap_id"),
                        "status": "DEFERRED",
                        "action": "AUTO_DEFER_AND_CONTINUE",
                    }
                )
            elif gap_type == "CURRENT_URL_MISSING" and gap.get("url"):
                investigations.append(
                    {
                        "gap_id": gap.get("gap_id"),
                        "status": "PARTIAL",
                        "action": "URL documented; reachability unconfirmed at gap closure",
                    }
                )
            else:
                deferred.append({**gap, "resolution": "DEFERRED", "reason": "Not independently researchable in generic pass"})
                investigations.append({"gap_id": gap.get("gap_id"), "status": "DEFERRED", "action": "continue"})

        summary = {
            "batch_id": slug,
            "closed_at": self._now(),
            "builder": "generic_gap_closure_builder",
            "gaps_total": len(gaps),
            "resolved": resolved,
            "deferred": len(deferred),
            "investigations": len(investigations),
        }

        for name, payload in [
            ("knowledge_gaps.json", {"batch_id": slug, "gaps": deferred}),
            ("gap_investigations.json", {"investigations": investigations}),
            ("summary.json", summary),
            ("service_readiness.json", {"batch_id": slug, "services": batch.get("service_ids") or []}),
        ]:
            (gap_dir / name).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        report = self.repo_root / "docs" / "research" / f"{slug}-gap-closure.md"
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(
            f"# {batch.get('name', slug)} — Gap Closure\n\n"
            f"Generic gap closure on {self._now()}.\n\n"
            f"- Total gaps: {len(gaps)}\n"
            f"- Deferred: {len(deferred)}\n"
            f"- Resolved: {resolved}\n\n"
            f"Fee and document gaps deferred — no invented authoritative data.\n",
            encoding="utf-8",
        )

        if (verify_dir / "summary.json").exists():
            verify_summary = json.loads((verify_dir / "summary.json").read_text(encoding="utf-8"))
            verify_summary["knowledge_gaps_open"] = len(deferred)
            verify_summary["knowledge_gaps"] = len(deferred)
            (verify_dir / "summary.json").write_text(
                json.dumps(verify_summary, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

        StagingBuilder(self.repo_root).build_staging(batch)

        return {"complete": True, "summary": summary, "output_dir": str(gap_dir)}
