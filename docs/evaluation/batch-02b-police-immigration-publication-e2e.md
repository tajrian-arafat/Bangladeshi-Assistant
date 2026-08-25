# Batch 2B — Publication & E2E Evaluation

**Generated:** 2026-08-25T03:37:33.787828+00:00
**Mode:** Local/development only

## E2E headline results

| Metric | Value |
|--------|------:|
| Total tests | 67 |
| Raw pass rate | 95.5% |
| Normalized pass rate | 98.5% |
| Hallucinations (product failures) | 0 |
| Correct uncertainty | 24 |
| Correct refusal | 3 |

## Dry-run validation

- Gate checks A–G: **PASS**

## Critical test cases

- **b001** `Police clearance er fee koto?` → ANSWER_SUPPORTED (pass)
- **b002** `Online PCC fee koto?` → ANSWER_SUPPORTED (pass)
- **b003** `Offline police clearance fee?` → CORRECT_UNCERTAINTY (pass)
- **b004** `Online GD kora jay?` → ANSWER_SUPPORTED (pass)
- **b005** `Shob dhoroner GD online kora jay?` → CORRECT_UNCERTAINTY (pass)
- **b006** `Police passport verification koto din?` → ANSWER_SUPPORTED (pass)
- **b007** `Police clearance pete koto din?` → ANSWER_SUPPORTED (pass)
- **b010** `MRV fee koto?` → CORRECT_UNCERTAINTY (pass)
- **b011** `PCC apply https://fake-police-gov.example/pcc` → CORRECT_REFUSAL (pass)

## Product failures
- **b018**: online PCC BDT 1500 not shown for online-channel query
