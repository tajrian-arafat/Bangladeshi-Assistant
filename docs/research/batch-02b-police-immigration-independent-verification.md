# Batch 2B — Independent Claim Verification (Police + Immigration)

**Date:** 2026-08-24  
**Verifier:** `cursor-cloud-agent`  
**Layer:** `data/research/verification/batch-02b-police-immigration` (STAGING ONLY)  
**Published to runtime:** No  
**publish_verified_knowledge.py run:** No

## Policy used

- High-risk OFFICIAL claims require Tier 1–2 explicit support on live fetches.
- Tier 5 news (GD expansion) does NOT promote to VERIFIED.
- PCC fee conflict: online BDT 1,500 VERIFIED for online channel; offline BDT 500 CONFLICTING — not published as universal fee.
- Passport verification SLAs kept separate from PCC SLAs.
- See `verification_policy.json`.

## Totals

1. Total claims: **77**
2. VERIFIED: **60**
3. PARTIALLY_VERIFIED: **10**
4. UNVERIFIED: **6**
5. CONFLICTING: **1**
6. OUTDATED: **0**
7. REJECTED: **0**
8. Official claims verified: **57**
9. Practical claims: **1**
10. Resolved conflicts: **2**
11. Unresolved conflicts: **1**
12. Knowledge gaps: **10**
13. GREEN services: **1**
14. YELLOW services: **10**
15. RED services: **0**

## PCC fee conflict (critical)

| Channel | Amount | Treasury code | Status |
|---------|--------|---------------|--------|
| Online (`pcc.police.gov.bd`) | BDT 1,500 | 1-7301-0001-2681 | **VERIFIED** (online channel) |
| Offline page (`police.gov.bd/en/police_clearance_certificate`) | BDT 500 | 1-2201-0001-2681 | **CONFLICTING** |
| Citizen charter (online clearance row) | BDT 1,500 | — | **VERIFIED** |

Classification: **channel_specific_unreconciled**. No gazette/circular captured to confirm whether legacy paper path remains at 500.

## Evidence limitations

Live Tier-1: pcc.police.gov.bd (full PCC terms/fees/steps), dip.gov.bd, dip visa-online page. Live Tier-2: police citizen charter (GD/PCC/passport verification/employment/firearms/expatriate rows), police.gov.bd offline PCC page. Official PDFs: DIP visa types Dec 2024 (machine-readable); MRV fees Dec 2024 PDF scanned/unreadable. Failed fetches: gd.police.gov.bd (502), visa.gov.bd (SSL). Tier-5 GD expansion claims left UNVERIFIED.

## Conflict outcomes

- `conflict-pcc-fee-online-vs-offline` — **PARTIALLY_RESOLVED** (channel_specific_unreconciled): Likely channel-specific (online vs legacy paper procedure) but NOT authoritatively reconciled: no circular/gazette found stating offline paper path fee. Online 1500 VERIFIED for online channel. Offline 500 claim marked CONFLICTING — do not publish as current universal PCC fee.
- `conflict-pcc-treasury-code` — **PARTIALLY_RESOLVED** (channel_specific): Treasury codes differ by channel documentation; treat as paired with fee conflict.
- `conflict-gd-online-scope-timeline` — **UNRESOLVED** (historical_rollout_vs_current_capability_unknown): Current online GD scope UNVERIFIED. Charter confirms online channel exists but not complaint-type matrix.
- `conflict-passport-verification-vs-pcc` — **RESOLVED** (distinct_services_not_contradiction): Not a factual conflict — different catalogue services with different charter rows. Must not merge SLAs in product answers.
- `conflict-pcc-portal-url-variants` — **RESOLVED** (same_apex_app_multiple_entry_routes): Multiple entry URLs for same PCC system; catalogue canonical URL live-verified.

## Service readiness

### GREEN
- `police-cyber-support-women` — All charter-sourced PCSW claims VERIFIED on live citizen charter.

### YELLOW
- `migration-visa-application-dip` — DIP portal links and Dec 2024 visa-types PDF partially verified; visa.gov.bd unreachable; MRV fee matrix UNVERIFIED (scanned PDF).
- `police-clearance-certificate` — Online PCC core rules live-verified (Tier 1 portal + charter) but offline fee CONFLICTING; collection/delivery and correction workflows still gapped.
- `police-employment-verification` — Pathway verified; fee amount and numeric SLA not on Tier 1–2 sources.
- `police-expatriate-services` — Charter scope verified; detailed procedures beyond charter not captured.
- `police-firearms-license` — Charter pathway/SLA verified; eligibility/documents/legal basis beyond charter not captured.
- `police-general-diary` — Charter SLA/fee/channels verified; gd.police.gov.bd unreachable; online scope/expansion UNVERIFIED.
- `police-general-diary-online` — Charter SLA/fee/channels verified; gd.police.gov.bd unreachable; online scope/expansion UNVERIFIED.
- `police-nid-address-verification` — Conditional NID/address rules verified via PCC pages; no standalone service portal.
- `police-passport-police-verification` — Service boundaries verified; e-Passport onboarding PV steps only partially verified (batch-02a).
- `police-passport-verification` — Passport verification SLAs VERIFIED on charter; fee amount missing; distinct from PCC.

### RED

## Knowledge gaps (open)

- `MISSING_GD_PORTAL_SNAPSHOT` — gd.police.gov.bd SSL fetch failed; Tier-1 portal text not independently snapshotted in this pass.
- `MISSING_VISA_GOV_BD_SNAPSHOT` — visa.gov.bd application workflow, fees, and document upload rules not captured from live portal.
- `MISSING_MRV_FEE_TABLE_EXTRACT` — DIP MRV fee page fetched but structured fee matrix not extracted (likely embedded PDF/image).
- `MISSING_VISA_TYPES_MATRIX` — Visa types/documents page last updated 2022; per-visa-type document list not machine-read in this pass.
- `MISSING_EMPLOYMENT_VERIFICATION_FEE_AMOUNT` — Charter cites government fee but no numeric amount on Tier 1–2 pages reviewed.
- `MISSING_PASSPORT_VERIFICATION_FEE_AMOUNT` — Charter cites government fee but no numeric amount on Tier 1–2 pages reviewed.
- `MISSING_PCC_COLLECTION_DELIVERY_OFFICIAL` — Courier/mail delivery options referenced in third-party guides; not confirmed on Tier 1 portal pages captured.
- `MISSING_FIREARMS_DOCUMENT_CHECKLIST` — No dedicated firearms license document checklist found on Tier 1–2 sources in this pass.
- `MISSING_GD_DUPLICATE_CANONICAL_RESOLUTION` — Two catalogue entries share gd.police.gov.bd; relationship (alias vs subprocess) not resolved in research phase.
- `MISSING_PCC_REISSUE_CORRECTION_PROCESS` — Correction/reissue workflow for issued PCC not found on official pages reviewed.

## Explicit non-actions

- Did not publish claims
- Did not start Batch 3 / BRTA / Tax / Land / Education
- Did not deploy or modify frontend

## Machine-readable outputs

- `data/research/verification/batch-02b-police-immigration/claims_verification.json`
- `data/research/verification/batch-02b-police-immigration/conflicts_resolution.json`
- `data/research/verification/batch-02b-police-immigration/knowledge_gaps.json`
- `data/research/verification/batch-02b-police-immigration/service_readiness.json`
- `data/research/verification/batch-02b-police-immigration/summary.json`
- `data/research/verification/batch-02b-police-immigration/verification_policy.json`
- `data/research/verification/batch-02b-police-immigration/source_evidence.json`

