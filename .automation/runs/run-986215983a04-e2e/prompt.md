# BDA Cloud Task — E2E

**Batch:** BATCH_12 (Local Government)
**Run ID:** run-986215983a04-e2e

## Safety
- LOCAL_DEV_ONLY — deployment_allowed must remain false
- Do NOT deploy, merge to main, or use external paid AI APIs
- Never publish UNVERIFIED/CONFLICTING claims as authoritative
- Write validated result.json — do not mutate project_state.json directly

## Required outputs
- `data/evaluation/batch-12-local-gov/queries.json`
- `data/evaluation/batch-12-local-gov/summary.json`
- `docs/evaluation/batch-12-local-gov-publication-e2e.md`
- `.automation/runs/run-986215983a04-e2e/result.json`

## Context
```json
{
  "batch": {
    "batch_id": "BATCH_12",
    "slug": "batch-12-local-gov",
    "name": "Local Government",
    "status": "IN_PROGRESS",
    "service_ids": [
      "dc-attestation-photocopy",
      "dc-citizen-charter-bagerhat",
      "dc-citizen-charter-comilla",
      "dc-citizen-charter-dhaka",
      "dc-citizen-charter-rajshahi",
      "dc-district-e-application",
      "dc-guardianship-certificate",
      "dc-nothi-citizen-application",
      "dc-revenue-branch-services",
      "local-holding-tax-payment",
      "local-unno-digital-upazila-services"
    ],
    "service_count": 11,
    "phases_completed": [
      "RESEARCH",
      "VERIFICATION",
      "GAP_CLOSURE"
    ]
  },
  "phase": "E2E",
  "run_id": "run-986215983a04-e2e",
  "service_ids": [
    "dc-attestation-photocopy",
    "dc-citizen-charter-bagerhat",
    "dc-citizen-charter-comilla",
    "dc-citizen-charter-dhaka",
    "dc-citizen-charter-rajshahi",
    "dc-district-e-application",
    "dc-guardianship-certificate",
    "dc-nothi-citizen-application",
    "dc-revenue-branch-services",
    "local-holding-tax-payment",
    "local-unno-digital-upazila-services"
  ],
  "gaps": [
    {
      "gap_id": "gap-dc-attestation-photocopy-portal-unreachable",
      "service_id": "dc-attestation-photocopy",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for DC Office Document Attestation/Photocopy Certification.",
      "severity": "MEDIUM",
      "url": "https://www.dhaka.gov.bd/en"
    },
    {
      "gap_id": "gap-dc-attestation-photocopy-fee-unverified",
      "service_id": "dc-attestation-photocopy",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for DC Office Document Attestation/Photocopy Certification.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-dc-attestation-photocopy-documents-unverified",
      "service_id": "dc-attestation-photocopy",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for DC Office Document Attestation/Photocopy Certification.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-dc-citizen-charter-bagerhat-portal-unreachable",
      "service_id": "dc-citizen-charter-bagerhat",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Bagerhat District Citizen Charter Services.",
      "severity": "MEDIUM",
      "url": "https://bagerhat.gov.bd/en"
    },
    {
      "gap_id": "gap-dc-citizen-charter-bagerhat-fee-unverified",
      "service_id": "dc-citizen-charter-bagerhat",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Bagerhat District Citizen Charter Services.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-dc-citizen-charter-bagerhat-documents-unverified",
      "service_id": "dc-citizen-charter-bagerhat",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Bagerhat District Citizen Charter Services.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-dc-citizen-charter-comilla-portal-unreachable",
      "service_id": "dc-citizen-charter-comilla",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Cumilla District Citizen Charter Services.",
      "severity": "MEDIUM",
      "url": "https://www.comilla.gov.bd/en"
    },
    {
      "gap_id": "gap-dc-citizen-charter-comilla-fee-unverified",
      "service_id": "dc-citizen-charter-comilla",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Cumilla District Citizen Charter Services.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-dc-citizen-charter-comilla-documents-unverified",
      "service_id": "dc-citizen-charter-comilla",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Cumilla District Citizen Charter Services.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-dc-citizen-charter-dhaka-portal-unreachable",
      "service_id": "dc-citizen-charter-dhaka",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Dhaka District Citizen Charter Services.",
      "severity": "MEDIUM",
      "url": "https://www.dhaka.gov.bd/en"
    },
    {
      "gap_id": "gap-dc-citizen-charter-dhaka-fee-unverified",
      "service_id": "dc-citizen-charter-dhaka",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Dhaka District Citizen Charter Services.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-dc-citizen-charter-dhaka-documents-unverified",
      "service_id": "dc-citizen-charter-dhaka",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Dhaka District Citizen Charter Services.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-dc-citizen-charter-rajshahi-portal-unreachable",
      "service_id": "dc-citizen-charter-rajshahi",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Rajshahi District Citizen Charter Services.",
      "severity": "MEDIUM",
      "url": "https://rajshahi.gov.bd/en"
    },
    {
      "gap_id": "gap-dc-citizen-charter-rajshahi-fee-unverified",
      "service_id": "dc-citizen-charter-rajshahi",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Rajshahi District Citizen Charter Services.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-dc-citizen-charter-rajshahi-documents-unverified",
      "service_id": "dc-citizen-charter-rajshahi",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Rajshahi District Citizen Charter Services.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-dc-district-e-application-portal-unreachable",
      "service_id": "dc-district-e-application",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for District Online Forms Application.",
      "severity": "MEDIUM",
      "url": "http://online.forms.gov.bd/"
    },
    {
      "gap_id": "gap-dc-district-e-application-fee-unverified",
      "service_id": "dc-district-e-application",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for District Online Forms Application.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-dc-district-e-application-documents-unverified",
      "service_id": "dc-district-e-application",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for District Online Forms Application.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-dc-guardianship-certificate-portal-unreachable",
      "service_id": "dc-guardianship-certificate",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Guardianship Certificate (DC Office).",
      "severity": "MEDIUM",
      "url": "https://www.dhaka.gov.bd/en"
    },
    {
      "gap_id": "gap-dc-guardianship-certificate-fee-unverified",
      "service_id": "dc-guardianship-certificate",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Guardianship Certificate (DC Office).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-dc-guardianship-certificate-documents-unverified",
      "service_id": "dc-guardianship-certificate",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Guardianship Certificate (DC Office).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-dc-nothi-citizen-application-portal-unreachable",
      "service_id": "dc-nothi-citizen-application",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Nothi Citizen Application (District/DC Office).",
      "severity": "MEDIUM",
      "url": "http://nothi.gov.bd/dak_nagoriks/NagorikAbedon"
    },
    {
      "gap_id": "gap-dc-nothi-citizen-application-fee-unverified",
      "service_id": "dc-nothi-citizen-application",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Nothi Citizen Application (District/DC Office).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-dc-nothi-citizen-application-documents-unverified",
      "service_id": "dc-nothi-citizen-application",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Nothi Citizen Application (District/DC Office).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-dc-revenue-branch-services-portal-unreachable",
      "service_id": "dc-revenue-branch-services",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for DC Office Revenue Branch Services.",
      "severity": "MEDIUM",
      "url": "http://file-dhaka.portal.gov.bd/uploads/c744821c-aa9f-44f9-a403-07fc560350c2/61d/d71/949/61dd71949329c483376321.pdf"
    },
    {
      "gap_id": "gap-dc-revenue-branch-services-fee-unverified",
      "service_id": "dc-revenue-branch-services",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for DC Office Revenue Branch Services.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-dc-revenue-branch-services-documents-unverified",
      "service_id": "dc-revenue-branch-services",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for DC Office Revenue Branch Services.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-local-holding-tax-payment-portal-unreachable",
      "service_id": "local-holding-tax-payment",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Local Government Holding Tax Payment.",
      "severity": "MEDIUM",
      "url": "https://dncc.gov.bd/"
    },
    {
      "gap_id": "gap-local-holding-tax-payment-fee-unverified",
      "service_id": "local-holding-tax-payment",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Local Government Holding Tax Payment.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-local-holding-tax-payment-documents-unverified",
      "service_id": "local-holding-tax-payment",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Local Government Holding Tax Payment.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-local-unno-digital-upazila-services-official-url",
      "service_id": "local-unno-digital-upazila-services",
      "gap_type": "OFFICIAL_URL_MISSING",
      "description": "No reachable official URL confirmed for Upazila Nirbahi Officer (UNO) Digital Citizen Services.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-local-unno-digital-upazila-services-fee-unverified",
      "service_id": "local-unno-digital-upazila-services",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Upazila Nirbahi Officer (UNO) Digital Citizen Services.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-local-unno-digital-upazila-services-documents-unverified",
      "service_id": "local-unno-digital-upazila-services",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Upazila Nirbahi Officer (UNO) Digital Citizen Services.",
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
Write machine-readable `.automation/runs/run-986215983a04-e2e/result.json` when complete.
