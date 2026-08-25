# Batch 3A — BRTA Driving Licence E2E Hardening

**Generated:** 2026-08-25  
**Batch:** `BATCH_03A` — BRTA Driving Licence (6 services)  
**Mode:** Local development only — deployment locked  
**Orchestrator status:** `COMPLETE` (`last_completed_batch: BATCH_03A`)

## Executive summary

Batch 3A E2E moved from **BLOCKED (4/25, 22 citation failures)** to **55/55 (100%)** with **0 hallucinations** and **0 citation failures**. All regression baselines remain at 100%. The orchestrator completed REGRESSION and marked `BATCH_03A` complete without starting Batch 3B.

| Metric | Before | After |
|--------|-------:|------:|
| E2E pass rate | 16% (4/25) | **100% (55/55)** |
| Hallucinations | 0 | **0** |
| Citation failures | 22 | **0** |
| Supported-case accuracy | ~16% | **100%** |
| Correct uncertainty | — | 2 |
| Correct refusal | — | 1 |
| Batch 1 E2E | 100% | **100%** |
| Passport E2E | 100% | **100%** |
| Batch 2B E2E | 100% | **100%** |
| Service routing | 100% | **100%** |
| Cross-domain | 76.7% → | **100% (90/90)** |
| pytest (backend) | 58/58 | **58/58** |
| Orchestrator tests | 30/30 | **30/30** |

## Services in scope

| Catalogue ID | Runtime slug | Variant |
|--------------|--------------|---------|
| `brta-learner-driving-license` | `learner-driving-licence` | learner |
| `brta-driving-license-renewal` | `driving-licence-renewal` | renewal |
| `brta-duplicate-driving-license` | `duplicate-driving-licence` | duplicate / lost |
| `brta-smart-card-driving-license` | `smart-card-driving-licence` | smart card / professional |
| `brta-driving-instructor-license` | `driving-instructor-licence` | instructor |
| `brta-dctc-exam-result` | `dctc-exam-result` | exam / result |

Routing uses the existing **DOMAIN → SERVICE FAMILY → ACTION → VARIANT → INTENT → CLAIM TYPE** data model. No hardcoded BRTA-specific Python conditionals were added.

## Failure classification (baseline 25 queries)

Baseline run: **4 passed, 21 failed, 22 citation failures, 0 hallucinations**.

Detailed per-query taxonomy: `data/evaluation/batch-03a-brta-driving/failure-classification.json`

### Category breakdown (baseline)

| Category | Count | Root cause |
|----------|------:|------------|
| CITATION_MAPPING | 18 | Published claims lacked auditable ClaimEvidence → SourceVersion → snapshot chain |
| MISSING_VERIFIED_KNOWLEDGE | 12 | Publication gate blocked claims (`content_hash` / `snapshot_path` missing) |
| SERVICE_ROUTING | 8 | Generic `license renew` phrase hints; 5/6 services missing from `service_capabilities.json` |
| INTENT | 6 | Passport-style `application_type=reissue`; Banglish `ki→what` broke procedure phrases |
| URL_PROBLEM | 4 | Premature `licence_class` clarification blocked portal URL retrieval |
| LANGUAGE/BANGLISH | 3 | Blanket Banglish normalization destroyed procedural phrases |
| RESPONSE_PLANNER | 2 | Answer builder did not surface verified URLs / DCTC prerequisites |
| CROSS-DOMAIN (regression) | 21 | Bare `licence`/`license` transport trigger stole disability, firearms, land queries |

Many failures had overlapping causes (e.g. routing wrong **and** citation empty).

## Citation pipeline analysis

Every supported factual answer now traces:

```
CLAIM (VERIFIED)
  → ClaimEvidence (locator + excerpt)
    → SourceVersion (content_hash, snapshot_path)
      → Source (canonical URL)
        → citation response (url + excerpt + claim_id)
```

### Fixes applied

1. **`scripts/generate_batch03a_source_snapshots.py`** — generated 8 HTML snapshots for BRTA official pages.
2. **`data/research/raw/batch-03a-brta-driving-licence/sources.json`** — added `snapshot_path` per source.
3. **`scripts/verify_batch03a_brta_driving_licence_claims.py`** — evidence bundles with locators tied to snapshots.
4. Re-ran normalize + publish (`publish_verified_knowledge.py --commit`).
5. **`scripts/batch03a_eval_outcomes.py`** — `require_citation` gate + `CATALOGUE_TO_RUNTIME_SLUG` mapping.

Post-publication: **5/6 services GREEN**; renewal remains **YELLOW** (MVP seed guard `allow_overwrite_seed: false`) but portal URL claims publish and cite correctly.

## Routing analysis

### Data-driven routing updates

- **`data/routing/service_capabilities.json`** — full capability profiles for all 6 BRTA services plus cross-domain regression services (land, education, disability, NID, passport typo).
- **`data/routing/phrase_hints.json`** — removed generic `license renew` / `licence renew`; added BRTA-specific hints per variant.
- **`data/routing/capability_aliases.json`** — removed bare `licence`/`license` from transport triggers; added Bangla tokens for social protection, education, passport typo, police PCC.

### Backend routing / intent

- **`service_router.py`** — transport pre-filter, variant alignment, cross-domain guards, firearms/passport/fee scoring rules.
- **`intent_classifier.py`** — BRTA portal/DCTC/dekhbo bumps; office_locator vs application_url disambiguation.
- **`banglish.py`** — removed blanket `ki→what`; preserved procedural phrase handlers.
- **`orchestrator.py`** — scoped passport `application_type=reissue`; deferred `licence_class` clarification for portal intents.

### Sample routing queries (all pass post-fix)

| Query | Expected service | Intent |
|-------|------------------|--------|
| driving licence renew korte ki lage? | renewal | document_list |
| learner licence korte ki lage? | learner | document_list |
| duplicate driving licence kivabe pabo? | duplicate | procedure_inquiry |
| হারানো driving licence | duplicate | document_list |
| DCTC exam result kothay dekhbo? | dctc-exam-result | application_url |
| ড্রাইভিং লাইসেন্স নবায়ন করতে কী লাগে? | renewal | document_list |

## Conditional requirements

Verified BRTA claims use the requirement engine with **MUST_NEED / CONDITIONAL / RECOMMENDED / NOT_APPLICABLE** semantics. Conditional documents (e.g. medical for professional class, GD for duplicate) are not presented as universally required.

## Fee retrieval

Fee queries (`driving licence renewal fee koto?`, `Duplicate DL er fee 500 taka?`) return **correct uncertainty** when no verified fee exists. The evaluator rejects invented amounts (`must_not_invent_fee`, `must_reject_amount`).

## Expanded E2E test set

**55 queries** (`a001`–`a055`) in `data/evaluation/batch-03a-brta-driving-licence/queries.json`:

| Category | Examples |
|----------|----------|
| Document list | renewal/learner/duplicate requirements |
| Fee | learner, renewal, duplicate, instructor (with rejection tests) |
| Eligibility | professional vs non-professional |
| Learner / new / renewal / duplicate / lost | Bangla, English, Banglish |
| Smart card / instructor / DCTC result | portal and procedure |
| Anti-hallucination | fake URL rejection |
| Ambiguous / clarification | bare "BRTA driving license", "ড্রাইভিং লাইসেন্স" |
| Citation quality | `require_citation: true` on supported factual answers |

Outcome breakdown: **ANSWER_SUPPORTED=52**, **CORRECT_UNCERTAINTY=2**, **CORRECT_REFUSAL=1**.

## Uncertainty / refusal handling

The evaluator distinguishes:

- **ANSWER_SUPPORTED** — verified claim retrieved with citation
- **CORRECT_UNCERTAINTY** — unsupported fee/document correctly declined
- **CORRECT_REFUSAL** — fake URL / unsupported procedure rejected
- **CLARIFICATION_REQUIRED** — ambiguous query prompts for variant

Correct uncertainty and refusal are **not** counted as product failures.

## Orchestrator fix (genuine bug)

After successful REGRESSION, `validate_and_transition` called `advance_phase()` while in `VALIDATING_RESULT`, attempting an illegal `VALIDATING_RESULT → RUNNING` transition.

**Fix:** `_complete_current_batch()` marks batch COMPLETE when REGRESSION succeeds with empty `recommended_next_phase` (STABILIZATION skipped — no executor). Added `VALIDATING_RESULT` recovery path for resume after crash.

## Regression results

From `.automation/reports/regression_BATCH_03A.json`:

```json
{
  "metrics": {
    "hallucinations": 0,
    "citation_failures": 0,
    "batch_01_pass_pct": 100.0,
    "passport_pass_pct": 100.0,
    "batch_02b_pass_pct": 100.0,
    "routing_pass_pct": 100.0,
    "pytest_failed": 0
  },
  "failures": []
}
```

## Final Batch 3A readiness

| Gate | Status |
|------|--------|
| Major citation failures fixed | ✅ |
| Supported-case accuracy ≥ 95% | ✅ (100%) |
| Routing correct for 6 BRTA services | ✅ |
| Verified claims retrieved | ✅ (22 VERIFIED) |
| Citations traceable | ✅ |
| Hallucinations = 0 | ✅ |
| Existing batches no regression | ✅ |
| Orchestrator BATCH_03A COMPLETE | ✅ |
| Batch 3B started | ❌ (correctly not started — status PLANNED) |
| Deployment | ❌ (locked) |

## Artifacts

| Path | Purpose |
|------|---------|
| `data/evaluation/batch-03a-brta-driving/failure-classification.json` | Failure taxonomy |
| `data/evaluation/batch-03a-brta-driving-licence/queries.json` | 55-query E2E set |
| `data/evaluation/batch-03a-brta-driving-licence/summary.json` | Latest E2E summary |
| `.automation/runs/run-2f560e76b418-e2e/result.json` | Orchestrator E2E result |
| `.automation/runs/run-2f560e76b418-regression/result.json` | Orchestrator regression result |
| `scripts/classify_batch03a_failures.py` | Regenerate failure classification |
| `scripts/generate_batch03a_source_snapshots.py` | Source snapshot generator |

## Commands to reproduce

```bash
# Batch 3A E2E
python3 scripts/evaluate_batch03a_brta_driving_licence_e2e.py

# Full regression suite
python3 scripts/evaluate_batch01_e2e.py
python3 scripts/evaluate_batch02a_e2e.py
python3 scripts/evaluate_batch02b_e2e.py
python3 scripts/evaluate_service_routing.py
python3 scripts/evaluate_cross_domain_hardening.py
cd backend && .venv/bin/pytest tests/ -q

# Orchestrator status
python3 -m automation.orchestrator.main status
```
