# BDA Cloud Task — RESEARCH

**Batch:** BATCH_09 (Agriculture / Fisheries / Livestock)
**Run ID:** run-b05a68e7c01a-research

## Safety
- LOCAL_DEV_ONLY — deployment_allowed must remain false
- Do NOT deploy, merge to main, or use external paid AI APIs
- Never publish UNVERIFIED/CONFLICTING claims as authoritative
- Write validated result.json — do not mutate project_state.json directly

## Required outputs
- `data/research/raw/batch-09-agriculture/scope.json`
- `data/research/raw/batch-09-agriculture/services_index.json`
- `data/research/raw/batch-09-agriculture/services/*.json`
- `data/research/raw/batch-09-agriculture/claims.json`
- `data/research/raw/batch-09-agriculture/sources.json`
- `data/research/raw/batch-09-agriculture/conflicts.json`
- `data/research/raw/batch-09-agriculture/knowledge_gaps.json`
- `data/research/raw/batch-09-agriculture/metadata.json`
- `docs/research/batch-09-agriculture-research.md`
- `.automation/runs/run-b05a68e7c01a-research/result.json`

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
    "phases_completed": []
  },
  "phase": "RESEARCH",
  "run_id": "run-b05a68e7c01a-research",
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
Write machine-readable `.automation/runs/run-b05a68e7c01a-research/result.json` when complete.
