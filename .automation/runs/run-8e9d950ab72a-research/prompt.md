# BDA Cloud Task — RESEARCH

**Batch:** BATCH_05 (Land & Property Records)
**Run ID:** run-8e9d950ab72a-research

## Safety
- LOCAL_DEV_ONLY — deployment_allowed must remain false
- Do NOT deploy, merge to main, or use external paid AI APIs
- Never publish UNVERIFIED/CONFLICTING claims as authoritative
- Write validated result.json — do not mutate project_state.json directly

## Required outputs
- `data/research/raw/batch-05-land/scope.json`
- `data/research/raw/batch-05-land/services_index.json`
- `data/research/raw/batch-05-land/services/*.json`
- `data/research/raw/batch-05-land/claims.json`
- `data/research/raw/batch-05-land/sources.json`
- `data/research/raw/batch-05-land/conflicts.json`
- `data/research/raw/batch-05-land/knowledge_gaps.json`
- `data/research/raw/batch-05-land/metadata.json`
- `docs/research/batch-05-land-research.md`
- `.automation/runs/run-8e9d950ab72a-research/result.json`

## Context
```json
{
  "batch": {
    "batch_id": "BATCH_05",
    "slug": "batch-05-land",
    "name": "Land & Property Records",
    "status": "IN_PROGRESS",
    "service_ids": [
      "land-deed-registration",
      "land-dlrms-application-track",
      "land-khatian-certified-copy",
      "land-khatian-correction",
      "land-khatian-online-copy",
      "land-mortgage-info-search",
      "land-mouza-map",
      "land-mutation-apply",
      "land-mutation-dcr",
      "land-mutation-khatian-search",
      "land-mutation-review",
      "land-mutation-track",
      "land-partition-consolidation",
      "land-survey-khatian-search",
      "local-upazila-land-tax-payment"
    ],
    "service_count": 15,
    "phases_completed": []
  },
  "phase": "RESEARCH",
  "run_id": "run-8e9d950ab72a-research",
  "service_ids": [
    "land-deed-registration",
    "land-dlrms-application-track",
    "land-khatian-certified-copy",
    "land-khatian-correction",
    "land-khatian-online-copy",
    "land-mortgage-info-search",
    "land-mouza-map",
    "land-mutation-apply",
    "land-mutation-dcr",
    "land-mutation-khatian-search",
    "land-mutation-review",
    "land-mutation-track",
    "land-partition-consolidation",
    "land-survey-khatian-search",
    "local-upazila-land-tax-payment"
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
Write machine-readable `.automation/runs/run-8e9d950ab72a-research/result.json` when complete.
