# BDA Cloud Task — RESEARCH

**Batch:** BATCH_14 (Remaining Government / Public Services)
**Run ID:** run-c18a40f59d04-research

## Safety
- LOCAL_DEV_ONLY — deployment_allowed must remain false
- Do NOT deploy, merge to main, or use external paid AI APIs
- Never publish UNVERIFIED/CONFLICTING claims as authoritative
- Write validated result.json — do not mutate project_state.json directly

## Required outputs
- `data/research/raw/batch-14-remaining/scope.json`
- `data/research/raw/batch-14-remaining/services_index.json`
- `data/research/raw/batch-14-remaining/services/*.json`
- `data/research/raw/batch-14-remaining/claims.json`
- `data/research/raw/batch-14-remaining/sources.json`
- `data/research/raw/batch-14-remaining/conflicts.json`
- `data/research/raw/batch-14-remaining/knowledge_gaps.json`
- `data/research/raw/batch-14-remaining/metadata.json`
- `docs/research/batch-14-remaining-research.md`
- `.automation/runs/run-c18a40f59d04-research/result.json`

## Context
```json
{
  "batch": {
    "batch_id": "BATCH_14",
    "slug": "batch-14-remaining",
    "name": "Remaining Government / Public Services",
    "status": "IN_PROGRESS",
    "service_ids": [
      "bpdb-high-tension-connection",
      "bpdb-new-connection-general",
      "bpdb-online-bill",
      "btrc-dnams",
      "btrc-lims-license",
      "btrc-neir-device-registration",
      "btrc-neir-imei-check",
      "btrc-nid-sim-check",
      "civil-birth-registration-copy",
      "civil-birth-registration-duplicate-cancel",
      "civil-death-registration-copy",
      "civil-death-registration-correction",
      "civil-death-registration-duplicate-cancel",
      "civil-marriage-certificate-search",
      "desco-application-fee-payment",
      "desco-demand-note-payment",
      "desco-emergency-service",
      "desco-load-calculator",
      "desco-load-change",
      "desco-meter-information-submission",
      "desco-new-connection",
      "desco-ocsms-registration",
      "desco-solar-document-submission",
      "digital-centre-assisted-services",
      "digital-centre-entrepreneur-registration",
      "digital-centre-helpdesk",
      "digital-challan-treasury-payment",
      "digital-ekpay-government-payment",
      "digital-mygov-citizen-registration",
      "dm-committee-database",
      "dm-disaster-alert-app",
      "dm-egpp-plus-mis",
      "dm-emergency-operational-dashboard",
      "dm-lims-lightning",
      "dm-rapid-services-list",
      "dm-shelter-information-system",
      "dpdc-application-tracking",
      "dpdc-net-metering",
      "dpdc-new-connection",
      "dpdc-online-bill-payment",
      "dpdc-online-complaint",
      "dpdc-prepaid-recharge",
      "election-candidate-nomination",
      "env-ecc-certificate-verification",
      "env-ecc-entrepreneur-registration",
      "env-ecc-online-application",
      "environment-forest-clearance",
      "hajj-call-center",
      "hajj-pilgrim-search",
      "hajj-pre-registration",
      "housing-bhbfc-loan-application",
      "housing-cda-building-permit",
      "housing-nha-allotment-application",
      "housing-nha-citizen-charter",
      "housing-nha-projects",
      "housing-rajuk-construction-permit",
      "housing-rajuk-large-special-project",
      "housing-rajuk-occupancy-certificate",
      "housing-rajuk-planning-permit",
      "housing-rajuk-professional-registration",
      "identity-voter-slip-download",
      "licence-trade-local-government",
      "local-certificate-verify",
      "local-death-certificate-union",
      "local-marital-status-certificate",
      "local-nationality-certificate",
      "local-noc-certificate",
      "local-passport-attestation",
      "local-voter-transfer-attestation",
      "nid-card-info-correction",
      "nid-claim-account",
      "nid-combined-correction",
      "nid-download-copy",
      "nid-expatriate-registration",
      "nid-fee-calculator",
      "nid-new-voter-registration",
      "nid-online-account-registration",
      "nid-other-info-correction",
      "nid-photo-signature-appointment",
      "nid-reissue-lost",
      "nid-voter-area-change",
      "permits-fire-e-license",
      "permits-fire-noc-enoc",
      "permits-fire-safety-firm-registration",
      "permits-forest-timber-transit",
      "post-cash-card",
      "post-domestic-mail",
      "post-ems",
      "post-emts",
      "post-gep",
      "post-international-mail",
      "post-life-insurance",
      "post-mail-tracking",
      "post-money-order",
      "post-postage-calculator",
      "post-savings-bank",
      "post-savings-certificate",
      "post-speed-post",
      "railway-helpline-131",
      "railway-online-ticket",
      "railway-rail-sheba-app",
      "tax-challan-payment",
      "titas-domestic-gas-connection",
      "titas-industry-gas-connection",
      "wasa-application-tracking",
      "wasa-connection-enlargement",
      "wasa-line-shifting",
      "wasa-new-water-connection",
      "wasa-second-connection",
      "wasa-sewerage-connection",
      "wasa-temporary-connection"
    ],
    "service_count": 111,
    "phases_completed": []
  },
  "phase": "RESEARCH",
  "run_id": "run-c18a40f59d04-research",
  "service_ids": [
    "bpdb-high-tension-connection",
    "bpdb-new-connection-general",
    "bpdb-online-bill",
    "btrc-dnams",
    "btrc-lims-license",
    "btrc-neir-device-registration",
    "btrc-neir-imei-check",
    "btrc-nid-sim-check",
    "civil-birth-registration-copy",
    "civil-birth-registration-duplicate-cancel",
    "civil-death-registration-copy",
    "civil-death-registration-correction",
    "civil-death-registration-duplicate-cancel",
    "civil-marriage-certificate-search",
    "desco-application-fee-payment",
    "desco-demand-note-payment",
    "desco-emergency-service",
    "desco-load-calculator",
    "desco-load-change",
    "desco-meter-information-submission",
    "desco-new-connection",
    "desco-ocsms-registration",
    "desco-solar-document-submission",
    "digital-centre-assisted-services",
    "digital-centre-entrepreneur-registration",
    "digital-centre-helpdesk",
    "digital-challan-treasury-payment",
    "digital-ekpay-government-payment",
    "digital-mygov-citizen-registration",
    "dm-committee-database",
    "dm-disaster-alert-app",
    "dm-egpp-plus-mis",
    "dm-emergency-operational-dashboard",
    "dm-lims-lightning",
    "dm-rapid-services-list",
    "dm-shelter-information-system",
    "dpdc-application-tracking",
    "dpdc-net-metering",
    "dpdc-new-connection",
    "dpdc-online-bill-payment",
    "dpdc-online-complaint",
    "dpdc-prepaid-recharge",
    "election-candidate-nomination",
    "env-ecc-certificate-verification",
    "env-ecc-entrepreneur-registration",
    "env-ecc-online-application",
    "environment-forest-clearance",
    "hajj-call-center",
    "hajj-pilgrim-search",
    "hajj-pre-registration",
    "housing-bhbfc-loan-application",
    "housing-cda-building-permit",
    "housing-nha-allotment-application",
    "housing-nha-citizen-charter",
    "housing-nha-projects",
    "housing-rajuk-construction-permit",
    "housing-rajuk-large-special-project",
    "housing-rajuk-occupancy-certificate",
    "housing-rajuk-planning-permit",
    "housing-rajuk-professional-registration",
    "identity-voter-slip-download",
    "licence-trade-local-government",
    "local-certificate-verify",
    "local-death-certificate-union",
    "local-marital-status-certificate",
    "local-nationality-certificate",
    "local-noc-certificate",
    "local-passport-attestation",
    "local-voter-transfer-attestation",
    "nid-card-info-correction",
    "nid-claim-account",
    "nid-combined-correction",
    "nid-download-copy",
    "nid-expatriate-registration",
    "nid-fee-calculator",
    "nid-new-voter-registration",
    "nid-online-account-registration",
    "nid-other-info-correction",
    "nid-photo-signature-appointment",
    "nid-reissue-lost",
    "nid-voter-area-change",
    "permits-fire-e-license",
    "permits-fire-noc-enoc",
    "permits-fire-safety-firm-registration",
    "permits-forest-timber-transit",
    "post-cash-card",
    "post-domestic-mail",
    "post-ems",
    "post-emts",
    "post-gep",
    "post-international-mail",
    "post-life-insurance",
    "post-mail-tracking",
    "post-money-order",
    "post-postage-calculator",
    "post-savings-bank",
    "post-savings-certificate",
    "post-speed-post",
    "railway-helpline-131",
    "railway-online-ticket",
    "railway-rail-sheba-app",
    "tax-challan-payment",
    "titas-domestic-gas-connection",
    "titas-industry-gas-connection",
    "wasa-application-tracking",
    "wasa-connection-enlargement",
    "wasa-line-shifting",
    "wasa-new-water-connection",
    "wasa-second-connection",
    "wasa-sewerage-connection",
    "wasa-temporary-connection"
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
Write machine-readable `.automation/runs/run-c18a40f59d04-research/result.json` when complete.
