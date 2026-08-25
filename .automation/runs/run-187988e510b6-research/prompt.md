# BDA Cloud Task — RESEARCH

**Batch:** BATCH_07 (Health)
**Run ID:** run-187988e510b6-research

## Safety
- LOCAL_DEV_ONLY — deployment_allowed must remain false
- Do NOT deploy, merge to main, or use external paid AI APIs
- Never publish UNVERIFIED/CONFLICTING claims as authoritative
- Write validated result.json — do not mutate project_state.json directly

## Required outputs
- `data/research/raw/batch-07-health/scope.json`
- `data/research/raw/batch-07-health/services_index.json`
- `data/research/raw/batch-07-health/services/*.json`
- `data/research/raw/batch-07-health/claims.json`
- `data/research/raw/batch-07-health/sources.json`
- `data/research/raw/batch-07-health/conflicts.json`
- `data/research/raw/batch-07-health/knowledge_gaps.json`
- `data/research/raw/batch-07-health/metadata.json`
- `docs/research/batch-07-health-research.md`
- `.automation/runs/run-187988e510b6-research/result.json`

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
    "phases_completed": []
  },
  "phase": "RESEARCH",
  "run_id": "run-187988e510b6-research",
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
Write machine-readable `.automation/runs/run-187988e510b6-research/result.json` when complete.
