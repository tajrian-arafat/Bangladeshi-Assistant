# Final Knowledge Construction Audit

Generated: 2026-08-25T03:41:01.574371+00:00

## Executive verdict

**KNOWLEDGE_INCOMPLETE**

The overnight orchestrator reported `KNOWLEDGE_COMPLETE` after all 17 batches executed, but this audit finds that **batch completion ≠ service-specific knowledge completeness**. Batches 04–14 were processed primarily by generic research/verification builders producing boilerplate catalogue-derived claims. Those batches must not be treated as fully researched.

## Catalogue coverage

| Metric | Count |
|--------|------:|
| Canonical catalogue | 464 |
| Confirmed services audited | 454 |
| COMPLETE | 37 |
| PARTIAL | 416 |
| DEFERRED | 0 |
| BLOCKED | 1 |

## False completion detection

- Services flagged `FALSE_COMPLETION_RISK`: **389**
- Services with generic boilerplate only: **389**
- Services from generic-builder batches (04–14): **393**
- Services with zero verified claims: **132**
- Services with catalogue-only sources: **12**

Generic builder pattern produces 2–3 claims per service (`application-portal`, `responsible-authority`, `official-source`) copied from catalogue metadata. Land services incorrectly reference 'NBR e-service portal'. Fees and mandatory documents remain explicitly unverified.

## Completeness by batch

| Batch | COMPLETE | PARTIAL | DEFERRED | BLOCKED |
|-------|--------:|--------:|---------:|--------:|
| BATCH_01 | 3 | 10 | 0 | 0 |
| BATCH_02A | 2 | 8 | 0 | 0 |
| BATCH_02B | 5 | 5 | 0 | 1 |
| BATCH_03A | 6 | 0 | 0 | 0 |
| BATCH_03B | 6 | 0 | 0 | 0 |
| BATCH_03C | 15 | 0 | 0 | 0 |
| BATCH_04 | 0 | 11 | 0 | 0 |
| BATCH_05 | 0 | 15 | 0 | 0 |
| BATCH_06 | 0 | 11 | 0 | 0 |
| BATCH_07 | 0 | 14 | 0 | 0 |
| BATCH_08 | 0 | 158 | 0 | 0 |
| BATCH_09 | 0 | 14 | 0 | 0 |
| BATCH_10 | 0 | 12 | 0 | 0 |
| BATCH_11 | 0 | 27 | 0 | 0 |
| BATCH_12 | 0 | 11 | 0 | 0 |
| BATCH_13 | 0 | 9 | 0 | 0 |
| BATCH_14 | 0 | 111 | 0 | 0 |

## Claim statistics (staging)

- Total claims: **1242**
- Verified: **496**
- Partially verified: **702**
- Unverified: **33**
- Conflicting: **5**

## E2E quality (not pass-rate alone)

- Aggregate pass rate (batch E2E): **57.7%** (652/1130)
- Hallucinations: **0**
- Citation failures: **0**

### Hand-researched batches (01–03)

- `batch-01`: 55/55 passed (100.0%)
- `batch-02a-passport`: 57/57 passed (100.0%)
- `batch-02b-police-immigration`: 66/67 passed (98.5%)
- `batch-03a-brta-driving-licence`: 55/55 passed (100.0%)
- `batch-03b-brta-vehicle`: 55/55 passed (100.0%)
- `batch-03c-brta-fitness-tax-permit`: 55/55 passed (100.0%)

### Generic-builder batches (04–14)

- `batch-04-tax-vat-customs`: 1/22 passed (4.55%) — **insufficient for COMPLETE**
- `batch-05-land`: 9/30 passed (30.0%) — **insufficient for COMPLETE**
- `batch-06-education`: 9/22 passed (40.91%) — **insufficient for COMPLETE**
- `batch-07-health`: 0/28 passed (None%) — **insufficient for COMPLETE**
- `batch-08-social-protection`: 246/316 passed (77.85%) — **insufficient for COMPLETE**
- `batch-09-agriculture`: 4/28 passed (14.29%) — **insufficient for COMPLETE**
- `batch-10-employment-migration`: 5/24 passed (20.83%) — **insufficient for COMPLETE**
- `batch-11-business-trade`: 2/54 passed (3.7%) — **insufficient for COMPLETE**
- `batch-12-local-gov`: 1/22 passed (4.55%) — **insufficient for COMPLETE**
- `batch-13-judiciary`: 3/18 passed (16.67%) — **insufficient for COMPLETE**
- `batch-14-remaining`: 29/222 passed (13.06%) — **insufficient for COMPLETE**

Outcome breakdown (where recorded): `{"PRODUCT_FAILURE": 821, "PASS_LEGACY": 309}`

## Routing / cross-domain

- Service routing: **34/34** passed
- Cross-domain hardening: **90/90** passed

Routing suites test known well-researched domains (batch 01–03). They do **not** validate batches 04–14 quality.

## Source quality

Hand-researched batches include Tier 1–2 official sources with evidence snapshots. Generic-builder batches rely predominantly on `src-catalogue` (Tier 1 catalogue file) with optional unreachable URL probes — **not independent official verification**.

## Runtime / research consistency

- Runtime DB available: **False**
- Consistency issues found: **10**

## Legacy seed state

- Legacy seed rows: **7**
- Verified replacements available: **3**
- Automatic replacement: **NOT APPROVED** (manual review required)

## Major risks

1. **False completion**: 393 services in batches 04–14 have generic boilerplate, not service-specific research.
2. **E2E failures**: Generic batches show 0–40% pass rates; failures are mostly RETRIEVAL_BUG / service mismatch.
3. **No verified fees/documents** for most post-batch-03 services.
4. **Empty runtime DB**: Published knowledge may not be loaded into runtime for verification.
5. **Geographic variation**: Local/district services marked NATIONAL without evidence.

## Recommended next work

1. Re-research batches 04–14 with service-specific official source retrieval (not generic builder).
2. Do not mark batches COMPLETE until E2E pass rate and verified claim thresholds met.
3. Populate runtime DB and re-run publication dry-run with citation integrity checks.
4. Resolve legacy seed replacements through manual approval workflow.
5. Keep deployment locked until KNOWLEDGE_INCOMPLETE → COMPLETE transition is evidence-based.

## Safety

- deployment_allowed: **false**
- auto_merge: **false**
- No deployment, merge, or external publication performed by this audit.

