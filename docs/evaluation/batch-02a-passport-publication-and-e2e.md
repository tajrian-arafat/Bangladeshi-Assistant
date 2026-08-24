# Batch 2A Passport — Controlled Publication & E2E Evaluation

**Generated:** 2026-08-24  
**Mode:** Local/development only — no deployment, no Batch 2B

## Executive summary

Step 13 merged Batch 2A independent verification with gap-closure results, ran a publication dry-run (all gate checks passed), applied **local-only** claim-level publication, and executed **57** realistic passport E2E queries.

| Phase | Result |
|-------|--------|
| Staging merge + supersession | 78 claims (55 original + 23 gap-closure) |
| Dry-run gate checks | **PASS** — no blockers |
| Local publication | **29** eligible official claims published |
| E2E pass rate | **15.8%** (9/57) — primary blocker: service retrieval, not hallucination |
| Hallucination class (E2E) | **0** |
| Citation failure class (E2E) | **0** |
| Accidental outdated fee publish | **0** |

## 1. Merged verification & versioning

Sources merged without overwriting historical records:

- `data/research/verification/batch-02a-passport/claims_verification.json` (55 claims)
- `data/research/verification/batch-02a-passport-gap-closure/new_claims.json` (23 claims)

Staging artifact: `data/research/staging/batch-02a-passport/` (via `scripts/normalize_batch02a_to_staging.py`).

### Supersession pairs (historical → current)

| Historical (OUTDATED / superseded) | Current (VERIFIED, July 2026 browser evidence) |
|-----------------------------------|-----------------------------------------------|
| `epassport-fee-payment::c-fee-48p-5y-regular` | `gap-closure::c-fee-domestic-48p_5y-regular-current` |
| `epassport-fee-payment::c-fee-48p-10y-regular` | `gap-closure::c-fee-domestic-48p_10y-regular-current` |
| `epassport-fee-payment::c-fee-64p-5y-regular` | `gap-closure::c-fee-domestic-64p_5y-regular-current` |
| `epassport-fee-payment::c-fee-64p-10y-regular` | `gap-closure::c-fee-domestic-64p_10y-regular-current` |

Payment method: prior `c-payment-ekpay-official` research claim remains **unpublished**; current verified gateways are `A-Challan`, `DGePay`, `ShurjoPay` via `gap-closure::c-payment-gateways-achallan-dgepay-shurjopay`.

DB lineage uses `supersedes_claim_id` / `superseded_by_claim_id` on the `claims` table.

## 2. Publication dry-run

Command:

```bash
python scripts/publish_verified_knowledge.py --batch batch-02a-passport --dry-run --sync-claims --publish
```

### Dry-run audit

| Metric | Count |
|--------|------:|
| Claims synced | 78 |
| Eligible for publication | 29 |
| Skipped (non-VERIFIED / superseded / blocklisted) | 49 |
| Rejected by gate | 2 |
| Fees (would publish) | **12** |
| Checklist items | 3 |
| Procedure steps | 3 |
| Official URLs | 3 |
| Practical notes | 2 |
| Superseded historical fees skipped | 4 |

### Gate verification checklist

| Check | Result |
|-------|--------|
| No March 2023 OUTDATED fee published as current | **PASS** (4 `skip_superseded`) |
| No universal Super Express rule published | **PASS** (conditional / partial only) |
| No Abu Dhabi WEFF surcharge published | **PASS** (`skip_blocklisted` / UNVERIFIED) |
| No MRP historical fee as current | **PASS** (OUTDATED gap-closure claim not published) |
| No ekpay as authoritative payment method | **PASS** (blocklisted / superseded) |
| Every published claim has provenance chain | **PASS** |
| No practical claim in MUST NEED | **PASS** |

Full dry-run JSON: `data/evaluation/batch-02a-passport/publication_summary.json`

## 3. Local publication applied

Command:

```bash
python scripts/publish_verified_knowledge.py --batch batch-02a-passport --sync-claims --publish --commit
```

### Published claim counts by type

| Type | Published |
|------|----------:|
| Domestic e-Passport fees (full matrix) | 12 |
| Documents (checklist) | 3 |
| Procedure steps | 3 |
| Application URLs | 3 |
| Practical tips | 2 |
| **Total eligible official** | **29** |

### July 2026 domestic fee matrix (BDT, incl. 15% VAT)

Evidence: browser-rendered `https://www.epassport.gov.bd/instructions/passport-fees` — **Last updated: 12 July 2026** (`source_snapshots/epassport_fees.txt`).

| Pages | Validity | Regular | Express | Super Express |
|------:|---------|--------:|--------:|--------------:|
| 48 | 5y | 4,025 | 6,325 | 8,625 |
| 48 | 10y | 5,750 | 8,050 | 10,350 |
| 64 | 5y | 6,325 | 8,625 | 12,075 |
| 64 | 10y | 8,050 | 10,350 | 13,800 |

Each fee row retains `claim_id`, `service_id` (`epassport-fee-payment`), structured variant metadata, `source_version_id`, evidence snapshot hash, and `verified_at`.

### Explicitly NOT published as authoritative

- PARTIALLY_VERIFIED / UNVERIFIED / OUTDATED / REJECTED claims (except historical records retained in DB)
- March 2023 indexed fee claims (superseded, not current)
- ekpay payment method
- Universal police verification rule
- Universal Super Express interpretation
- MRP fee amounts (no current Tier-1 table)
- Abu Dhabi WEFF 10% surcharge
- Singapore broken URL mission rules

## 4. E2E evaluation (57 queries)

Artifacts:

- `data/evaluation/batch-02a-passport/queries.json`
- `data/evaluation/batch-02a-passport/results.jsonl`
- `data/evaluation/batch-02a-passport/summary.json`
- `data/evaluation/batch-02a-passport/failures.json`

Command:

```bash
python scripts/evaluate_batch02a_e2e.py
```

### Query coverage

Bangla, English, Banglish, misspellings, short/vague queries, follow-ups, fees, documents, eligibility, Super Express, MRP vs e-Passport, police verification, payment methods, status, minors, lost/damaged/correction, expatriate/mission cases, unsupported-claim probes, citation tests, and versioning tests.

### Results

| Metric | Value |
|--------|------:|
| Total | 57 |
| Passed | 9 |
| Failed | 48 |
| Pass rate | 15.8% |
| Hallucination failures | **0** |
| Citation failures | **0** |
| Retrieval failures | 38 |
| Language failures | 3 |

### Unsupported-claim behavior

Queries probing MRP fees, Abu Dhabi surcharge, universal PV, ekpay, and fake URLs: **no hallucination-class failures**. Appropriate uncertainty is inconsistent because **service retrieval** often routes to the wrong passport variant (e.g. fee queries matching `passport-mrp-initial` instead of `epassport-fee-payment`).

### Versioning test

When the correct service is retrieved, published July 2026 fee claims are available in DB. Retrieval misrouting prevents most fee-specific E2E cases from reaching the published fee rows — a **retrieval-layer** issue, not a publication regression.

## 5. Service readiness (post-publication)

| Service | Readiness |
|---------|-----------|
| epassport-new-application | GREEN |
| epassport-fee-payment | GREEN |
| epassport-urgent-super-express | GREEN |
| passport-mrp-initial | GREEN |
| passport-mrp-reissue | GREEN |
| police-passport-police-verification | GREEN |
| epassport-reissue | YELLOW |
| passport-application-status | YELLOW |
| epassport-enrollment-appointment | RED |
| epassport-application-status | RED |
| epassport-rpo-secretariat | RED |
| police-passport-verification | RED |

## 6. Remaining knowledge gaps

1. Universal police verification Tier-1 rule (CONDITIONAL mission evidence only)
2. Super Express eligibility conflict: June 2026 “any citizen” vs Oct 2022 MRP/address-change NOTE
3. MRP current fee schedule — DIP page last updated Feb 2017, no machine-readable table
4. Abu Dhabi WEFF 10% surcharge — CMS shell empty
5. Singapore mission e-passport rules URL returns 404
6. Damaged passport distinct rules not separately enumerated on Tier-1 instructions

## 7. Publication vs E2E targets

| Target | Publication | E2E |
|--------|:-----------:|:---:|
| 0 hallucinations (published as current fact) | ✅ | ✅ (0 HALLUCINATION class) |
| 0 citation failures (gate) | ✅ | ✅ (0 CITATION_BUG class) |
| 0 unsupported current-fee answers published | ✅ | ⚠️ retrieval prevents fee answers |
| 0 accidental outdated claim publication | ✅ | ✅ |

## 8. Stop condition

Step 13 complete. **Stopped** — no Batch 2B, no BRTA, no deploy, no frontend redesign, no vector RAG.

### Files added/updated in this step

- `scripts/normalize_batch02a_to_staging.py`
- `scripts/evaluate_batch02a_e2e.py`
- `backend/app/application/knowledge/verification_sync.py` (batch-02a + gap-closure merge)
- `backend/app/application/knowledge/publisher.py` (batch-02a staging, supersession, blocklist, gaps fix)
- `data/research/staging/batch-02a-passport/*`
- `data/evaluation/batch-02a-passport/*`
