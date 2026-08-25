# BDA Cloud Task — RESEARCH

**Batch:** BATCH_12 (Local Government)
**Run ID:** run-986215983a04-research

## Safety
- LOCAL_DEV_ONLY — deployment_allowed must remain false
- Do NOT deploy, merge to main, or use external paid AI APIs
- Never publish UNVERIFIED/CONFLICTING claims as authoritative
- Write validated result.json — do not mutate project_state.json directly

## Required outputs
- `data/research/raw/batch-12-local-gov/scope.json`
- `data/research/raw/batch-12-local-gov/services_index.json`
- `data/research/raw/batch-12-local-gov/services/*.json`
- `data/research/raw/batch-12-local-gov/claims.json`
- `data/research/raw/batch-12-local-gov/sources.json`
- `data/research/raw/batch-12-local-gov/conflicts.json`
- `data/research/raw/batch-12-local-gov/knowledge_gaps.json`
- `data/research/raw/batch-12-local-gov/metadata.json`
- `docs/research/batch-12-local-gov-research.md`
- `.automation/runs/run-986215983a04-research/result.json`

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
    "phases_completed": []
  },
  "phase": "RESEARCH",
  "run_id": "run-986215983a04-research",
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
  "gaps": [],
  "conflicts": []
}
```

## Phase instructions
# Research phase prompt

Follow `docs/research/BATCH_RESEARCH_TEMPLATE.md` exactly.

## Goals
- Identify in-scope services from catalogue
- Search broadly; prioritize Tier 1–2 official sources
- Separate official / practical / discovery evidence
- Create atomic claims with provenance
- Record conflicts and knowledge gaps
- **Never publish**
- **Never mark VERIFIED** because a source merely exists

## Outputs
- `data/research/raw/<batch-slug>/services/*.json`
- `data/research/raw/<batch-slug>/claims.json`
- `data/research/raw/<batch-slug>/sources.json`
- `data/research/raw/<batch-slug>/conflicts.json`
- `data/research/raw/<batch-slug>/knowledge_gaps.json`

Write `result.json` when complete.


Follow docs/research/BATCH_RESEARCH_TEMPLATE.md for RESEARCH.
Write machine-readable `.automation/runs/run-986215983a04-research/result.json` when complete.
