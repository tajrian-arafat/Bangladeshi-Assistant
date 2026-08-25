"""Structured logging for the automation orchestrator."""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def setup_logging(repo_root: Path, run_id: str | None = None) -> logging.Logger:
    logger = logging.getLogger("bda.automation")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
    logger.addHandler(handler)

    log_dir = repo_root / ".automation" / "reports"
    log_dir.mkdir(parents=True, exist_ok=True)
    suffix = run_id or "orchestrator"
    file_handler = logging.FileHandler(log_dir / f"{suffix}.log", encoding="utf-8")
    file_handler.setFormatter(handler.formatter)
    logger.addHandler(file_handler)
    return logger


def write_report(repo_root: Path, name: str, payload: dict[str, Any]) -> Path:
    reports = repo_root / ".automation" / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    path = reports / name
    payload = {**payload, "generated_at": datetime.now(timezone.utc).isoformat()}
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path
