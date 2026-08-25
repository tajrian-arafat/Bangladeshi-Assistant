# BDA Cloud Task — VERIFICATION

**Batch:** BATCH_10 (Employment / Labour / Expatriate / Migration)
**Run ID:** run-107a9e6bea1a-verification

## Safety
- LOCAL_DEV_ONLY — deployment_allowed must remain false
- Do NOT deploy, merge to main, or use external paid AI APIs
- Never publish UNVERIFIED/CONFLICTING claims as authoritative
- Write validated result.json — do not mutate project_state.json directly

## Required outputs
- `data/research/verification/batch-10-employment-migration/claims_verification.json`
- `data/research/verification/batch-10-employment-migration/summary.json`
- `.automation/runs/run-107a9e6bea1a-verification/result.json`

## Context
```json
{
  "batch": {
    "batch_id": "BATCH_10",
    "slug": "batch-10-employment-migration",
    "name": "Employment / Labour / Expatriate / Migration",
    "status": "IN_PROGRESS",
    "service_ids": [
      "employment-boesl-overseas-recruitment",
      "employment-labour-court-adr",
      "employment-trade-union-registration",
      "expatriate-bmet-training",
      "expatriate-emigration-clearance",
      "expatriate-recruiting-agent-verify",
      "expatriate-worker-registration",
      "migration-e-apostille",
      "mofa-csat",
      "mofa-document-attestation",
      "mofa-education-attestation-chain",
      "mofa-nv-loi-application"
    ],
    "service_count": 12,
    "phases_completed": [
      "RESEARCH"
    ]
  },
  "phase": "VERIFICATION",
  "run_id": "run-107a9e6bea1a-verification",
  "service_ids": [
    "employment-boesl-overseas-recruitment",
    "employment-labour-court-adr",
    "employment-trade-union-registration",
    "expatriate-bmet-training",
    "expatriate-emigration-clearance",
    "expatriate-recruiting-agent-verify",
    "expatriate-worker-registration",
    "migration-e-apostille",
    "mofa-csat",
    "mofa-document-attestation",
    "mofa-education-attestation-chain",
    "mofa-nv-loi-application"
  ],
  "gaps": [
    {
      "gap_id": "gap-employment-boesl-overseas-recruitment-fee-unverified",
      "service_id": "employment-boesl-overseas-recruitment",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for BOESL Overseas Job Seeker Registration.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-employment-boesl-overseas-recruitment-documents-unverified",
      "service_id": "employment-boesl-overseas-recruitment",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for BOESL Overseas Job Seeker Registration.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-employment-labour-court-adr-portal-unreachable",
      "service_id": "employment-labour-court-adr",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Labour Court Alternative Dispute Resolution.",
      "severity": "MEDIUM",
      "url": "https://mole.gov.bd/"
    },
    {
      "gap_id": "gap-employment-labour-court-adr-fee-unverified",
      "service_id": "employment-labour-court-adr",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Labour Court Alternative Dispute Resolution.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-employment-labour-court-adr-documents-unverified",
      "service_id": "employment-labour-court-adr",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Labour Court Alternative Dispute Resolution.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-employment-trade-union-registration-portal-unreachable",
      "service_id": "employment-trade-union-registration",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Trade Union Registration.",
      "severity": "MEDIUM",
      "url": "https://mole.gov.bd/"
    },
    {
      "gap_id": "gap-employment-trade-union-registration-fee-unverified",
      "service_id": "employment-trade-union-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Trade Union Registration.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-employment-trade-union-registration-documents-unverified",
      "service_id": "employment-trade-union-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Trade Union Registration.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-expatriate-bmet-training-portal-unreachable",
      "service_id": "expatriate-bmet-training",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for BMET Skill Development Training.",
      "severity": "MEDIUM",
      "url": "https://old.bmet.gov.bd/BMET/downloadAction"
    },
    {
      "gap_id": "gap-expatriate-bmet-training-fee-unverified",
      "service_id": "expatriate-bmet-training",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for BMET Skill Development Training.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-expatriate-bmet-training-documents-unverified",
      "service_id": "expatriate-bmet-training",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for BMET Skill Development Training.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-expatriate-emigration-clearance-portal-unreachable",
      "service_id": "expatriate-emigration-clearance",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Emigration Clearance for Overseas Employment.",
      "severity": "MEDIUM",
      "url": "https://oc.bmet.gov.bd/bmet_clr/rlEnrollment"
    },
    {
      "gap_id": "gap-expatriate-emigration-clearance-fee-unverified",
      "service_id": "expatriate-emigration-clearance",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Emigration Clearance for Overseas Employment.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-expatriate-emigration-clearance-documents-unverified",
      "service_id": "expatriate-emigration-clearance",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Emigration Clearance for Overseas Employment.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-expatriate-recruiting-agent-verify-portal-unreachable",
      "service_id": "expatriate-recruiting-agent-verify",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Recruiting Agent Verification.",
      "severity": "MEDIUM",
      "url": "https://old.bmet.gov.bd/BMET/agentlistpreview"
    },
    {
      "gap_id": "gap-expatriate-recruiting-agent-verify-fee-unverified",
      "service_id": "expatriate-recruiting-agent-verify",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Recruiting Agent Verification.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-expatriate-recruiting-agent-verify-documents-unverified",
      "service_id": "expatriate-recruiting-agent-verify",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Recruiting Agent Verification.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-expatriate-worker-registration-portal-unreachable",
      "service_id": "expatriate-worker-registration",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Overseas Worker Registration.",
      "severity": "MEDIUM",
      "url": "https://old.bmet.gov.bd/BMET/downloadAction"
    },
    {
      "gap_id": "gap-expatriate-worker-registration-fee-unverified",
      "service_id": "expatriate-worker-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Overseas Worker Registration.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-expatriate-worker-registration-documents-unverified",
      "service_id": "expatriate-worker-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Overseas Worker Registration.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-migration-e-apostille-portal-unreachable",
      "service_id": "migration-e-apostille",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for e-Apostille Document Authentication.",
      "severity": "MEDIUM",
      "url": "https://apostille.mygov.bd/"
    },
    {
      "gap_id": "gap-migration-e-apostille-fee-unverified",
      "service_id": "migration-e-apostille",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for e-Apostille Document Authentication.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-migration-e-apostille-documents-unverified",
      "service_id": "migration-e-apostille",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for e-Apostille Document Authentication.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-mofa-csat-fee-unverified",
      "service_id": "mofa-csat",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for MOFA Consular Service Appointment (CSAT).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-mofa-csat-documents-unverified",
      "service_id": "mofa-csat",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for MOFA Consular Service Appointment (CSAT).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-mofa-document-attestation-fee-unverified",
      "service_id": "mofa-document-attestation",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for MOFA Document Attestation.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-mofa-document-attestation-documents-unverified",
      "service_id": "mofa-document-attestation",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for MOFA Document Attestation.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-mofa-education-attestation-chain-portal-unreachable",
      "service_id": "mofa-education-attestation-chain",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Educational Certificate MOFA Attestation (via Ministry of Education).",
      "severity": "MEDIUM",
      "url": "https://istanbul.mofa.gov.bd/en/site/page/Document-attestation"
    },
    {
      "gap_id": "gap-mofa-education-attestation-chain-fee-unverified",
      "service_id": "mofa-education-attestation-chain",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Educational Certificate MOFA Attestation (via Ministry of Education).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-mofa-education-attestation-chain-documents-unverified",
      "service_id": "mofa-education-attestation-chain",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Educational Certificate MOFA Attestation (via Ministry of Education).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-mofa-nv-loi-application-fee-unverified",
      "service_id": "mofa-nv-loi-application",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Note Verbale and Letter of Introduction (LOI) Application.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-mofa-nv-loi-application-documents-unverified",
      "service_id": "mofa-nv-loi-application",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Note Verbale and Letter of Introduction (LOI) Application.",
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
Write machine-readable `.automation/runs/run-107a9e6bea1a-verification/result.json` when complete.
