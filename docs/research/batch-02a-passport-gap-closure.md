# Batch 2A — Targeted Passport Gap Closure

**Date:** 2026-08-24  
**Agent:** `cursor-cloud-agent`  
**Layer:** `data/research/verification/batch-02a-passport-gap-closure` (STAGING ONLY)  
**Published to runtime:** No

## Scope

Targeted investigation of highest-priority unresolved gaps from Step 11 verification. Did not re-verify all 55 original claims. Created **versioned new claims**; original claim records unchanged.

## Gap investigation summary

- Gaps investigated: **11**
- Resolved: **2**
- Partially resolved: **4**
- Unresolved / open: **5**
- New sources: **8**
- New claims: **23**

## Priority 1 — Current e-Passport fee (CRITICAL)

**RESOLVED** via `puppeteer_headless_chrome` render of [https://www.epassport.gov.bd/instructions/passport-fees](https://www.epassport.gov.bd/instructions/passport-fees).

- **Last updated:** 12 July 2026 (not March 2023 index metadata)
- Domestic BDT tiers verified at official listed amounts (48p/64p × 5y/10y × regular/express/super express)
- Mission USD tiers captured in browser snapshot
- Prior Step 11 OUTDATED fee claims superseded by new `gap-closure::c-fee-domestic-*-current` claims

## Priority 2 — Police verification (HIGH)

**PARTIALLY RESOLVED — classification: CONDITIONAL**

- Tier-2 Dubai: first-time passport/e-Passport → PV mandatory in Bangladesh
- Tier-2 Dubai: reissue with no mismatch → PV may not be required
- Tier-1 onboarding: police station selection verified (browser render)
- No Tier-1 DIP circular stating universal vs abolished PV captured

## Priority 2 — Abu Dhabi mission (HIGH)

**PARTIALLY RESOLVED**

- Static CMS URL located: `abudhabi.mofa.gov.bd/pages/static-pages/6952667d35ce18e1c05a9876`
- Page title present; **instructional body empty** in browser capture
- Legacy `/en/site/page/E-Passport-Issue--Reissue:` → 404
- WEFF 10% surcharge claim remains **UNVERIFIED**

## Priority 3 — MRP fees, status portal, payment gateway

| Topic | Outcome |
|-------|---------|
| MRP fee schedule | **UNRESOLVED** — DIP page Feb 2017, no fee table in render |
| e-Passport status | **PARTIAL** — FAQ: Application ID or Online Registration ID + DOB; status route not accessible |
| MRP status | **VERIFIED** — Enrolment ID + DOB + captcha at passport.gov.bd/OnlineStatus.aspx |
| Payment gateway | **RESOLVED** — A-Challan, DGePay, ShurjoPay (July 2026 fee page) |

## Priority 4 — Lower gaps

- **Lost passport:** GD rules verified in Aug 2026 instructions
- **Damaged passport:** No distinct rules found — gap remains open
- **Singapore mission e-passport URL:** Confirmed 404
- **Cancellation service / unified expatriate procedure / PV dedicated URL:** Not resolved

## New conflicts

1. **Fee freshness** — RESOLVED (July 2026 browser page vs March 2023 index)
2. **Payment gateway** — RESOLVED (ekpay → A-Challan/DGePay/ShurjoPay on current page)
3. **Super Express eligibility** — UNRESOLVED (June 2026 'any citizen' vs Oct 2022 MRP-only NOTE)

## Updated service readiness

- GREEN: **1**
- YELLOW: **11**
- RED: **0** (`epassport-fee-payment` upgraded RED→YELLOW)

## Evidence limitations

- epassport.gov.bd API endpoints return 403 to curl; browser render required
- Status check dedicated route 404/403; FAQ API dated 2020 for field names
- Abu Dhabi/Singapore mission CMS pages incomplete or 404
- Bright Data MCP unavailable (401)

## Explicit non-actions

- Did not publish claims
- Did not run `publish_verified_knowledge.py`
- Did not start Batch 2B
- Did not deploy or modify frontend

## Machine-readable outputs

- `data/research/verification/batch-02a-passport-gap-closure/gap_investigations.json`
- `data/research/verification/batch-02a-passport-gap-closure/new_claims.json`
- `data/research/verification/batch-02a-passport-gap-closure/new_sources.json`
- `data/research/verification/batch-02a-passport-gap-closure/conflicts_resolution.json`
- `data/research/verification/batch-02a-passport-gap-closure/knowledge_gaps.json`
- `data/research/verification/batch-02a-passport-gap-closure/service_readiness.json`
- `data/research/verification/batch-02a-passport-gap-closure/summary.json`
- `data/research/verification/batch-02a-passport-gap-closure/source_snapshots/`
