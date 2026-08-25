# BDA Cloud Task — VERIFICATION

**Batch:** BATCH_04 (Tax / VAT / Customs)
**Run ID:** run-1cfd083e93d9-verification

## Safety
- LOCAL_DEV_ONLY — deployment_allowed must remain false
- Do NOT deploy, merge to main, or use external paid AI APIs
- Never publish UNVERIFIED/CONFLICTING claims as authoritative
- Write validated result.json — do not mutate project_state.json directly

## Required outputs
- `data/research/verification/batch-04-tax-vat-customs/claims_verification.json`
- `data/research/verification/batch-04-tax-vat-customs/summary.json`
- `.automation/runs/run-1cfd083e93d9-verification/result.json`

## Context
```json
{
  "batch": {
    "batch_id": "BATCH_04",
    "slug": "batch-04-tax-vat-customs",
    "name": "Tax / VAT / Customs",
    "status": "IN_PROGRESS",
    "service_ids": [
      "customs-asycuda-declaration",
      "customs-bond-up-application",
      "customs-import-export-control-licence",
      "tax-clearance-foreigners",
      "tax-etin-registration",
      "tax-income-return-file",
      "tax-income-tax-return-filing",
      "tax-source-tax-deduction-certificate",
      "vat-bin-registration",
      "vat-return-filing",
      "vat-turnover-enlistment"
    ],
    "service_count": 11,
    "phases_completed": [
      "RESEARCH"
    ]
  },
  "phase": "VERIFICATION",
  "run_id": "run-1cfd083e93d9-verification",
  "service_ids": [
    "customs-asycuda-declaration",
    "customs-bond-up-application",
    "customs-import-export-control-licence",
    "tax-clearance-foreigners",
    "tax-etin-registration",
    "tax-income-return-file",
    "tax-income-tax-return-filing",
    "tax-source-tax-deduction-certificate",
    "vat-bin-registration",
    "vat-return-filing",
    "vat-turnover-enlistment"
  ],
  "gaps": [],
  "conflicts": []
}
```

## Phase instructions
# Verification phase prompt

Verification is **independent** from research.

## Verdicts per claim
VERIFIED | PARTIALLY_VERIFIED | UNVERIFIED | CONFLICTING | OUTDATED | REJECTED

## High-risk claims require stronger evidence
- fees, mandatory documents, legal requirements, eligibility
- official URLs, payment instructions, deadlines, SLAs

## Outputs
- `data/research/verification/<batch-slug>/claims_verification.json`
- `data/research/verification/<batch-slug>/conflicts_resolution.json`
- `data/research/verification/<batch-slug>/knowledge_gaps.json`

Write `result.json` when complete.


Follow docs/research/BATCH_RESEARCH_TEMPLATE.md for RESEARCH.
Write machine-readable `.automation/runs/run-1cfd083e93d9-verification/result.json` when complete.
