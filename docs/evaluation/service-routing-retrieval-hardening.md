# Service Routing & Retrieval Hardening

**Generated:** 2026-08-24  
**Mode:** Local/dev only — no deployment, no Batch 2B, publication gates unchanged

## Problem statement

Batch 2A E2E (pre-fix) exposed **38/48 failures as RETRIEVAL / SERVICE-ROUTING** — not hallucination, citation, or outdated publication. Root cause: phrase hints + fuzzy string matching over ~452 services with weak intent awareness.

Examples that previously mis-routed:

| Query | Was routing to | Now routes to |
|-------|----------------|---------------|
| `e-passport fee koto?` | `passport-mrp-initial` | `epassport-fee-payment` |
| `passport status check` | application/reissue | `epassport-application-status` |
| `passport payment ki?` | generic passport | `epassport-fee-payment` |

## Architecture (separated pipeline)

```
USER QUERY
  → language / Banglish normalization
  → intent classification (primary + secondary)
  → domain entity extraction (passport_type, action, speed, channel, …)
  → domain-scoped service candidate retrieval
  → intent-aware scoring + claim-coverage signal
  → disambiguation OR minimal clarification
  → intent-filtered claim retrieval
  → answer composition
```

### New modules

| Path | Role |
|------|------|
| `backend/app/ai/routing/intent_classifier.py` | Multi-intent taxonomy |
| `backend/app/ai/routing/domain_entities.py` | Variant dimensions (e/MRP, express, mission, …) |
| `backend/app/ai/routing/service_router.py` | Candidate scoring & disambiguation |
| `backend/app/ai/routing/claim_retrieval.py` | Intent-filtered VERIFIED claim fetch |
| `backend/app/ai/routing/loader.py` | Data-driven config loader |
| `data/routing/*.json` | Capabilities, aliases, intents, phrase hints |

## Service capability model

Structured JSON (`data/routing/service_capabilities.json`) per service:

- `domain`, `service_type`, `intent_capabilities`, `intent_boost`
- `variants`: `passport_type`, `actions`, `speeds`, `channels`, `applicants`
- `aliases_en` / `aliases_bn` / `aliases_banglish`
- `capability_keywords`

Reusable alias groups live in `data/routing/capability_aliases.json` (fee, status, appointment, e_passport, mrp, lost, …).

Intent → claim-type mapping: `data/routing/intent_taxonomy.json`.

## Routing algorithm (scoring)

For each domain-scoped candidate:

1. **Intent compatibility** — `intent_capabilities` + `intent_boost` (+ service_type affinity)
2. **Phrase hints** — longest match first (`loader.py` sorts by length)
3. **Alias / keyword overlap** — EN, BN, Banglish
4. **Variant alignment** — passport type, action, speed, channel
5. **Published claim coverage** — count of VERIFIED published claims matching intent claim-types (capped boost)
6. **Weak fuzzy name match** — capped, never primary signal
7. **Penalties** — e.g. fee intent vs application service; police verification vs renewal

If top two scores are within **5 points** on ambiguous passport fee/type queries → clarification (`MRP naki e-passport-er fee jante chacchen?`).

Domain filtering uses **capability profile domain**, not raw DB category (fixes `passport-renewal` miscategorized as `IDENTITY`).

## Intent taxonomy

Supported intents include: `fee_inquiry`, `payment`, `document_list`, `procedure_inquiry`, `application`, `application_url`, `status`, `appointment`, `eligibility`, `office_locator`, `processing_time`, `renewal`, `reissue`, `correction`, `lost_document`, `comparison`, `general_info`, …

Multi-intent example: *"e-passport renew korte koto taka lage ebong ki ki lage?"* → primary `fee_inquiry`, secondary `document_list`.

## Claim retrieval

After service selection, `ClaimRetrieval` filters by:

- `service_id`
- intent → `claim_types` from taxonomy
- `pipeline_status = VERIFIED`, `information_class = OFFICIAL`, `is_published = true`

Orchestrator answer building is intent-aware:

- **FEE_INQUIRY** → fees linked to published fee claims only
- **DOCUMENT_LIST** → checklist
- **STATUS / PROCEDURE / APPOINTMENT** → procedure steps

## Regression suites

| Suite | Tests | Result |
|-------|------:|--------|
| pytest | 58 | **58 passed** |
| Service routing benchmark | 19 | **19/19 (100%)** |
| Batch 1 E2E | 55 | **42/55 (76.4%)** — service ID **92.3%** |
| Batch 2A Passport E2E | 57 | **34/57 (59.6%)** — service ID **93.0%** |

### Previous vs new (Batch 2A Passport)

| Metric | Before | After |
|--------|-------:|------:|
| E2E pass rate | 15.8% (9/57) | **59.6% (34/57)** |
| RETRIEVAL_BUG count | 38 | **4** |
| Service identification | ~35% (est.) | **93.0%** |
| Hallucinations | 0 | **0** |
| Citation failures | 0 | **0** |

### Service routing benchmark (100%)

Passport + Batch 1 non-regression queries in `data/evaluation/service-routing/queries.json` — asserts `expected_intent`, `expected_service`, `acceptable_services`, `expected_claim_types`.

Candidate ranking examples: `data/evaluation/service-routing/candidate_ranking_examples.json`.

## Remaining failures (Batch 2A)

| ID | Issue class | Notes |
|----|-------------|-------|
| p037 | RETRIEVAL | Fake URL + "passport fee" — phrase hint prefers fee service over application URL intent |
| p045 | RETRIEVAL | Follow-up "express tier?" — partial clarification context |
| p046 | RETRIEVAL | SLA query — close call between two police verification services |
| p047 | RETRIEVAL | Charter timeline — same police service family ambiguity |

Additional failures are **LANGUAGE_BUG**, **CLAIM_SELECTION**, or **expected uncertainty** cases — not routing regressions.

## Success threshold assessment

| Target | Result | Met? |
|--------|--------|:----:|
| Service identification ≥ 95% | 93.0% (Batch 2A), 100% (routing benchmark) | Close |
| Intent identification ≥ 95% | 66.7% (Batch 2A E2E strict), 100% (routing benchmark) | Partial |
| Claim retrieval ≥ 95% | 100% (routing benchmark, knowledge-gap aware) | Yes* |
| Hallucination = 0 | 0 | Yes |
| Citation failure = 0 | 0 | Yes |

\*Many Batch 2A services remain RED/YELLOW readiness — routing succeeds but claims are not yet published.

## Recommended follow-up

1. **Police verification service family** — evaluator alias for `police-passport-police-verification` vs `police-passport-verification` when intent is `processing_time`.
2. **Follow-up context** — wire `clarifications.service` into conversation persistence (partial support added).
3. **Expand capability profiles** beyond passport + Batch 1 seeds (BRTA, tax, land) using same JSON schema.
4. **Intent E2E alignment** — Batch 2A uses legacy intent names (`eligibility_inquiry`, `application_url`); map in evaluator or extend taxonomy aliases.
5. **Do not start Batch 2B** until remaining RED services have verified claims published.

## Commands

```bash
cd backend && .venv/bin/python3 -m pytest tests/ -q
cd .. && backend/.venv/bin/python3 scripts/evaluate_service_routing.py
backend/.venv/bin/python3 scripts/evaluate_batch01_e2e.py
backend/.venv/bin/python3 scripts/evaluate_batch02a_e2e.py
```
