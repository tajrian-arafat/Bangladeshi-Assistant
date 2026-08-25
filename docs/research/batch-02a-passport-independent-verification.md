# Batch 2A — Independent Claim Verification (Passport Services)

**Date:** 2026-08-24  
**Verifier:** `cursor-cloud-agent`  
**Layer:** `data/research/verification/batch-02a-passport` (STAGING ONLY)  
**Published to runtime:** No  
**publish_verified_knowledge.py run:** No

## Policy used

- High-risk OFFICIAL claims require Tier 1–2 explicit support; search-index excerpts alone → PARTIAL/OUTDATED, not VERIFIED.
- epassport.gov.bd instructional pages are Angular SPAs; live/Wayback returned shells without instructional text.
- Conditional requirements stay conditional.
- PRACTICAL never promoted to MUST_NEED.
- See `data/research/verification/batch-02a-passport/verification_policy.json`.

## Totals

1. Total claims: **55**
2. VERIFIED: **13**
3. PARTIALLY_VERIFIED: **35**
4. UNVERIFIED: **2**
5. CONFLICTING: **0**
6. OUTDATED: **4**
7. REJECTED: **1**
8. Official claims verified: **10**
9. Practical claims: **2**
10. Resolved conflicts: **2**
11. Unresolved conflicts: **0**
12. Knowledge gaps: **4**
13. GREEN services: **1**
14. YELLOW services: **10**
15. RED services: **1**

## Evidence limitations

Live Tier-1 HTML: passport.gov.bd (MRP), dip.gov.bd (dual e-Passport+MRP links), police.gov.bd citizen charter (passport verification SLAs). Live Tier-2: bcgdubai.gov.bd/e-passport/ (mission rules). epassport.gov.bd landing HTTP 200 but instructional routes are Angular SPA shells; onboarding returned 403; Wayback captures also SPA-only. Fee/instruction/urgent/enrollment claims rely on search-index excerpts of official URLs — explicitly NOT treated as direct page evidence. Singapore e-passport rules URL returned 404. Abu Dhabi page body not retrieved.

## Conflict outcomes

- `conflict-super-express-eligibility` — **RESOLVED**: Urgent page headline allows any citizen to apply for Super Express delivery type, but NOTE restricts current operational availability to existing MRP holders not changing permanent address. Represent as IF existing_mrp AND NOT permanent_address_change THEN super_express_available.
- `conflict-mrp-vs-epassport-primary` — **RESOLVED**: DIP home (live Tier-1) lists BOTH 'ই-পাসপোর্ট আবেদন' (epassport.gov.bd) and 'অনলাইন এমআরপি আবেদন' (passport.gov.bd) as active internal e-services. e-Passport is primary/current for new biometric passports; MRP portal remains operational (legacy channel). Do not collapse to single channel.
- `conflict-fee-freshness` — **PARTIALLY_RESOLVED**: Tier-1 fee page last updated 8 March 2023 per indexed metadata. No newer official fee gazette, notice, or machine-readable fee snapshot captured in verification pass. Domestic BDT amounts marked OUTDATED; fee tier structure PARTIALLY_VERIFIED via index excerpt only.

## Service readiness

### GREEN
- `passport-application-status` — Critical claims largely verified with Tier 1–2 evidence.

### YELLOW
- `epassport-application-status` — e-Passport claims rely on SPA/index excerpts; material gaps on fees, status fields, or mission rules.
- `epassport-enrollment-appointment` — Useful partial verification; gaps remain.
- `epassport-new-application` — Useful partial verification; gaps remain.
- `epassport-reissue` — Useful partial verification; gaps remain.
- `epassport-rpo-secretariat` — Useful partial verification; gaps remain.
- `epassport-urgent-super-express` — Useful partial verification; gaps remain.
- `passport-mrp-initial` — Core MRP portal facts verified; one REJECTED claim (5-day validity error).
- `passport-mrp-reissue` — Form 2 URL verified; reissue/lost/damaged document matrix incomplete.
- `police-passport-police-verification` — PV pathway partially corroborated; universal requirement and SB procedure page missing.
- `police-passport-verification` — Charter SLAs verified; linkage to e-Passport universal PV requirement not established.

### RED
- `epassport-fee-payment` — Critical fee amounts OUTDATED or only index-excerpt sourced; not safe for authoritative fee publication.

## Knowledge gaps

- `MISSING_MRP_FEE_SCHEDULE_MACHINE_READABLE` — MRP portal references bank deposit fees but structured fee table not extracted from official live source in this research pass.
- `MISSING_PASSPORT_CANCELLATION_SERVICE` — No dedicated canonical catalogue entry for passport cancellation; may be embedded in reissue/lost workflows.
- `MISSING_EXPATRIATE_UNIFIED_NATIONAL_PROCEDURE` — Mission-specific document lists (Dubai, Singapore, etc.) vary; no single DIP page consolidates all expatriate requirements.
- `MISSING_POLICE_PV_DEDICATED_OFFICIAL_URL` — Catalogue points to dip.gov.bd for passport police verification; no standalone SB passport PV procedure page captured.
- `MISSING_PAYMENT_GATEWAY_OFFICIAL_ENUM` — Current official list of online payment gateways (ekpay vs A-Challan vs others) not fully captured from live JS portal in this pass.
- `MISSING_DAMAGED_PASSPORT_DISTINCT_RULES` — Lost passport GD rules found; damaged passport distinct documentary rules not separately enumerated on Tier-1 pages reviewed.
- `MISSING_CURRENT_EPASSPORT_FEE_TIER1_SNAPSHOT` — Identified during Batch 2A independent verification.
- `MISSING_ABUDHABI_MISSION_EPASSPORT_PAGE` — Identified during Batch 2A independent verification.
- `MISSING_EPASSPORT_STATUS_PORTAL_FIELDS` — Identified during Batch 2A independent verification.
- `MISSING_TIER1_PV_REQUIREMENT_RULE_2025` — Identified during Batch 2A independent verification.

## Explicit non-actions

- Did not publish claims
- Did not start Batch 2B
- Did not deploy
- Did not modify frontend

## Machine-readable outputs

- `data/research/verification/batch-02a-passport/claims_verification.json`
- `data/research/verification/batch-02a-passport/conflicts_resolution.json`
- `data/research/verification/batch-02a-passport/knowledge_gaps.json`
- `data/research/verification/batch-02a-passport/service_readiness.json`
- `data/research/verification/batch-02a-passport/summary.json`
- `data/research/verification/batch-02a-passport/verification_policy.json`
- `data/research/verification/batch-02a-passport/source_evidence.json`

