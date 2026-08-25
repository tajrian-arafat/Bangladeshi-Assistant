# BDA Cloud Task — E2E

**Batch:** BATCH_11 (Business / Trade / Industry / Professional)
**Run ID:** run-c468b4664114-e2e

## Safety
- LOCAL_DEV_ONLY — deployment_allowed must remain false
- Do NOT deploy, merge to main, or use external paid AI APIs
- Never publish UNVERIFIED/CONFLICTING claims as authoritative
- Write validated result.json — do not mutate project_state.json directly

## Required outputs
- `data/evaluation/batch-11-business-trade/queries.json`
- `data/evaluation/batch-11-business-trade/summary.json`
- `docs/evaluation/batch-11-business-trade-publication-e2e.md`
- `.automation/runs/run-c468b4664114-e2e/result.json`

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
    "phases_completed": [
      "RESEARCH",
      "VERIFICATION",
      "GAP_CLOSURE"
    ]
  },
  "phase": "E2E",
  "run_id": "run-c468b4664114-e2e",
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
  "gaps": [
    {
      "gap_id": "gap-bida-aftercare-services-fee-unverified",
      "service_id": "bida-aftercare-services",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for BIDA Aftercare Services for Investors.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-bida-aftercare-services-documents-unverified",
      "service_id": "bida-aftercare-services",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for BIDA Aftercare Services for Investors.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-bida-commercial-office-services-fee-unverified",
      "service_id": "bida-commercial-office-services",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Branch, Liaison and Representative Office Services (BIDA).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-bida-commercial-office-services-documents-unverified",
      "service_id": "bida-commercial-office-services",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Branch, Liaison and Representative Office Services (BIDA).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-bida-invest-bangladesh-oss-fee-unverified",
      "service_id": "bida-invest-bangladesh-oss",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Invest Bangladesh OSS Portal.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-bida-invest-bangladesh-oss-documents-unverified",
      "service_id": "bida-invest-bangladesh-oss",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Invest Bangladesh OSS Portal.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-bida-irms-platform-fee-unverified",
      "service_id": "bida-irms-platform",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for BIDA Investment Relationship Management System (IRMS).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-bida-irms-platform-documents-unverified",
      "service_id": "bida-irms-platform",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for BIDA Investment Relationship Management System (IRMS).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-bida-osspid-registration-portal-unreachable",
      "service_id": "bida-osspid-registration",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for OSSPID Account Registration (BIDA).",
      "severity": "MEDIUM",
      "url": "https://irms.bida.gov.bd/set-registration-type/investor"
    },
    {
      "gap_id": "gap-bida-osspid-registration-fee-unverified",
      "service_id": "bida-osspid-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for OSSPID Account Registration (BIDA).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-bida-osspid-registration-documents-unverified",
      "service_id": "bida-osspid-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for OSSPID Account Registration (BIDA).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-bida-work-permit-security-clearance-fee-unverified",
      "service_id": "bida-work-permit-security-clearance",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for BIDA Work Permit Security Clearance (Online).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-bida-work-permit-security-clearance-documents-unverified",
      "service_id": "bida-work-permit-security-clearance",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for BIDA Work Permit Security Clearance (Online).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-business-company-incorporation-portal-unreachable",
      "service_id": "business-company-incorporation",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Company Incorporation.",
      "severity": "MEDIUM",
      "url": "https://app.roc.gov.bd/Guidlines/Introduction.htm"
    },
    {
      "gap_id": "gap-business-company-incorporation-fee-unverified",
      "service_id": "business-company-incorporation",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Company Incorporation.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-business-company-incorporation-documents-unverified",
      "service_id": "business-company-incorporation",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Company Incorporation.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-business-cooperative-society-registration-fee-unverified",
      "service_id": "business-cooperative-society-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Cooperative Society Registration.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-business-cooperative-society-registration-documents-unverified",
      "service_id": "business-cooperative-society-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Cooperative Society Registration.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-business-entity-name-search-portal-unreachable",
      "service_id": "business-entity-name-search",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Entity Name Search.",
      "severity": "MEDIUM",
      "url": "https://app.roc.gov.bd/psp/nc_search"
    },
    {
      "gap_id": "gap-business-entity-name-search-fee-unverified",
      "service_id": "business-entity-name-search",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Entity Name Search.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-business-entity-name-search-documents-unverified",
      "service_id": "business-entity-name-search",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Entity Name Search.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-business-foreign-company-registration-portal-unreachable",
      "service_id": "business-foreign-company-registration",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Foreign Company Registration (Branch/Liaison).",
      "severity": "MEDIUM",
      "url": "https://app.roc.gov.bd/Guidlines/Introduction.htm"
    },
    {
      "gap_id": "gap-business-foreign-company-registration-fee-unverified",
      "service_id": "business-foreign-company-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Foreign Company Registration (Branch/Liaison).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-business-foreign-company-registration-documents-unverified",
      "service_id": "business-foreign-company-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Foreign Company Registration (Branch/Liaison).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-business-name-clearance-portal-unreachable",
      "service_id": "business-name-clearance",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Company Name Clearance.",
      "severity": "MEDIUM",
      "url": "https://app.roc.gov.bd/Guidlines/RJSC_bus_pro_NC.htm"
    },
    {
      "gap_id": "gap-business-name-clearance-fee-unverified",
      "service_id": "business-name-clearance",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Company Name Clearance.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-business-name-clearance-documents-unverified",
      "service_id": "business-name-clearance",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Company Name Clearance.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-business-ngoab-ngo-registration-portal-unreachable",
      "service_id": "business-ngoab-ngo-registration",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for NGO Registration (NGO Affairs Bureau).",
      "severity": "MEDIUM",
      "url": "https://ngoa.gov.bd/"
    },
    {
      "gap_id": "gap-business-ngoab-ngo-registration-fee-unverified",
      "service_id": "business-ngoab-ngo-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for NGO Registration (NGO Affairs Bureau).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-business-ngoab-ngo-registration-documents-unverified",
      "service_id": "business-ngoab-ngo-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for NGO Registration (NGO Affairs Bureau).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-business-partnership-registration-portal-unreachable",
      "service_id": "business-partnership-registration",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Partnership Firm Registration.",
      "severity": "MEDIUM",
      "url": "https://app.roc.gov.bd/Guidlines/Download/Downloads.htm"
    },
    {
      "gap_id": "gap-business-partnership-registration-fee-unverified",
      "service_id": "business-partnership-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Partnership Firm Registration.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-business-partnership-registration-documents-unverified",
      "service_id": "business-partnership-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Partnership Firm Registration.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-business-rjsc-certified-copy-portal-unreachable",
      "service_id": "business-rjsc-certified-copy",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for RJSC Certified Copy of Documents.",
      "severity": "MEDIUM",
      "url": "https://app.roc.gov.bd/psp/RJSC_Fees"
    },
    {
      "gap_id": "gap-business-rjsc-certified-copy-fee-unverified",
      "service_id": "business-rjsc-certified-copy",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for RJSC Certified Copy of Documents.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-business-rjsc-certified-copy-documents-unverified",
      "service_id": "business-rjsc-certified-copy",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for RJSC Certified Copy of Documents.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-business-society-registration-portal-unreachable",
      "service_id": "business-society-registration",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Society Registration.",
      "severity": "MEDIUM",
      "url": "https://app.roc.gov.bd/Guidlines/Download/Downloads.htm"
    },
    {
      "gap_id": "gap-business-society-registration-fee-unverified",
      "service_id": "business-society-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Society Registration.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-business-society-registration-documents-unverified",
      "service_id": "business-society-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Society Registration.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-business-trade-organization-registration-portal-unreachable",
      "service_id": "business-trade-organization-registration",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Trade Organization Registration.",
      "severity": "MEDIUM",
      "url": "https://app.roc.gov.bd/Guidlines/Introduction.htm"
    },
    {
      "gap_id": "gap-business-trade-organization-registration-fee-unverified",
      "service_id": "business-trade-organization-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Trade Organization Registration.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-business-trade-organization-registration-documents-unverified",
      "service_id": "business-trade-organization-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Trade Organization Registration.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-professional-bar-council-enrolment-portal-unreachable",
      "service_id": "professional-bar-council-enrolment",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Bangladesh Bar Council Advocate Enrolment.",
      "severity": "MEDIUM",
      "url": "https://www.barcouncil.gov.bd/"
    },
    {
      "gap_id": "gap-professional-bar-council-enrolment-fee-unverified",
      "service_id": "professional-bar-council-enrolment",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Bangladesh Bar Council Advocate Enrolment.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-professional-bar-council-enrolment-documents-unverified",
      "service_id": "professional-bar-council-enrolment",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Bangladesh Bar Council Advocate Enrolment.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-professional-bmdc-doctor-registration-portal-unreachable",
      "service_id": "professional-bmdc-doctor-registration",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for BMDC Doctor Registration.",
      "severity": "MEDIUM",
      "url": "https://www.bmdc.org.bd/"
    },
    {
      "gap_id": "gap-professional-bmdc-doctor-registration-fee-unverified",
      "service_id": "professional-bmdc-doctor-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for BMDC Doctor Registration.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-professional-bmdc-doctor-registration-documents-unverified",
      "service_id": "professional-bmdc-doctor-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for BMDC Doctor Registration.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-professional-engineer-registration-portal-unreachable",
      "service_id": "professional-engineer-registration",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Professional Engineer Registration.",
      "severity": "MEDIUM",
      "url": "https://www.ieb.org.bd/"
    },
    {
      "gap_id": "gap-professional-engineer-registration-fee-unverified",
      "service_id": "professional-engineer-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Professional Engineer Registration.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-professional-engineer-registration-documents-unverified",
      "service_id": "professional-engineer-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Professional Engineer Registration.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-professional-nursing-council-registration-portal-unreachable",
      "service_id": "professional-nursing-council-registration",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Nursing and Midwifery Council Registration.",
      "severity": "MEDIUM",
      "url": "https://www.bnmc.gov.bd/"
    },
    {
      "gap_id": "gap-professional-nursing-council-registration-fee-unverified",
      "service_id": "professional-nursing-council-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Nursing and Midwifery Council Registration.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-professional-nursing-council-registration-documents-unverified",
      "service_id": "professional-nursing-council-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Nursing and Midwifery Council Registration.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-professional-pharmacy-council-registration-portal-unreachable",
      "service_id": "professional-pharmacy-council-registration",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for Pharmacy Council Pharmacist Registration.",
      "severity": "MEDIUM",
      "url": "https://www.pcb.gov.bd/"
    },
    {
      "gap_id": "gap-professional-pharmacy-council-registration-fee-unverified",
      "service_id": "professional-pharmacy-council-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Pharmacy Council Pharmacist Registration.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-professional-pharmacy-council-registration-documents-unverified",
      "service_id": "professional-pharmacy-council-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Pharmacy Council Pharmacist Registration.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-trade-bsti-standard-certification-portal-unreachable",
      "service_id": "trade-bsti-standard-certification",
      "gap_type": "CURRENT_URL_MISSING",
      "description": "Catalogue/portal URL not reachable at research time for BSTI Product Standard Certification.",
      "severity": "MEDIUM",
      "url": "https://bsti.gov.bd/"
    },
    {
      "gap_id": "gap-trade-bsti-standard-certification-fee-unverified",
      "service_id": "trade-bsti-standard-certification",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for BSTI Product Standard Certification.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-trade-bsti-standard-certification-documents-unverified",
      "service_id": "trade-bsti-standard-certification",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for BSTI Product Standard Certification.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-trade-dpd-patent-registration-fee-unverified",
      "service_id": "trade-dpd-patent-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Patent Registration.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-trade-dpd-patent-registration-documents-unverified",
      "service_id": "trade-dpd-patent-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Patent Registration.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-trade-dpd-trademark-registration-fee-unverified",
      "service_id": "trade-dpd-trademark-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Trademark Registration.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-trade-dpd-trademark-registration-documents-unverified",
      "service_id": "trade-dpd-trademark-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Trademark Registration.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-trade-erc-registration-fee-unverified",
      "service_id": "trade-erc-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Export Registration Certificate (ERC).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-trade-erc-registration-documents-unverified",
      "service_id": "trade-erc-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Export Registration Certificate (ERC).",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-trade-irc-erc-renewal-fee-unverified",
      "service_id": "trade-irc-erc-renewal",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for IRC/ERC Renewal.",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-trade-irc-erc-renewal-documents-unverified",
      "service_id": "trade-irc-erc-renewal",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for IRC/ERC Renewal.",
      "severity": "MEDIUM"
    },
    {
      "gap_id": "gap-trade-irc-registration-fee-unverified",
      "service_id": "trade-irc-registration",
      "gap_type": "CURRENT_FEE_MISSING",
      "description": "Fee schedule not independently verified for Import Registration Certificate (IRC).",
      "severity": "HIGH"
    },
    {
      "gap_id": "gap-trade-irc-registration-documents-unverified",
      "service_id": "trade-irc-registration",
      "gap_type": "LOCAL_RULE_MISSING",
      "description": "Mandatory document checklist not fully verified for Import Registration Certificate (IRC).",
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
Write machine-readable `.automation/runs/run-c468b4664114-e2e/result.json` when complete.
