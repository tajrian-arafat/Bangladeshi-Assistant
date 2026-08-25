# Batch 3B — BRTA Vehicle Publication & E2E

**Batch:** `batch-03b-brta-vehicle`  
**Layer:** evaluation (local/dev only)  
**Status:** Generated during autonomous GAP_CLOSURE → COMPLETE pipeline

## Scope

Six in-scope services:

- `brta-new-vehicle-registration`
- `brta-ownership-transfer`
- `brta-digital-registration-certificate`
- `brta-vehicle-info-correction`
- `brta-retro-reflective-number-plate`
- `brta-trustee-board-certificate`

Out of scope: `brta-fitness-certificate` (deferred to BATCH_03C).

## E2E query suite

- **Queries:** 55 (`data/evaluation/batch-03b-brta-vehicle/queries.json`)
- **Evaluator:** `scripts/evaluate_batch03b_brta_vehicle_e2e.py`
- **Outcome helper:** `scripts/batch03b_eval_outcomes.py`

Categories: new registration, ownership transfer, DRC, info correction, retro plate, TBC, anti-hallucination, fee honesty (CALCULATOR_DERIVED), fitness deferral, ambiguous routing.

## Publication gate

- Staging: `data/research/staging/batch-03b-brta-vehicle/`
- Normalizer: `scripts/normalize_batch03b_brta_vehicle_to_staging.py`
- Publisher: `scripts/publish_verified_knowledge.py --batch batch-03b-brta-vehicle`

Rules enforced:

- No invented static vehicle fees
- BSP 404 off-hours = `TEMPORARILY_UNAVAILABLE`
- Fitness validity-by-class deferred to BATCH_03C
- Lost RC remains sub-procedure under DRC/ownership

## Service readiness (post gap-closure)

| Service | Readiness |
|---------|-----------|
| All 6 in-scope services | YELLOW |

No service classified RED solely due to BATCH_03C fitness deferral.

## Artifacts

- `data/evaluation/batch-03b-brta-vehicle/summary.json`
- `data/evaluation/batch-03b-brta-vehicle/results.jsonl`
- `data/evaluation/batch-03b-brta-vehicle/failures.json`
- `docs/research/batch-03b-brta-vehicle-gap-closure.md`

## Regression inclusion

Batch 3A driving licence E2E included in REGRESSION phase suite alongside Batch 1, passport, Batch 2B, routing, and cross-domain benchmarks.

## Final E2E results (orchestrator run `run-7500f93b1207`)

| Metric | Value |
|--------|-------|
| Queries | 55 |
| Passed | 55 (100%) |
| Hallucinations | 0 |
| Citation failures | 0 |
| Outcomes | ANSWER_SUPPORTED: 30, CORRECT_UNCERTAINTY: 23, CORRECT_REFUSAL: 2 |

## Regression results

All regression suites passed at 100% baseline (Batch 1, passport, Batch 2B, Batch 3A, routing, cross-domain, pytest).

## Orchestrator final state

**BATCH_03B = COMPLETE** — workflow_status `COMPLETE`, last_completed_batch `BATCH_03B`. BATCH_03C remains PLANNED.
