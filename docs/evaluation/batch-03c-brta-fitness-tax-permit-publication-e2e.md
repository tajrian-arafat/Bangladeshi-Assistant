# Batch 3C — BRTA Fitness / Tax Token / Route Permit Publication & E2E

**Batch:** `batch-03c-brta-fitness-tax-permit`  
**Layer:** evaluation (local/dev only)  
**Status:** E2E and regression validated; fitness validity-by-class intentionally deferred

## Scope

Fifteen in-scope services:

- `brta-fitness-certificate`
- `brta-tax-token`
- `brta-mv-tax-payment`
- `brta-route-permit`
- `transport-route-permit`
- `brta-fee-calculator`
- `brta-advance-income-tax`
- `brta-bsp-user-registration`
- `brta-e-document-verification`
- `brta-payment-verification`
- `brta-color-change`
- `brta-engine-change`
- `brta-tire-size-change`
- `brta-driving-school-registration`
- `transport-driving-school-licence`

## Cross-batch dependency (BATCH_03B)

**Dependency:** `dep-03b-fitness-validity-03c`  
**Status:** `PARTIALLY_RESOLVED` — portal page identity verified; class-by-class validity periods remain **UNVERIFIED**

Evidence confirms the BRTA fitness renewal portal title (`ফিটনেস নবায়ন`) but CMS body is placeholder content. No authoritative validity matrix was published. Historical BATCH_03B claims were **not** rewritten; supersession records are in gap-closure artifacts.

## E2E query suite

- **Queries:** 55 (`data/evaluation/batch-03c-brta-fitness-tax-permit/queries.json`)
- **Evaluator:** `scripts/evaluate_batch03c_brta_fitness_tax_permit_e2e.py`
- **Outcome helper:** `scripts/batch03c_eval_outcomes.py`

Categories: fitness renewal, tax token, MV tax, route permit, fee calculator, vehicle modification, driving school, anti-hallucination, CALCULATOR_DERIVED fee honesty, cross-batch fitness deferral, Bangla/English/Banglish/typo routing.

## Publication gate

- Staging: `data/research/staging/batch-03c-brta-fitness-tax-permit/`
- Normalizer: `scripts/normalize_batch03c_brta_fitness_tax_permit_to_staging.py`
- Publisher: `scripts/publish_verified_knowledge.py --batch batch-03c-brta-fitness-tax-permit`

Rules enforced:

- No invented fitness validity-by-class periods
- CALCULATOR_DERIVED fees labelled honestly (not OFFICIAL_STATIC)
- MV tax portal DNS failure recorded as KnowledgeGap
- BSP portal title verified where tier-1 evidence exists

## Verification summary

| Tier | Count |
|------|-------|
| VERIFIED | 37 |
| PARTIALLY_VERIFIED | 83 |
| UNVERIFIED | 8 |

## Service readiness (post gap-closure)

All 15 services: **YELLOW** (safe partial coverage, no unsafe authoritative claims)

## Final E2E results

| Metric | Value |
|--------|-------|
| Queries | 55 |
| Passed | 55 (100%) |
| Hallucinations | 0 |
| Citation failures | 0 |
| Outcomes | ANSWER_SUPPORTED: 32, CORRECT_UNCERTAINTY: 20, CORRECT_REFUSAL: 3 |

## Regression results

All regression suites at 100% baseline after routing fix (Batch 1, passport, Batch 2B, Batch 3A, Batch 3B, Batch 3C, routing, cross-domain, pytest).

## Artifacts

- `data/evaluation/batch-03c-brta-fitness-tax-permit/summary.json`
- `data/evaluation/batch-03c-brta-fitness-tax-permit/results.jsonl`
- `data/research/verification/batch-03c-brta-fitness-tax-permit-gap-closure/cross_batch_dependency_resolution.json`
- `docs/research/batch-03c-brta-fitness-tax-permit-research.md`
- `docs/research/batch-03c-brta-fitness-tax-permit-gap-closure.md`

## Orchestrator final state

**BATCH_03C = COMPLETE** after REGRESSION phase passes with zero hallucinations and zero citation failures.
