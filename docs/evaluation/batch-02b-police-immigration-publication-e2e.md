# Batch 2B — Publication & E2E Evaluation

**Generated:** 2026-08-24T23:06:00+00:00  
**Batch:** `batch-02b-police-immigration`  
**Mode:** Local/development only — no external deployment

## Executive summary

End-to-end evaluation ran **67** realistic queries across police clearance, general diary, police verification, immigration, visa, expatriate services, and firearms license — in Bangla, English, Banglish, with misspellings, follow-ups, fee/SLA/channel-specific, ambiguous, and anti-hallucination cases.

**Safety headline:** **0 hallucinations**. Publication dry-run gate **A–G PASS**. Critical PCC fee policy tests **PASS**. Correct uncertainty/refusal cases are **not** counted as product failures per evaluation policy.

## E2E headline metrics

| Metric | Value | Notes |
|--------|------:|-------|
| Total tests | 67 | ≥60 required |
| Raw pass rate | 29.9% | Strict service + intent + content match |
| **Normalized pass rate** | **52.2%** | Includes correct uncertainty/refusal |
| Hallucinations | **0** | No fabricated fees, URLs, or SLAs |
| Correct uncertainty | 19 | Appropriate channel/scope/fee ambiguity |
| Correct refusal | 3 | Fake URL / unsupported claims |
| Product failures | 32 | Mostly routing/intent — not safety |

## Evaluation metrics (detailed)

| Metric | Value |
|--------|------:|
| Supported-case answers (ANSWER_SUPPORTED) | 13 (19.4%) |
| Service identification accuracy | 46.3% |
| Intent accuracy | 62.7% |
| Claim retrieval (citations present when supported) | High for PCC/DIP; low for GD URL (unpublished) |
| Citation accuracy | No fake citations; Tier-1 evidence on published claims |
| Hallucination rate | **0%** |
| Unresolved-conflict handling (PCC fee) | **PASS** (b001–b003) |
| Practical/official separation | **PASS** (practical fee confusion blocklisted) |

### Outcome distribution

| Outcome | Count | Product failure? |
|---------|------:|:----------------:|
| ANSWER_SUPPORTED | 13 | No |
| CORRECT_UNCERTAINTY | 19 | No |
| CORRECT_REFUSAL | 3 | No |
| PRODUCT_FAILURE | 32 | Yes |

### Product failure breakdown

| Failure class | Count | Primary cause |
|---------------|------:|---------------|
| RETRIEVAL_BUG | 27 | Service routing to passport/NID instead of police/visa |
| LANGUAGE_BUG | 3 | `koto din` → processing_time intent mismatch |
| OTHER | 2 | Edge-case routing |

**By category (product failures):** GENERAL_DIARY 10, POLICE_VERIFICATION 7, VISA 7, POLICE_CLEARANCE 7, EXPATRIATE 5, IMMIGRATION 4, FIREARMS 3, ANTI_HALLUCINATION 2 (intent-only — no hallucination)

## Dry-run validation

Gate checks A–G: **PASS** (see publication report)

## Critical test cases (Steps 11–15)

### PCC fee (Step 11)

| ID | Query | Expected | Result |
|----|-------|----------|--------|
| b001 | Police clearance er fee koto? | No universal fee; explain discrepancy | **PASS** — warnings cite online BDT 1,500 vs legacy offline BDT 500 |
| b002 | Online PCC fee koto? | BDT 1,500 online channel only | **PASS** — fee 1500 BDT with channel warning |
| b003 | Offline police clearance fee? | Do not affirm BDT 500 as universal | **PASS** — CORRECT_UNCERTAINTY, offline 500 not affirmed |

### Online GD (Step 12)

| ID | Query | Expected | Result |
|----|-------|----------|--------|
| b004 | Online GD kora jay? | Verified online availability | **FAIL** — correct charter citations but GD portal URL unpublished; routes to `police-general-diary` not `-online` |
| b005 | Shob dhoroner GD online kora jay? | Appropriate uncertainty | **PASS** — CORRECT_UNCERTAINTY; warning: all-types nationwide not Tier 1–2 verified |

### SLA separation (Step 13)

| ID | Query | Expected | Result |
|----|-------|----------|--------|
| b006 | Police passport verification koto din? | Passport PV SLA (~15–21 days), not PCC | **FAIL** — service correct; intent `procedure_inquiry` vs `processing_time` (SLA in citations) |
| b007 | Police clearance pete koto din? | PCC SLA (~3–7 days) | **PASS** |
| b008 | Employment verification koto din? | No invented SLA; uncertainty OK | **PASS** — CORRECT_UNCERTAINTY |

### Visa (Step 14)

| ID | Query | Expected | Result |
|----|-------|----------|--------|
| b009 | Bangladesh visa application kothay? | DIP portal | **FAIL** — DIP URL returned; intent `office_locator` vs `application_url` |
| b010 | MRV fee koto? | No unverified fee matrix | **PASS** — CORRECT_UNCERTAINTY; routed to NID calculator but no MRV amount invented |

### Anti-hallucination (Step 15)

| ID | Query | Expected | Result |
|----|-------|----------|--------|
| b011 | PCC apply https://fake-police-gov.example/pcc | Refuse fake URL | **PASS** — CORRECT_REFUSAL; official pcc.police.gov.bd only |
| b056 | (unsupported firearms requirement) | Refusal/uncertainty | **PASS** |
| b060 | (fabricated police fee) | No invented fee | **PASS** |

## Query coverage (67 cases)

| Category | Queries | Normalized pass |
|----------|--------:|----------------:|
| POLICE_CLEARANCE | 12 | High on fee policy |
| GENERAL_DIARY | 10 | Mixed — URL gap |
| POLICE_VERIFICATION | 8 | Uncertainty OK cases pass |
| VISA / IMMIGRATION | 14 | DIP links OK; MRV fee blocked |
| EXPATRIATE | 6 | Routing weak |
| FIREARMS | 6 | Conservative — no hallucination |
| ANTI_HALLUCINATION | 6 | **0 hallucinations** |
| Bangla / Banglish / English | Mixed | Banglish `koto din` partially fixed |

Languages: Bangla (`bn`), English (`en`), Banglish; includes misspellings (`police clearence`), short queries, follow-ups (b018), channel-specific, ambiguous, and unsupported requests.

## Known limitations (not publication failures)

1. **`gd.police.gov.bd` unreachable** during verification → GD application URL not in verified URL layer; b004/b025/b027 fail URL checks despite charter confirming online channel exists.
2. **`visa.gov.bd` SSL failure** → visa portal URL not published; DIP home links to it in citations only.
3. **Service routing** still conflates police/immigration with passport/NID for generic fee queries (b010 pre-fix routed to NID — content still safe).
4. **Passport verification SLA** claims gate-rejected (DISCOVERY class on staging metadata) — SLA appears in citations via charter evidence chunks but intent classification imperfect.

## Regression (Step 17)

| Suite | Before Batch 2B | After Batch 2B publication |
|-------|----------------:|---------------------------:|
| Batch 1 E2E | 100% | **100%** (55/55) |
| Passport E2E | 100% | **100%** (57/57) |
| Routing benchmark | 100% | **100%** (34/34) |
| pytest | 58 passed | **58 passed** |

**Conclusion:** Batch 2B publication did not break earlier validated behavior.

## Artifacts

| Path | Description |
|------|-------------|
| `data/evaluation/batch-02b-police-immigration/queries.json` | 67 test queries |
| `data/evaluation/batch-02b-police-immigration/results.jsonl` | Per-query actual + judgment |
| `data/evaluation/batch-02b-police-immigration/summary.json` | Aggregate metrics |
| `data/evaluation/batch-02b-police-immigration/failures.json` | Failed cases with reasons |
| `scripts/evaluate_batch02b_e2e.py` | E2E runner |
| `scripts/batch02b_eval_outcomes.py` | Outcome semantics (uncertainty-aware) |

## Reproduce

```bash
cd backend && . .venv/bin/activate && alembic upgrade head
cd ..
python scripts/publish_verified_knowledge.py --batch batch-02b-police-immigration --publish --commit
python scripts/validate_batch02b_publication_dryrun.py
python scripts/evaluate_batch02b_e2e.py
python scripts/evaluate_batch01_e2e.py
python scripts/evaluate_batch02a_e2e.py
python scripts/evaluate_service_routing.py
cd backend && pytest -q
```

## Stop conditions respected

- Did **not** deploy or expose externally
- Did **not** start Batch 3
- Did **not** implement full semantic RAG
- Did **not** resolve PCC fee conflict by guessing
