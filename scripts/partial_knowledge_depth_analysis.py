#!/usr/bin/env python3
"""Generate partial-knowledge taxonomy, user-value matrix, and bottleneck analysis."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from automation.orchestrator.partial_knowledge_analyzer import PartialKnowledgeAnalyzer


def main() -> int:
    analyzer = PartialKnowledgeAnalyzer(ROOT)
    result = analyzer.run_full_analysis()

    audit_dir = ROOT / "data" / "audit"
    audit_dir.mkdir(parents=True, exist_ok=True)

    taxonomy_path = audit_dir / "partial-knowledge-taxonomy.json"
    matrix_path = audit_dir / "service-user-value-matrix.json"
    bottlenecks_path = audit_dir / "partial-knowledge-bottlenecks.json"

    taxonomy_path.write_text(
        json.dumps(
            {
                "generated_at": result["generated_at"],
                "total_partial_services": result["total_partial_services"],
                "categories": result["taxonomy"]["categories"],
                "reason_frequency": result["taxonomy"]["reason_frequency"],
                "by_category": result["taxonomy"]["by_category"],
                "by_domain": result["taxonomy"]["by_domain"],
                "services": result["taxonomy"]["services"],
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    matrix_path.write_text(
        json.dumps(
            {
                "generated_at": result["generated_at"],
                "questions": result["user_value_matrix"]["questions"],
                "aggregate_supported_coverage": result["user_value_matrix"]["aggregate_supported_coverage"],
                "services": result["user_value_matrix"]["services"],
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    bottlenecks_path.write_text(json.dumps(result["bottlenecks"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps({"ok": True, "total_partial": result["total_partial_services"], "primary_bottleneck": result["bottlenecks"]["primary_bottleneck"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
