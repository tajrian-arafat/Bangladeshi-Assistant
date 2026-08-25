"""Result schema validation tests."""

from __future__ import annotations

import json
from pathlib import Path

from automation.orchestrator.result_validator import ResultValidator
from automation.schemas.result import PhaseResult, validate_phase_result


def test_valid_result_passes() -> None:
    result = PhaseResult.empty_success(
        run_id="r1",
        batch_id="BATCH_03A",
        phase="RESEARCH",
        summary="ok",
    )
    ok, errors = validate_phase_result(result.to_dict())
    assert ok, errors


def test_missing_fields_fail(tmp_path: Path) -> None:
    bad = tmp_path / "result.json"
    bad.write_text('{"run_id": "x", "status": "SUCCESS"}')
    ok, errors = ResultValidator().validate_file(bad)
    assert not ok
    assert any("missing" in e for e in errors)


def test_malformed_json_fails(tmp_path: Path) -> None:
    bad = tmp_path / "result.json"
    bad.write_text("{not json")
    ok, errors = ResultValidator().validate_file(bad)
    assert not ok
