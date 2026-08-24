# Batch 1 End-to-End Assistant Evaluation

**Generated:** 2026-08-24T23:03:36.982349+00:00
**Mode:** Local/development only — no deployment

## Headline results

| Metric | Value |
|--------|------:|
| Total tests | 55 |
| Passed | 55 |
| Failed | 0 |
| Pass rate | 100.0% |
| Hallucinations | 0 |
| Citation failures | 0 |
| Retrieval failures | 0 |
| Rule failures | 0 |
| Seed-data issues | 0 |
| Knowledge gaps | 0 |

## Metrics

- **service_identification_accuracy_pct:** 100.0
- **intent_accuracy_pct:** 100.0
- **bangla_pass_pct:** 100.0
- **banglish_pass_pct:** 100.0
- **hallucination_suite_pass_pct:** 100.0
- **unsupported_claim_rate_pct:** 0.0
- **unanswered_rate_pct:** 1.8
- **appropriate_uncertainty_pct:** 100.0

## Failure classification


## Highest-priority fixes


## Pipeline under test

USER QUERY → language → Banglish normalize → intent → service ID → entities → clarification → structured retrieval → claim-linked fees/checklist/steps → authority (support_level) → conflict → answer → citations → support level

## Fixes applied during evaluation (underlying causes)

1. Banglish glossary: `jonmo`/`nibondhon` → birth/registration
2. Bangla intent keywords for documents/fees/procedures
3. Phrase/URL-aware service matching with published-claim boost
4. Seed checklist/steps/fees without `claim_id` excluded from official MUST NEED
5. PRACTICAL claims surfaced only in `practical_notes` with explicit label
6. Citations prefer verified `ServiceLink` / claim evidence over decorative names
7. Explicit refusal of unsupported fee amounts (230/345/460/500)
8. Stale `CONFLICTED` service status no longer forced without conflicting claims

## Sample failures

## Machine-readable artifacts

- `data/evaluation/batch-01/queries.json`
- `data/evaluation/batch-01/results.jsonl`
- `data/evaluation/batch-01/summary.json`
- `data/evaluation/batch-01/failures.json`

## Stop condition

Evaluation complete. No Batch 2. No deploy. MVP seeds not overwritten.
