"""Generate machine-readable Cloud Agent task specifications per workflow phase."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from automation.orchestrator.batch_manager import BatchManager
from automation.orchestrator.phase_completion import batch_slug, raw_research_dir
from automation.schemas.state import ProjectState


@dataclass
class CloudTaskSpec:
    task_id: str
    batch_id: str
    batch_slug: str
    phase: str
    run_id: str
    service_ids: list[str]
    service_names: dict[str, str]
    domain: str
    project_state: dict[str, Any]
    previous_artifacts: list[str]
    knowledge_gaps: list[dict[str, Any]]
    known_conflicts: list[dict[str, Any]]
    required_outputs: list[str]
    result_schema: str
    safety_constraints: list[str]
    deployment_locked: bool
    no_external_paid_api: bool
    prompt_text: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def write(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


class TaskFactory:
    SAFETY = [
        "LOCAL_DEV_ONLY — deployment_allowed must remain false",
        "Do NOT deploy, merge to main, or use external paid AI APIs",
        "Never publish UNVERIFIED/CONFLICTING claims as authoritative",
        "Write validated result.json — do not mutate project_state.json directly",
    ]

    PHASE_OUTPUTS: dict[str, list[str]] = {
        "RESEARCH": [
            "data/research/raw/{slug}/scope.json",
            "data/research/raw/{slug}/services_index.json",
            "data/research/raw/{slug}/services/*.json",
            "data/research/raw/{slug}/claims.json",
            "data/research/raw/{slug}/sources.json",
            "data/research/raw/{slug}/conflicts.json",
            "data/research/raw/{slug}/knowledge_gaps.json",
            "data/research/raw/{slug}/metadata.json",
            "docs/research/{slug}-research.md",
            ".automation/runs/{run_id}/result.json",
        ],
        "VERIFICATION": [
            "data/research/verification/{slug}/claims_verification.json",
            "data/research/verification/{slug}/summary.json",
            ".automation/runs/{run_id}/result.json",
        ],
        "GAP_CLOSURE": [
            "data/research/verification/{slug}-gap-closure/summary.json",
            "docs/research/{slug}-gap-closure.md",
            ".automation/runs/{run_id}/result.json",
        ],
        "PUBLICATION": [
            "data/research/staging/{slug}/",
            "docs/research/{slug}-publication-report.md",
            ".automation/runs/{run_id}/result.json",
        ],
        "E2E": [
            "data/evaluation/{slug}/queries.json",
            "data/evaluation/{slug}/summary.json",
            "docs/evaluation/{slug}-publication-e2e.md",
            ".automation/runs/{run_id}/result.json",
        ],
        "REGRESSION": [
            ".automation/reports/regression_{batch_id}.json",
            ".automation/runs/{run_id}/result.json",
        ],
    }

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.batch_manager = BatchManager(repo_root)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _load_gaps(self, batch: dict[str, Any]) -> list[dict[str, Any]]:
        slug = batch_slug(batch)
        gaps_path = self.repo_root / "data" / "research" / "verification" / slug / "knowledge_gaps.json"
        if gaps_path.exists():
            data = json.loads(gaps_path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
            return list(data.get("gaps") or [])
        raw_gaps = raw_research_dir(self.repo_root, batch) / "knowledge_gaps.json"
        if raw_gaps.exists():
            data = json.loads(raw_gaps.read_text(encoding="utf-8"))
            return list(data.get("gaps") or [])
        return []

    def _load_conflicts(self, batch: dict[str, Any]) -> list[dict[str, Any]]:
        slug = batch_slug(batch)
        path = raw_research_dir(self.repo_root, batch) / "conflicts.json"
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            return list(data.get("conflicts") or [])
        return []

    def _service_names(self, batch: dict[str, Any]) -> dict[str, str]:
        catalogue = {s.get("service_id") or s.get("id"): s for s in self.batch_manager.load_catalogue()}
        names: dict[str, str] = {}
        for sid in batch.get("service_ids") or []:
            entry = catalogue.get(sid) or {}
            names[sid] = entry.get("service_name_en") or sid
        return names

    def _domain(self, batch: dict[str, Any]) -> str:
        catalogue = {s.get("service_id") or s.get("id"): s for s in self.batch_manager.load_catalogue()}
        cats: set[str] = set()
        for sid in batch.get("service_ids") or []:
            entry = catalogue.get(sid) or {}
            if entry.get("category_id"):
                cats.add(str(entry["category_id"]))
        return ",".join(sorted(cats)) or "government"

    def _format_outputs(self, batch: dict[str, Any], phase: str, run_id: str) -> list[str]:
        slug = batch_slug(batch)
        batch_id = batch["batch_id"]
        template = self.PHASE_OUTPUTS.get(phase, [])
        return [t.format(slug=slug, batch_id=batch_id, run_id=run_id) for t in template]

    def _read_template(self, phase: str) -> str:
        name = {
            "RESEARCH": "research",
            "VERIFICATION": "verification",
            "GAP_CLOSURE": "gap_closure",
            "PUBLICATION": "publication",
            "E2E": "e2e",
            "REGRESSION": "regression_fix",
        }.get(phase, "research")
        path = self.repo_root / "automation" / "prompts" / f"{name}.md"
        return path.read_text(encoding="utf-8") if path.exists() else ""

    def build_task(
        self,
        *,
        batch: dict[str, Any],
        phase: str,
        run_id: str,
        state: ProjectState | None = None,
        extra_context: dict[str, Any] | None = None,
    ) -> CloudTaskSpec:
        slug = batch_slug(batch)
        task_id = f"{batch['batch_id']}:{phase}:{run_id}"
        template = self._read_template(phase)
        outputs = self._format_outputs(batch, phase, run_id)
        project = state.to_dict() if state else {}
        ctx = {
            "batch": batch,
            "phase": phase,
            "run_id": run_id,
            "service_ids": batch.get("service_ids") or [],
            "gaps": self._load_gaps(batch),
            "conflicts": self._load_conflicts(batch),
            **(extra_context or {}),
        }
        prompt = (
            f"# BDA Cloud Task — {phase}\n\n"
            f"**Batch:** {batch['batch_id']} ({batch.get('name', slug)})\n"
            f"**Run ID:** {run_id}\n\n"
            f"## Safety\n"
            + "\n".join(f"- {s}" for s in self.SAFETY)
            + f"\n\n## Required outputs\n"
            + "\n".join(f"- `{o}`" for o in outputs)
            + f"\n\n## Context\n```json\n{json.dumps(ctx, indent=2)}\n```\n\n"
            f"## Phase instructions\n{template}\n\n"
            f"Follow docs/research/BATCH_RESEARCH_TEMPLATE.md for RESEARCH.\n"
            f"Write machine-readable `.automation/runs/{run_id}/result.json` when complete.\n"
        )
        return CloudTaskSpec(
            task_id=task_id,
            batch_id=batch["batch_id"],
            batch_slug=slug,
            phase=phase,
            run_id=run_id,
            service_ids=list(batch.get("service_ids") or []),
            service_names=self._service_names(batch),
            domain=self._domain(batch),
            project_state=project,
            previous_artifacts=[],
            knowledge_gaps=self._load_gaps(batch),
            known_conflicts=self._load_conflicts(batch),
            required_outputs=outputs,
            result_schema="automation.schemas.result.PhaseResult",
            safety_constraints=self.SAFETY,
            deployment_locked=True,
            no_external_paid_api=True,
            prompt_text=prompt,
            metadata={"created_at": self._now()},
        )

    def create_research_task(self, batch: dict[str, Any], run_id: str, state: ProjectState | None = None) -> CloudTaskSpec:
        return self.build_task(batch=batch, phase="RESEARCH", run_id=run_id, state=state)

    def create_verification_task(self, batch: dict[str, Any], run_id: str, state: ProjectState | None = None) -> CloudTaskSpec:
        return self.build_task(batch=batch, phase="VERIFICATION", run_id=run_id, state=state)

    def create_gap_closure_task(self, batch: dict[str, Any], run_id: str, state: ProjectState | None = None) -> CloudTaskSpec:
        return self.build_task(batch=batch, phase="GAP_CLOSURE", run_id=run_id, state=state)

    def create_publication_task(self, batch: dict[str, Any], run_id: str, state: ProjectState | None = None) -> CloudTaskSpec:
        return self.build_task(batch=batch, phase="PUBLICATION", run_id=run_id, state=state)

    def create_e2e_task(self, batch: dict[str, Any], run_id: str, state: ProjectState | None = None) -> CloudTaskSpec:
        return self.build_task(batch=batch, phase="E2E", run_id=run_id, state=state)

    def create_regression_task(self, batch: dict[str, Any], run_id: str, state: ProjectState | None = None) -> CloudTaskSpec:
        return self.build_task(batch=batch, phase="REGRESSION", run_id=run_id, state=state)

    def create_fix_task(
        self,
        batch: dict[str, Any],
        run_id: str,
        *,
        issue: str,
        state: ProjectState | None = None,
    ) -> CloudTaskSpec:
        return self.build_task(
            batch=batch,
            phase="REGRESSION",
            run_id=run_id,
            state=state,
            extra_context={"fix_issue": issue, "task_kind": "FIX"},
        )
