"""Helpers to apply Batch 1 independent verification into claim sync."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from app.domain.enums import ClaimPipelineStatus, ClaimType


VERIFICATION_STATUS_TO_PIPELINE: dict[str, str] = {
    "VERIFIED": ClaimPipelineStatus.VERIFIED.value,
    "PARTIALLY_VERIFIED": ClaimPipelineStatus.PARTIALLY_VERIFIED.value,
    "UNVERIFIED": ClaimPipelineStatus.UNVERIFIED.value,
    "REJECTED": ClaimPipelineStatus.REJECTED.value,
    "CONFLICTING": ClaimPipelineStatus.CONFLICTING.value,
    "OUTDATED": ClaimPipelineStatus.OUTDATED.value,
}


def verification_dir(repo_root: Path, batch_id: str) -> Path | None:
    candidates = [
        repo_root / "data" / "research" / "verification" / batch_id,
    ]
    if batch_id.startswith("batch-01"):
        candidates.append(repo_root / "data" / "research" / "verification" / "batch-01")
    if batch_id.startswith("batch-02a"):
        candidates.append(repo_root / "data" / "research" / "verification" / "batch-02a-passport")
    if batch_id.startswith("batch-02b"):
        candidates.append(
            repo_root / "data" / "research" / "verification" / "batch-02b-police-immigration"
        )
    if batch_id.startswith("batch-03a"):
        candidates.append(
            repo_root / "data" / "research" / "verification" / "batch-03a-brta-driving-licence"
        )
    for path in candidates:
        if (path / "claims_verification.json").exists():
            return path
    return None


def _gap_closure_sources(repo_root: Path) -> dict[str, dict[str, Any]]:
    path = (
        repo_root
        / "data"
        / "research"
        / "verification"
        / "batch-02a-passport-gap-closure"
        / "new_sources.json"
    )
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {s["source_id"]: s for s in data.get("sources", [])}


def _gap_closure_to_verification(
    gc: dict[str, Any], sources: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    """Convert gap-closure claim record to independent verification shape."""
    claim_type = gc.get("claim_type") or "other"
    type_map = {
        "conditional_document": "conditional_document",
        "application_url": "application_url",
        "procedure_step": "procedure_step",
        "document": "document",
        "fee": "fee",
        "payment_method": "other",
        "eligibility_rule": "other",
        "procedure": "procedure_step",
        "portal_function": "application_url",
        "official_metadata": "other",
        "procedure_gap": "other",
        "mission_evidence": "other",
    }
    evidence = []
    for sid in gc.get("source_ids") or []:
        src = sources.get(sid, {})
        evidence.append(
            {
                "source_id": sid,
                "source_url": src.get("source_url"),
                "authority_tier": src.get("authority_tier", 1),
                "retrieved_via": src.get("retrieval_method") or "puppeteer_headless_chrome",
                "snapshot": src.get("snapshot"),
                "retrieved_live_at": src.get("retrieved_at"),
                "evidence_excerpt": gc.get("evidence_excerpt"),
            }
        )
    return {
        "claim_id": gc["claim_id"],
        "service_id": gc.get("service_id"),
        "claim_text": gc.get("claim_text"),
        "verification_status": gc.get("verification_status"),
        "information_class": "OFFICIAL",
        "claim_type": type_map.get(claim_type, claim_type),
        "reasoning": gc.get("evidence_excerpt") or gc.get("note") or gc.get("evidence_limitation"),
        "evidence": evidence,
        "evidence_excerpt": gc.get("evidence_excerpt"),
        "condition": gc.get("condition"),
        "applicability": gc.get("applicability"),
        "fee_metadata": gc.get("fee_metadata"),
        "verified_at": gc.get("verified_at") or "2026-08-24T21:22:37.453479+00:00",
        "verifier": "batch-02a-gap-closure",
        "publication_status": "STAGING_ONLY",
    }


def load_verification_index(repo_root: Path, batch_id: str) -> dict[str, dict[str, Any]]:
    vdir = verification_dir(repo_root, batch_id)
    if not vdir:
        return {}
    data = json.loads((vdir / "claims_verification.json").read_text(encoding="utf-8"))
    index = {c["claim_id"]: c for c in data.get("claims", [])}

    if batch_id.startswith("batch-02a"):
        gap_path = (
            repo_root
            / "data"
            / "research"
            / "verification"
            / "batch-02a-passport-gap-closure"
            / "new_claims.json"
        )
        if gap_path.exists():
            gap_data = json.loads(gap_path.read_text(encoding="utf-8"))
            sources = _gap_closure_sources(repo_root)
            for gc in gap_data.get("claims", []):
                cid = gc["claim_id"]
                index[cid] = _gap_closure_to_verification(gc, sources)
    return index


def hash_snapshot(repo_root: Path, snapshot_ref: str | None) -> str | None:
    if not snapshot_ref:
        return None
    path = repo_root / snapshot_ref
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_fee_structured_by_claim(staging: Path) -> dict[str, list[dict[str, Any]]]:
    """Map research claim_id → fee structured payloads (may be multiple tiers per claim)."""
    fees_path = staging / "fees.json"
    if not fees_path.exists():
        return {}
    rows = json.loads(fees_path.read_text(encoding="utf-8")).get("fees", [])
    out: dict[str, list[dict[str, Any]]] = {}
    for fee in rows:
        for cid in fee.get("claim_ids", []):
            if fee.get("amount") is None:
                payload = {
                    "fee_mode": "calculator",
                    "calculator_url": "https://services.nidw.gov.bd/nid-pub/fees",
                    "currency": fee.get("currency", "BDT"),
                    "condition": fee.get("condition"),
                    "description": fee.get("description"),
                    "fee_id": fee.get("fee_id"),
                }
            else:
                payload = {
                    "amount": str(fee["amount"]),
                    "currency": fee.get("currency", "BDT"),
                    "condition": fee.get("condition"),
                    "description": fee.get("description"),
                    "fee_id": fee.get("fee_id"),
                }
            out.setdefault(cid, []).append(payload)
    return out


def pipeline_status_for_claim(
    staging_claim: dict[str, Any],
    verification: dict[str, Any] | None,
) -> str:
    if verification:
        vstatus = verification.get("verification_status")
        if vstatus in VERIFICATION_STATUS_TO_PIPELINE:
            return VERIFICATION_STATUS_TO_PIPELINE[vstatus]
    # Preserve non-verified staging status; never promote from staging alone
    return staging_claim.get("pipeline_status") or ClaimPipelineStatus.DISCOVERED.value


def claim_type_from_verification(
    staging_claim: dict[str, Any],
    verification: dict[str, Any] | None,
) -> str:
    if verification and verification.get("claim_type"):
        return str(verification["claim_type"])
    explicit = staging_claim.get("claim_type")
    if explicit and explicit != "other":
        return explicit
    field = (staging_claim.get("field") or "").lower()
    text = (staging_claim.get("claim_text") or staging_claim.get("claim") or "").lower()
    if "fee" in field or "fee" in text or "bdt" in text:
        return ClaimType.FEE.value
    if "document" in field or "certificate" in text:
        return ClaimType.DOCUMENT.value
    if "url" in field or "http" in text:
        return ClaimType.APPLICATION_URL.value
    if "step" in field or "procedure" in text:
        return ClaimType.PROCEDURE_STEP.value
    if staging_claim.get("information_class") == "PRACTICAL":
        return ClaimType.PRACTICAL_TIP.value
    return ClaimType.OTHER.value


def evidence_excerpt_from_verification(
    ev: dict[str, Any], verification: dict[str, Any]
) -> str:
    for key in ("evidence_location", "notes", "cites"):
        val = ev.get(key)
        if val:
            return str(val)[:2000]
    reasoning = verification.get("reasoning")
    if reasoning:
        return str(reasoning)[:2000]
    return f"Verified against {ev.get('source_url', 'official source')}"


def parse_verified_at(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    return None


def domain_from_url(url: str) -> str:
    return urlparse(url).netloc or "unknown"
