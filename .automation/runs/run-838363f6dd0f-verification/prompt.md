# BDA Cloud Task — VERIFICATION

**Batch:** BATCH_13 (Judiciary / Legal / Courts)
**Run ID:** run-838363f6dd0f-verification

## Safety
- LOCAL_DEV_ONLY — deployment_allowed must remain false
- Do NOT deploy, merge to main, or use external paid AI APIs
- Never publish UNVERIFIED/CONFLICTING claims as authoritative
- Write validated result.json — do not mutate project_state.json directly

## Required outputs
- `data/research/verification/batch-13-judiciary/claims_verification.json`
- `data/research/verification/batch-13-judiciary/summary.json`
- `.automation/runs/run-838363f6dd0f-verification/result.json`

## Context
```json
{
  "batch": {
    "batch_id": "BATCH_13",
    "slug": "batch-13-judiciary",
    "name": "Judiciary / Legal / Courts",
    "status": "IN_PROGRESS",
    "service_ids": [
      "judiciary-case-status-tracking",
      "judiciary-supreme-court-certified-copy",
      "judiciary-supreme-court-e-filing",
      "judiciary-virtual-court-services",
      "legal-aid-district-helpline-16430",
      "legal-aid-government-service",
      "legal-aid-helpline-16699",
      "legal-aid-online-application",
      "legal-aid-panel-lawyer-list"
    ],
    "service_count": 9,
    "phases_completed": [
      "RESEARCH"
    ]
  },
  "phase": "VERIFICATION",
  "run_id": "run-838363f6dd0f-verification",
  "service_ids": [
    "judiciary-case-status-tracking",
    "judiciary-supreme-court-certified-copy",
    "judiciary-supreme-court-e-filing",
    "judiciary-virtual-court-services",
    "legal-aid-district-helpline-16430",
    "legal-aid-government-service",
    "legal-aid-helpline-16699",
    "legal-aid-online-application",
    "legal-aid-panel-lawyer-list"
  ],
  "gaps": [
    {
      "gap_id": "gap-judiciary-case-status-tracking-fee-unverified",
      "service_id": "judiciary-case-status-tracking",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Court Case Status Tracking.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-judiciary-case-status-tracking-documents-unverified",
      "service_id": "judiciary-case-status-tracking",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Court Case Status Tracking.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-judiciary-supreme-court-certified-copy-fee-unverified",
      "service_id": "judiciary-supreme-court-certified-copy",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Supreme Court Certified Copy of Judgment/Order.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-judiciary-supreme-court-certified-copy-documents-unverified",
      "service_id": "judiciary-supreme-court-certified-copy",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Supreme Court Certified Copy of Judgment/Order.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-judiciary-supreme-court-e-filing-fee-unverified",
      "service_id": "judiciary-supreme-court-e-filing",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Supreme Court e-Filing (Lawyers Panel).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-judiciary-supreme-court-e-filing-documents-unverified",
      "service_id": "judiciary-supreme-court-e-filing",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Supreme Court e-Filing (Lawyers Panel).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-judiciary-virtual-court-services-fee-unverified",
      "service_id": "judiciary-virtual-court-services",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Virtual Court Services.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-judiciary-virtual-court-services-documents-unverified",
      "service_id": "judiciary-virtual-court-services",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Virtual Court Services.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-legal-aid-district-helpline-16430-portal-unreachable",
      "service_id": "legal-aid-district-helpline-16430",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for District Legal Aid Toll-free Helpline (16430).",
      "severity": "MEDIUM",
      "url": "https://jamalpur.judiciary.gov.bd/en/menu/page/legal-aid-helpline"
    },
    {
      "gap_id": "gap-legal-aid-district-helpline-16430-fee-unverified",
      "service_id": "legal-aid-district-helpline-16430",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for District Legal Aid Toll-free Helpline (16430).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-legal-aid-district-helpline-16430-documents-unverified",
      "service_id": "legal-aid-district-helpline-16430",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for District Legal Aid Toll-free Helpline (16430).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-legal-aid-government-service-fee-unverified",
      "service_id": "legal-aid-government-service",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Government-funded Legal Aid Service.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-legal-aid-government-service-documents-unverified",
      "service_id": "legal-aid-government-service",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Government-funded Legal Aid Service.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-legal-aid-helpline-16699-fee-unverified",
      "service_id": "legal-aid-helpline-16699",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for National Legal Aid Helpline (16699).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-legal-aid-helpline-16699-documents-unverified",
      "service_id": "legal-aid-helpline-16699",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for National Legal Aid Helpline (16699).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-legal-aid-online-application-fee-unverified",
      "service_id": "legal-aid-online-application",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for National Legal Aid Online Application.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-legal-aid-online-application-documents-unverified",
      "service_id": "legal-aid-online-application",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for National Legal Aid Online Application.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-legal-aid-panel-lawyer-list-fee-unverified",
      "service_id": "legal-aid-panel-lawyer-list",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Panel Lawyer List (District Legal Aid).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-legal-aid-panel-lawyer-list-documents-unverified",
      "service_id": "legal-aid-panel-lawyer-list",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Panel Lawyer List (District Legal Aid).",
      "severity": "MEDIUM"
    }
  ],
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
Write machine-readable `.automation/runs/run-838363f6dd0f-verification/result.json` when complete.
