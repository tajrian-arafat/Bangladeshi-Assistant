"""Validate phase result.json before workflow transitions."""

from __future__ import annotations

import json
from pathlib import Path

from automation.schemas.result import validate_phase_result


class ResultValidator:
    def validate_file(self, path: Path) -> tuple[bool, list[str]]:
        if not path.exists():
            return False, [f"result file not found: {path}"]
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return False, [f"invalid JSON: {exc}"]
        return validate_phase_result(data)

    def load_validated(self, path: Path) -> dict:
        ok, errors = self.validate_file(path)
        if not ok:
            raise ValueError("; ".join(errors))
        return json.loads(path.read_text(encoding="utf-8"))
