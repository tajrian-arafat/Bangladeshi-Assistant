# BDA Cloud Task — E2E

**Batch:** BATCH_04 (Tax / VAT / Customs)
**Run ID:** run-1cfd083e93d9-e2e

## Safety
- LOCAL_DEV_ONLY — deployment_allowed must remain false
- Do NOT deploy, merge to main, or use external paid AI APIs
- Never publish UNVERIFIED/CONFLICTING claims as authoritative
- Write validated result.json — do not mutate project_state.json directly

## Required outputs
- `data/evaluation/batch-04-tax-vat-customs/queries.json`
- `data/evaluation/batch-04-tax-vat-customs/summary.json`
- `docs/evaluation/batch-04-tax-vat-customs-publication-e2e.md`
- `.automation/runs/run-1cfd083e93d9-e2e/result.json`

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
      "RESEARCH",
      "VERIFICATION"
    ]
  },
  "phase": "E2E",
  "run_id": "run-1cfd083e93d9-e2e",
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
  "gaps": [
    {
      "gap_id": "gap-customs-asycuda-declaration-fee-unverified",
      "service_id": "customs-asycuda-declaration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Customs Declaration (ASYCUDA World).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-customs-asycuda-declaration-documents-unverified",
      "service_id": "customs-asycuda-declaration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Customs Declaration (ASYCUDA World).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-customs-bond-up-application-fee-unverified",
      "service_id": "customs-bond-up-application",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Customs Bond Utilization Permit (UP) Application.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-customs-bond-up-application-documents-unverified",
      "service_id": "customs-bond-up-application",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Customs Bond Utilization Permit (UP) Application.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-customs-import-export-control-licence-fee-unverified",
      "service_id": "customs-import-export-control-licence",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Import/Export Control Licence.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-customs-import-export-control-licence-documents-unverified",
      "service_id": "customs-import-export-control-licence",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Import/Export Control Licence.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-tax-clearance-foreigners-fee-unverified",
      "service_id": "tax-clearance-foreigners",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Tax Clearance Certificate for Foreigners.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-tax-clearance-foreigners-documents-unverified",
      "service_id": "tax-clearance-foreigners",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Tax Clearance Certificate for Foreigners.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-tax-etin-registration-fee-unverified",
      "service_id": "tax-etin-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for e-TIN Registration.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-tax-etin-registration-documents-unverified",
      "service_id": "tax-etin-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for e-TIN Registration.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-tax-income-return-file-fee-unverified",
      "service_id": "tax-income-return-file",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Income Tax Return Filing (e-Return).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-tax-income-return-file-documents-unverified",
      "service_id": "tax-income-return-file",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Income Tax Return Filing (e-Return).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-tax-income-tax-return-filing-fee-unverified",
      "service_id": "tax-income-tax-return-filing",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Income Tax Return Filing.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-tax-income-tax-return-filing-documents-unverified",
      "service_id": "tax-income-tax-return-filing",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Income Tax Return Filing.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-tax-source-tax-deduction-certificate-fee-unverified",
      "service_id": "tax-source-tax-deduction-certificate",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Tax Deduction at Source Certificate.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-tax-source-tax-deduction-certificate-documents-unverified",
      "service_id": "tax-source-tax-deduction-certificate",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Tax Deduction at Source Certificate.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-vat-bin-registration-fee-unverified",
      "service_id": "vat-bin-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for VAT Registration (Business Identification Number).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-vat-bin-registration-documents-unverified",
      "service_id": "vat-bin-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for VAT Registration (Business Identification Number).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-vat-return-filing-fee-unverified",
      "service_id": "vat-return-filing",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for VAT Return Filing.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-vat-return-filing-documents-unverified",
      "service_id": "vat-return-filing",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for VAT Return Filing.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-vat-turnover-enlistment-fee-unverified",
      "service_id": "vat-turnover-enlistment",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Turnover Tax Enlistment.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-vat-turnover-enlistment-documents-unverified",
      "service_id": "vat-turnover-enlistment",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Turnover Tax Enlistment.",
      "severity": "MEDIUM"
    }
  ],
  "conflicts": []
}
```

## Phase instructions
# E2E evaluation prompt

Generate realistic user questions: Bangla, English, Banglish, typos, ambiguity, follow-ups, multi-turn.

Correct uncertainty/refusal is NOT failure. Wrong factual answers ARE failures.

Write eval artifacts under `data/evaluation/<batch-slug>/` and `result.json`.


Follow docs/research/BATCH_RESEARCH_TEMPLATE.md for RESEARCH.
Write machine-readable `.automation/runs/run-1cfd083e93d9-e2e/result.json` when complete.
