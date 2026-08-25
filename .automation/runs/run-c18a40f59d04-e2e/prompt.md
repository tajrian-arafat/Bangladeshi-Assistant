# BDA Cloud Task — E2E

**Batch:** BATCH_14 (Remaining Government / Public Services)
**Run ID:** run-c18a40f59d04-e2e

## Safety
- LOCAL_DEV_ONLY — deployment_allowed must remain false
- Do NOT deploy, merge to main, or use external paid AI APIs
- Never publish UNVERIFIED/CONFLICTING claims as authoritative
- Write validated result.json — do not mutate project_state.json directly

## Required outputs
- `data/evaluation/batch-14-remaining/queries.json`
- `data/evaluation/batch-14-remaining/summary.json`
- `docs/evaluation/batch-14-remaining-publication-e2e.md`
- `.automation/runs/run-c18a40f59d04-e2e/result.json`

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
    "phases_completed": [
      "RESEARCH",
      "VERIFICATION",
      "GAP_CLOSURE"
    ]
  },
  "phase": "E2E",
  "run_id": "run-c18a40f59d04-e2e",
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
  "gaps": [
    {
      "gap_id": "gap-bpdb-high-tension-connection-portal-unreachable",
      "service_id": "bpdb-high-tension-connection",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for BPDB High Tension Connection Application.",
      "severity": "MEDIUM",
      "url": "https://bpdb.gov.bd/"
    },
    {
      "gap_id": "gap-bpdb-high-tension-connection-fee-unverified",
      "service_id": "bpdb-high-tension-connection",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for BPDB High Tension Connection Application.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-bpdb-high-tension-connection-documents-unverified",
      "service_id": "bpdb-high-tension-connection",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for BPDB High Tension Connection Application.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-bpdb-new-connection-general-portal-unreachable",
      "service_id": "bpdb-new-connection-general",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for BPDB New Electricity Connection (General Customer).",
      "severity": "MEDIUM",
      "url": "https://bpdb.gov.bd/pages/static-pages/6922dfe0933eb65569e24717"
    },
    {
      "gap_id": "gap-bpdb-new-connection-general-fee-unverified",
      "service_id": "bpdb-new-connection-general",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for BPDB New Electricity Connection (General Customer).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-bpdb-new-connection-general-documents-unverified",
      "service_id": "bpdb-new-connection-general",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for BPDB New Electricity Connection (General Customer).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-bpdb-online-bill-fee-unverified",
      "service_id": "bpdb-online-bill",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for BPDB Online Electricity Bill.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-bpdb-online-bill-documents-unverified",
      "service_id": "bpdb-online-bill",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for BPDB Online Electricity Bill.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-btrc-dnams-fee-unverified",
      "service_id": "btrc-dnams",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Demand Note Automation Management System (DNAMS).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-btrc-dnams-documents-unverified",
      "service_id": "btrc-dnams",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Demand Note Automation Management System (DNAMS).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-btrc-lims-license-fee-unverified",
      "service_id": "btrc-lims-license",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Telecom License and Registration (LIMS).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-btrc-lims-license-documents-unverified",
      "service_id": "btrc-lims-license",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Telecom License and Registration (LIMS).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-btrc-neir-device-registration-fee-unverified",
      "service_id": "btrc-neir-device-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Mobile Device Registration (NEIR).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-btrc-neir-device-registration-documents-unverified",
      "service_id": "btrc-neir-device-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Mobile Device Registration (NEIR).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-btrc-neir-imei-check-fee-unverified",
      "service_id": "btrc-neir-imei-check",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for NEIR IMEI Verification.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-btrc-neir-imei-check-documents-unverified",
      "service_id": "btrc-neir-imei-check",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for NEIR IMEI Verification.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-btrc-nid-sim-check-portal-unreachable",
      "service_id": "btrc-nid-sim-check",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for SIM Numbers Registered Under NID Check.",
      "severity": "MEDIUM",
      "url": "https://neir.btrc.gov.bd/homepage"
    },
    {
      "gap_id": "gap-btrc-nid-sim-check-fee-unverified",
      "service_id": "btrc-nid-sim-check",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for SIM Numbers Registered Under NID Check.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-btrc-nid-sim-check-documents-unverified",
      "service_id": "btrc-nid-sim-check",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for SIM Numbers Registered Under NID Check.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-civil-birth-registration-copy-portal-unreachable",
      "service_id": "civil-birth-registration-copy",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Birth Registration Copy (Reprint).",
      "severity": "MEDIUM",
      "url": "https://bdris.gov.bd/br/reprint/add"
    },
    {
      "gap_id": "gap-civil-birth-registration-copy-fee-unverified",
      "service_id": "civil-birth-registration-copy",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Birth Registration Copy (Reprint).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-civil-birth-registration-copy-documents-unverified",
      "service_id": "civil-birth-registration-copy",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Birth Registration Copy (Reprint).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-civil-birth-registration-duplicate-cancel-portal-unreachable",
      "service_id": "civil-birth-registration-duplicate-cancel",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Cancellation of Duplicate Birth Registrations.",
      "severity": "MEDIUM",
      "url": "https://bdris.gov.bd/application/print"
    },
    {
      "gap_id": "gap-civil-birth-registration-duplicate-cancel-fee-unverified",
      "service_id": "civil-birth-registration-duplicate-cancel",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Cancellation of Duplicate Birth Registrations.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-civil-birth-registration-duplicate-cancel-documents-unverified",
      "service_id": "civil-birth-registration-duplicate-cancel",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Cancellation of Duplicate Birth Registrations.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-civil-death-registration-copy-portal-unreachable",
      "service_id": "civil-death-registration-copy",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Death Registration Copy (Reprint).",
      "severity": "MEDIUM",
      "url": "https://bdris.gov.bd/dr/reprint/add"
    },
    {
      "gap_id": "gap-civil-death-registration-copy-fee-unverified",
      "service_id": "civil-death-registration-copy",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Death Registration Copy (Reprint).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-civil-death-registration-copy-documents-unverified",
      "service_id": "civil-death-registration-copy",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Death Registration Copy (Reprint).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-civil-death-registration-correction-portal-unreachable",
      "service_id": "civil-death-registration-correction",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Death Registration Information Correction.",
      "severity": "MEDIUM",
      "url": "https://bdris.gov.bd/dr/correction"
    },
    {
      "gap_id": "gap-civil-death-registration-correction-fee-unverified",
      "service_id": "civil-death-registration-correction",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Death Registration Information Correction.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-civil-death-registration-correction-documents-unverified",
      "service_id": "civil-death-registration-correction",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Death Registration Information Correction.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-civil-death-registration-duplicate-cancel-portal-unreachable",
      "service_id": "civil-death-registration-duplicate-cancel",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Cancellation of Duplicate Death Registrations.",
      "severity": "MEDIUM",
      "url": "https://bdris.gov.bd/application/print"
    },
    {
      "gap_id": "gap-civil-death-registration-duplicate-cancel-fee-unverified",
      "service_id": "civil-death-registration-duplicate-cancel",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Cancellation of Duplicate Death Registrations.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-civil-death-registration-duplicate-cancel-documents-unverified",
      "service_id": "civil-death-registration-duplicate-cancel",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Cancellation of Duplicate Death Registrations.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-civil-marriage-certificate-search-fee-unverified",
      "service_id": "civil-marriage-certificate-search",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Completed Marriage Certificate Search.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-civil-marriage-certificate-search-documents-unverified",
      "service_id": "civil-marriage-certificate-search",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Completed Marriage Certificate Search.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-desco-application-fee-payment-fee-unverified",
      "service_id": "desco-application-fee-payment",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for DESCO Application Fee Payment.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-desco-application-fee-payment-documents-unverified",
      "service_id": "desco-application-fee-payment",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for DESCO Application Fee Payment.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-desco-demand-note-payment-fee-unverified",
      "service_id": "desco-demand-note-payment",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for DESCO Demand Note Fee Payment.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-desco-demand-note-payment-documents-unverified",
      "service_id": "desco-demand-note-payment",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for DESCO Demand Note Fee Payment.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-desco-emergency-service-fee-unverified",
      "service_id": "desco-emergency-service",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for DESCO Power Interruption Emergency Service.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-desco-emergency-service-documents-unverified",
      "service_id": "desco-emergency-service",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for DESCO Power Interruption Emergency Service.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-desco-load-calculator-fee-unverified",
      "service_id": "desco-load-calculator",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for DESCO Load Calculator.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-desco-load-calculator-documents-unverified",
      "service_id": "desco-load-calculator",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for DESCO Load Calculator.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-desco-load-change-fee-unverified",
      "service_id": "desco-load-change",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for DESCO Load Change or Division.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-desco-load-change-documents-unverified",
      "service_id": "desco-load-change",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for DESCO Load Change or Division.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-desco-meter-information-submission-fee-unverified",
      "service_id": "desco-meter-information-submission",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for DESCO Meter Information Submission.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-desco-meter-information-submission-documents-unverified",
      "service_id": "desco-meter-information-submission",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for DESCO Meter Information Submission.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-desco-new-connection-fee-unverified",
      "service_id": "desco-new-connection",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for DESCO New Electricity Connection.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-desco-new-connection-documents-unverified",
      "service_id": "desco-new-connection",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for DESCO New Electricity Connection.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-desco-ocsms-registration-fee-unverified",
      "service_id": "desco-ocsms-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for DESCO OCSMS User Registration.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-desco-ocsms-registration-documents-unverified",
      "service_id": "desco-ocsms-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for DESCO OCSMS User Registration.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-desco-solar-document-submission-fee-unverified",
      "service_id": "desco-solar-document-submission",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for DESCO Solar Document Submission.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-desco-solar-document-submission-documents-unverified",
      "service_id": "desco-solar-document-submission",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for DESCO Solar Document Submission.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-digital-centre-assisted-services-fee-unverified",
      "service_id": "digital-centre-assisted-services",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Assisted Government Services via Digital Centres.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-digital-centre-assisted-services-documents-unverified",
      "service_id": "digital-centre-assisted-services",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Assisted Government Services via Digital Centres.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-digital-centre-entrepreneur-registration-fee-unverified",
      "service_id": "digital-centre-entrepreneur-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Digital Centre Entrepreneur Registration (Ekseba).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-digital-centre-entrepreneur-registration-documents-unverified",
      "service_id": "digital-centre-entrepreneur-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Digital Centre Entrepreneur Registration (Ekseba).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-digital-centre-helpdesk-fee-unverified",
      "service_id": "digital-centre-helpdesk",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Digital Centre Support Helpdesk.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-digital-centre-helpdesk-documents-unverified",
      "service_id": "digital-centre-helpdesk",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Digital Centre Support Helpdesk.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-digital-challan-treasury-payment-portal-unreachable",
      "service_id": "digital-challan-treasury-payment",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Treasury Challan Online Payment (aChallan).",
      "severity": "MEDIUM",
      "url": "https://www.achallan.gov.bd/"
    },
    {
      "gap_id": "gap-digital-challan-treasury-payment-fee-unverified",
      "service_id": "digital-challan-treasury-payment",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Treasury Challan Online Payment (aChallan).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-digital-challan-treasury-payment-documents-unverified",
      "service_id": "digital-challan-treasury-payment",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Treasury Challan Online Payment (aChallan).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-digital-ekpay-government-payment-fee-unverified",
      "service_id": "digital-ekpay-government-payment",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Ekpay Unified Government Payment Gateway.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-digital-ekpay-government-payment-documents-unverified",
      "service_id": "digital-ekpay-government-payment",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Ekpay Unified Government Payment Gateway.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-digital-mygov-citizen-registration-fee-unverified",
      "service_id": "digital-mygov-citizen-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for myGov Citizen Account Registration.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-digital-mygov-citizen-registration-documents-unverified",
      "service_id": "digital-mygov-citizen-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for myGov Citizen Account Registration.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-dm-committee-database-fee-unverified",
      "service_id": "dm-committee-database",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Disaster Management Committee Database.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-dm-committee-database-documents-unverified",
      "service_id": "dm-committee-database",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Disaster Management Committee Database.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-dm-disaster-alert-app-fee-unverified",
      "service_id": "dm-disaster-alert-app",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Disaster Alert for BD Mobile App.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-dm-disaster-alert-app-documents-unverified",
      "service_id": "dm-disaster-alert-app",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Disaster Alert for BD Mobile App.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-dm-egpp-plus-mis-fee-unverified",
      "service_id": "dm-egpp-plus-mis",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for EGPP+ Management Information System.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-dm-egpp-plus-mis-documents-unverified",
      "service_id": "dm-egpp-plus-mis",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for EGPP+ Management Information System.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-dm-emergency-operational-dashboard-fee-unverified",
      "service_id": "dm-emergency-operational-dashboard",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Emergency Operational Dashboard (EOD).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-dm-emergency-operational-dashboard-documents-unverified",
      "service_id": "dm-emergency-operational-dashboard",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Emergency Operational Dashboard (EOD).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-dm-lims-lightning-fee-unverified",
      "service_id": "dm-lims-lightning",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Lightning Information Management System (LIMS).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-dm-lims-lightning-documents-unverified",
      "service_id": "dm-lims-lightning",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Lightning Information Management System (LIMS).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-dm-rapid-services-list-fee-unverified",
      "service_id": "dm-rapid-services-list",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for DDM RAPID Platform Services.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-dm-rapid-services-list-documents-unverified",
      "service_id": "dm-rapid-services-list",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for DDM RAPID Platform Services.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-dm-shelter-information-system-fee-unverified",
      "service_id": "dm-shelter-information-system",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Cyclone Shelter Information Management System.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-dm-shelter-information-system-documents-unverified",
      "service_id": "dm-shelter-information-system",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Cyclone Shelter Information Management System.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-dpdc-application-tracking-fee-unverified",
      "service_id": "dpdc-application-tracking",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for DPDC Online Application Status Tracking.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-dpdc-application-tracking-documents-unverified",
      "service_id": "dpdc-application-tracking",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for DPDC Online Application Status Tracking.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-dpdc-net-metering-portal-unreachable",
      "service_id": "dpdc-net-metering",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for DPDC Net Metering Application.",
      "severity": "MEDIUM",
      "url": "https://onlineapplication.dpdc.org.bd/frm_Apply_NetMetering.php"
    },
    {
      "gap_id": "gap-dpdc-net-metering-fee-unverified",
      "service_id": "dpdc-net-metering",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for DPDC Net Metering Application.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-dpdc-net-metering-documents-unverified",
      "service_id": "dpdc-net-metering",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for DPDC Net Metering Application.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-dpdc-new-connection-fee-unverified",
      "service_id": "dpdc-new-connection",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for DPDC New Electricity Connection.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-dpdc-new-connection-documents-unverified",
      "service_id": "dpdc-new-connection",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for DPDC New Electricity Connection.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-dpdc-online-bill-payment-fee-unverified",
      "service_id": "dpdc-online-bill-payment",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for DPDC Online Bill Payment.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-dpdc-online-bill-payment-documents-unverified",
      "service_id": "dpdc-online-bill-payment",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for DPDC Online Bill Payment.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-dpdc-online-complaint-fee-unverified",
      "service_id": "dpdc-online-complaint",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for DPDC Online Complaint and Service Request.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-dpdc-online-complaint-documents-unverified",
      "service_id": "dpdc-online-complaint",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for DPDC Online Complaint and Service Request.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-dpdc-prepaid-recharge-fee-unverified",
      "service_id": "dpdc-prepaid-recharge",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for DPDC Prepaid Meter Online Recharge.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-dpdc-prepaid-recharge-documents-unverified",
      "service_id": "dpdc-prepaid-recharge",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for DPDC Prepaid Meter Online Recharge.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-election-candidate-nomination-portal-unreachable",
      "service_id": "election-candidate-nomination",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Election Candidate Nomination and Schedule Services.",
      "severity": "MEDIUM",
      "url": "https://www.ecs.gov.bd/"
    },
    {
      "gap_id": "gap-election-candidate-nomination-fee-unverified",
      "service_id": "election-candidate-nomination",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Election Candidate Nomination and Schedule Services.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-election-candidate-nomination-documents-unverified",
      "service_id": "election-candidate-nomination",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Election Candidate Nomination and Schedule Services.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-env-ecc-certificate-verification-fee-unverified",
      "service_id": "env-ecc-certificate-verification",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Environmental Clearance Certificate Verification.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-env-ecc-certificate-verification-documents-unverified",
      "service_id": "env-ecc-certificate-verification",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Environmental Clearance Certificate Verification.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-env-ecc-entrepreneur-registration-fee-unverified",
      "service_id": "env-ecc-entrepreneur-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for DoE ECC Entrepreneur Registration.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-env-ecc-entrepreneur-registration-documents-unverified",
      "service_id": "env-ecc-entrepreneur-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for DoE ECC Entrepreneur Registration.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-env-ecc-online-application-fee-unverified",
      "service_id": "env-ecc-online-application",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Environmental Clearance Certificate (ECC) Online Application.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-env-ecc-online-application-documents-unverified",
      "service_id": "env-ecc-online-application",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Environmental Clearance Certificate (ECC) Online Application.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-environment-forest-clearance-portal-unreachable",
      "service_id": "environment-forest-clearance",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Forest Clearance Certificate.",
      "severity": "MEDIUM",
      "url": "https://bforest.gov.bd/"
    },
    {
      "gap_id": "gap-environment-forest-clearance-fee-unverified",
      "service_id": "environment-forest-clearance",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Forest Clearance Certificate.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-environment-forest-clearance-documents-unverified",
      "service_id": "environment-forest-clearance",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Forest Clearance Certificate.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-hajj-call-center-portal-unreachable",
      "service_id": "hajj-call-center",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Hajj Call Center (16136).",
      "severity": "MEDIUM",
      "url": "https://pilgrim.hajj.gov.bd/"
    },
    {
      "gap_id": "gap-hajj-call-center-fee-unverified",
      "service_id": "hajj-call-center",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Hajj Call Center (16136).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-hajj-call-center-documents-unverified",
      "service_id": "hajj-call-center",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Hajj Call Center (16136).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-hajj-pilgrim-search-portal-unreachable",
      "service_id": "hajj-pilgrim-search",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Hajj Pilgrim Search and Status.",
      "severity": "MEDIUM",
      "url": "https://hajj.gov.bd/"
    },
    {
      "gap_id": "gap-hajj-pilgrim-search-fee-unverified",
      "service_id": "hajj-pilgrim-search",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Hajj Pilgrim Search and Status.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-hajj-pilgrim-search-documents-unverified",
      "service_id": "hajj-pilgrim-search",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Hajj Pilgrim Search and Status.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-hajj-pre-registration-portal-unreachable",
      "service_id": "hajj-pre-registration",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Hajj Pre-registration.",
      "severity": "MEDIUM",
      "url": "https://pilgrim.hajj.gov.bd/"
    },
    {
      "gap_id": "gap-hajj-pre-registration-fee-unverified",
      "service_id": "hajj-pre-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Hajj Pre-registration.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-hajj-pre-registration-documents-unverified",
      "service_id": "hajj-pre-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Hajj Pre-registration.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-housing-bhbfc-loan-application-portal-unreachable",
      "service_id": "housing-bhbfc-loan-application",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for House Building Loan (BHBFC).",
      "severity": "MEDIUM",
      "url": "https://bhbfc.khulna.gov.bd/en/site/page/%E0%A6%AC%E0%A6%BE%E0%A7%9C%E0%A6%BF-%E0%A6%A8%E0%A6%BF%E0%A6%B0%E0%A7%8D%E0%A6%AE%E0%A6%BE%E0%A6%A3-%E0%A6%8B%E0%A6%A3-%E0%A6%B8%E0%A6%82%E0%A6%95%E0%A7%8D%E0%A6%B0%E0%A6%BE%E0%A6%A8%E0%A7%8D%E0%A6%A4-%E0%A6%AA%E0%A6%A4%E0%A7%8D%E0%A6%B0"
    },
    {
      "gap_id": "gap-housing-bhbfc-loan-application-fee-unverified",
      "service_id": "housing-bhbfc-loan-application",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for House Building Loan (BHBFC).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-housing-bhbfc-loan-application-documents-unverified",
      "service_id": "housing-bhbfc-loan-application",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for House Building Loan (BHBFC).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-housing-cda-building-permit-portal-unreachable",
      "service_id": "housing-cda-building-permit",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Chattogram Development Authority Building Plan Approval.",
      "severity": "MEDIUM",
      "url": "https://cda.gov.bd/"
    },
    {
      "gap_id": "gap-housing-cda-building-permit-fee-unverified",
      "service_id": "housing-cda-building-permit",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Chattogram Development Authority Building Plan Approval.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-housing-cda-building-permit-documents-unverified",
      "service_id": "housing-cda-building-permit",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Chattogram Development Authority Building Plan Approval.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-housing-nha-allotment-application-portal-unreachable",
      "service_id": "housing-nha-allotment-application",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for National Housing Authority Flat Allotment Application.",
      "severity": "MEDIUM",
      "url": "https://nha.gov.bd/"
    },
    {
      "gap_id": "gap-housing-nha-allotment-application-fee-unverified",
      "service_id": "housing-nha-allotment-application",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for National Housing Authority Flat Allotment Application.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-housing-nha-allotment-application-documents-unverified",
      "service_id": "housing-nha-allotment-application",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for National Housing Authority Flat Allotment Application.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-housing-nha-citizen-charter-portal-unreachable",
      "service_id": "housing-nha-citizen-charter",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for NHA Citizen Charter Services.",
      "severity": "MEDIUM",
      "url": "https://nha.gov.bd/site/office_citizen_charter/7e6aa951-ece7-40fb-af0a-0abd5bd4ad3f/-"
    },
    {
      "gap_id": "gap-housing-nha-citizen-charter-fee-unverified",
      "service_id": "housing-nha-citizen-charter",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for NHA Citizen Charter Services.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-housing-nha-citizen-charter-documents-unverified",
      "service_id": "housing-nha-citizen-charter",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for NHA Citizen Charter Services.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-housing-nha-projects-portal-unreachable",
      "service_id": "housing-nha-projects",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for National Housing Authority (NHA) Projects.",
      "severity": "MEDIUM",
      "url": "https://nha.gov.bd/"
    },
    {
      "gap_id": "gap-housing-nha-projects-fee-unverified",
      "service_id": "housing-nha-projects",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for National Housing Authority (NHA) Projects.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-housing-nha-projects-documents-unverified",
      "service_id": "housing-nha-projects",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for National Housing Authority (NHA) Projects.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-housing-rajuk-construction-permit-portal-unreachable",
      "service_id": "housing-rajuk-construction-permit",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for RAJUK Construction Permit (CP).",
      "severity": "MEDIUM",
      "url": "https://ecps.gov.bd/permits/construction-permit/"
    },
    {
      "gap_id": "gap-housing-rajuk-construction-permit-fee-unverified",
      "service_id": "housing-rajuk-construction-permit",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for RAJUK Construction Permit (CP).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-housing-rajuk-construction-permit-documents-unverified",
      "service_id": "housing-rajuk-construction-permit",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for RAJUK Construction Permit (CP).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-housing-rajuk-large-special-project-portal-unreachable",
      "service_id": "housing-rajuk-large-special-project",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for RAJUK Large and Special Project Clearance (LSP).",
      "severity": "MEDIUM",
      "url": "https://ecps.gov.bd/"
    },
    {
      "gap_id": "gap-housing-rajuk-large-special-project-fee-unverified",
      "service_id": "housing-rajuk-large-special-project",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for RAJUK Large and Special Project Clearance (LSP).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-housing-rajuk-large-special-project-documents-unverified",
      "service_id": "housing-rajuk-large-special-project",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for RAJUK Large and Special Project Clearance (LSP).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-housing-rajuk-occupancy-certificate-portal-unreachable",
      "service_id": "housing-rajuk-occupancy-certificate",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for RAJUK Occupancy Certificate.",
      "severity": "MEDIUM",
      "url": "https://ecps.gov.bd/"
    },
    {
      "gap_id": "gap-housing-rajuk-occupancy-certificate-fee-unverified",
      "service_id": "housing-rajuk-occupancy-certificate",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for RAJUK Occupancy Certificate.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-housing-rajuk-occupancy-certificate-documents-unverified",
      "service_id": "housing-rajuk-occupancy-certificate",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for RAJUK Occupancy Certificate.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-housing-rajuk-planning-permit-portal-unreachable",
      "service_id": "housing-rajuk-planning-permit",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for RAJUK Planning Permit (PP).",
      "severity": "MEDIUM",
      "url": "https://ecps.gov.bd/"
    },
    {
      "gap_id": "gap-housing-rajuk-planning-permit-fee-unverified",
      "service_id": "housing-rajuk-planning-permit",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for RAJUK Planning Permit (PP).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-housing-rajuk-planning-permit-documents-unverified",
      "service_id": "housing-rajuk-planning-permit",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for RAJUK Planning Permit (PP).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-housing-rajuk-professional-registration-portal-unreachable",
      "service_id": "housing-rajuk-professional-registration",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for RAJUK Professional Registration (ECPS).",
      "severity": "MEDIUM",
      "url": "https://ecps.gov.bd/"
    },
    {
      "gap_id": "gap-housing-rajuk-professional-registration-fee-unverified",
      "service_id": "housing-rajuk-professional-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for RAJUK Professional Registration (ECPS).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-housing-rajuk-professional-registration-documents-unverified",
      "service_id": "housing-rajuk-professional-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for RAJUK Professional Registration (ECPS).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-identity-voter-slip-download-fee-unverified",
      "service_id": "identity-voter-slip-download",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Voter Information Slip Download.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-identity-voter-slip-download-documents-unverified",
      "service_id": "identity-voter-slip-download",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Voter Information Slip Download.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-licence-trade-local-government-portal-unreachable",
      "service_id": "licence-trade-local-government",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Local Government Trade Licence.",
      "severity": "MEDIUM",
      "url": "https://dncc.gov.bd/"
    },
    {
      "gap_id": "gap-licence-trade-local-government-fee-unverified",
      "service_id": "licence-trade-local-government",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Local Government Trade Licence.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-licence-trade-local-government-documents-unverified",
      "service_id": "licence-trade-local-government",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Local Government Trade Licence.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-local-certificate-verify-fee-unverified",
      "service_id": "local-certificate-verify",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Union Certificate Verification Search.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-local-certificate-verify-documents-unverified",
      "service_id": "local-certificate-verify",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Union Certificate Verification Search.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-local-death-certificate-union-fee-unverified",
      "service_id": "local-death-certificate-union",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Death Certificate (Union Parishad).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-local-death-certificate-union-documents-unverified",
      "service_id": "local-death-certificate-union",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Death Certificate (Union Parishad).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-local-marital-status-certificate-portal-unreachable",
      "service_id": "local-marital-status-certificate",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Marital Status Certificate.",
      "severity": "MEDIUM",
      "url": "https://www.palshaup.gov.bd/new/application/citizen/17"
    },
    {
      "gap_id": "gap-local-marital-status-certificate-fee-unverified",
      "service_id": "local-marital-status-certificate",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Marital Status Certificate.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-local-marital-status-certificate-documents-unverified",
      "service_id": "local-marital-status-certificate",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Marital Status Certificate.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-local-nationality-certificate-fee-unverified",
      "service_id": "local-nationality-certificate",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Nationality Certificate.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-local-nationality-certificate-documents-unverified",
      "service_id": "local-nationality-certificate",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Nationality Certificate.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-local-noc-certificate-fee-unverified",
      "service_id": "local-noc-certificate",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for No Objection Certificate (NOC).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-local-noc-certificate-documents-unverified",
      "service_id": "local-noc-certificate",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for No Objection Certificate (NOC).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-local-passport-attestation-fee-unverified",
      "service_id": "local-passport-attestation",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Passport-related Attestation (Union).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-local-passport-attestation-documents-unverified",
      "service_id": "local-passport-attestation",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Passport-related Attestation (Union).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-local-voter-transfer-attestation-fee-unverified",
      "service_id": "local-voter-transfer-attestation",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Voter Area Transfer Attestation.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-local-voter-transfer-attestation-documents-unverified",
      "service_id": "local-voter-transfer-attestation",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Voter Area Transfer Attestation.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-nid-card-info-correction-fee-unverified",
      "service_id": "nid-card-info-correction",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for NID Card Information Correction.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-nid-card-info-correction-documents-unverified",
      "service_id": "nid-card-info-correction",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for NID Card Information Correction.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-nid-claim-account-fee-unverified",
      "service_id": "nid-claim-account",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Claim NID Online Account.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-nid-claim-account-documents-unverified",
      "service_id": "nid-claim-account",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Claim NID Online Account.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-nid-combined-correction-fee-unverified",
      "service_id": "nid-combined-correction",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Combined NID and Other Information Correction.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-nid-combined-correction-documents-unverified",
      "service_id": "nid-combined-correction",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Combined NID and Other Information Correction.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-nid-download-copy-fee-unverified",
      "service_id": "nid-download-copy",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Download NID Card Copy.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-nid-download-copy-documents-unverified",
      "service_id": "nid-download-copy",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Download NID Card Copy.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-nid-expatriate-registration-fee-unverified",
      "service_id": "nid-expatriate-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Expatriate Bangladeshi NID Application.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-nid-expatriate-registration-documents-unverified",
      "service_id": "nid-expatriate-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Expatriate Bangladeshi NID Application.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-nid-fee-calculator-fee-unverified",
      "service_id": "nid-fee-calculator",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for NID Service Fee Calculator.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-nid-fee-calculator-documents-unverified",
      "service_id": "nid-fee-calculator",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for NID Service Fee Calculator.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-nid-new-voter-registration-fee-unverified",
      "service_id": "nid-new-voter-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for New Voter and National ID Registration.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-nid-new-voter-registration-documents-unverified",
      "service_id": "nid-new-voter-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for New Voter and National ID Registration.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-nid-online-account-registration-fee-unverified",
      "service_id": "nid-online-account-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Voter Online Account Registration.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-nid-online-account-registration-documents-unverified",
      "service_id": "nid-online-account-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Voter Online Account Registration.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-nid-other-info-correction-fee-unverified",
      "service_id": "nid-other-info-correction",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for NID Other Information Correction.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-nid-other-info-correction-documents-unverified",
      "service_id": "nid-other-info-correction",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for NID Other Information Correction.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-nid-photo-signature-appointment-fee-unverified",
      "service_id": "nid-photo-signature-appointment",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Photo or Signature Change Appointment.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-nid-photo-signature-appointment-documents-unverified",
      "service_id": "nid-photo-signature-appointment",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Photo or Signature Change Appointment.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-nid-reissue-lost-fee-unverified",
      "service_id": "nid-reissue-lost",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for NID Reissue for Lost or Damaged Card.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-nid-reissue-lost-documents-unverified",
      "service_id": "nid-reissue-lost",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for NID Reissue for Lost or Damaged Card.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-nid-voter-area-change-fee-unverified",
      "service_id": "nid-voter-area-change",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Voter Area or Address Change (Form 13).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-nid-voter-area-change-documents-unverified",
      "service_id": "nid-voter-area-change",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Voter Area or Address Change (Form 13).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-permits-fire-e-license-fee-unverified",
      "service_id": "permits-fire-e-license",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for e-Fire License Application.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-permits-fire-e-license-documents-unverified",
      "service_id": "permits-fire-e-license",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for e-Fire License Application.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-permits-fire-noc-enoc-fee-unverified",
      "service_id": "permits-fire-noc-enoc",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Fire Service No Objection Certificate (e-NOC).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-permits-fire-noc-enoc-documents-unverified",
      "service_id": "permits-fire-noc-enoc",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Fire Service No Objection Certificate (e-NOC).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-permits-fire-safety-firm-registration-fee-unverified",
      "service_id": "permits-fire-safety-firm-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Fire Safety Firm Registration.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-permits-fire-safety-firm-registration-documents-unverified",
      "service_id": "permits-fire-safety-firm-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Fire Safety Firm Registration.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-permits-forest-timber-transit-portal-unreachable",
      "service_id": "permits-forest-timber-transit",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Forest Timber Transit Permit.",
      "severity": "MEDIUM",
      "url": "https://bforest.gov.bd/"
    },
    {
      "gap_id": "gap-permits-forest-timber-transit-fee-unverified",
      "service_id": "permits-forest-timber-transit",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Forest Timber Transit Permit.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-permits-forest-timber-transit-documents-unverified",
      "service_id": "permits-forest-timber-transit",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Forest Timber Transit Permit.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-post-cash-card-portal-unreachable",
      "service_id": "post-cash-card",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Postal Cash Card.",
      "severity": "MEDIUM",
      "url": "https://bdpost.gov.bd/site/page/3f85b1c5-c356-47a9-b55c-de1938dc6c76/-"
    },
    {
      "gap_id": "gap-post-cash-card-fee-unverified",
      "service_id": "post-cash-card",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Postal Cash Card.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-post-cash-card-documents-unverified",
      "service_id": "post-cash-card",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Postal Cash Card.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-post-domestic-mail-portal-unreachable",
      "service_id": "post-domestic-mail",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Domestic Mail Service.",
      "severity": "MEDIUM",
      "url": "https://bdpost.gov.bd/site/page/921b98dc-cb15-4be4-8f0d-0125130c19f3/-"
    },
    {
      "gap_id": "gap-post-domestic-mail-fee-unverified",
      "service_id": "post-domestic-mail",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Domestic Mail Service.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-post-domestic-mail-documents-unverified",
      "service_id": "post-domestic-mail",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Domestic Mail Service.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-post-ems-portal-unreachable",
      "service_id": "post-ems",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Express Mail Service (EMS).",
      "severity": "MEDIUM",
      "url": "https://bdpost.gov.bd/site/page/a375dd34-3e14-4021-83f9-736d357d7eda/-"
    },
    {
      "gap_id": "gap-post-ems-fee-unverified",
      "service_id": "post-ems",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Express Mail Service (EMS).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-post-ems-documents-unverified",
      "service_id": "post-ems",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Express Mail Service (EMS).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-post-emts-portal-unreachable",
      "service_id": "post-emts",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Electronic Money Transfer Service (EMTS).",
      "severity": "MEDIUM",
      "url": "https://bdpost.portal.gov.bd/site/page/f51a53e6-926b-48a7-a927-8331e2f326ff/-"
    },
    {
      "gap_id": "gap-post-emts-fee-unverified",
      "service_id": "post-emts",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Electronic Money Transfer Service (EMTS).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-post-emts-documents-unverified",
      "service_id": "post-emts",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Electronic Money Transfer Service (EMTS).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-post-gep-portal-unreachable",
      "service_id": "post-gep",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Government Express Post (GEP).",
      "severity": "MEDIUM",
      "url": "https://bdpost.gov.bd/site/page/7eadb9ba-596e-482b-a1fe-712ec361a946/-"
    },
    {
      "gap_id": "gap-post-gep-fee-unverified",
      "service_id": "post-gep",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Government Express Post (GEP).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-post-gep-documents-unverified",
      "service_id": "post-gep",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Government Express Post (GEP).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-post-international-mail-portal-unreachable",
      "service_id": "post-international-mail",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for International Mail Service.",
      "severity": "MEDIUM",
      "url": "https://bdpost.gov.bd/site/page/1e0924ce-788d-4304-b47a-54d76748abf5/%E0%A6%86%E0%A6%A8%E0%A7%8D%E0%A6%A4%E0%A6%B0%E0%A7%8D%E0%A6%9C%E0%A6%BE%E0%A6%A4%E0%A6%BF%E0%A6%95-%E0%A6%A1%E0%A6%BE%E0%A6%95%E0%A6%B8%E0%A7%87%E0%A6%AC%E0%A6%BE"
    },
    {
      "gap_id": "gap-post-international-mail-fee-unverified",
      "service_id": "post-international-mail",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for International Mail Service.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-post-international-mail-documents-unverified",
      "service_id": "post-international-mail",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for International Mail Service.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-post-life-insurance-portal-unreachable",
      "service_id": "post-life-insurance",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Postal Life Insurance.",
      "severity": "MEDIUM",
      "url": "https://bdpost.gov.bd/site/page/4ad27a53-60f4-4fb8-9c7e-28d9ec5669a2/-"
    },
    {
      "gap_id": "gap-post-life-insurance-fee-unverified",
      "service_id": "post-life-insurance",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Postal Life Insurance.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-post-life-insurance-documents-unverified",
      "service_id": "post-life-insurance",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Postal Life Insurance.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-post-mail-tracking-fee-unverified",
      "service_id": "post-mail-tracking",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Domestic Mail Item Tracking.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-post-mail-tracking-documents-unverified",
      "service_id": "post-mail-tracking",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Domestic Mail Item Tracking.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-post-money-order-portal-unreachable",
      "service_id": "post-money-order",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Postal Money Order.",
      "severity": "MEDIUM",
      "url": "https://bdpost.gov.bd/site/page/2b5d6dac-0cd7-4342-9cab-e0b66765aa69/-"
    },
    {
      "gap_id": "gap-post-money-order-fee-unverified",
      "service_id": "post-money-order",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Postal Money Order.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-post-money-order-documents-unverified",
      "service_id": "post-money-order",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Postal Money Order.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-post-postage-calculator-fee-unverified",
      "service_id": "post-postage-calculator",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Postal Postage Calculator.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-post-postage-calculator-documents-unverified",
      "service_id": "post-postage-calculator",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Postal Postage Calculator.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-post-savings-bank-portal-unreachable",
      "service_id": "post-savings-bank",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Post Office Savings Bank.",
      "severity": "MEDIUM",
      "url": "https://bdpost.gov.bd/site/page/ac7d5cfe-11e9-441a-a1b4-61cde1245484/-"
    },
    {
      "gap_id": "gap-post-savings-bank-fee-unverified",
      "service_id": "post-savings-bank",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Post Office Savings Bank.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-post-savings-bank-documents-unverified",
      "service_id": "post-savings-bank",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Post Office Savings Bank.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-post-savings-certificate-portal-unreachable",
      "service_id": "post-savings-certificate",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Postal Savings Certificate.",
      "severity": "MEDIUM",
      "url": "https://bdpost.gov.bd/site/page/32495e81-3fa6-420d-a368-b05587397d0a/-"
    },
    {
      "gap_id": "gap-post-savings-certificate-fee-unverified",
      "service_id": "post-savings-certificate",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Postal Savings Certificate.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-post-savings-certificate-documents-unverified",
      "service_id": "post-savings-certificate",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Postal Savings Certificate.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-post-speed-post-portal-unreachable",
      "service_id": "post-speed-post",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Speed Post.",
      "severity": "MEDIUM",
      "url": "https://bdpost.gov.bd/site/page/34b7ea83-3911-429f-8ec5-58f0367c53bd/-"
    },
    {
      "gap_id": "gap-post-speed-post-fee-unverified",
      "service_id": "post-speed-post",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Speed Post.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-post-speed-post-documents-unverified",
      "service_id": "post-speed-post",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Speed Post.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-railway-helpline-131-fee-unverified",
      "service_id": "railway-helpline-131",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Bangladesh Railway Service Helpline (131).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-railway-helpline-131-documents-unverified",
      "service_id": "railway-helpline-131",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Bangladesh Railway Service Helpline (131).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-railway-online-ticket-fee-unverified",
      "service_id": "railway-online-ticket",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Bangladesh Railway Online Ticket Booking.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-railway-online-ticket-documents-unverified",
      "service_id": "railway-online-ticket",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Bangladesh Railway Online Ticket Booking.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-railway-rail-sheba-app-fee-unverified",
      "service_id": "railway-rail-sheba-app",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Rail Sheba Mobile App Registration and Booking.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-railway-rail-sheba-app-documents-unverified",
      "service_id": "railway-rail-sheba-app",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Rail Sheba Mobile App Registration and Booking.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-tax-challan-payment-fee-unverified",
      "service_id": "tax-challan-payment",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Tax/VAT Challan Payment.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-tax-challan-payment-documents-unverified",
      "service_id": "tax-challan-payment",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Tax/VAT Challan Payment.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-titas-domestic-gas-connection-fee-unverified",
      "service_id": "titas-domestic-gas-connection",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Titas Gas Domestic Connection Application.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-titas-domestic-gas-connection-documents-unverified",
      "service_id": "titas-domestic-gas-connection",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Titas Gas Domestic Connection Application.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-titas-industry-gas-connection-fee-unverified",
      "service_id": "titas-industry-gas-connection",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Titas Gas Industry or Captive Power Connection.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-titas-industry-gas-connection-documents-unverified",
      "service_id": "titas-industry-gas-connection",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Titas Gas Industry or Captive Power Connection.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-wasa-application-tracking-fee-unverified",
      "service_id": "wasa-application-tracking",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for WASA Application Tracking.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-wasa-application-tracking-documents-unverified",
      "service_id": "wasa-application-tracking",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for WASA Application Tracking.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-wasa-connection-enlargement-fee-unverified",
      "service_id": "wasa-connection-enlargement",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Water Connection Enlargement.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-wasa-connection-enlargement-documents-unverified",
      "service_id": "wasa-connection-enlargement",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Water Connection Enlargement.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-wasa-line-shifting-fee-unverified",
      "service_id": "wasa-line-shifting",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Water Line Shifting.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-wasa-line-shifting-documents-unverified",
      "service_id": "wasa-line-shifting",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Water Line Shifting.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-wasa-new-water-connection-fee-unverified",
      "service_id": "wasa-new-water-connection",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Dhaka WASA New Water Connection.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-wasa-new-water-connection-documents-unverified",
      "service_id": "wasa-new-water-connection",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Dhaka WASA New Water Connection.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-wasa-second-connection-fee-unverified",
      "service_id": "wasa-second-connection",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Second or Additional Water Connection.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-wasa-second-connection-documents-unverified",
      "service_id": "wasa-second-connection",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Second or Additional Water Connection.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-wasa-sewerage-connection-fee-unverified",
      "service_id": "wasa-sewerage-connection",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Dhaka WASA Sewerage Connection.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-wasa-sewerage-connection-documents-unverified",
      "service_id": "wasa-sewerage-connection",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Dhaka WASA Sewerage Connection.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-wasa-temporary-connection-fee-unverified",
      "service_id": "wasa-temporary-connection",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Temporary Water Connection.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-wasa-temporary-connection-documents-unverified",
      "service_id": "wasa-temporary-connection",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Temporary Water Connection.",
      "severity": "MEDIUM"
    }
  ],
  "conflicts": []
}
```

## Phase instructions
# E2E evaluation prompt

Generate realistic user questions: Bangla, English, Banglish, typos, ambiguity, follow-ups, multi-turn.

Correct uncertainty/refusal is NOT failure. Wrong factual answers ARE failures.

Write eval artifacts under `data/evaluation/<batch-slug>/` and `result.json`.


Follow docs/research/BATCH_RESEARCH_TEMPLATE.md for RESEARCH.
Write machine-readable `.automation/runs/run-c18a40f59d04-e2e/result.json` when complete.
