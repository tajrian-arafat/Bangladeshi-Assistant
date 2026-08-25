# Automation Phase: RESEARCH

**Batch:** BATCH_03A

**Mode:** LOCAL_DEV_ONLY — do NOT deploy or publish without orchestrator gates.

## Context

```json
{
  "batch": {
    "batch_id": "BATCH_03A",
    "slug": "batch-03a-brta-driving-licence",
    "name": "BRTA Driving Licence",
    "status": "READY",
    "service_ids": [
      "brta-learner-driving-license",
      "brta-driving-license-renewal",
      "brta-duplicate-driving-license",
      "brta-smart-card-driving-license",
      "brta-driving-instructor-license",
      "brta-dctc-exam-result"
    ],
    "service_count": 6,
    "phases_completed": [],
    "authority_id": "brta",
    "category_id": "transport"
  },
  "template": "docs/research/BATCH_RESEARCH_TEMPLATE.md",
  "artifacts_created": [
    "data/research/raw/batch-03a-brta-driving-licence/scope.json",
    "data/research/raw/batch-03a-brta-driving-licence/services_index.json"
  ],
  "rules": [
    "Never publish during research",
    "Never mark VERIFIED without independent verification",
    "Use authority tiers",
    "Preserve provenance"
  ]
}
```

## Instructions

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


## Required output

Write machine-readable result to:
`.automation/runs/<run_id>/result.json`

Follow the phase result schema exactly. Do not change workflow state directly.
