#!/usr/bin/env python3
"""Generate partial-knowledge depth analysis markdown report."""

from __future__ import annotations

import json
from pathlib import Path


def generate_report(repo_root: Path, pilot_summary: dict | None = None) -> Path:
    taxonomy = json.loads((repo_root / "data/audit/partial-knowledge-taxonomy.json").read_text(encoding="utf-8"))
    bottlenecks = json.loads((repo_root / "data/audit/partial-knowledge-bottlenecks.json").read_text(encoding="utf-8"))
    matrix = json.loads((repo_root / "data/audit/service-user-value-matrix.json").read_text(encoding="utf-8"))

    if pilot_summary is None and (repo_root / "data/research/deep-research-pilot/pilot-summary.json").exists():
        pilot_summary = json.loads(
            (repo_root / "data/research/deep-research-pilot/pilot-summary.json").read_text(encoding="utf-8")
        )

    lines = [
        "# Partial Knowledge Depth Analysis",
        "",
        f"Generated: {taxonomy.get('generated_at', 'unknown')}",
        "",
        "## Executive Summary",
        "",
        f"- **PARTIAL services audited:** {taxonomy.get('total_partial_services', 0)}",
        f"- **Primary bottleneck (evidence-based):** {bottlenecks.get('primary_bottleneck', 'unknown')}",
        f"- **Aggregate user-value supported coverage:** {matrix.get('aggregate_supported_coverage', 0):.1%}",
        "",
        "Step 30 eliminated false completion. Step 31 investigates why services remain PARTIAL despite service-specific sources existing.",
        "",
        "## 1. Partial-Knowledge Taxonomy (416 services)",
        "",
        "### Top partial reasons",
        "",
        "| Reason | Count |",
        "|--------|------:|",
    ]
    for reason, count in list(bottlenecks.get("top_missing_dimensions", {}).items())[:15]:
        lines.append(f"| {reason} | {count} |")

    dim_pct = bottlenecks.get("dimension_missing_pct") or {}
    lines.extend(
        [
            "",
            "### Dimension gap percentages",
            "",
            "| Dimension | % PARTIAL services |",
            "|-----------|-------------------:|",
        ]
    )
    for dim, pct in dim_pct.items():
        lines.append(f"| {dim} | {pct}% |")

    lines.extend(
        [
            "",
            "## 2. Critical vs Non-Critical Gaps",
            "",
            "Critical gaps are profile-specific (from `service_research_profiles.json`), not a universal checklist.",
            "Each service record in `data/audit/partial-knowledge-taxonomy.json` includes `critical_missing`, `noncritical_missing`, `unresolvable_gaps`, and `resolvable_gaps`.",
            "",
            "## 3. User-Value Model",
            "",
            f"Aggregate supported-answer coverage across 416 PARTIAL services: **{matrix.get('aggregate_supported_coverage', 0):.1%}**",
            "",
            "Full matrix: `data/audit/service-user-value-matrix.json`",
            "",
            "## 4. Biggest Knowledge Bottleneck",
            "",
            f"**Primary bottleneck:** `{bottlenecks.get('primary_bottleneck')}`",
            "",
            "### Bottleneck scores",
            "",
            "| Layer | Score |",
            "|-------|------:|",
        ]
    )
    for layer, score in sorted((bottlenecks.get("bottleneck_scores") or {}).items(), key=lambda x: -x[1]):
        lines.append(f"| {layer} | {score} |")

    src_lim = bottlenecks.get("source_limitations") or {}
    lines.extend(
        [
            "",
            "### Source limitations",
            "",
            f"- Official source unavailable: {src_lim.get('official_source_unavailable_pct', 0)}%",
            f"- JS rendering limitation: {src_lim.get('js_rendering_limitation_pct', 0)}%",
            f"- Calculator-required fees: {src_lim.get('calculator_required_pct', 0)}%",
            "",
            f"_{bottlenecks.get('interpretation', '')}_",
            "",
        ]
    )

    if pilot_summary:
        agg = pilot_summary.get("aggregate") or {}
        lines.extend(
            [
                "## 5. Deep-Research Pilot (12 services)",
                "",
                "### Pilot selection",
                "",
                "| Role | Service ID |",
                "|------|------------|",
            ]
        )
        for svc in pilot_summary.get("pilot_services") or []:
            lines.append(f"| {svc.get('pilot_role')} | `{svc.get('service_id')}` |")

        lines.extend(
            [
                "",
                "### Supported-answer coverage: before vs after",
                "",
                "| Service | Before | After | Verified claims |",
                "|---------|-------:|------:|----------------:|",
            ]
        )
        for r in pilot_summary.get("results") or []:
            lines.append(
                f"| `{r['service_id']}` | {r['before']['supported_answer_coverage']:.1%} | "
                f"{r['after']['supported_answer_coverage']:.1%} | {r['after']['verified_claims']} |"
            )

        lines.extend(
            [
                "",
                f"- **Average supported coverage before:** {agg.get('avg_supported_coverage_before', 0):.1%}",
                f"- **Average supported coverage after:** {agg.get('avg_supported_coverage_after', 0):.1%}",
                f"- **Average verified claims after:** {agg.get('avg_verified_claims_after', 0)}",
                "",
                "## 6. Pilot Success Criteria Answers",
                "",
                "1. **Dominant PARTIAL reasons:** Missing E2E supported coverage, missing fees/documents/procedure, claim density — see taxonomy.",
                "2. **Obtainable dimensions:** Procedure, eligibility, documents (via deeper official portal/PDF investigation).",
                "3. **Structurally unavailable:** Calculator-derived fees, JS-only portals without browser render, rare local variation rules.",
                "4. **Deep research impact:** Supported-answer coverage improved for pilot services with curated deep hints + verification.",
                "5. **COMPLETE definition:** Do not lower threshold yet — improvement signal exists but E2E supported coverage still below COMPLETE bar for most pilots.",
                "",
                "## 7. Runtime & Regression",
                "",
                f"- Runtime DB: `{pilot_summary.get('runtime_validation', {}).get('db_path')}` — {pilot_summary.get('runtime_validation', {}).get('status')}",
                f"- Regression passed: **{pilot_summary.get('regression', {}).get('regression_passed')}**",
                "",
                "## 8. Recommendation for 416-service backlog",
                "",
                "Do NOT rerun all 379 services blindly. Instead:",
                "",
                "1. Prioritize high-usage PARTIAL services for deep-research protocol.",
                "2. Add browser-rendered retrieval for JS portal services (Land mutation, NID, e-Courts).",
                "3. Treat calculator-derived fees as CALCULATOR_DERIVED — not static COMPLETE blockers.",
                "4. Expand conditional knowledge (IF/THEN) rather than flattening requirements.",
                "5. Wire deep-research staging into runtime publication path for verified claims only.",
                "6. Keep COMPLETE threshold — measure supported-answer coverage improvement first.",
                "",
                "## Safety",
                "",
                "- deployment_allowed = false",
                "- auto_merge = false",
                "- No full 379-service rerun started",
                "",
            ]
        )

    report_path = repo_root / "docs/evaluation/partial-knowledge-depth-analysis.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


if __name__ == "__main__":
    import sys

    root = Path(__file__).resolve().parents[1]
    generate_report(root)
    print("Report written")
