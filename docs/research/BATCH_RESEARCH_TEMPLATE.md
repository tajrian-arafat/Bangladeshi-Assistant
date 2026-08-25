# Batch Research Template

Reusable workflow for researching and publishing government service knowledge in batches.

## Pipeline Overview

```
DISCOVERY
  → STAGING
  → NORMALIZATION
  → CLAIM EXTRACTION
  → CROSS-CHECK
  → INDEPENDENT VERIFICATION
  → CLAIM-LEVEL PUBLICATION
  → E2E EVALUATION
  → KNOWLEDGE GAP FEEDBACK
  → (optional) SEED REPLACEMENT REVIEW
  → (optional) EVIDENCE → KNOWLEDGE CHUNK INGESTION
```

Each batch follows the same stages. Batch 1 established the patterns below.

---

## 1. DISCOVERY

**Goal:** Identify services in scope without inventing procedures.

- Source: national service catalogue (`data/research/catalogue/`)
- Output: batch service list with agency, category, keywords
- Rules:
  - Do not mass-crawl the web
  - Record catalogue IDs and runtime slug candidates
  - Flag local/geographic services separately

**Artifacts:** `data/research/raw/batch-NN/services_index.json`

---

## 2. STAGING

**Goal:** Hold research artifacts before DB sync.

- Create `data/research/staging/batch-NN/`
- Required files: `services.json`, `claims.json`, `evidence.json`, `fees.json`, `requirements.json`, `procedure_steps.json`, `conflicts.json`
- Link every claim to evidence IDs and source versions

**Artifacts:** staging JSON + `runtime_gap_register.json`

---

## 3. NORMALIZATION

**Goal:** Map catalogue services → runtime services without silent overwrite.

- Run catalogue/runtime sync
- Maintain `data/research/catalogue_runtime_mappings.json`
- MVP seed slugs require explicit `allow_overwrite_seed` or approved `SeedReplacement`

**Script:** `scripts/sync_catalogue_runtime.py`

---

## 4. CLAIM EXTRACTION

**Goal:** Atomic, typed claims with information class.

| Field | Values |
|-------|--------|
| `claim_type` | fee, document, procedure_step, application_url, practical_tip, … |
| `information_class` | OFFICIAL, PRACTICAL, DISCOVERY |
| `pipeline_status` | DISCOVERED → … → VERIFIED / PARTIALLY_VERIFIED / UNVERIFIED / REJECTED |

**Rules:**
- One fact per claim
- PRACTICAL never populates MUST NEED checklist
- High-risk claims (fees, legal basis) require stronger evidence

---

## 5. CROSS-CHECK

**Goal:** Detect conflicts before verification.

- Output: `conflicts.json` with conflicting claim pairs
- CONFLICTING claims block authoritative publication
- Unresolved NID static fees → calculator path only

---

## 6. INDEPENDENT VERIFICATION

**Goal:** Human/agent review separate from extraction.

- Output: `data/research/verification/batch-NN/claims_verification.json`
- Statuses: VERIFIED, PARTIALLY_VERIFIED, UNVERIFIED, REJECTED
- Store live retrieval metadata, snapshots, reasoning
- Record gaps in `knowledge_gaps.json` (key: `knowledge_gaps`)

**Script:** `scripts/verify_batch01_claims.py` (adapt per batch)

---

## 7. CLAIM-LEVEL PUBLICATION

**Goal:** Publish only gate-eligible VERIFIED OFFICIAL claims.

**Gates (all required for authoritative publish):**
- `pipeline_status == VERIFIED`
- `information_class == OFFICIAL`
- Complete evidence chain (Claim → Evidence → SourceVersion → Source)
- Content hash present where required
- No unresolved conflict on same claim type
- `verified_at` set

**Workflow:**
```bash
python scripts/publish_verified_knowledge.py --batch batch-NN --dry-run
python scripts/publish_verified_knowledge.py --batch batch-NN
```

**MVP seed replacement (when runtime slug is a seed):**
```bash
python scripts/review_seed_replacements.py --dry-run
python scripts/review_seed_replacements.py --record --approve-all --apply
```

Never auto-overwrite seed structured data.

---

## 8. E2E EVALUATION

**Goal:** 50+ realistic queries; zero hallucinations.

- Queries: BN / EN / Banglish
- Inspect full pipeline (intent, service match, fees, citations, warnings)
- Classify failures: hallucination, citation, retrieval, rule, seed-data

**Script:** `scripts/evaluate_batch01_e2e.py` (adapt per batch)

**Pass criteria:**
- No invented fees or documents
- Unsupported amounts refused
- PRACTICAL separated from MUST NEED
- Appropriate uncertainty when evidence insufficient

---

## 9. KNOWLEDGE GAP FEEDBACK

**Goal:** Track what is missing without blocking the batch.

**Gap classifications:**
| Class | Meaning |
|-------|---------|
| missing_official_national_source | No authoritative national page |
| geographic_local_variation | Union/DC procedures differ by locality |
| insufficient_evidence | Source exists but claim not confirmed |
| service_identification_problem | Catalogue/runtime mapping unclear |
| source_discovery_problem | Expected URL unreachable |
| actual_knowledge_gap | Genuinely unknown; do not invent |

**Script:** `scripts/classify_batch01_gaps.py`

Only CRITICAL gaps (block common queries) should delay batch sign-off.

---

## Evidence Rules

| Tier | Source type |
|------|-------------|
| 1 | Direct responsible authority |
| 2 | Other official BD government |
| 3–4 | Public institutions |
| 5–7 | Media, guides, community (never authoritative alone) |

- Fees require tier ≤ 2 or dual independent tier ≤ 4
- Snapshots stored under `verification/batch-NN/source_snapshots/`

---

## Source Tiers

See `SourceTier` in `backend/app/domain/enums.py`. Tiers are never auto-upgraded by LLM.

---

## High-Risk Claims

Require independent verification + publication gate:
- Fee amounts
- Application URLs
- Legal basis / eligibility
- Processing deadlines

NID fees: use official calculator; do not publish static 230/345/460 amounts.

---

## Conditional Requirements

- Store conditions in claim `structured_value.condition`
- ChecklistEngine evaluates against clarifications
- Conversation context supplies clarification answers across turns

---

## Practical Information

- `information_class = PRACTICAL` → `practical_notes` in answers only
- Never populate REQUIRED checklist from PRACTICAL claims
- May be published for user guidance with clear non-official labeling

---

## Conflict Handling

1. Mark conflicting claims `CONFLICTING`
2. Block authoritative publish for that claim type
3. Service may remain YELLOW/RED without forcing CONFLICTED status on unrelated claims
4. Resolve in verification JSON before re-publish

---

## Publication Gates

Implemented in `backend/app/application/knowledge/publication_gate.py`:
- `evaluate_official_publication`
- `can_populate_fee`
- `can_populate_must_need`
- `can_populate_procedure_step`
- `assert_mapping_safe`

---

## Seed Replacement (MVP Services)

MVP seeds: `passport-renewal`, `nid-correction`, `driving-licence-renewal`, `birth-registration`, `tin-registration`

Replacement requires:
1. VERIFIED + OFFICIAL claim
2. Publication gate passed
3. Explicit `SeedReplacement` approval
4. Audit log on apply/rollback

---

## Knowledge Chunks (RAG Preparation)

No embeddings in Batch 1. Ingestion path:

```
Verified Evidence → KnowledgeDocument → KnowledgeChunk
```

Metadata per chunk: `source_version_id`, `claim_id`, `service_id`, `information_class`, `authority_tier`, `locator`, `last_verified_at`

**Service:** `EvidenceIngestionService` — PRACTICAL claims skipped.

---

## Conversation Context

Persist per conversation (no PII):
- `active_service_slug`, `active_intent`, `active_entities`
- ClarificationState key/value pairs
- Follow-up resolution for short replies ("Naam" → name correction)

---

## Test Requirements (Every Batch)

1. Publication gate unit tests
2. Seed replacement regression (approve / block partial / block unverified / rollback)
3. Follow-up context tests
4. Evidence ingestion tests
5. E2E evaluation suite (50+ queries)
6. Readiness recalculation from runtime DB

```bash
cd backend && .venv/bin/pytest tests/ -q
python scripts/recalculate_batch01_readiness.py
```

---

## Readiness Levels

| Level | Meaning |
|-------|---------|
| GREEN | Verified official claims published; no critical gaps |
| YELLOW | Partial publish; some verified claims remain |
| RED | No verified publish or critical gate failures |

Recalculate from runtime — do not reuse stale JSON numbers.

---

## Do NOT

- Deploy without explicit approval
- Start next batch before current batch hardening complete
- Build full vector RAG prematurely
- Mass-crawl the web
- Weaken verification or remove audit trails
- Mark uncertain knowledge as verified
- Invent local procedures

---

## Batch Checklist

- [ ] Discovery list approved
- [ ] Staging JSON complete
- [ ] Mappings synced
- [ ] Claims extracted with evidence
- [ ] Cross-check conflicts logged
- [ ] Independent verification complete
- [ ] Dry-run publication clean
- [ ] Publication applied
- [ ] Seed replacements reviewed (if MVP seeds affected)
- [ ] E2E evaluation passed
- [ ] Gaps classified
- [ ] Readiness recalculated
- [ ] Hardening report written
