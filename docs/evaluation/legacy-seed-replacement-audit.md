# Legacy Seed Replacement — Generic Architecture Audit

**Generated:** 2026-08-25  
**Scope:** MVP seed protection hardening (all batches); Batch 3A dry-run impact  
**Deployment:** Locked — no replacements applied

## Executive summary

The verified-claim → legacy-seed replacement system is now **generic and auditable**. Readiness distinguishes **knowledge gaps** from **legacy seed blocks**. Replacement candidates are detected automatically but require **explicit human approval** before apply.

| Metric | All MVP seeds | Batch 3A (renewal) |
|--------|--------------:|-------------------:|
| Legacy seed rows | 44 | 7 |
| With verified replacement coverage | 18 | 3 |
| Gate-eligible replacement candidates | 11 | 1 |
| Approved | 0 | 0 |
| Pending | 0 | 0 |
| Rejected | 0 | 0 |

## Architecture changes

### 1. Readiness calculation (`backend/app/application/knowledge/readiness.py`)

Post-publication readiness now returns extended detail:

| Field | Meaning |
|-------|---------|
| `readiness` | GREEN / YELLOW / RED (unchanged surface) |
| `knowledge_ready` | Verified OFFICIAL coverage is sufficient |
| `legacy_replacement_pending` | Legacy MVP seed rows block structured publish |
| `runtime_replacement_pending` | Knowledge ready but runtime still on seed data |
| `blocking_reason` | `KNOWLEDGE_GAP`, `LEGACY_DATA_REPLACEMENT_PENDING`, `MIXED`, or null |

**Key rule:** A service may be `KNOWLEDGE_READY` + `RUNTIME_REPLACEMENT_PENDING` without being classified as a knowledge-quality failure.

### 2. Generic replacement engine (`SeedReplacementService`)

Supports structured types:

- `fee` → `Fee`
- `checklist` → `ChecklistItem` (document / conditional_document claims)
- `procedure_step` → `ProcedureStep`
- `service_link` → inventory only (legacy unverified links; URLs publish without seed guard)

Requirements before apply (unchanged):

- VERIFIED + OFFICIAL
- Full publication gate + type-specific gate
- Evidence + provenance + content hash
- Explicit `APPROVED` status (never auto-apply)

Workflow commands:

```bash
# Audit all legacy rows
python3 scripts/audit_legacy_seed_inventory.py

# Dry-run candidates for a batch
python3 scripts/review_seed_replacements.py --batch batch-03a-brta-driving-licence --dry-run

# Record PENDING (no apply)
python3 scripts/review_seed_replacements.py --batch batch-03a-brta-driving-licence --record

# Approve one replacement (preferred)
python3 scripts/review_seed_replacements.py --approve <replacement-uuid>

# Apply approved only
python3 scripts/review_seed_replacements.py --batch batch-03a-brta-driving-licence --apply

# Reject / rollback
python3 scripts/review_seed_replacements.py --reject <replacement-uuid>
python3 scripts/review_seed_replacements.py --rollback <replacement-uuid>
```

`--approve-all` remains available but is **not** the default workflow.

### 3. Automatic candidate detection

After publication, the orchestrator runs:

```bash
python3 scripts/detect_legacy_seed_candidates.py --batch <slug> --record
```

If PENDING replacements exist → `requires_escalation=True` → `HUMAN_APPROVAL_REQUIRED`.  
No AI prompt or script auto-approves replacements.

### 4. Audit artifacts

| Path | Contents |
|------|----------|
| `data/audit/legacy-seed-inventory.json` | Full legacy row inventory + candidates |
| `data/audit/seed-candidates-<batch>.json` | Per-batch detection report |

## Batch 3A — `driving-licence-renewal` dry-run

### Legacy seed rows blocking runtime (7 rows)

| Field type | Count | Examples |
|------------|------:|----------|
| checklist_item | 4 | Current/expired licence, NID, photos, medical (conditional) |
| procedure_step | 3 | Check licence status, medical test, pay fees |

All have `claim_id: null`, `source: mvp_seed`, `seed_status: LEGACY_SEED`.

### Post-publication readiness (dry-run)

```json
{
  "readiness": "YELLOW",
  "knowledge_ready": true,
  "legacy_replacement_pending": true,
  "runtime_replacement_pending": true,
  "blocking_reason": "LEGACY_DATA_REPLACEMENT_PENDING",
  "verified_official_count": 5,
  "published_verified_count": 4,
  "seed_blocked_count": 1,
  "knowledge_gap_count": 0
}
```

**Interpretation:** Renewal is YELLOW because **1 verified procedure_step claim** (`c-circle-office-collection`) is seed-blocked — not because knowledge is missing. Portal URL and metadata claims publish successfully; E2E passes at 55/55.

### Replacement candidate (gate-eligible, not applied)

| Claim | Kind | Status |
|-------|------|--------|
| `brta-driving-license-renewal::c-circle-office-collection` | procedure_step | NEW (would be PENDING after `--record`) |

Fee/checklist renewal claims (`c-renewal-fee-calculator`, `c-medical-for-renewal-professional`) do not yet pass type-specific publication gates — they are **knowledge gaps**, not seed-block candidates.

### Would replacement improve runtime?

- **Procedure step approval + apply:** Would publish verified circle-office collection step; may improve structured procedure answers. **Low regression risk** — E2E already passes via URL/metadata paths.
- **Fee/checklist:** Require gate fixes before they become replacement candidates; applying without gate passage would violate publication rules.

**No replacements were applied** in this step.

## Regression results (post-implementation)

| Suite | Result |
|-------|--------|
| Batch 1 E2E | 55/55 (100%) |
| Passport E2E | 57/57 (100%) |
| Batch 2B E2E | 67/67 (100%) |
| Batch 3A E2E | 55/55 (100%) |
| Service routing | 34/34 (100%) |
| Cross-domain | 90/90 (100%) |
| Backend pytest | 62/62 |
| Orchestrator tests | 30/30 |

## MVP seed services affected

| Runtime slug | Legacy rows | Candidates |
|--------------|------------:|-----------:|
| birth-registration | 8 | 2 |
| driving-licence-renewal | 7 | 1 |
| nid-correction | 9 | 3 |
| passport-renewal | 12 | 4 |
| tin-registration | 8 | 1 |

## Stop conditions respected

- Batch 3B **not** started
- Deployment **locked**
- No merge
- No automatic seed replacement apply
- No publication/citation gate weakening

## Next human action (optional)

To move `driving-licence-renewal` from YELLOW → GREEN for structured fields:

1. `python3 scripts/review_seed_replacements.py --batch batch-03a-brta-driving-licence --record`
2. Review candidate `c-circle-office-collection`
3. `python3 scripts/review_seed_replacements.py --approve <replacement-uuid>`
4. `python3 scripts/review_seed_replacements.py --batch batch-03a-brta-driving-licence --apply`
5. Re-run publication dry-run and E2E

Fee/checklist claims need verification gate passage before they enter the replacement queue.
