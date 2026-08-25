"""Tests for partial-knowledge depth analysis."""

from __future__ import annotations

import json
from pathlib import Path

from automation.orchestrator.partial_knowledge_analyzer import PartialKnowledgeAnalyzer

REPO = Path(__file__).resolve().parents[2]


def test_partial_taxonomy_covers_all_partial_services() -> None:
    analyzer = PartialKnowledgeAnalyzer(REPO)
    result = analyzer.run_full_analysis()
    audit = json.loads((REPO / "data/audit/final-service-completeness.json").read_text(encoding="utf-8"))
    partial_count = sum(1 for s in audit["services"] if s.get("completeness") == "PARTIAL")
    assert result["total_partial_services"] == partial_count
    assert len(result["taxonomy"]["services"]) == partial_count


def test_pilot_selects_twelve_partial_services() -> None:
    analyzer = PartialKnowledgeAnalyzer(REPO)
    pilot = analyzer.select_pilot_services()
    assert len(pilot) == 12
    roles = {p["pilot_role"] for p in pilot}
    assert "land" in roles
    assert "education" in roles
    assert "health" in roles
    assert "judiciary" in roles


def test_bottleneck_has_primary() -> None:
    analyzer = PartialKnowledgeAnalyzer(REPO)
    result = analyzer.run_full_analysis()
    assert result["bottlenecks"]["primary_bottleneck"]
    assert result["bottlenecks"]["bottleneck_scores"]
