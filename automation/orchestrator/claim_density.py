"""Complexity-based claim density scoring — not arbitrary claim counts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

COMPLEXITY_TIERS = ("SIMPLE", "STANDARD", "COMPLEX", "HIGHLY_COMPLEX")

PROFILE_COMPLEXITY: dict[str, str] = {
    "IDENTITY_CIVIL": "STANDARD",
    "PASSPORT": "COMPLEX",
    "POLICE": "COMPLEX",
    "BRTA": "COMPLEX",
    "TAX": "COMPLEX",
    "VAT": "STANDARD",
    "CUSTOMS": "COMPLEX",
    "LAND": "COMPLEX",
    "EDUCATION": "STANDARD",
    "HEALTH": "STANDARD",
    "SOCIAL_PROTECTION": "STANDARD",
    "DISABILITY": "STANDARD",
    "JUDICIARY": "COMPLEX",
    "UTILITIES": "STANDARD",
    "BUSINESS": "COMPLEX",
    "PROFESSIONAL": "STANDARD",
    "OTHER": "SIMPLE",
}

TIER_EXPECTATIONS: dict[str, dict[str, int]] = {
    "SIMPLE": {"critical_min": 2, "optional_min": 0, "conditional_min": 0, "variant_min": 0},
    "STANDARD": {"critical_min": 3, "optional_min": 1, "conditional_min": 1, "variant_min": 0},
    "COMPLEX": {"critical_min": 4, "optional_min": 2, "conditional_min": 2, "variant_min": 1},
    "HIGHLY_COMPLEX": {"critical_min": 6, "optional_min": 3, "conditional_min": 3, "variant_min": 2},
}


@dataclass
class ClaimDensityScore:
    service_id: str
    profile_key: str
    complexity_tier: str
    critical_covered: int
    critical_expected: int
    optional_covered: int
    conditional_covered: int
    variant_covered: int
    evidence_backed: int
    density_score: float
    meets_expectation: bool
    breakdown: dict[str, Any] = field(default_factory=dict)


def _is_evidence_backed(claim: dict[str, Any]) -> bool:
    if claim.get("claim_class") == "CATALOGUE_METADATA":
        return False
    if not claim.get("source_ids") or claim.get("source_ids") == ["src-catalogue"]:
        return False
    return claim.get("verification_status") in {"VERIFIED", "PARTIALLY_VERIFIED", "PENDING_INDEPENDENT_VERIFICATION"}


def _requirement_class(claim: dict[str, Any]) -> str:
    cond = claim.get("condition") or {}
    rc = cond.get("requirement_class")
    if rc in {"MUST_NEED", "CONDITIONAL", "RECOMMENDED", "NOT_APPLICABLE"}:
        return rc
    if cond.get("if"):
        return "CONDITIONAL"
    if claim.get("claim_type") in {"document", "document_requirement"}:
        return "MUST_NEED"
    return "OPTIONAL"


def score_claim_density(
    service_id: str,
    profile_key: str,
    claims: list[dict[str, Any]],
    dimension_coverage: dict[str, bool] | None = None,
) -> ClaimDensityScore:
    complexity = PROFILE_COMPLEXITY.get(profile_key, "STANDARD")
    expectations = TIER_EXPECTATIONS[complexity]
    dimension_coverage = dimension_coverage or {}

    meaningful = [c for c in claims if c.get("claim_class") != "CATALOGUE_METADATA"]
    critical_dims = ["identity", "authority", "official_url", "procedure", "documents", "eligibility"]
    critical_covered = sum(1 for d in critical_dims if dimension_coverage.get(d))
    if not dimension_coverage:
        critical_types = {"procedure", "procedure_step", "document", "document_requirement", "eligibility", "application_url"}
        critical_covered = len({c.get("claim_type") for c in meaningful if c.get("claim_type") in critical_types})

    conditional_covered = sum(1 for c in meaningful if _requirement_class(c) == "CONDITIONAL")
    variant_covered = sum(
        1 for c in meaningful if (c.get("condition") or {}).get("if") and "variant" in str((c.get("condition") or {}).get("if")).lower()
    )
    optional_covered = max(0, len(meaningful) - critical_covered - conditional_covered)
    evidence_backed = sum(1 for c in meaningful if _is_evidence_backed(c))

    critical_expected = expectations["critical_min"]
    score_parts = [
        min(1.0, critical_covered / max(critical_expected, 1)),
        min(1.0, conditional_covered / max(expectations["conditional_min"], 1)) if expectations["conditional_min"] else 1.0,
        min(1.0, evidence_backed / max(len(meaningful), 1)),
    ]
    density_score = round(sum(score_parts) / len(score_parts), 4)
    meets = (
        critical_covered >= critical_expected
        and conditional_covered >= expectations["conditional_min"]
        and evidence_backed >= max(2, critical_expected - 1)
    )

    return ClaimDensityScore(
        service_id=service_id,
        profile_key=profile_key,
        complexity_tier=complexity,
        critical_covered=critical_covered,
        critical_expected=critical_expected,
        optional_covered=optional_covered,
        conditional_covered=conditional_covered,
        variant_covered=variant_covered,
        evidence_backed=evidence_backed,
        density_score=density_score,
        meets_expectation=meets,
        breakdown={
            "expectations": expectations,
            "meaningful_claims": len(meaningful),
        },
    )
