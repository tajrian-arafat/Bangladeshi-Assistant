# BDA Cloud Task — VERIFICATION

**Batch:** BATCH_09 (Agriculture / Fisheries / Livestock)
**Run ID:** run-b05a68e7c01a-gap_closure

## Safety
- LOCAL_DEV_ONLY — deployment_allowed must remain false
- Do NOT deploy, merge to main, or use external paid AI APIs
- Never publish UNVERIFIED/CONFLICTING claims as authoritative
- Write validated result.json — do not mutate project_state.json directly

## Required outputs
- `data/research/verification/batch-09-agriculture/claims_verification.json`
- `data/research/verification/batch-09-agriculture/summary.json`
- `.automation/runs/run-b05a68e7c01a-gap_closure/result.json`

## Context
```json
{
  "batch": {
    "batch_id": "BATCH_09",
    "slug": "batch-09-agriculture",
    "name": "Agriculture / Fisheries / Livestock",
    "status": "IN_PROGRESS",
    "service_ids": [
      "agri-bamis-farmer-registration",
      "agri-dae-district-extension",
      "agri-e-pesticide-prescription",
      "agri-farmer-digital-address",
      "agri-farmers-window",
      "agri-fsmms-farmer-registration",
      "agriculture-fisheries-fish-farm-registration",
      "agriculture-livestock-farm-registration",
      "fisheries-export-health-certificate",
      "fisheries-fioc-user-registration",
      "fisheries-import-noc",
      "fisheries-import-registration-certificate",
      "fisheries-import-release-order",
      "fisheries-processing-plant-license"
    ],
    "service_count": 14,
    "phases_completed": [
      "RESEARCH",
      "VERIFICATION"
    ]
  },
  "phase": "VERIFICATION",
  "run_id": "run-b05a68e7c01a-gap_closure",
  "service_ids": [
    "agri-bamis-farmer-registration",
    "agri-dae-district-extension",
    "agri-e-pesticide-prescription",
    "agri-farmer-digital-address",
    "agri-farmers-window",
    "agri-fsmms-farmer-registration",
    "agriculture-fisheries-fish-farm-registration",
    "agriculture-livestock-farm-registration",
    "fisheries-export-health-certificate",
    "fisheries-fioc-user-registration",
    "fisheries-import-noc",
    "fisheries-import-registration-certificate",
    "fisheries-import-release-order",
    "fisheries-processing-plant-license"
  ],
  "gaps": [
    {
      "gap_id": "gap-agri-bamis-farmer-registration-fee-unverified",
      "service_id": "agri-bamis-farmer-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for BAMIS Farmer Registration.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-agri-bamis-farmer-registration-documents-unverified",
      "service_id": "agri-bamis-farmer-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for BAMIS Farmer Registration.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-agri-dae-district-extension-portal-unreachable",
      "service_id": "agri-dae-district-extension",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for District Agricultural Extension Services.",
      "severity": "MEDIUM",
      "url": "https://dae.kishoreganj.gov.bd/en"
    },
    {
      "gap_id": "gap-agri-dae-district-extension-fee-unverified",
      "service_id": "agri-dae-district-extension",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for District Agricultural Extension Services.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-agri-dae-district-extension-documents-unverified",
      "service_id": "agri-dae-district-extension",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for District Agricultural Extension Services.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-agri-e-pesticide-prescription-portal-unreachable",
      "service_id": "agri-e-pesticide-prescription",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for E-Pesticide Prescription.",
      "severity": "MEDIUM",
      "url": "https://dae.kishoreganj.gov.bd/en"
    },
    {
      "gap_id": "gap-agri-e-pesticide-prescription-fee-unverified",
      "service_id": "agri-e-pesticide-prescription",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for E-Pesticide Prescription.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-agri-e-pesticide-prescription-documents-unverified",
      "service_id": "agri-e-pesticide-prescription",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for E-Pesticide Prescription.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-agri-farmer-digital-address-portal-unreachable",
      "service_id": "agri-farmer-digital-address",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Farmer Digital Address.",
      "severity": "MEDIUM",
      "url": "https://dae.kishoreganj.gov.bd/en"
    },
    {
      "gap_id": "gap-agri-farmer-digital-address-fee-unverified",
      "service_id": "agri-farmer-digital-address",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Farmer Digital Address.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-agri-farmer-digital-address-documents-unverified",
      "service_id": "agri-farmer-digital-address",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Farmer Digital Address.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-agri-farmers-window-fee-unverified",
      "service_id": "agri-farmers-window",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Farmer's Window (SACP/DAE).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-agri-farmers-window-documents-unverified",
      "service_id": "agri-farmers-window",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Farmer's Window (SACP/DAE).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-agri-fsmms-farmer-registration-fee-unverified",
      "service_id": "agri-fsmms-farmer-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Food Department Farmer/Mill Owner Registration (FSMMS).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-agri-fsmms-farmer-registration-documents-unverified",
      "service_id": "agri-fsmms-farmer-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Food Department Farmer/Mill Owner Registration (FSMMS).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-agriculture-fisheries-fish-farm-registration-portal-unreachable",
      "service_id": "agriculture-fisheries-fish-farm-registration",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Fish Farm Registration.",
      "severity": "MEDIUM",
      "url": "https://fisheries.gov.bd/"
    },
    {
      "gap_id": "gap-agriculture-fisheries-fish-farm-registration-fee-unverified",
      "service_id": "agriculture-fisheries-fish-farm-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Fish Farm Registration.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-agriculture-fisheries-fish-farm-registration-documents-unverified",
      "service_id": "agriculture-fisheries-fish-farm-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Fish Farm Registration.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-agriculture-livestock-farm-registration-portal-unreachable",
      "service_id": "agriculture-livestock-farm-registration",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Livestock Farm Registration (DLS).",
      "severity": "MEDIUM",
      "url": "https://dls.gov.bd/"
    },
    {
      "gap_id": "gap-agriculture-livestock-farm-registration-fee-unverified",
      "service_id": "agriculture-livestock-farm-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Livestock Farm Registration (DLS).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-agriculture-livestock-farm-registration-documents-unverified",
      "service_id": "agriculture-livestock-farm-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Livestock Farm Registration (DLS).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-fisheries-export-health-certificate-portal-unreachable",
      "service_id": "fisheries-export-health-certificate",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Fisheries Export Health Certificate.",
      "severity": "MEDIUM",
      "url": "https://www.ecertificate.fisheries.gov.bd/"
    },
    {
      "gap_id": "gap-fisheries-export-health-certificate-fee-unverified",
      "service_id": "fisheries-export-health-certificate",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Fisheries Export Health Certificate.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-fisheries-export-health-certificate-documents-unverified",
      "service_id": "fisheries-export-health-certificate",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Fisheries Export Health Certificate.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-fisheries-fioc-user-registration-portal-unreachable",
      "service_id": "fisheries-fioc-user-registration",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for FIQC e-Certification User Registration.",
      "severity": "MEDIUM",
      "url": "https://www.ecertificate.fisheries.gov.bd/"
    },
    {
      "gap_id": "gap-fisheries-fioc-user-registration-fee-unverified",
      "service_id": "fisheries-fioc-user-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for FIQC e-Certification User Registration.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-fisheries-fioc-user-registration-documents-unverified",
      "service_id": "fisheries-fioc-user-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for FIQC e-Certification User Registration.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-fisheries-import-noc-portal-unreachable",
      "service_id": "fisheries-import-noc",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Fisheries Import No Objection Certificate (NOC).",
      "severity": "MEDIUM",
      "url": "https://www.ecertificate.fisheries.gov.bd/"
    },
    {
      "gap_id": "gap-fisheries-import-noc-fee-unverified",
      "service_id": "fisheries-import-noc",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Fisheries Import No Objection Certificate (NOC).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-fisheries-import-noc-documents-unverified",
      "service_id": "fisheries-import-noc",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Fisheries Import No Objection Certificate (NOC).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-fisheries-import-registration-certificate-portal-unreachable",
      "service_id": "fisheries-import-registration-certificate",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Fisheries Import Registration Certificate.",
      "severity": "MEDIUM",
      "url": "https://www.ecertificate.fisheries.gov.bd/"
    },
    {
      "gap_id": "gap-fisheries-import-registration-certificate-fee-unverified",
      "service_id": "fisheries-import-registration-certificate",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Fisheries Import Registration Certificate.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-fisheries-import-registration-certificate-documents-unverified",
      "service_id": "fisheries-import-registration-certificate",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Fisheries Import Registration Certificate.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-fisheries-import-release-order-portal-unreachable",
      "service_id": "fisheries-import-release-order",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Fisheries Import Release Order.",
      "severity": "MEDIUM",
      "url": "https://www.ecertificate.fisheries.gov.bd/"
    },
    {
      "gap_id": "gap-fisheries-import-release-order-fee-unverified",
      "service_id": "fisheries-import-release-order",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Fisheries Import Release Order.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-fisheries-import-release-order-documents-unverified",
      "service_id": "fisheries-import-release-order",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Fisheries Import Release Order.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-fisheries-processing-plant-license-portal-unreachable",
      "service_id": "fisheries-processing-plant-license",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Fish Processing Plant Licence.",
      "severity": "MEDIUM",
      "url": "https://www.ecertificate.fisheries.gov.bd/"
    },
    {
      "gap_id": "gap-fisheries-processing-plant-license-fee-unverified",
      "service_id": "fisheries-processing-plant-license",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Fish Processing Plant Licence.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-fisheries-processing-plant-license-documents-unverified",
      "service_id": "fisheries-processing-plant-license",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Fish Processing Plant Licence.",
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
Write machine-readable `.automation/runs/run-b05a68e7c01a-gap_closure/result.json` when complete.
