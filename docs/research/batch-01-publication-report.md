# Batch 01 — Controlled Claim-Level Publication Report

**Date:** 2026-08-24  
**Batch:** `batch-01-identity-civil-registration`  
**Publication mode:** Local/development runtime only (no deploy, no public exposure)  
**Pipeline:** Independent verification → sync + gate → runtime DB

---

## Summary

| Metric | Count |
|--------|------:|
| Total claims (staging + verification) | 69 |
| Synced to runtime `claims` table | 69 |
| **Published claims** (`is_published=true`) | **27** |
| Skipped (gate / status / MVP seed / unresolved fee) | 42 |
| Gate rejections | 0 |
| Publication errors | 0 |

### Verification status preserved in runtime (not promoted)

| Status | Count |
|--------|------:|
| VERIFIED | 38 |
| PARTIALLY_VERIFIED | 19 |
| UNVERIFIED | 11 |
| REJECTED | 1 |

---

## Published runtime artifacts

| Artifact | Count | Notes |
|----------|------:|-------|
| `fees` (claim-linked) | 9 | Includes **1 calculator fee** (`USE_OFFICIAL_CALCULATOR`); **0** static NID 230/345/460 amounts |
| `checklist_items` (claim-linked) | 1 | Conditional document with preserved condition |
| `procedure_steps` (claim-linked) | 5 | Verified steps only |
| `service_links` (verified) | 1 | `https://everify.bdris.gov.bd/` |
| Practical layer (`claims`, `PRACTICAL`) | 1 | `civil-birth-registration::c-br-docs-practical` (PARTIALLY_VERIFIED — non-authoritative) |

### Published official claim categories (metadata + structured)

- **Fees:** birth/death copy & correction tiers; death registration tier fees; NID reissue calculator path
- **Requirements:** marriage registration conditional document (1)
- **Procedures:** NID correction/reissue/download steps (5)
- **URLs:** birth/death verification portal (1)
- **Metadata-only official claims:** eligibility, legal basis, availability, etc. (12)

---

## Skipped claims (by rule)

| Rule | Approx. count | Examples |
|------|--------------:|---------|
| `PARTIALLY_VERIFIED` / `UNVERIFIED` / `REJECTED` official | 26 | Portal deep-page claims, upload limits, registrar lists |
| MVP seed structured overwrite blocked | 11 | `birth-registration`, `nid-correction` fees/steps/checklist |
| Practical `UNVERIFIED` / `REJECTED` | 4 | News NID fee amounts, rejected BDT 500 guide claim |
| Unresolved NID static fee (`fee-amount-news`) | 3 | Skipped as `UNVERIFIED` + explicit block |
| Fee claim without structured value | 1 | — |

**Confirmed:** No `PARTIALLY_VERIFIED` or `UNVERIFIED` claim entered authoritative `Fee` / `ChecklistItem` MUST NEED fields. No `REJECTED` claim published.

---

## High-risk claim handling

| Risk area | Result |
|-----------|--------|
| NID static fees (230/345/460) | **Not published** — news/practical claims remain staging/runtime history only |
| NID official calculator | **Published** as `USE_OFFICIAL_CALCULATOR` with portal URL in fee notes |
| Birth late-fee conflict (BDT 500 guide) | **REJECTED** — not published |
| Birth/death official fee tiers | **Published** from Tier-1 ORGBDR Wayback + MOFA (VERIFIED claims) |
| Official URLs | Only verification-confirmed URL published (`everify.bdris.gov.bd`) |

---

## Post-publication service readiness (from published claims)

Readiness recalculated from runtime publication — **not** copied from pre-publication research labels.

| Readiness | Services |
|-----------|----------|
| **YELLOW** | 14 — partial official coverage (e.g. `civil-birth-death-verify`, NID correction family, marriage registration) |
| **RED** | 20 — no published official claims or critical gaps remain |
| **GREEN** | 0 — no service yet has full critical authoritative coverage after MVP-seed blocks |

Representative **YELLOW** services: `civil-birth-death-verify`, `civil-birth-registration-copy`, `civil-birth-registration-correction`, `nid-card-info-correction`, `nid-reissue-lost`.

Representative **RED** services: `civil-bdris-application-print`, `civil-marriage-registrar-muslim-list`, `nid-fee-calculator`, local attestation services without verified claims published.

---

## Provenance & evidence

- **Claims with evidence links:** 69/69 synced
- **Evidence rows with excerpt/locator:** 95
- **SourceVersion content hashes:** populated from verification snapshots where available (Tier-1 captures)
- **Provenance chain:** Claim → ClaimEvidence → SourceVersion → Source
- **Staging / verification history:** preserved (no silent deletion)

---

## Practical information layer

| Claim | Class | Status | Runtime |
|-------|-------|--------|---------|
| `civil-birth-registration::c-br-docs-practical` | PRACTICAL | PARTIALLY_VERIFIED | Stored on `claims` (`is_published=true`); **not** in `checklist_items` |
| NID news fee practical claims | PRACTICAL | UNVERIFIED | **Not published** |

---

## Remaining gaps

1. MVP seed services (`birth-registration`, `nid-correction`) — structured fees/steps/checklist blocked pending `allow_overwrite_seed` review  
2. BDRIS deep application pages (403) — portal/upload claims remain PARTIAL/UNVERIFIED  
3. Marriage/divorce registrar list services — UNVERIFIED (RED)  
4. NID static fee schedule — official calculator published; amounts remain unresolved  
5. Local attestation / DC services — no VERIFIED official claims to publish  
6. Hindu Marriage Act text extraction — related claims UNVERIFIED  

---

## Commands used

```bash
# Dry-run (sync + gate + rollback)
python scripts/publish_verified_knowledge.py --batch batch-01 --dry-run

# Apply (local runtime DB only)
python scripts/publish_verified_knowledge.py --batch batch-01 --publish --commit
```

---

## Publication errors

None. Transaction committed atomically.

---

## Explicit non-actions (per phase scope)

- No deployment or public hosting  
- No Batch 2 research  
- No verification decision changes  
- No frontend / RAG work  
- No invention of missing fees, documents, or procedure steps  
