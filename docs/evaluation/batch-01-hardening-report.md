# Batch 01 Hardening Report (Step 10)

**Date:** 2026-08-24  
**Environment:** LOCAL / DEV ONLY — not deployed  
**Branch:** `cursor/service-catalogue-discovery-3400`

---

## Summary

Step 10 addressed architectural limitations identified after the 55/55 end-to-end evaluation pass. The system now supports **controlled MVP seed replacement**, **conversation context for follow-ups**, **knowledge chunk preparation (no RAG)**, **classified knowledge gaps**, and a **reusable batch research template**.

---

## Changes Made

### 1. Safe MVP Seed Replacement

| Component | Path |
|-----------|------|
| Model | `backend/app/domain/models/seed_replacement.py` |
| Migration | `backend/alembic/versions/004_seed_replacement_hardening.py` |
| Service | `backend/app/application/knowledge/seed_replacement.py` |
| Script | `scripts/review_seed_replacements.py` |
| Publisher hook | `publish_verified(..., approved_seed_replacement_claim_ids=...)` |

**Mechanism:**
- Legacy seed structured data (Fee/Checklist/Step with `claim_id=null`) remains protected by default.
- Gate-eligible VERIFIED OFFICIAL claims on MVP seed slugs are discovered as replacement **candidates**.
- Replacement requires explicit `SeedReplacement` row with status `APPROVED`.
- Apply runs publication with approved claim IDs; audit logs record apply/rollback.
- No automatic overwrite.

**Dry-run candidates (local runtime):**
- `civil-birth-registration::c-br-fee-free45` (fee) → `birth-registration`
- `civil-birth-registration::c-br-fee-late` (fee) → `birth-registration`
- NID correction fee/checklist/step claims → `nid-correction` (calculator fees; no static amounts)

**Status:** Candidates identified; **not applied** in this hardening pass (requires explicit `--record --approve-all --apply`).

### 2. Conversation Context

| Component | Path |
|-----------|------|
| Service | `backend/app/application/services/conversation_context.py` |
| Integration | `chat_service.py`, `orchestrator.py` |

**Persisted (conversation-scoped, no PII):**
- `active_service_slug`, `active_intent`, `active_entities` (safe keys only)
- `ClarificationState` key/value pairs
- Pending clarification questions from last assistant turn

**Follow-up behavior:**
- Short replies (`Naam`, `name`, `dob`) inherit prior service from context
- Birth correction clarification: "Naam" → `correction_type=name`
- Banglish/Bangla follow-ups supported via token detection

### 3. Knowledge Chunk Preparation (No RAG)

| Component | Path |
|-----------|------|
| Service | `backend/app/application/knowledge/evidence_ingestion.py` |
| Script | `scripts/ingest_verified_evidence_chunks.py` |

**Path:** Verified Evidence → `KnowledgeDocument` → `KnowledgeChunk`

**Chunk metadata:** `source_version_id`, `claim_id`, `service_id`, `information_class`, `language`, `excerpt`, `locator`, `authority_tier`, `last_verified_at`

**Ingestion result (local):** 12 documents, **51 chunks**, 0 embeddings. PRACTICAL claims skipped.

### 4. Knowledge Gap Sync & Classification

- **Bug fixed:** Publisher now reads `knowledge_gaps` key (was incorrectly reading `gaps`).
- **Script:** `scripts/classify_batch01_gaps.py` created 5 classified gaps:

| Service | Classification | Critical? |
|---------|----------------|-----------|
| `civil-marriage-registrar-hindu-list` | insufficient_evidence | No |
| `civil-marriage-registrar-muslim-list` | insufficient_evidence | No |
| `dc-attestation-photocopy` | source_discovery_problem | No |
| `local-passport-attestation` | geographic_local_variation | No |
| `local-voter-transfer-attestation` | geographic_local_variation | No |

None are CRITICAL to common national queries; Batch 1 is not blocked.

### 5. Readiness Re-evaluation

**Script:** `scripts/recalculate_batch01_readiness.py`  
**Output:** `data/evaluation/batch-01/readiness-recalc.json`

| Metric | Runtime value |
|--------|---------------|
| Published official claims | 32 |
| Published fees | 9 |
| Published checklist items | 1 |
| Published procedure steps | 170 |
| Verified URLs | 1 |
| Practical claims (published) | 1 |
| Knowledge chunks | 51 |
| Open gaps | 5 |

| Readiness | Services |
|-----------|----------|
| GREEN | 15 |
| YELLOW | 3 |
| RED | 16 |

**Note:** `birth-registration` remains **RED** for fees until approved seed replacement is applied (verified fee claims exist but Fee rows blocked by seed guard — by design).

### 6. Reusable Batch Template

Created: `docs/research/BATCH_RESEARCH_TEMPLATE.md`

---

## Regression Tests Added

**File:** `backend/tests/test_batch01_hardening.py`

| ID | Scenario | Status |
|----|----------|--------|
| A | Verified claim replaces seed only after approval | Pass |
| B | Partial claim cannot replace seed | Pass |
| C | Unverified claim cannot replace seed | Pass |
| D | Follow-up retains service context | Pass |
| E | Follow-up retains clarification context | Pass |
| F | Evidence → KnowledgeDocument/Chunk | Pass |
| G | Practical cannot become official chunk | Pass |
| H | Conflict blocks authoritative publication | Pass |
| I | Unsupported fee remains unsupported | Pass |
| J | Provenance intact after replacement | Pass |

---

## Total Test Results

| Suite | Result |
|-------|--------|
| Backend pytest | **45/45 passed** |
| Batch 01 E2E evaluation | **55/55 passed** (re-run post-hardening) |
| Hallucinations | 0 |
| Citation failures | 0 |
| Seed-data issues | 0 |

---

## Seed Replacement Status

| Item | Status |
|------|--------|
| Mechanism implemented | Yes |
| Audit logging | Yes |
| Rollback support | Yes |
| Birth-registration fees applied | **No** (awaiting explicit approval) |
| NID correction seed overwrite | **No** (calculator path already published on canonical services) |

---

## Conversation Context Status

| Capability | Status |
|------------|--------|
| Load prior service/intent | Implemented |
| Persist clarifications | Implemented |
| Follow-up "Naam" → name correction | Implemented |
| Language switch support | Implemented |
| PII minimization | Implemented (safe entity keys only) |

---

## Knowledge Chunk Preparation Status

| Item | Status |
|------|--------|
| Schema ready | Yes |
| Ingestion path | Yes |
| Embeddings | Not implemented (by design) |
| Chunks in runtime DB | 51 |
| System functional without RAG | Yes (structured claims + evidence + URLs) |

---

## Remaining Knowledge Gaps

1. Birth-registration **fee Fee rows** — blocked until seed replacement approved
2. Registrar list search UI — insufficient evidence on marriage.gov.bd
3. DC/local attestation — geographic variation; no single national procedure page
4. BDRIS upload constraints, helpline publication — from verification JSON
5. NID static fee schedule — intentionally routed to calculator

---

## Architecture Improvements Reusable for Future Batches

1. **SeedReplacement** approval workflow with dry-run/apply/rollback
2. **ConversationContextService** for multi-turn clarification without PII
3. **EvidenceIngestionService** — RAG-ready chunks without premature vectors
4. **Knowledge gap classification** taxonomy and sync fix
5. **Readiness recalculation** from live DB (not stale JSON)
6. **BATCH_RESEARCH_TEMPLATE.md** — standard pipeline documentation

---

## Explicit Non-Actions (Per Instructions)

- Batch 2 **not started**
- **No deployment** or public exposure
- **No full vector RAG**
- **No mass web crawl**
- Verification gates **not weakened**
- Audit trails **retained**

---

## Recommended Next Steps (When Ready)

1. Review seed replacement dry-run output
2. Approve and apply birth-registration fee replacements locally
3. Re-run readiness recalculation
4. Confirm fee E2E queries return verified amounts
5. Begin Batch 2 using `BATCH_RESEARCH_TEMPLATE.md`

**STOP — Batch 1 hardening complete.**
