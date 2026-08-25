# BDA Cloud Task — RESEARCH

**Batch:** BATCH_10 (Employment / Labour / Expatriate / Migration)
**Run ID:** run-107a9e6bea1a-research

## Safety
- LOCAL_DEV_ONLY — deployment_allowed must remain false
- Do NOT deploy, merge to main, or use external paid AI APIs
- Never publish UNVERIFIED/CONFLICTING claims as authoritative
- Write validated result.json — do not mutate project_state.json directly

## Required outputs
- `data/research/raw/batch-10-employment-migration/scope.json`
- `data/research/raw/batch-10-employment-migration/services_index.json`
- `data/research/raw/batch-10-employment-migration/services/*.json`
- `data/research/raw/batch-10-employment-migration/claims.json`
- `data/research/raw/batch-10-employment-migration/sources.json`
- `data/research/raw/batch-10-employment-migration/conflicts.json`
- `data/research/raw/batch-10-employment-migration/knowledge_gaps.json`
- `data/research/raw/batch-10-employment-migration/metadata.json`
- `docs/research/batch-10-employment-migration-research.md`
- `.automation/runs/run-107a9e6bea1a-research/result.json`

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
    "phases_completed": []
  },
  "phase": "RESEARCH",
  "run_id": "run-107a9e6bea1a-research",
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
Write machine-readable `.automation/runs/run-107a9e6bea1a-research/result.json` when complete.
