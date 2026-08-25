# Batch 1 — Independent Claim Verification

**Date:** 2026-08-24  
**Verifier:** `cursor-cloud-agent`  
**Layer:** `data/research/verification/batch-01` (STAGING ONLY)  
**Published to runtime:** No  
**publish_verified_knowledge.py run:** No

## Policy used

- High-risk OFFICIAL claims require Tier 1–2 explicit support; Tier ≥5 never promoted to OFFICIAL VERIFIED.
- Finding a source ≠ VERIFIED; live/Wayback inspection required.
- Conditional requirements stay conditional (never auto MUST NEED).
- PRACTICAL stays PRACTICAL.
- Conflicts resolved only with evidence; otherwise left UNRESOLVED.
- See `data/research/verification/batch-01/verification_policy.json`.

## Totals

1. Total claims: **69**
2. VERIFIED: **38**
3. PARTIALLY_VERIFIED: **19**
4. CONFLICTING: **0**
5. OUTDATED: **0**
6. UNVERIFIED: **11**
7. REJECTED: **1**
8. Official claims verified: **38**
9. Practical claims: **5**
10. Claims requiring manual review: **30**
11. Conflicts resolved: **2**
12. Conflicts unresolved: **3**
13. Knowledge gaps created: **10**
14. Services GREEN: **14**
15. Services YELLOW: **18**
16. Services RED: **2**
17. Evidence coverage: Primary live Tier-1: services.nidw.gov.bd FAQ/fees; www.bdris.gov.bd home; everify.bdris.gov.bd; bdlaws Muslim Marriage Act; marriage.gov.bd (+ manual PDF). Tier-1 ORGBDR fee page via Wayback 2026-04-05. MOFA fee notice via Wayback 2023-06. Bright Data unlocker unavailable (401). Several BDRIS deep pages 403.
18. Verification coverage: 69/69 claims assigned a primary verification status
19. Main limitations:

   - BDRIS application deep pages blocked (403) — portal claims often PARTIAL
   - Live ORGBDR/MOFA hosts unreachable — used Wayback for fee schedule
   - NID static fee amounts not on official calculator page
   - Hindu Marriage Act text extraction failed
   - No claims published to runtime Fee/Checklist tables

## Conflict outcomes

- `conf-br-fee-10y` — **RESOLVED** (secondary_error_vs_official_schedule): Official ORGBDR schedule has free/25/50 tiers only. BDT 500 after 10 years REJECTED for official use.
- `conf-bdris-corr-other-fee` — **RESOLVED** (resolved_prefer_tier1_other_fee_50): ORGBDR Tier-1: other-info correction BDT 50; DOB BDT 100.
- `conf-nid-card-info-correction-fee-amount` — **UNRESOLVED** (unresolved_static_amounts_vs_official_calculator): Use official calculator; do not publish news static amounts as OFFICIAL.
- `conf-nid-combined-correction-fee-amount` — **UNRESOLVED** (unresolved_static_amounts_vs_official_calculator): Same as card-info correction fee conflict.
- `conf-nid-other-info-correction-fee-amount` — **UNRESOLVED** (unresolved_static_amounts_vs_official_calculator): Same as card-info correction fee conflict.

## Service readiness

### GREEN
- `civil-birth-death-verify` — Core official facts verified against Tier 1 sources.
- `civil-birth-registration` — Fee schedule and key portal facts verified; helpline/email claim unverified (does not block fee publication).
- `civil-birth-registration-copy` — Core official facts verified against Tier 1 sources.
- `civil-birth-registration-correction` — Core official facts verified against Tier 1 sources.
- `civil-death-registration` — Core official facts verified against Tier 1 sources.
- `civil-death-registration-copy` — Core official facts verified against Tier 1 sources.
- `nid-claim-account` — Core official facts verified against Tier 1 sources.
- `nid-download-copy` — Core official facts verified against Tier 1 sources.
- `nid-fee-calculator` — Core official facts verified against Tier 1 sources.
- `nid-new-voter-registration` — Core official facts verified against Tier 1 sources.
- `nid-online-account-registration` — Core official facts verified against Tier 1 sources.
- `nid-photo-signature-appointment` — Core official facts verified against Tier 1 sources.
- `nid-reissue-lost` — Core official facts verified against Tier 1 sources.
- `nid-voter-area-change` — Core official facts verified against Tier 1 sources.

### YELLOW
- `civil-bdris-application-print` — Service existence partially corroborated; deep-page or channel details incomplete.
- `civil-birth-registration-duplicate-cancel` — Service existence partially corroborated; deep-page or channel details incomplete.
- `civil-death-registration-correction` — Other-info fee verified; DOB-analog fee only partially verified for death records.
- `civil-death-registration-duplicate-cancel` — Service existence partially corroborated; deep-page or channel details incomplete.
- `civil-divorce-registration` — Service existence partially corroborated; deep-page or channel details incomplete.
- `civil-marriage-registration` — Service existence partially corroborated; deep-page or channel details incomplete.
- `dc-attestation-photocopy` — Local/LGI instance services — example URLs only; no national authoritative fee/doc pack.
- `dc-guardianship-certificate` — Local/LGI instance services — example URLs only; no national authoritative fee/doc pack.
- `identity-voter-slip-download` — Useful verified/partial information exists but material gaps remain.
- `local-character-certificate` — Local/LGI instance services — example URLs only; no national authoritative fee/doc pack.
- `local-death-certificate-union` — Local/LGI instance services — example URLs only; no national authoritative fee/doc pack.
- `local-nationality-certificate` — Local/LGI instance services — example URLs only; no national authoritative fee/doc pack.
- `local-passport-attestation` — Local/LGI instance services — example URLs only; no national authoritative fee/doc pack.
- `local-voter-transfer-attestation` — Local/LGI instance services — example URLs only; no national authoritative fee/doc pack.
- `nid-card-info-correction` — Correction rules/channels/fees-exist verified; exact static fee amounts unresolved (use calculator). Not GREEN for authoritative amount publication.
- `nid-combined-correction` — Correction rules/channels/fees-exist verified; exact static fee amounts unresolved (use calculator). Not GREEN for authoritative amount publication.
- `nid-expatriate-registration` — Service existence partially corroborated; deep-page or channel details incomplete.
- `nid-other-info-correction` — Correction rules/channels/fees-exist verified; exact static fee amounts unresolved (use calculator). Not GREEN for authoritative amount publication.

### RED
- `civil-marriage-registrar-hindu-list` — Registrar list/search function not independently confirmed; do not expose as authoritative.
- `civil-marriage-registrar-muslim-list` — Registrar list/search function not independently confirmed; do not expose as authoritative.

## Knowledge gaps

- `MISSING_BDRIS_APPLICATION_UPLOAD_CONSTRAINTS` — claims: `civil-birth-registration::c-br-upload`
- `MISSING_CURRENT_BDRIS_HELPLINE_PUBLICATION` — claims: `civil-birth-registration::c-br-helpline`
- `MISSING_DEATH_CORRECTION_FEE_WORDING` — claims: `civil-death-registration-correction::c-corr-fee-dob`
- `MISSING_HINDU_REGISTRAR_LIST_EVIDENCE` — claims: `civil-marriage-registrar-hindu-list::c-reg-list`
- `MISSING_MUSLIM_REGISTRAR_LIST_EVIDENCE` — claims: `civil-marriage-registrar-muslim-list::c-reg-list`
- `MISSING_HINDU_MARRIAGE_ACT_TEXT_EXTRACTION` — claims: `civil-marriage-registration::c-hm-optional`
- `MISSING_LGI_EXAMPLE_URL_REACHABILITY` — claims: `dc-attestation-photocopy::c-dc-attestation-photocopy-exists`, `dc-guardianship-certificate::c-dc-guardianship-certificate-exists`
- `MISSING_OFFICIAL_NID_FEE_SCHEDULE_STATIC` — claims: `nid-card-info-correction::c-nid-card-info-correction-fee-amount-news`, `nid-combined-correction::c-nid-combined-correction-fee-amount-news`, `nid-other-info-correction::c-nid-other-info-correction-fee-amount-news`
- `MISSING_EXPATRIATE_OTP_CHANNEL_RULE` — claims: `nid-expatriate-registration::c-exp-otp`
- `MISSING_NID_REISSUE_STATUTORY_CITATION` — claims: `nid-reissue-lost::c-reissue-law`

## Explicit non-actions

- Did not start Batch 2
- Did not publish Fee/Checklist/Procedure rows
- Did not invent fees/URLs
- Did not convert PRACTICAL → MUST NEED

## Machine-readable outputs

- `data/research/verification/batch-01/claims_verification.json`
- `data/research/verification/batch-01/conflicts_resolution.json`
- `data/research/verification/batch-01/knowledge_gaps.json`
- `data/research/verification/batch-01/service_readiness.json`
- `data/research/verification/batch-01/summary.json`
- `data/research/verification/batch-01/verification_policy.json`
