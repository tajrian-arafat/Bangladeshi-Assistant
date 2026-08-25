# BDA Cloud Task — E2E

**Batch:** BATCH_06 (Education)
**Run ID:** run-8fecce0cd898-e2e

## Safety
- LOCAL_DEV_ONLY — deployment_allowed must remain false
- Do NOT deploy, merge to main, or use external paid AI APIs
- Never publish UNVERIFIED/CONFLICTING claims as authoritative
- Write validated result.json — do not mutate project_state.json directly

## Required outputs
- `data/evaluation/batch-06-education/queries.json`
- `data/evaluation/batch-06-education/summary.json`
- `docs/evaluation/batch-06-education-publication-e2e.md`
- `.automation/runs/run-8fecce0cd898-e2e/result.json`

## Context
```json
{
  "batch": {
    "batch_id": "BATCH_06",
    "slug": "batch-06-education",
    "name": "Education",
    "status": "IN_PROGRESS",
    "service_ids": [
      "education-class-registration",
      "education-duplicate-certificate",
      "education-foreign-enrollment-permission",
      "education-foreign-equivalency",
      "education-hsc-certificate",
      "education-hsc-transcript",
      "education-registration-card-correction",
      "education-ssc-certificate",
      "education-ssc-hsc-result-verify",
      "education-ssc-transcript",
      "education-ugc-university-recognition"
    ],
    "service_count": 11,
    "phases_completed": [
      "RESEARCH",
      "VERIFICATION",
      "GAP_CLOSURE"
    ]
  },
  "phase": "E2E",
  "run_id": "run-8fecce0cd898-e2e",
  "service_ids": [
    "education-class-registration",
    "education-duplicate-certificate",
    "education-foreign-enrollment-permission",
    "education-foreign-equivalency",
    "education-hsc-certificate",
    "education-hsc-transcript",
    "education-registration-card-correction",
    "education-ssc-certificate",
    "education-ssc-hsc-result-verify",
    "education-ssc-transcript",
    "education-ugc-university-recognition"
  ],
  "gaps": [
    {
      "gap_id": "gap-education-class-registration-portal-unreachable",
      "service_id": "education-class-registration",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Class IX/XI Board Registration.",
      "severity": "MEDIUM",
      "url": "http://www.educationboard.gov.bd/sylhet/activities.php"
    },
    {
      "gap_id": "gap-education-class-registration-fee-unverified",
      "service_id": "education-class-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Class IX/XI Board Registration.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-education-class-registration-documents-unverified",
      "service_id": "education-class-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Class IX/XI Board Registration.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-education-duplicate-certificate-portal-unreachable",
      "service_id": "education-duplicate-certificate",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Duplicate SSC/HSC Certificate or Transcript.",
      "severity": "MEDIUM",
      "url": "http://www.educationboard.gov.bd/edb_rules_regulations_powers_duties_controller.php"
    },
    {
      "gap_id": "gap-education-duplicate-certificate-fee-unverified",
      "service_id": "education-duplicate-certificate",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Duplicate SSC/HSC Certificate or Transcript.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-education-duplicate-certificate-documents-unverified",
      "service_id": "education-duplicate-certificate",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Duplicate SSC/HSC Certificate or Transcript.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-education-foreign-enrollment-permission-portal-unreachable",
      "service_id": "education-foreign-enrollment-permission",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Permission for Class XI Enrollment (Foreign Qualification).",
      "severity": "MEDIUM",
      "url": "http://www.educationboard.gov.bd/dhaka/rules_business.php"
    },
    {
      "gap_id": "gap-education-foreign-enrollment-permission-fee-unverified",
      "service_id": "education-foreign-enrollment-permission",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Permission for Class XI Enrollment (Foreign Qualification).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-education-foreign-enrollment-permission-documents-unverified",
      "service_id": "education-foreign-enrollment-permission",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Permission for Class XI Enrollment (Foreign Qualification).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-education-foreign-equivalency-portal-unreachable",
      "service_id": "education-foreign-equivalency",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Foreign Qualification Equivalency.",
      "severity": "MEDIUM",
      "url": "http://www.educationboard.gov.bd/dhaka/rules_business.php"
    },
    {
      "gap_id": "gap-education-foreign-equivalency-fee-unverified",
      "service_id": "education-foreign-equivalency",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Foreign Qualification Equivalency.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-education-foreign-equivalency-documents-unverified",
      "service_id": "education-foreign-equivalency",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Foreign Qualification Equivalency.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-education-hsc-certificate-portal-unreachable",
      "service_id": "education-hsc-certificate",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for HSC Certificate Issuance.",
      "severity": "MEDIUM",
      "url": "http://www.educationboard.gov.bd/sylhet/activities.php"
    },
    {
      "gap_id": "gap-education-hsc-certificate-fee-unverified",
      "service_id": "education-hsc-certificate",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for HSC Certificate Issuance.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-education-hsc-certificate-documents-unverified",
      "service_id": "education-hsc-certificate",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for HSC Certificate Issuance.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-education-hsc-transcript-portal-unreachable",
      "service_id": "education-hsc-transcript",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for HSC Academic Transcript.",
      "severity": "MEDIUM",
      "url": "http://www.educationboard.gov.bd/sylhet/activities.php"
    },
    {
      "gap_id": "gap-education-hsc-transcript-fee-unverified",
      "service_id": "education-hsc-transcript",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for HSC Academic Transcript.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-education-hsc-transcript-documents-unverified",
      "service_id": "education-hsc-transcript",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for HSC Academic Transcript.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-education-registration-card-correction-portal-unreachable",
      "service_id": "education-registration-card-correction",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Registration Card Information Correction.",
      "severity": "MEDIUM",
      "url": "http://www.educationboard.gov.bd/dhaka/rules_business.php"
    },
    {
      "gap_id": "gap-education-registration-card-correction-fee-unverified",
      "service_id": "education-registration-card-correction",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Registration Card Information Correction.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-education-registration-card-correction-documents-unverified",
      "service_id": "education-registration-card-correction",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Registration Card Information Correction.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-education-ssc-certificate-portal-unreachable",
      "service_id": "education-ssc-certificate",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for SSC Certificate Issuance.",
      "severity": "MEDIUM",
      "url": "http://www.educationboard.gov.bd/sylhet/activities.php"
    },
    {
      "gap_id": "gap-education-ssc-certificate-fee-unverified",
      "service_id": "education-ssc-certificate",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for SSC Certificate Issuance.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-education-ssc-certificate-documents-unverified",
      "service_id": "education-ssc-certificate",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for SSC Certificate Issuance.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-education-ssc-hsc-result-verify-fee-unverified",
      "service_id": "education-ssc-hsc-result-verify",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for SSC/HSC Result Verification.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-education-ssc-hsc-result-verify-documents-unverified",
      "service_id": "education-ssc-hsc-result-verify",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for SSC/HSC Result Verification.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-education-ssc-transcript-portal-unreachable",
      "service_id": "education-ssc-transcript",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for SSC Academic Transcript.",
      "severity": "MEDIUM",
      "url": "http://www.educationboard.gov.bd/chittagong/general_program.php"
    },
    {
      "gap_id": "gap-education-ssc-transcript-fee-unverified",
      "service_id": "education-ssc-transcript",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for SSC Academic Transcript.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-education-ssc-transcript-documents-unverified",
      "service_id": "education-ssc-transcript",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for SSC Academic Transcript.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-education-ugc-university-recognition-portal-unreachable",
      "service_id": "education-ugc-university-recognition",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for UGC University/Institution Recognition Verification.",
      "severity": "MEDIUM",
      "url": "https://www.ugc.gov.bd/"
    },
    {
      "gap_id": "gap-education-ugc-university-recognition-fee-unverified",
      "service_id": "education-ugc-university-recognition",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for UGC University/Institution Recognition Verification.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-education-ugc-university-recognition-documents-unverified",
      "service_id": "education-ugc-university-recognition",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for UGC University/Institution Recognition Verification.",
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
Write machine-readable `.automation/runs/run-8fecce0cd898-e2e/result.json` when complete.
