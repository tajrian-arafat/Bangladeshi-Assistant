"""Wave-level quality gates for controlled re-research."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


WAVE_SOURCE_THRESHOLD = 0.80
WAVE_VERIFIED_THRESHOLD = 0.80


@dataclass
class WaveQualityResult:
    passed: bool
    wave_id: str
    services_total: int
    false_completion_count: int
    services_with_sources: int
    services_with_verified_claims: int
    source_rate: float
    verified_rate: float
    hallucinations: int
    citation_failures: int
    regression_failures: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)
    service_statuses: dict[str, str] = field(default_factory=dict)


def evaluate_wave_quality(
    wave_id: str,
    service_results: list[dict[str, Any]],
    *,
    regression: dict[str, Any] | None = None,
    e2e_summary: dict[str, Any] | None = None,
) -> WaveQualityResult:
    total = len(service_results)
    if total == 0:
        return WaveQualityResult(
            passed=False,
            wave_id=wave_id,
            services_total=0,
            false_completion_count=0,
            services_with_sources=0,
            services_with_verified_claims=0,
            source_rate=0.0,
            verified_rate=0.0,
            hallucinations=0,
            citation_failures=0,
            blocking_reasons=["empty wave"],
        )

    false_count = sum(1 for r in service_results if r.get("false_completion_risk") or r.get("research_status") == "FALSE_COMPLETION_RISK")
    with_sources = sum(1 for r in service_results if int(r.get("service_specific_sources") or 0) >= 1)
    with_verified = sum(1 for r in service_results if int(r.get("verified_claims") or 0) >= 1)
    source_rate = with_sources / total
    verified_rate = with_verified / total

    hallucinations = int((e2e_summary or {}).get("hallucinations") or 0)
    citation_failures = int((e2e_summary or {}).get("citation_failures") or 0)
    regression_failures = list((regression or {}).get("failures") or [])

    blocking: list[str] = []
    if false_count > 0:
        blocking.append(f"{false_count} services still FALSE_COMPLETION_RISK")
    if hallucinations > 0:
        blocking.append(f"hallucinations={hallucinations}")
    if citation_failures > 0:
        blocking.append(f"citation_failures={citation_failures}")
    if regression_failures:
        blocking.append(f"regression failures: {regression_failures[:5]}")
    if source_rate < WAVE_SOURCE_THRESHOLD:
        blocking.append(f"source rate {source_rate:.0%} < {WAVE_SOURCE_THRESHOLD:.0%}")
    if verified_rate < WAVE_VERIFIED_THRESHOLD:
        blocking.append(f"verified rate {verified_rate:.0%} < {WAVE_VERIFIED_THRESHOLD:.0%}")

    statuses = {r["service_id"]: r.get("final_status") or r.get("research_status") or "UNKNOWN" for r in service_results}

    return WaveQualityResult(
        passed=len(blocking) == 0,
        wave_id=wave_id,
        services_total=total,
        false_completion_count=false_count,
        services_with_sources=with_sources,
        services_with_verified_claims=with_verified,
        source_rate=round(source_rate, 4),
        verified_rate=round(verified_rate, 4),
        hallucinations=hallucinations,
        citation_failures=citation_failures,
        regression_failures=regression_failures,
        blocking_reasons=blocking,
        service_statuses=statuses,
    )
