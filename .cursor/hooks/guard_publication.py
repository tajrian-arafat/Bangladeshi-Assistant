#!/usr/bin/env python3
"""Block publication when workflow requires human approval."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from automation.orchestrator.gate_engine import GateEngine  # noqa: E402


def main() -> int:
    payload = json.loads(sys.stdin.read() or "{}")
    command = payload.get("command") or payload.get("toolName") or ""
    gate = GateEngine(REPO).check_publication_command(str(command))
    if not gate.passed:
        print(json.dumps({"decision": "deny", "reason": gate.message}))
        return 2
    print(json.dumps({"decision": "allow"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
