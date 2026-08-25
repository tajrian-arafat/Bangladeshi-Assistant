"""Wave rerun quality gate tests."""

from __future__ import annotations

from automation.orchestrator.wave_quality import evaluate_wave_quality


def test_wave_quality_passes_good_wave() -> None:
    results = [
        {
            "service_id": f"s{i}",
            "false_completion_risk": False,
            "service_specific_sources": 1,
            "verified_claims": 2,
            "final_status": "COMPLETE",
        }
        for i in range(10)
    ]
    q = evaluate_wave_quality("wave-001", results, regression={"failures": []}, e2e_summary={"hallucinations": 0, "citation_failures": 0})
    assert q.passed
    assert q.source_rate == 1.0
    assert q.verified_rate == 1.0


def test_wave_quality_fails_false_completion() -> None:
    results = [{"service_id": "bad", "false_completion_risk": True, "service_specific_sources": 0, "verified_claims": 0}]
    q = evaluate_wave_quality("wave-002", results, regression={"failures": []})
    assert not q.passed
    assert any("FALSE_COMPLETION" in r for r in q.blocking_reasons)


def test_wave_quality_fails_low_source_rate() -> None:
    results = [
        {"service_id": f"s{i}", "false_completion_risk": False, "service_specific_sources": 1 if i < 5 else 0, "verified_claims": 1 if i < 5 else 0}
        for i in range(10)
    ]
    q = evaluate_wave_quality("wave-003", results, regression={"failures": []})
    assert not q.passed
