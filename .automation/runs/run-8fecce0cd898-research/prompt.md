# BDA Cloud Task — RESEARCH

**Batch:** BATCH_06 (Education)
**Run ID:** run-8fecce0cd898-research

## Safety
- LOCAL_DEV_ONLY — deployment_allowed must remain false
- Do NOT deploy, merge to main, or use external paid AI APIs
- Never publish UNVERIFIED/CONFLICTING claims as authoritative
- Write validated result.json — do not mutate project_state.json directly

## Required outputs
- `data/research/raw/batch-06-education/scope.json`
- `data/research/raw/batch-06-education/services_index.json`
- `data/research/raw/batch-06-education/services/*.json`
- `data/research/raw/batch-06-education/claims.json`
- `data/research/raw/batch-06-education/sources.json`
- `data/research/raw/batch-06-education/conflicts.json`
- `data/research/raw/batch-06-education/knowledge_gaps.json`
- `data/research/raw/batch-06-education/metadata.json`
- `docs/research/batch-06-education-research.md`
- `.automation/runs/run-8fecce0cd898-research/result.json`

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
    "phases_completed": []
  },
  "phase": "RESEARCH",
  "run_id": "run-8fecce0cd898-research",
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
Write machine-readable `.automation/runs/run-8fecce0cd898-research/result.json` when complete.
