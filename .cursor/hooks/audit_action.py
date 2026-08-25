#!/usr/bin/env python3
"""Audit hook events to automation reports."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
AUDIT = REPO / ".automation" / "reports" / "hook_audit.jsonl"


def main() -> int:
    payload = json.loads(sys.stdin.read() or "{}")
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    entry = {"ts": datetime.now(timezone.utc).isoformat(), "event": payload}
    with AUDIT.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")
    print(json.dumps({"decision": "allow"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
