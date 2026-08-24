# Research → Runtime Pipeline

**Version:** 1.1  
**Date:** 2026-08-24

---

## Path

```
data/service_catalogue/     Finalized CONFIRMED catalogue (identity of services)
        ↓ sync_catalogue_runtime.py
runtime DB: Agency, Service, service_catalogue_mappings
        ↓ (structural only — no claims/facts)

data/research/raw/          DISCOVERED material
        ↓
data/research/staging/      NORMALIZED / CROSS_CHECKED / CONFLICTING (file SoT for research)
        ↓ sync-claims
runtime DB: Source, SourceVersion, Claim, ClaimEvidence, KnowledgeGap
        ↓ human verification (admin APIs)
Claim.pipeline_status = VERIFIED (+ verified_at)
        ↓ publish (gate)
runtime Fee / ChecklistItem / ProcedureStep (claim_id linked)
        ↓
Answer pipeline (support_level controls wording)
```

Catalogue → runtime Service sync is **orthogonal** to claim verification. Syncing a service does **not** verify any claim and does **not** publish fees, requirements, or procedures.

---

## When a catalogue service becomes a runtime `Service`

A catalogue entry becomes (or maps to) a runtime `Service` **only** via:

```bash
python scripts/sync_catalogue_runtime.py --dry-run   # propose
python scripts/sync_catalogue_runtime.py --apply     # commit
```

### Eligible for sync

| Catalogue status | Action |
|------------------|--------|
| **CONFIRMED** | Must be mapped or explicitly `REVIEW_REQUIRED` |
| UNVERIFIED | **Never** create runtime rows |
| NOT_A_SERVICE | **Never** create (redirects only) |
| DUPLICATE | **Never** create (redirects only) |
| DEPRECATED / MERGED | **Never** create as new runtime rows |

### Resolution order (per CONFIRMED `service_id`)

1. **Explicit file mapping** in `data/research/catalogue_runtime_mappings.json`  
   - `runtime_slug` present → link to that existing runtime service  
   - `mapping_type=alias` → `ALIAS_MATCH`  
   - `mapping_type=merge` → `MERGED_MATCH`  
   - otherwise → `EXACT_MATCH` (existing seed / known slug)  
   - If listed slug is missing in DB → `REVIEW_REQUIRED` (no create)
2. **Already linked** (`Service.catalogue_service_id` == canonical id) → `EXACT_MATCH`
3. **Slug equals canonical id** and runtime row exists → `EXACT_MATCH`
4. **Else** create new runtime `Service` with:
   - `slug` = stable canonical `service_id`
   - `catalogue_service_id` = same id
   - `status=UNDER_REVIEW`, `review_state=DRAFT`
   - mapping status `NEW_RUNTIME_SERVICE`
5. Collision with an MVP seed slug without an explicit mapping → `REVIEW_REQUIRED` (never auto-create over a seed)

### Mapping statuses

| Status | Meaning |
|--------|---------|
| `EXACT_MATCH` | Canonical id ↔ one runtime service (seed or slug match) |
| `ALIAS_MATCH` | Canonical id aliases into an existing runtime service |
| `MERGED_MATCH` | Canonical id merged into an existing runtime service |
| `NEW_RUNTIME_SERVICE` | Created a new runtime row for this confirmed id |
| `UNRESOLVED` | Not finished (must not remain for confirmed after sync) |
| `REVIEW_REQUIRED` | Explicit hold — human must decide before create/link |

Bidirectional fields: `catalogue_service_id` ↔ `runtime_service_id` (+ `runtime_slug`), with `provenance_json` and `mapping_status` on `service_catalogue_mappings`.

### Safety invariants

- Idempotent: re-running `--apply` does not duplicate services or mappings.
- MVP seed slugs are never deleted or field-overwritten by sync.
- No duplicate `Service.slug`; unique `catalogue_service_id` on services.
- One catalogue id → at most one mapping row (no silent multi-runtime fan-out).
- Validation failure rolls back the apply transaction.
- Sync does **not** set any Claim to `VERIFIED` and does **not** write Fee/Checklist/Procedure facts.

---

## What each stage may do

| Stage | May set VERIFIED? | May write Fee/Checklist? | May create Service? |
|-------|-------------------|--------------------------|---------------------|
| Research / staging JSON | **No** | No | No |
| `sync_catalogue_runtime` | **No** | No | Yes (CONFIRMED only, structural) |
| `sync-claims` | **No** | No | No |
| Admin approve (gate pass) | Yes | No (marks claim only) | No |
| `publish --commit` | No (reads VERIFIED) | Yes, if gate passes | No |

---

## Catalogue ↔ runtime mapping artifacts

| Artifact | Role |
|----------|------|
| `data/research/catalogue_runtime_mappings.json` | Explicit seed/alias/merge overrides + exported sync result |
| `service_catalogue_mappings` table | Runtime bidirectional mapping + provenance |
| `services.catalogue_service_id` | Stable back-link from runtime row to catalogue |

MVP seeds are never silently overwritten. `allow_overwrite_seed` must be explicitly true after review (knowledge overwrite — out of scope for structural sync).

---

## Admin review APIs

| Method | Path | Action |
|--------|------|--------|
| GET | `/api/v1/admin/claims` | List |
| GET | `/api/v1/admin/claims/{id}/provenance` | Inspect chain |
| POST | `/api/v1/admin/claims/{id}/approve` | Verify (gate) |
| POST | `/api/v1/admin/claims/{id}/reject` | Reject |
| POST | `/api/v1/admin/claims/{id}/mark-conflict` | Conflict |
| POST | `/api/v1/admin/claims/{id}/request-evidence` | Pending review |
| POST | `/api/v1/admin/claims/{id}/mark-outdated` | Outdated |
| GET | `/api/v1/admin/knowledge-gaps` | Gaps |

All mutating actions write `audit_logs`.

---

## Batch 1 status

Batch 1 remains **STAGING ONLY** with **0 VERIFIED** claims. Catalogue→runtime sync may create empty/DRAFT Service shells for Batch 1 CONFIRMED ids; that is **not** knowledge publication.

---

## Explicit non-goals (this phase)

- No Batch 1 claim verification
- No Batch 2 research
- No mass crawling
- No full semantic RAG / embeddings
- No frontend redesign
- No deletion of staging research or conflicting evidence
- No automatic VERIFIED marking
- No publishing of requirements, fees, or procedures
