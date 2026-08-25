# Batch 1 Pipeline Status — Research Guardrail Report

**Date:** 2026-08-24  
**Batch:** `batch-01-identity-civil-registration`  
**Runtime DB published:** **No**  
**Frontend redesigned:** **No**  
**RAG / embeddings implemented:** **No**

---

## Inspection of actual runtime (what exists today)

Inspected:

- `backend/app/domain/models/knowledge.py`
- `backend/app/domain/enums.py`
- `backend/alembic/versions/001_initial_schema.py`
- `scripts/seed_database.py` + `data/seeds/mvp_services.json`
- Design docs: `docs/KNOWLEDGE_ARCHITECTURE.md`, `docs/VERIFICATION_FRAMEWORK.md`, `docs/CURRENT_SYSTEM_AUDIT.md`

### Reusable runtime models (exist, mostly empty)

`Agency`, `Service`, `Procedure`, `ProcedureStep`, `ChecklistItem`, `ChecklistCondition`, `Fee`, `Form`, `ServiceLink`, `ServiceOffice`, `Source`, `SourceVersion`, `KnowledgeDocument`, `KnowledgeChunk`.

Production-ish answers still come from **5 MVP seed templates**, all `UNDER_REVIEW` / `DRAFT`. Batch 1 research was **not** loaded into them.

### Missing runtime representations (cannot pretend they exist)

| Concept | Runtime status |
|---------|----------------|
| `Claim` table | **Missing** |
| `ClaimEvidence` table | **Missing** |
| `KnowledgeGap` table | **Missing** |
| Claim pipeline states (`DISCOVERED`…`VERIFIED`…) | **Missing** (only `ServiceStatus` / `ReviewState`) |
| Research→DB publish gate / loader | **Missing** |
| Durable `SourceVersion.content_hash` + body archive | Table exists; **empty / unused** |

Therefore Batch 1 is stored as **research/staging JSON**, not forced into `Fee.amount` / `ChecklistItem` / `Service.source_provenance`.

---

## Provenance chain preserved in staging

```
Source
  → Source Version
    → Evidence
      → Claim
        → Service binding
          → Requirement / Procedure / Fee
            → pipeline_status
            → confidence
            → provenance
```

Files: `data/research/staging/batch-01/`  
Schema: `data/research/staging/schema.json`  
Normalizer: `scripts/normalize_batch01_to_staging.py`

### Pipeline states (enforced)

`DISCOVERED` | `EXTRACTED` | `NORMALIZED` | `CROSS_CHECKED` | `PENDING_REVIEW` | `VERIFIED` | `CONFLICTING` | `OUTDATED` | `REJECTED`

**Batch 1 emitted `VERIFIED` claims: 0**  
**Discovery-phase false `VERIFIED` demotions: 64**

---

## Explicit end-of-phase report

### 1. What was stored as raw / discovered research

- Original discovery dump: `data/knowledge/batch-01/` (legacy; see README there)
- Immutable raw copy: `data/research/raw/batch-01/`
- Contents: 34 service packs, 21 sources, 69 claims, 6 conflicts, narrative report notes
- Nature: manual research notes + portal fetches; **not** durable crawled SourceVersion bodies

### 2. What was normalized

- Staging outputs under `data/research/staging/batch-01/`:
  - `sources.json` (21)
  - `source_versions.json` (21; `content_hash` null — gap)
  - `evidence.json` (80 evidence links)
  - `claims.json` (69; remapped IDs `service_id::claim_id`)
  - `services.json` (34; `publication_status: STAGING_ONLY`)
  - `requirements.json` (56)
  - `fees.json` (22)
  - `procedure_steps.json` (16)
  - `conflicts.json` (6; `blocks_official_publication: true`)
  - `demotion_log.json`, `runtime_gap_register.json`, `pipeline_summary.json`

Normalization includes structured MUST/CONDITIONAL requirements, fee conditions, and OFFICIAL vs PRACTICAL `information_class`.

### 3. What was cross-checked

- Claims with Tier 1–2 sources **and** captured excerpts → `CROSS_CHECKED` (8 claims)
- Fee conflicts explicitly recorded (birth late fee ৳50 vs ৳500; NID news fee tiers vs calculator; correction fee ৳50 vs ৳100) → `CONFLICTING` / unresolved
- Practical rejection anecdotes retained as PRACTICAL and **not** promoted to MUST

Cross-check here means **research-time comparison**, not the formal verification phase.

### 4. What remains unverified

- **All 69 staging claims** (none `VERIFIED`)
- All fees / requirements / steps (`publication_status: STAGING_ONLY`)
- SourceVersion integrity (`content_hash` / archived body missing)
- Full BDRIS Guidelines 2021 document matrix
- EC fee gazette / controlled fee-calculator capture
- Marriage/divorce citizen fee–document matrices
- Per-LGI local certificate schedules
- Expatriate NID mission workflows
- Processing SLAs where FAQ is silent
- Anything formerly labeled `VERIFIED` in the discovery dump

### 5. Schema / runtime gaps that prevented proper storage

1. No `Claim` / `ClaimEvidence` tables → cannot persist atomic facts with pipeline state in DB  
2. No claim status enum in `backend/app/domain/enums.py`  
3. `Source` / `SourceVersion` unused by seed; no research ingest worker  
4. No publish gate linking staging → `ChecklistItem` / `Fee` / `ProcedureStep`  
5. `evidence_ids` on `ProcedureStep` and `evidence_chunk_id` on Fee/Checklist are orphan hooks without ClaimEvidence  
6. Catalogue (464 services) is file inventory only — not the runtime `services` table  
7. Premature discovery dump lived under `data/knowledge/` naming that implied SoT — corrected via staging + demotion

### 6. Changes required before verification / publication phase

1. **Add DB models + migration:** `Claim`, `ClaimEvidence` (and preferably `KnowledgeGap`) aligned to `docs/VERIFICATION_FRAMEWORK.md`, with full pipeline status enum including the states listed above.  
2. **Implement SourceVersion capture:** store URL fetch body or object storage pointer + `content_hash` + `fetched_at`.  
3. **Build staged loader with publish gate:** staging JSON → draft Claim rows only; human/review queue; publish VERIFIED OFFICIAL claims into checklist/fees/steps.  
4. **Map catalogue `service_id` ↔ runtime `Service.slug`** without overwriting MVP seeds until reviewed.  
5. **Conflict workflow:** `CONFLICTING` claims must block official answer fields.  
6. **Separate KQS:** research completeness score ≠ runtime `Service.confidence`.  
7. **Do not** enable RAG/embeddings as a substitute for verified claims.  
8. **Do not** redesign frontend during verification setup beyond citing verified fields already supported.

---

## Claim pipeline status counts (Batch 1 staging)

From `data/research/staging/batch-01/pipeline_summary.json`:

| Status | Count |
|--------|------:|
| NORMALIZED | 39 |
| CONFLICTING | 13 |
| EXTRACTED | 9 |
| CROSS_CHECKED | 8 |
| VERIFIED | **0** |

---

## Safety confirmation

- [x] Runtime schema inspected before storage decisions  
- [x] Existing models reused where appropriate (documented mapping only)  
- [x] Research concepts without adequate runtime representation stored in staging  
- [x] Provenance chain preserved  
- [x] Discovery `VERIFIED` demoted  
- [x] Practical/social not converted to official MUST  
- [x] MVP / seed structured fields not overwritten  
- [x] Frontend not redesigned  
- [x] Full RAG / embeddings not implemented
