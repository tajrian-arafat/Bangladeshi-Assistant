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
        repo_root / "data" / "research" / "verification" / "batch-01",
    ]
    if batch_id.startswith("batch-01"):
        candidates.insert(0, repo_root / "data" / "research" / "verification" / "batch-01")
    for path in candidates:
        if (path / "claims_verification.json").exists():
            return path
    return None


def load_verification_index(repo_root: Path, batch_id: str) -> dict[str, dict[str, Any]]:
    vdir = verification_dir(repo_root, batch_id)
    if not vdir:
        return {}
    data = json.loads((vdir / "claims_verification.json").read_text(encoding="utf-8"))
    return {c["claim_id"]: c for c in data.get("claims", [])}


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
