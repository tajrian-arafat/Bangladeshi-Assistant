"""Cloud executor and generic research builder tests."""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from automation.orchestrator.cloud_executor import CloudExecutor, ExecutionMode, ExecutorMode
from automation.orchestrator.cloud_worker import CloudWorker
from automation.orchestrator.research_builder import ResearchBuilder
from automation.orchestrator.task_factory import TaskFactory
from automation.orchestrator.verification_builder import VerificationBuilder

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture()
def batch04() -> dict:
    queue = json.loads((REPO / ".automation" / "batch_queue.json").read_text(encoding="utf-8"))
    return next(b for b in queue["batches"] if b["batch_id"] == "BATCH_04")


def test_cloud_executor_in_process_available() -> None:
    executor = CloudExecutor(REPO)
    with patch.dict(os.environ, {"CURSOR_AGENT": "1", "CURSOR_CONVERSATION_ID": "bc-test-agent"}):
        assert executor.in_process_cloud_available is True
        assert executor.executor_available() is True


def test_task_factory_research_task(batch04: dict) -> None:
    factory = TaskFactory(REPO)
    task = factory.create_research_task(batch04, "run-test-cloud")
    assert task.batch_id == "BATCH_04"
    assert task.phase == "RESEARCH"
    assert len(task.service_ids) == 11
    assert "result.json" in task.prompt_text
    assert task.deployment_locked is True
    assert task.no_external_paid_api is True


def test_research_builder_produces_artifacts(batch04: dict, tmp_path: Path) -> None:
    import shutil
    cat_src = REPO / "data" / "service_catalogue"
    cat_dst = tmp_path / "data" / "service_catalogue"
    shutil.copytree(cat_src, cat_dst)

    raw = tmp_path / "data" / "research" / "raw" / "batch-04-tax-vat-customs"
    raw.mkdir(parents=True)
    (raw / "scope.json").write_text('{"in_scope": []}')
    (raw / "services_index.json").write_text('{"services": []}')

    builder = ResearchBuilder(tmp_path)
    with patch.object(builder.batch_manager, "load_catalogue") as mock_cat:
        mock_cat.return_value = [
            {
                "service_id": sid,
                "service_name_en": sid.replace("-", " ").title(),
                "status": "CONFIRMED",
                "authority_id": "nbr",
            }
            for sid in batch04["service_ids"][:2]
        ]
        batch = {**batch04, "service_ids": batch04["service_ids"][:2]}
        with patch.object(builder, "_fetch_probe", return_value={"reachable": True, "status_code": 200, "title": "NBR"}):
            result = builder.build_batch_research(batch)

    assert result["metadata"]["claims_total"] > 0
    assert (raw / "claims.json").exists()
    assert (raw / "metadata.json").exists()
    assert (raw / "services").is_dir()


def test_cloud_worker_research_in_process(batch04: dict) -> None:
    worker = CloudWorker(REPO)
    factory = TaskFactory(REPO)
    task = factory.create_research_task(batch04, "run-test123-research")
    with patch.dict(os.environ, {"CURSOR_AGENT": "1", "CURSOR_CONVERSATION_ID": "bc-test"}):
        with patch.object(worker.research_builder, "build_batch_research") as mock_build:
            mock_build.return_value = {"complete": True, "metadata": {"claims_total": 33}}
            raw = REPO / "data" / "research" / "raw" / "batch-04-tax-vat-customs"
            raw.mkdir(parents=True, exist_ok=True)
            meta = {
                "services_in_scope": 11,
                "services_researched": 11,
                "claims_total": 33,
                "knowledge_gaps": 22,
                "conflicts": 0,
                "scaffolding_only": True,
                "authoritative_research": False,
            }
            (raw / "metadata.json").write_text(json.dumps(meta))
            for name in ["scope.json", "services_index.json", "claims.json", "sources.json", "conflicts.json", "knowledge_gaps.json"]:
                if not (raw / name).exists():
                    (raw / name).write_text("{}")
            services = raw / "services"
            services.mkdir(exist_ok=True)
            for sid in batch04["service_ids"]:
                (services / f"{sid}.json").write_text(json.dumps({"service_id": sid}))

            result = worker.execute(task, batch04)
            # Generic builder batches fail service-level quality gate
            assert result.status == "PARTIAL"
            assert result.recommended_next_phase == "RESEARCH"


def test_verification_builder(batch04: dict, tmp_path: Path) -> None:
    slug = "batch-04-tax-vat-customs"
    raw = tmp_path / "data" / "research" / "raw" / slug
    raw.mkdir(parents=True)
    claims = {
        "claims": [
            {
                "claim_id": "tax-etin-registration::c-application-portal",
                "service_id": "tax-etin-registration",
                "claim_type": "application_url",
                "source_ids": ["src-tax-etin-registration"],
            }
        ]
    }
    sources = {
        "sources": [
            {
                "source_id": "src-tax-etin-registration",
                "url": "https://secure.incometax.gov.bd",
                "probe": {"reachable": True, "status_code": 200},
            }
        ]
    }
    (raw / "claims.json").write_text(json.dumps(claims))
    (raw / "sources.json").write_text(json.dumps(sources))
    (raw / "knowledge_gaps.json").write_text(json.dumps({"gaps": []}))

    builder = VerificationBuilder(tmp_path)
    out = builder.build_batch_verification(batch04)
    assert out["complete"] is True
    verify_dir = tmp_path / "data" / "research" / "verification" / slug
    assert (verify_dir / "claims_verification.json").exists()


def test_executor_unavailable_writes_decision(batch04: dict) -> None:
    executor = CloudExecutor(REPO)
    with patch.dict(os.environ, {"CURSOR_AGENT": "", "CURSOR_CONVERSATION_ID": ""}, clear=False):
        executor.mode = ExecutorMode.AUTO_CLOUD
        executor.adapter.api_key = None
        path = executor.write_executor_unavailable_decision("BATCH_04", "test unavailable")
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["status"] == "GLOBAL_BLOCKED"
