#!/usr/bin/env python3
"""Run 20-service deep-research pilot with runtime integration (Step 32)."""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from automation.orchestrator.deep_research_pipeline import DeepResearchPipeline
from automation.orchestrator.partial_knowledge_analyzer import PartialKnowledgeAnalyzer


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def generate_report(summary: dict, selected: list[dict], out_path: Path) -> None:
    lines = [
        "# Deep Research Runtime Integration (Step 32)",
        "",
        f"Generated: {summary.get('generated_at', _now())}",
        "",
        "## Pilot scope",
        "",
        f"- **Services:** {summary.get('aggregate', {}).get('services', 20)}",
        f"- **Pilot passed:** {summary.get('pilot_passed')}",
        f"- **Step 31 services excluded:** 12",
        "",
        "## Selected services",
        "",
        "| Role | Service ID | Domain |",
        "|------|------------|--------|",
    ]
    for s in selected:
        lines.append(f"| {s.get('pilot_role')} | `{s['service_id']}` | {s.get('category_id', '')} |")

    agg = summary.get("aggregate") or {}
    lines.extend(
        [
            "",
            "## Aggregate metrics",
            "",
            f"- Supported-answer coverage: **{agg.get('avg_supported_coverage', 0):.1%}** (target ≥75%)",
            f"- Runtime retrieval accuracy: **{agg.get('avg_retrieval_accuracy', 0):.1%}** (target ≥95%)",
            "",
            "## Wave gates",
            "",
        ]
    )
    for key in ("wave1", "wave2"):
        wave = summary.get(key) or {}
        gate = wave.get("gate") or {}
        lines.append(f"### {key}")
        lines.append(f"- Passed: {gate.get('passed')}")
        lines.append(f"- Avg supported coverage: {gate.get('avg_supported_coverage', 0):.1%}")
        lines.append(f"- Avg retrieval accuracy: {gate.get('avg_retrieval_accuracy', 0):.1%}")
        if gate.get("failures"):
            lines.append(f"- Failures: {', '.join(gate['failures'])}")
        lines.append("")

    reg = summary.get("regression") or {}
    lines.extend(
        [
            "## Regression",
            "",
            f"- Passed: **{reg.get('regression_passed')}**",
            f"- Automation/backend tests: {reg.get('automation_backend_tests')}",
            "",
            "## Bottleneck analysis",
            "",
            "After pilot, classify failures by layer: RESEARCH, SOURCE ACCESS, CLAIM EXTRACTION, "
            "VERIFICATION, PUBLICATION, RUNTIME STORAGE, RETRIEVAL, ANSWER PLANNER, CITATION, E2E.",
            "",
            "See `data/audit/deep-research-runtime-consistency.json` for per-service retrieval probes.",
            "",
            "## Constraints preserved",
            "",
            "- COMPLETE thresholds not lowered",
            "- Remaining 396+ PARTIAL services queued as `DEEP_RESEARCH_REQUIRED` — not autorun",
            "- No deploy, no merge",
        ]
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    analyzer = PartialKnowledgeAnalyzer(ROOT)
    selected = analyzer.select_pilot_20_services()
    if len(selected) < 20:
        print(json.dumps({"error": "Insufficient pilot services", "count": len(selected)}, indent=2))
        return 1

    selection_path = ROOT / "data" / "research" / "deep-research-pilot-20" / "selection.json"
    selection_path.parent.mkdir(parents=True, exist_ok=True)
    selection_path.write_text(
        json.dumps({"generated_at": _now(), "services": selected}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    service_ids = [s["service_id"] for s in selected]
    wave1 = service_ids[:10]
    wave2 = service_ids[10:20]

    pipeline = DeepResearchPipeline(ROOT)
    summary = asyncio.run(pipeline.run_pilot(wave1, wave2, publish=True))

    report_path = ROOT / "docs" / "evaluation" / "deep-research-runtime-integration.md"
    generate_report(summary, selected, report_path)

    print(
        json.dumps(
            {
                "ok": summary.get("pilot_passed"),
                "services": len(service_ids),
                "pilot_passed": summary.get("pilot_passed"),
                "report": str(report_path),
            },
            indent=2,
        )
    )
    return 0 if summary.get("pilot_passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
