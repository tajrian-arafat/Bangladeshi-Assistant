# Batch 2B — Controlled Publication Report

**Generated:** 2026-08-24T23:06:00+00:00  
**Batch:** `batch-02b-police-immigration`  
**Mode:** LOCAL/DEV ONLY — not deployed, not exposed externally

## Executive summary

Controlled publication applied the existing claim-level publication gate to Batch 2B (police + immigration). Of **77** verified research claims, **56–57** were eligible for authoritative publication; **6** fee records, **10** checklist items, **11** procedure steps, **3** verified URLs, and **1** practical note were written to the local SQLite runtime (`backend/data/bda.db`). Dry-run gate checks **A–G all PASS**. The unresolved PCC fee channel conflict was **not** reconciled by guessing.

## Pre-publication verification state

| Metric | Count |
|--------|------:|
| Total claims | 77 |
| VERIFIED | 60 |
| PARTIALLY_VERIFIED | 10 |
| UNVERIFIED | 6 |
| CONFLICTING | 1 |
| Official verified | 57 |
| Practical | 1 |
| Conflicts unresolved | 1 |
| Knowledge gaps open | 10 |
| Services GREEN / YELLOW / RED | 1 / 10 / 0 |

## Dry-run (`python scripts/publish_verified_knowledge.py --batch batch-02b-police-immigration --dry-run`)

| Category | Count |
|----------|------:|
| Eligible claims | 57 |
| Blocked / skipped | 27 |
| Rejected by gate | 5 |
| Fee records (dry-run) | 6 |
| Checklist items | 10 |
| Procedure steps | 11 |
| Verified URLs | 3 |
| Practical layer | 1 |

### Gate checks A–G (explicit validation)

Run: `python scripts/validate_batch02b_publication_dryrun.py`

| Check | Description | Result |
|-------|-------------|--------|
| **A** | PCC universal offline BDT 500 **not** published | PASS |
| **B** | Online PCC BDT 1,500 preserved (channel-specific) | PASS |
| **C** | Tier-5 “all GD types nationwide” **not** published as official | PASS |
| **D** | Unverified MRV fee matrix **not** published | PASS |
| **E** | Passport PV vs PCC SLAs remain separate services | PASS |
| **F** | No practical claim enters MUST_NEED authoritative layer | PASS |
| **G** | Every published fee has evidence + provenance | PASS |

### Published fee keys (dry-run)

- `police-clearance-certificate::c-online-fee-1500` — **BDT 1,500**, channel `online_pcc`, `not_universal: true`
- `police-cyber-support-women::c-pcsw-free` — BDT 0
- `police-expatriate-services::c-expat-charter-free` — BDT 0
- `police-firearms-license::c-firearms-charter-fee-na` — USE_OFFICIAL_CALCULATOR
- `police-general-diary::c-charter-gd-fee-free` — BDT 0
- `police-general-diary-online::c-charter-gd-fee-free` — BDT 0

**Not published:** `police-clearance-certificate::c-offline-fee-500-chalan` (blocklisted — CONFLICTING / not universal)

## Blocked / skipped claims (policy)

### Blocklisted (explicit publication blocklist)

| Claim key | Reason |
|-----------|--------|
| `police-clearance-certificate::c-offline-fee-500-chalan` | Unresolved channel conflict — offline BDT 500 not universal |
| `police-clearance-certificate::c-practical-fee-confusion` | Practical — not authoritative |
| `police-general-diary::c-gd-not-all-types-historically` | Tier-5 scope — not Tier 1–2 official |
| `police-general-diary-online::c-gd-all-types-expansion` | Tier-5 nationwide/all-types — not published as official |

### Rejected by publication gate

| Claim key | Gate reason |
|-----------|-------------|
| `police-employment-verification::c-ev-no-universal-rule` | `information_class` DISCOVERY (not OFFICIAL) |
| `police-nid-address-verification::c-nid-not-standalone-service-url` | DISCOVERY class |
| `police-passport-verification::c-pv-charter-sla` | DISCOVERY class on legacy staging metadata |
| `police-passport-verification::c-pv-district-scope` | DISCOVERY class |
| `migration-visa-application-dip::c-visa-foreign-embassy-not-in-scope` | Missing auditable SourceVersion content_hash |

### Skipped (non-VERIFIED status)

Representative skipped claims: GD portal URL (`PARTIALLY_VERIFIED` — `gd.police.gov.bd` unreachable), GD online registration/hotline (`UNVERIFIED`), employment verification charter fee/SLA (`PARTIALLY_VERIFIED`), MRV fees page (`UNVERIFIED` — scanned PDF unreadable), passport-police-verification pathway claims (`PARTIALLY_VERIFIED`).

## Local publication applied

```bash
python scripts/publish_verified_knowledge.py --batch batch-02b-police-immigration --publish --commit
```

### Post-publication runtime database (`backend/data/bda.db`)

| Table | Total rows (all batches) | Batch 2B notes |
|-------|-------------------------:|----------------|
| `claims` | 226 | 84 claims for police/immigration services |
| `fees` | 39 | 6 Batch 2B fee rows (see above) |
| `checklist_items` | 34 | PCC conditional docs, offline paper requirements |
| `procedure_steps` | 37 | PCC online/offline steps, PCSW, firearms |

### Batch 2B claim pipeline status in DB

| Status | Count |
|--------|------:|
| VERIFIED | 63 |
| PARTIALLY_VERIFIED | 14 |
| UNVERIFIED | 6 |
| CONFLICTING | 1 |

The single **CONFLICTING** claim is `police-clearance-certificate::c-offline-fee-500-chalan` — preserved as evidence, **not** published as authoritative fee.

### Verified URLs published

- `https://pcc.police.gov.bd/ords/r/pcc/pcc/9` — PCC online application
- `https://www.dip.gov.bd/` — DIP home / visa e-services hub
- PCSW citizen charter reference URL

**Not published:** `gd.police.gov.bd` (portal 502 during verification), `visa.gov.bd` (SSL failure)

## Policy enforcement highlights

### PCC fee — channel-specific rule

| Channel | Evidence | Publication |
|---------|----------|-------------|
| Online PCC | BDT 1,500, treasury `1-7301-0001-2681` | **VERIFIED**, published channel-specific only |
| Offline police.gov.bd | BDT 500, treasury `1-2201-0001-2681` | **CONFLICTING**, blocklisted — not universal |

Orchestrator behavior: ambiguous “Police clearance fee koto?” → **no single universal number**; explains channel discrepancy. “Online PCC fee koto?” → BDT 1,500 with online-channel warning only.

### Online GD

Published: free service (charter), SLA 1–7 days, existence of online channel (charter).  
**Not published:** Tier-5 “all GD types nationwide” expansion.

### Police verification services

Passport verification, PCC, and employment verification SLAs remain **separate service mappings** — not merged at publication layer.

### Immigration / visa

Published: DIP portal links, December 2024 official PDF–supported document claims.  
**Not published:** MRV fee amounts (unverified scanned PDF).

### Firearms license

Only authoritative government charter claims published; no practical/community layer as official.

## Post-publication service readiness

| Service | Readiness |
|---------|-----------|
| `police-cyber-support-women` | GREEN |
| `police-clearance-certificate` | YELLOW (CONFLICTED fee sibling in DB) |
| `police-employment-verification` | YELLOW |
| `police-expatriate-services` | YELLOW |
| `police-firearms-license` | YELLOW |
| `police-general-diary` | YELLOW |
| `police-general-diary-online` | YELLOW |
| `police-nid-address-verification` | YELLOW |
| `police-passport-police-verification` | YELLOW |
| `police-passport-verification` | YELLOW |
| `migration-visa-application-dip` | YELLOW |

## Unresolved knowledge gaps (preserved, not guessed)

1. PCC offline vs online fee reconciliation (1 unresolved conflict)
2. GD portal live verification (`gd.police.gov.bd` unreachable)
3. Nationwide online GD type coverage
4. MRV fee matrix (scanned PDF)
5. `visa.gov.bd` SSL / live portal verification
6. Employment verification numeric fee/SLA on charter
7. Passport-police-verification pathway detail
8. GD online registration NID requirement
9. GD digital copy seal policy
10. Foreign embassy visa scope edge case (gate-rejected)

## Regression (post-publication)

| Suite | Result |
|-------|--------|
| Batch 1 E2E (55 queries) | **100%** pass |
| Passport E2E (57 queries) | **100%** pass |
| 34-query routing benchmark | **100%** pass |
| `pytest` | **58 passed** |

No regression in earlier validated batches.

## Artifacts

| Path | Purpose |
|------|---------|
| `data/research/staging/batch-02b-police-immigration/` | Normalized staging claims |
| `data/research/verification/batch-02b-police-immigration/` | Independent verification artifacts |
| `scripts/normalize_batch02b_to_staging.py` | Staging normalizer |
| `scripts/validate_batch02b_publication_dryrun.py` | Gate A–G validator |
| `scripts/publish_verified_knowledge.py` | Publication CLI |
| `backend/app/application/knowledge/publisher.py` | Batch 2B blocklist + conflict-aware gate |

## Stop conditions respected

- Did **not** deploy
- Did **not** start Batch 3 / BRTA / Tax / Land
- Did **not** weaken verification rules
- Did **not** resolve PCC fee conflict by guessing
