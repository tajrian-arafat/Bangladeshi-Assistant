# BDA Cloud Task — E2E

**Batch:** BATCH_07 (Health)
**Run ID:** run-187988e510b6-e2e

## Safety
- LOCAL_DEV_ONLY — deployment_allowed must remain false
- Do NOT deploy, merge to main, or use external paid AI APIs
- Never publish UNVERIFIED/CONFLICTING claims as authoritative
- Write validated result.json — do not mutate project_state.json directly

## Required outputs
- `data/evaluation/batch-07-health/queries.json`
- `data/evaluation/batch-07-health/summary.json`
- `docs/evaluation/batch-07-health-publication-e2e.md`
- `.automation/runs/run-187988e510b6-e2e/result.json`

## Context
```json
{
  "batch": {
    "batch_id": "BATCH_07",
    "slug": "batch-07-health",
    "name": "Health",
    "status": "IN_PROGRESS",
    "service_ids": [
      "health-16263-telemedicine",
      "health-blood-bank-license",
      "health-bmdc-additional-qualification",
      "health-bmdc-eligibility-certificate",
      "health-bmdc-full-registration",
      "health-bmdc-registration-verify",
      "health-diagnostic-center-license",
      "health-facility-registry",
      "health-good-standing-certificate",
      "health-hospital-birth-notification",
      "health-immunization-card-mcv",
      "health-medical-assistant-registration",
      "health-private-clinic-license",
      "health-private-hospital-license"
    ],
    "service_count": 14,
    "phases_completed": [
      "RESEARCH",
      "VERIFICATION",
      "GAP_CLOSURE"
    ]
  },
  "phase": "E2E",
  "run_id": "run-187988e510b6-e2e",
  "service_ids": [
    "health-16263-telemedicine",
    "health-blood-bank-license",
    "health-bmdc-additional-qualification",
    "health-bmdc-eligibility-certificate",
    "health-bmdc-full-registration",
    "health-bmdc-registration-verify",
    "health-diagnostic-center-license",
    "health-facility-registry",
    "health-good-standing-certificate",
    "health-hospital-birth-notification",
    "health-immunization-card-mcv",
    "health-medical-assistant-registration",
    "health-private-clinic-license",
    "health-private-hospital-license"
  ],
  "gaps": [
    {
      "gap_id": "gap-health-16263-telemedicine-fee-unverified",
      "service_id": "health-16263-telemedicine",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for 16263 Telemedicine Health Advice.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-health-16263-telemedicine-documents-unverified",
      "service_id": "health-16263-telemedicine",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for 16263 Telemedicine Health Advice.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-health-blood-bank-license-portal-unreachable",
      "service_id": "health-blood-bank-license",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Blood Bank Licence.",
      "severity": "MEDIUM",
      "url": "https://git.dghs.gov.bd/riaz.somc/chatbot-knowledge/src/branch/main/PrivateHospitalRegistration.md"
    },
    {
      "gap_id": "gap-health-blood-bank-license-fee-unverified",
      "service_id": "health-blood-bank-license",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Blood Bank Licence.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-health-blood-bank-license-documents-unverified",
      "service_id": "health-blood-bank-license",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Blood Bank Licence.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-health-bmdc-additional-qualification-portal-unreachable",
      "service_id": "health-bmdc-additional-qualification",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for BMDC Additional Qualification Registration.",
      "severity": "MEDIUM",
      "url": "https://payment.bmdc.org.bd/home/page/form-list"
    },
    {
      "gap_id": "gap-health-bmdc-additional-qualification-fee-unverified",
      "service_id": "health-bmdc-additional-qualification",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for BMDC Additional Qualification Registration.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-health-bmdc-additional-qualification-documents-unverified",
      "service_id": "health-bmdc-additional-qualification",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for BMDC Additional Qualification Registration.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-health-bmdc-eligibility-certificate-portal-unreachable",
      "service_id": "health-bmdc-eligibility-certificate",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for BMDC Eligibility Certificate.",
      "severity": "MEDIUM",
      "url": "https://payment.bmdc.org.bd/home/page/form-list"
    },
    {
      "gap_id": "gap-health-bmdc-eligibility-certificate-fee-unverified",
      "service_id": "health-bmdc-eligibility-certificate",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for BMDC Eligibility Certificate.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-health-bmdc-eligibility-certificate-documents-unverified",
      "service_id": "health-bmdc-eligibility-certificate",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for BMDC Eligibility Certificate.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-health-bmdc-full-registration-portal-unreachable",
      "service_id": "health-bmdc-full-registration",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for BMDC Full Registration (MBBS/BDS).",
      "severity": "MEDIUM",
      "url": "https://payment.bmdc.org.bd/home/page/form-list"
    },
    {
      "gap_id": "gap-health-bmdc-full-registration-fee-unverified",
      "service_id": "health-bmdc-full-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for BMDC Full Registration (MBBS/BDS).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-health-bmdc-full-registration-documents-unverified",
      "service_id": "health-bmdc-full-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for BMDC Full Registration (MBBS/BDS).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-health-bmdc-registration-verify-portal-unreachable",
      "service_id": "health-bmdc-registration-verify",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for BMDC Registration Verification.",
      "severity": "MEDIUM",
      "url": "https://verify.bmdc.org.bd/"
    },
    {
      "gap_id": "gap-health-bmdc-registration-verify-fee-unverified",
      "service_id": "health-bmdc-registration-verify",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for BMDC Registration Verification.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-health-bmdc-registration-verify-documents-unverified",
      "service_id": "health-bmdc-registration-verify",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for BMDC Registration Verification.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-health-diagnostic-center-license-fee-unverified",
      "service_id": "health-diagnostic-center-license",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Diagnostic/Pathology Center Licence.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-health-diagnostic-center-license-documents-unverified",
      "service_id": "health-diagnostic-center-license",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Diagnostic/Pathology Center Licence.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-health-facility-registry-fee-unverified",
      "service_id": "health-facility-registry",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Health Facility Registry (HRIS).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-health-facility-registry-documents-unverified",
      "service_id": "health-facility-registry",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Health Facility Registry (HRIS).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-health-good-standing-certificate-portal-unreachable",
      "service_id": "health-good-standing-certificate",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Certificate of Good Standing (BMDC).",
      "severity": "MEDIUM",
      "url": "https://payment.bmdc.org.bd/home/page/form-list"
    },
    {
      "gap_id": "gap-health-good-standing-certificate-fee-unverified",
      "service_id": "health-good-standing-certificate",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Certificate of Good Standing (BMDC).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-health-good-standing-certificate-documents-unverified",
      "service_id": "health-good-standing-certificate",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Certificate of Good Standing (BMDC).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-health-hospital-birth-notification-fee-unverified",
      "service_id": "health-hospital-birth-notification",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Hospital Birth Notification (for BDRIS registration).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-health-hospital-birth-notification-documents-unverified",
      "service_id": "health-hospital-birth-notification",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Hospital Birth Notification (for BDRIS registration).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-health-immunization-card-mcv-fee-unverified",
      "service_id": "health-immunization-card-mcv",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Immunization / Vaccination Card (EPI).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-health-immunization-card-mcv-documents-unverified",
      "service_id": "health-immunization-card-mcv",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Immunization / Vaccination Card (EPI).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-health-medical-assistant-registration-portal-unreachable",
      "service_id": "health-medical-assistant-registration",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Medical Assistant BMDC Registration.",
      "severity": "MEDIUM",
      "url": "https://payment.bmdc.org.bd/home/page/form-list"
    },
    {
      "gap_id": "gap-health-medical-assistant-registration-fee-unverified",
      "service_id": "health-medical-assistant-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Medical Assistant BMDC Registration.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-health-medical-assistant-registration-documents-unverified",
      "service_id": "health-medical-assistant-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Medical Assistant BMDC Registration.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-health-private-clinic-license-portal-unreachable",
      "service_id": "health-private-clinic-license",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Private Clinic Licence.",
      "severity": "MEDIUM",
      "url": "https://hospitaldghs.gov.bd/"
    },
    {
      "gap_id": "gap-health-private-clinic-license-fee-unverified",
      "service_id": "health-private-clinic-license",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Private Clinic Licence.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-health-private-clinic-license-documents-unverified",
      "service_id": "health-private-clinic-license",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Private Clinic Licence.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-health-private-hospital-license-portal-unreachable",
      "service_id": "health-private-hospital-license",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Private Hospital Licence.",
      "severity": "MEDIUM",
      "url": "https://hospitaldghs.gov.bd/"
    },
    {
      "gap_id": "gap-health-private-hospital-license-fee-unverified",
      "service_id": "health-private-hospital-license",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Private Hospital Licence.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-health-private-hospital-license-documents-unverified",
      "service_id": "health-private-hospital-license",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Private Hospital Licence.",
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
Write machine-readable `.automation/runs/run-187988e510b6-e2e/result.json` when complete.
