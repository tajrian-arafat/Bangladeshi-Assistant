# BDA Cloud Task — VERIFICATION

**Batch:** BATCH_05 (Land & Property Records)
**Run ID:** run-8e9d950ab72a-verification

## Safety
- LOCAL_DEV_ONLY — deployment_allowed must remain false
- Do NOT deploy, merge to main, or use external paid AI APIs
- Never publish UNVERIFIED/CONFLICTING claims as authoritative
- Write validated result.json — do not mutate project_state.json directly

## Required outputs
- `data/research/verification/batch-05-land/claims_verification.json`
- `data/research/verification/batch-05-land/summary.json`
- `.automation/runs/run-8e9d950ab72a-verification/result.json`

## Context
```json
{
  "batch": {
    "batch_id": "BATCH_05",
    "slug": "batch-05-land",
    "name": "Land & Property Records",
    "status": "IN_PROGRESS",
    "service_ids": [
      "land-deed-registration",
      "land-dlrms-application-track",
      "land-khatian-certified-copy",
      "land-khatian-correction",
      "land-khatian-online-copy",
      "land-mortgage-info-search",
      "land-mouza-map",
      "land-mutation-apply",
      "land-mutation-dcr",
      "land-mutation-khatian-search",
      "land-mutation-review",
      "land-mutation-track",
      "land-partition-consolidation",
      "land-survey-khatian-search",
      "local-upazila-land-tax-payment"
    ],
    "service_count": 15,
    "phases_completed": [
      "RESEARCH"
    ]
  },
  "phase": "VERIFICATION",
  "run_id": "run-8e9d950ab72a-verification",
  "service_ids": [
    "land-deed-registration",
    "land-dlrms-application-track",
    "land-khatian-certified-copy",
    "land-khatian-correction",
    "land-khatian-online-copy",
    "land-mortgage-info-search",
    "land-mouza-map",
    "land-mutation-apply",
    "land-mutation-dcr",
    "land-mutation-khatian-search",
    "land-mutation-review",
    "land-mutation-track",
    "land-partition-consolidation",
    "land-survey-khatian-search",
    "local-upazila-land-tax-payment"
  ],
  "gaps": [
    {
      "gap_id": "gap-land-deed-registration-portal-unreachable",
      "service_id": "land-deed-registration",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Deed Registration (Sub-Registry).",
      "severity": "MEDIUM",
      "url": "https://www.land.gov.bd/poripotro"
    },
    {
      "gap_id": "gap-land-deed-registration-fee-unverified",
      "service_id": "land-deed-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Deed Registration (Sub-Registry).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-land-deed-registration-documents-unverified",
      "service_id": "land-deed-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Deed Registration (Sub-Registry).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-land-dlrms-application-track-portal-unreachable",
      "service_id": "land-dlrms-application-track",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Land Record Application Tracking (DLRMS).",
      "severity": "MEDIUM",
      "url": "https://dlrms.land.gov.bd/application/track"
    },
    {
      "gap_id": "gap-land-dlrms-application-track-fee-unverified",
      "service_id": "land-dlrms-application-track",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Land Record Application Tracking (DLRMS).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-land-dlrms-application-track-documents-unverified",
      "service_id": "land-dlrms-application-track",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Land Record Application Tracking (DLRMS).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-land-khatian-certified-copy-portal-unreachable",
      "service_id": "land-khatian-certified-copy",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Certified Khatian Copy.",
      "severity": "MEDIUM",
      "url": "https://land.gov.bd/vumisheba-fee"
    },
    {
      "gap_id": "gap-land-khatian-certified-copy-fee-unverified",
      "service_id": "land-khatian-certified-copy",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Certified Khatian Copy.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-land-khatian-certified-copy-documents-unverified",
      "service_id": "land-khatian-certified-copy",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Certified Khatian Copy.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-land-khatian-correction-portal-unreachable",
      "service_id": "land-khatian-correction",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Khatian Record Correction.",
      "severity": "MEDIUM",
      "url": "https://land.gov.bd/vumisheba-fee"
    },
    {
      "gap_id": "gap-land-khatian-correction-fee-unverified",
      "service_id": "land-khatian-correction",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Khatian Record Correction.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-land-khatian-correction-documents-unverified",
      "service_id": "land-khatian-correction",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Khatian Record Correction.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-land-khatian-online-copy-portal-unreachable",
      "service_id": "land-khatian-online-copy",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Online Khatian Copy.",
      "severity": "MEDIUM",
      "url": "https://dlrms.land.gov.bd/"
    },
    {
      "gap_id": "gap-land-khatian-online-copy-fee-unverified",
      "service_id": "land-khatian-online-copy",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Online Khatian Copy.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-land-khatian-online-copy-documents-unverified",
      "service_id": "land-khatian-online-copy",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Online Khatian Copy.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-land-mortgage-info-search-portal-unreachable",
      "service_id": "land-mortgage-info-search",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Land Mortgage Information Search.",
      "severity": "MEDIUM",
      "url": "https://mutation.land.gov.bd/search-mortgage-info"
    },
    {
      "gap_id": "gap-land-mortgage-info-search-fee-unverified",
      "service_id": "land-mortgage-info-search",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Land Mortgage Information Search.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-land-mortgage-info-search-documents-unverified",
      "service_id": "land-mortgage-info-search",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Land Mortgage Information Search.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-land-mouza-map-portal-unreachable",
      "service_id": "land-mouza-map",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Mouza Map Request.",
      "severity": "MEDIUM",
      "url": "https://land.gov.bd/vumisheba-fee"
    },
    {
      "gap_id": "gap-land-mouza-map-fee-unverified",
      "service_id": "land-mouza-map",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Mouza Map Request.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-land-mouza-map-documents-unverified",
      "service_id": "land-mouza-map",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Mouza Map Request.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-land-mutation-apply-portal-unreachable",
      "service_id": "land-mutation-apply",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Land Mutation (Namjari).",
      "severity": "MEDIUM",
      "url": "https://mutation.land.gov.bd/"
    },
    {
      "gap_id": "gap-land-mutation-apply-fee-unverified",
      "service_id": "land-mutation-apply",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Land Mutation (Namjari).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-land-mutation-apply-documents-unverified",
      "service_id": "land-mutation-apply",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Land Mutation (Namjari).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-land-mutation-dcr-portal-unreachable",
      "service_id": "land-mutation-dcr",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Mutation DCR and Khatian Download.",
      "severity": "MEDIUM",
      "url": "https://mutation.land.gov.bd/namjari-steps"
    },
    {
      "gap_id": "gap-land-mutation-dcr-fee-unverified",
      "service_id": "land-mutation-dcr",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Mutation DCR and Khatian Download.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-land-mutation-dcr-documents-unverified",
      "service_id": "land-mutation-dcr",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Mutation DCR and Khatian Download.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-land-mutation-khatian-search-portal-unreachable",
      "service_id": "land-mutation-khatian-search",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Mutation Khatian Search.",
      "severity": "MEDIUM",
      "url": "https://dlrms.land.gov.bd/"
    },
    {
      "gap_id": "gap-land-mutation-khatian-search-fee-unverified",
      "service_id": "land-mutation-khatian-search",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Mutation Khatian Search.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-land-mutation-khatian-search-documents-unverified",
      "service_id": "land-mutation-khatian-search",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Mutation Khatian Search.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-land-mutation-review-portal-unreachable",
      "service_id": "land-mutation-review",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Mutation Review Application.",
      "severity": "MEDIUM",
      "url": "https://land.gov.bd/vumisheba-fee"
    },
    {
      "gap_id": "gap-land-mutation-review-fee-unverified",
      "service_id": "land-mutation-review",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Mutation Review Application.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-land-mutation-review-documents-unverified",
      "service_id": "land-mutation-review",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Mutation Review Application.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-land-mutation-track-portal-unreachable",
      "service_id": "land-mutation-track",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Mutation Application Tracking.",
      "severity": "MEDIUM",
      "url": "https://mutation.land.gov.bd/search-application"
    },
    {
      "gap_id": "gap-land-mutation-track-fee-unverified",
      "service_id": "land-mutation-track",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Mutation Application Tracking.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-land-mutation-track-documents-unverified",
      "service_id": "land-mutation-track",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Mutation Application Tracking.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-land-partition-consolidation-portal-unreachable",
      "service_id": "land-partition-consolidation",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Land Partition and Consolidation (Record Correction).",
      "severity": "MEDIUM",
      "url": "https://www.land.gov.bd/nagorik-subidha"
    },
    {
      "gap_id": "gap-land-partition-consolidation-fee-unverified",
      "service_id": "land-partition-consolidation",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Land Partition and Consolidation (Record Correction).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-land-partition-consolidation-documents-unverified",
      "service_id": "land-partition-consolidation",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Land Partition and Consolidation (Record Correction).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-land-survey-khatian-search-portal-unreachable",
      "service_id": "land-survey-khatian-search",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Survey Khatian Search.",
      "severity": "MEDIUM",
      "url": "https://dlrms.land.gov.bd/"
    },
    {
      "gap_id": "gap-land-survey-khatian-search-fee-unverified",
      "service_id": "land-survey-khatian-search",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Survey Khatian Search.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-land-survey-khatian-search-documents-unverified",
      "service_id": "land-survey-khatian-search",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Survey Khatian Search.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-local-upazila-land-tax-payment-official-url",
      "service_id": "local-upazila-land-tax-payment",
      "gap_type": "OFFICIAL_URL_MISSING",
      "description": "No reachable official URL confirmed for Upazila Land Development Tax Payment.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-local-upazila-land-tax-payment-fee-unverified",
      "service_id": "local-upazila-land-tax-payment",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Upazila Land Development Tax Payment.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-local-upazila-land-tax-payment-documents-unverified",
      "service_id": "local-upazila-land-tax-payment",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Upazila Land Development Tax Payment.",
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
Write machine-readable `.automation/runs/run-8e9d950ab72a-verification/result.json` when complete.
