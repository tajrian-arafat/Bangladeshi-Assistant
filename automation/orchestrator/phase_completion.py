"""Phase artifact completion checks — research must not finish on kickoff files alone."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CompletionReport:
    complete: bool
    phase: str
    missing: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


def batch_slug(batch: dict[str, Any]) -> str:
    return batch.get("slug") or batch["batch_id"].lower().replace("_", "-")


def raw_research_dir(repo_root: Path, batch: dict[str, Any]) -> Path:
    return repo_root / "data" / "research" / "raw" / batch_slug(batch)


def check_research_complete(repo_root: Path, batch: dict[str, Any]) -> CompletionReport:
    """Require full discovery artifacts per BATCH_RESEARCH_TEMPLATE.md."""
    raw = raw_research_dir(repo_root, batch)
    service_ids: list[str] = list(batch.get("service_ids") or [])
    missing: list[str] = []

    required_top = [
        "scope.json",
        "services_index.json",
        "claims.json",
        "sources.json",
        "conflicts.json",
        "knowledge_gaps.json",
        "metadata.json",
    ]
    for name in required_top:
        if not (raw / name).exists():
            missing.append(str(raw / name))

    services_dir = raw / "services"
    if not services_dir.is_dir():
        missing.append(str(services_dir))
    else:
        for sid in service_ids:
            svc_path = services_dir / f"{sid}.json"
            if not svc_path.exists():
                missing.append(str(svc_path))

    details: dict[str, Any] = {"raw_dir": str(raw)}
    if not missing and (raw / "metadata.json").exists():
        meta = json.loads((raw / "metadata.json").read_text(encoding="utf-8"))
        details["metadata"] = meta
        researched = int(meta.get("services_researched") or 0)
        in_scope = int(meta.get("services_in_scope") or len(service_ids))
        if researched < in_scope:
            missing.append(f"metadata.services_researched ({researched}) < in_scope ({in_scope})")
        claims_total = int(meta.get("claims_total") or 0)
        if claims_total <= 0:
            missing.append("metadata.claims_total must be > 0")

    return CompletionReport(
        complete=len(missing) == 0,
        phase="RESEARCH",
        missing=missing,
        details=details,
    )


def check_verification_complete(repo_root: Path, batch: dict[str, Any]) -> CompletionReport:
    slug = batch_slug(batch)
    verify_dir = repo_root / "data" / "research" / "verification" / slug
    claims_file = verify_dir / "claims_verification.json"
    missing: list[str] = []
    if not claims_file.exists():
        missing.append(str(claims_file))
    return CompletionReport(complete=len(missing) == 0, phase="VERIFICATION", missing=missing)


def check_publication_complete(repo_root: Path, batch: dict[str, Any]) -> CompletionReport:
    slug = batch_slug(batch)
    report = repo_root / "docs" / "research" / f"{slug}-publication-report.md"
    missing: list[str] = []
    if not report.exists():
        missing.append(str(report))
    return CompletionReport(complete=len(missing) == 0, phase="PUBLICATION", missing=missing)


def check_e2e_complete(repo_root: Path, batch: dict[str, Any]) -> CompletionReport:
    slug = batch_slug(batch)
    eval_slug = slug.replace("batch-", "batch-")  # batch-03a-brta-driving-licence
    summary = repo_root / "data" / "evaluation" / eval_slug / "summary.json"
    missing: list[str] = []
    if not summary.exists():
        missing.append(str(summary))
    return CompletionReport(complete=len(missing) == 0, phase="E2E", missing=missing)


def check_regression_complete(repo_root: Path, batch: dict[str, Any]) -> CompletionReport:
    report = repo_root / ".automation" / "reports" / f"regression_{batch['batch_id']}.json"
    missing: list[str] = []
    if not report.exists():
        missing.append(str(report))
    return CompletionReport(complete=len(missing) == 0, phase="REGRESSION", missing=missing)


PHASE_COMPLETION_CHECKS = {
    "RESEARCH": check_research_complete,
    "VERIFICATION": check_verification_complete,
    "PUBLICATION": check_publication_complete,
    "E2E": check_e2e_complete,
    "REGRESSION": check_regression_complete,
}


def phase_artifacts_complete(repo_root: Path, batch: dict[str, Any], phase: str) -> CompletionReport:
    checker = PHASE_COMPLETION_CHECKS.get(phase)
    if checker is None:
        return CompletionReport(complete=True, phase=phase, details={"note": "no artifact check defined"})
    return checker(repo_root, batch)
