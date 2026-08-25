#!/usr/bin/env python3
"""Validate result.json when edited under .automation/runs/."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from automation.orchestrator.result_validator import ResultValidator  # noqa: E402


def main() -> int:
    payload = json.loads(sys.stdin.read() or "{}")
    file_path = payload.get("file") or payload.get("path") or ""
    if not file_path.endswith("result.json") or ".automation/runs/" not in file_path:
        print(json.dumps({"decision": "allow"}))
        return 0
    ok, errors = ResultValidator().validate_file(Path(file_path))
    if not ok:
        print(json.dumps({"decision": "warn", "errors": errors}))
        return 0
    print(json.dumps({"decision": "allow"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
