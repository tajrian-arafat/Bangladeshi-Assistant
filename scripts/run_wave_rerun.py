#!/usr/bin/env python3
"""Run controlled wave re-research of FALSE_COMPLETION_RISK services."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from automation.orchestrator.wave_runner import WaveRunner


def main() -> int:
    parser = argparse.ArgumentParser(description="Wave-based service re-research")
    parser.add_argument("--wave", type=int, default=None, help="Run a specific wave number")
    parser.add_argument("--max-waves", type=int, default=None, help="Maximum waves to run")
    parser.add_argument("--status", action="store_true", help="Show wave state only")
    args = parser.parse_args()

    runner = WaveRunner(ROOT)
    if args.status:
        print(json.dumps(runner.load_state(), indent=2))
        return 0

    if args.wave is not None:
        result = runner.run_wave(wave_num=args.wave)
    else:
        result = runner.run_until_blocked_or_complete(max_waves=args.max_waves)

    print(json.dumps(result, indent=2, default=str))
    if result.get("status") == "WAVE_FAILED" or result.get("global_blocked"):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
