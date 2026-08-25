#!/usr/bin/env python3
"""Validate Batch 2B publication dry-run gates (A–G checks)."""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BACKEND = REPO / "backend"
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)

from app.core.database import get_session_factory  # noqa: E402
from app.application.knowledge.publisher import KnowledgePublisher  # noqa: E402


async def main() -> int:
    session_factory = get_session_factory()
    async with session_factory() as session:
        publisher = KnowledgePublisher(session, repo_root=REPO, dry_run=True)
        sync_pub = KnowledgePublisher(session, repo_root=REPO, dry_run=False)
        await sync_pub.sync_claims_from_staging("batch-02b-police-immigration")
        report = await publisher.publish_verified("batch-02b-police-immigration")
        await session.rollback()

    actions = report.actions
    checks: dict[str, bool] = {}
    reasons: dict[str, str] = {}

    fee_actions = [a for a in actions if "fee" in a.get("action", "")]
    published_fee_keys = {
        a.get("research_claim_key")
        for a in fee_actions
        if a.get("action") in {"would_publish_fee", "publish_fee"}
    }
    blocked_offline = any(
        a.get("research_claim_key") == "police-clearance-certificate::c-offline-fee-500-chalan"
        and a.get("action") == "skip_blocklisted_claim"
        for a in actions
    )
    online_fee_ok = "police-clearance-certificate::c-online-fee-1500" in published_fee_keys

    # A: no universal offline 500 published
    checks["A_no_universal_offline_500"] = (
        "police-clearance-certificate::c-offline-fee-500-chalan" not in published_fee_keys
        and blocked_offline
    )
    # B: online channel fee preserved
    checks["B_online_channel_fee_preserved"] = online_fee_ok
    # C: Tier-5 all-GD-types not published
    checks["C_gd_all_types_not_published"] = all(
        a.get("action") != "mark_claim_published_metadata_only"
        for a in actions
        if a.get("research_claim_key", "").endswith("c-gd-all-types-expansion")
    ) and any(
        a.get("research_claim_key", "").endswith("c-gd-all-types-expansion")
        and a.get("action") == "skip_blocklisted_claim"
        for a in actions
    )
    # D: MRV fees not published
    checks["D_mrv_fees_not_published"] = not any(
        "c-visa-mrv-fees" in (a.get("research_claim_key") or "") and "publish" in a.get("action", "")
        for a in actions
    )
    # E: passport PV vs PCC SLAs both eligible as metadata (not merged fee rows)
    pv_sla = any(
        a.get("research_claim_key", "").startswith("police-passport-verification::c-pv-charter-sla")
        and "publish" in a.get("action", "")
        for a in actions
    )
    pcc_sla = any(
        a.get("research_claim_key") == "police-clearance-certificate::c-charter-online-fee-sla"
        and "publish" in a.get("action", "")
        for a in actions
    )
    checks["E_sla_services_separate"] = pv_sla and pcc_sla
    # F: practical not in checklist/fees
    practical_ok = all(
        a.get("research_claim_key") != "police-clearance-certificate::c-practical-fee-confusion"
        or a.get("action") == "skip_blocklisted_claim"
        for a in actions
    )
    checks["F_practical_not_must_need"] = practical_ok
    # G: every published fee action has claim_id
    checks["G_published_fees_have_provenance"] = all(
        a.get("claim_id") for a in fee_actions if a.get("action") in {"would_publish_fee", "publish_fee"}
    )

    out = {
        "batch_id": "batch-02b-police-immigration",
        "eligible_count": report.eligible_count,
        "published_fees_dry_run": report.published_fees,
        "skipped": report.skipped,
        "rejected_by_gate": report.rejected_by_gate_count,
        "checks": checks,
        "all_pass": all(checks.values()),
        "published_fee_keys": sorted(published_fee_keys),
    }
    print(json.dumps(out, indent=2))
    return 0 if out["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
