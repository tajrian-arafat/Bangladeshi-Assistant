# BDA Cloud Task — RESEARCH

**Batch:** BATCH_13 (Judiciary / Legal / Courts)
**Run ID:** run-838363f6dd0f-research

## Safety
- LOCAL_DEV_ONLY — deployment_allowed must remain false
- Do NOT deploy, merge to main, or use external paid AI APIs
- Never publish UNVERIFIED/CONFLICTING claims as authoritative
- Write validated result.json — do not mutate project_state.json directly

## Required outputs
- `data/research/raw/batch-13-judiciary/scope.json`
- `data/research/raw/batch-13-judiciary/services_index.json`
- `data/research/raw/batch-13-judiciary/services/*.json`
- `data/research/raw/batch-13-judiciary/claims.json`
- `data/research/raw/batch-13-judiciary/sources.json`
- `data/research/raw/batch-13-judiciary/conflicts.json`
- `data/research/raw/batch-13-judiciary/knowledge_gaps.json`
- `data/research/raw/batch-13-judiciary/metadata.json`
- `docs/research/batch-13-judiciary-research.md`
- `.automation/runs/run-838363f6dd0f-research/result.json`

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
    "phases_completed": []
  },
  "phase": "RESEARCH",
  "run_id": "run-838363f6dd0f-research",
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
Write machine-readable `.automation/runs/run-838363f6dd0f-research/result.json` when complete.
