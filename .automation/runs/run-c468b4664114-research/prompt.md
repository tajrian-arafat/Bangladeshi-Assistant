# BDA Cloud Task — RESEARCH

**Batch:** BATCH_11 (Business / Trade / Industry / Professional)
**Run ID:** run-c468b4664114-research

## Safety
- LOCAL_DEV_ONLY — deployment_allowed must remain false
- Do NOT deploy, merge to main, or use external paid AI APIs
- Never publish UNVERIFIED/CONFLICTING claims as authoritative
- Write validated result.json — do not mutate project_state.json directly

## Required outputs
- `data/research/raw/batch-11-business-trade/scope.json`
- `data/research/raw/batch-11-business-trade/services_index.json`
- `data/research/raw/batch-11-business-trade/services/*.json`
- `data/research/raw/batch-11-business-trade/claims.json`
- `data/research/raw/batch-11-business-trade/sources.json`
- `data/research/raw/batch-11-business-trade/conflicts.json`
- `data/research/raw/batch-11-business-trade/knowledge_gaps.json`
- `data/research/raw/batch-11-business-trade/metadata.json`
- `docs/research/batch-11-business-trade-research.md`
- `.automation/runs/run-c468b4664114-research/result.json`

## Context
```json
{
  "batch": {
    "batch_id": "BATCH_11",
    "slug": "batch-11-business-trade",
    "name": "Business / Trade / Industry / Professional",
    "status": "IN_PROGRESS",
    "service_ids": [
      "bida-aftercare-services",
      "bida-commercial-office-services",
      "bida-invest-bangladesh-oss",
      "bida-irms-platform",
      "bida-osspid-registration",
      "bida-work-permit-security-clearance",
      "business-company-incorporation",
      "business-cooperative-society-registration",
      "business-entity-name-search",
      "business-foreign-company-registration",
      "business-name-clearance",
      "business-ngoab-ngo-registration",
      "business-partnership-registration",
      "business-rjsc-certified-copy",
      "business-society-registration",
      "business-trade-organization-registration",
      "professional-bar-council-enrolment",
      "professional-bmdc-doctor-registration",
      "professional-engineer-registration",
      "professional-nursing-council-registration",
      "professional-pharmacy-council-registration",
      "trade-bsti-standard-certification",
      "trade-dpd-patent-registration",
      "trade-dpd-trademark-registration",
      "trade-erc-registration",
      "trade-irc-erc-renewal",
      "trade-irc-registration"
    ],
    "service_count": 27,
    "phases_completed": []
  },
  "phase": "RESEARCH",
  "run_id": "run-c468b4664114-research",
  "service_ids": [
    "bida-aftercare-services",
    "bida-commercial-office-services",
    "bida-invest-bangladesh-oss",
    "bida-irms-platform",
    "bida-osspid-registration",
    "bida-work-permit-security-clearance",
    "business-company-incorporation",
    "business-cooperative-society-registration",
    "business-entity-name-search",
    "business-foreign-company-registration",
    "business-name-clearance",
    "business-ngoab-ngo-registration",
    "business-partnership-registration",
    "business-rjsc-certified-copy",
    "business-society-registration",
    "business-trade-organization-registration",
    "professional-bar-council-enrolment",
    "professional-bmdc-doctor-registration",
    "professional-engineer-registration",
    "professional-nursing-council-registration",
    "professional-pharmacy-council-registration",
    "trade-bsti-standard-certification",
    "trade-dpd-patent-registration",
    "trade-dpd-trademark-registration",
    "trade-erc-registration",
    "trade-irc-erc-renewal",
    "trade-irc-registration"
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
Write machine-readable `.automation/runs/run-c468b4664114-research/result.json` when complete.
