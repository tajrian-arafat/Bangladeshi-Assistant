# Research → Runtime Pipeline

**Version:** 1.0  
**Date:** 2026-08-24

---

## Path

```
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

---

## What each stage may do

| Stage | May set VERIFIED? | May write Fee/Checklist? |
|-------|-------------------|--------------------------|
| Research / staging JSON | **No** | No |
| `sync-claims` | **No** | No |
| Admin approve (gate pass) | Yes | No (marks claim only) |
| `publish --commit` | No (reads VERIFIED) | Yes, if gate passes |

---

## Catalogue ↔ runtime mapping

File: `data/research/catalogue_runtime_mappings.json`  
Table: `service_catalogue_mappings`

Handles: existing MVP seed, new canonical, alias, merge, duplicate, retired.

**MVP seeds are never silently overwritten.** `allow_overwrite_seed` must be explicitly true after review.

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

Batch 1 remains **STAGING ONLY** with **0 VERIFIED** claims. Infrastructure is ready; verification of Batch 1 claims is a later phase.

---

## Explicit non-goals (this phase)

- No Batch 2 research
- No mass crawling
- No full semantic RAG / embeddings
- No frontend redesign
- No deletion of staging research or conflicting evidence
- No automatic VERIFIED marking
