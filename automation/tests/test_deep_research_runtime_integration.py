"""Tests for Step 32 deep-research pipeline and runtime integration."""

from __future__ import annotations

import json
from pathlib import Path

from automation.orchestrator.claim_density import score_claim_density
from automation.orchestrator.deep_research_pipeline import STEP31_EXCLUDED, DeepResearchPipeline
from automation.orchestrator.deep_research_staging import BATCH_SLUG, DeepResearchStagingBuilder
from automation.orchestrator.partial_knowledge_analyzer import PartialKnowledgeAnalyzer
from automation.orchestrator.task_factory import TaskFactory

REPO = Path(__file__).resolve().parents[2]


def test_select_pilot_20_excludes_step31() -> None:
    analyzer = PartialKnowledgeAnalyzer(REPO)
    selected = analyzer.select_pilot_20_services()
    assert len(selected) == 20
    ids = {s["service_id"] for s in selected}
    assert not ids & STEP31_EXCLUDED


def test_deep_research_task_factory() -> None:
    factory = TaskFactory(REPO)
    analyzer = PartialKnowledgeAnalyzer(REPO)
    sid = analyzer.select_pilot_20_services()[0]["service_id"]
    task = factory.create_deep_research_task(sid, "test-run")
    assert task.phase == "DEEP_RESEARCH"
    assert "DEEP RESEARCH THIS EXACT SERVICE" in task.prompt_text
    assert task.metadata.get("deep_research_brief", {}).get("instruction") == "DEEP RESEARCH THIS EXACT SERVICE"


def test_staging_builder_batch_slug() -> None:
    assert BATCH_SLUG == "deep-research-pilot-20"


def test_claim_density_not_arbitrary() -> None:
    claims = [
        {"claim_class": "SERVICE_SPECIFIC", "claim_type": "procedure", "verification_status": "VERIFIED", "source_ids": ["s1"]},
        {"claim_class": "SERVICE_SPECIFIC", "claim_type": "document", "condition": {"requirement_class": "MUST_NEED"}, "verification_status": "VERIFIED", "source_ids": ["s1"]},
    ]
    score = score_claim_density("test-svc", "EDUCATION", claims)
    assert score.complexity_tier == "STANDARD"
    assert score.critical_expected >= 2


def test_staging_from_deep_research_dir() -> None:
    pilot_dir = REPO / "data" / "research" / "deep-research-pilot" / "land-mutation-apply"
    if not pilot_dir.exists():
        return
    builder = DeepResearchStagingBuilder(REPO)
    catalogue = PartialKnowledgeAnalyzer(REPO).catalogue
    staging = builder.build_from_service_dirs([pilot_dir], catalogue)
    assert staging.name == "deep-research-pilot-20"
    claims = json.loads((staging / "claims.json").read_text()).get("claims") or []
    assert isinstance(claims, list)


def test_pipeline_wave_gate_thresholds() -> None:
    pipeline = DeepResearchPipeline(REPO)
    assert pipeline.SUPPORTED_COVERAGE_TARGET == 0.75
    assert pipeline.RETRIEVAL_ACCURACY_TARGET == 0.95
