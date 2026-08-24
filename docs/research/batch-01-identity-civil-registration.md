# Batch 1 Research Report — Identity & Civil Registration

**Batch ID:** `batch-01-identity-civil-registration`  
**Researched at:** 2026-08-24  
**Catalogue version:** `1.0.0-finalized`  
**Structured output:** `data/knowledge/batch-01/`  
**Builder:** `scripts/build_batch01_knowledge.py`

---

## 1. Scope & selection method

Batch 1 was selected from the **finalized master catalogue** (`data/service_catalogue/services.json`), not from an illustrative example list.

**Inclusion rules**

- Status must be **CONFIRMED** (UNVERIFIED catalogue entries are excluded from authoritative research).
- Category / subject must belong to Identity, Civil Registration, NID/voter identity, birth/death registration and related BDRIS flows, marriage/divorce registration, or closely related civil certificates/attestations used for identity pathways.

**Excluded from this batch**

- All 10 catalogue **UNVERIFIED** services (none fall in this batch).
- Umbrella DC citizen-charter pages, election nomination services, generic UNO/Nothi workflows.
- Non-identity certificate domains deferred to later batches.

**Result:** **34 CONFIRMED** services researched.

| Category (catalogue) | Count |
|----------------------|------:|
| `identity` | 13 |
| `civil_registration` | 14 |
| `certificates` | 5 |
| `local_government` | 2 |

---

## 2. Services researched

### Identity / NID / voter (13)

| Service ID | Research status | KQS |
|------------|-----------------|----:|
| `nid-new-voter-registration` | SUBSTANTIAL | 80.5 |
| `nid-online-account-registration` | SUBSTANTIAL | 80.0 |
| `nid-reissue-lost` | SUBSTANTIAL | 79.7 |
| `nid-voter-area-change` | SUBSTANTIAL | 79.5 |
| `nid-claim-account` | SUBSTANTIAL | 78.8 |
| `nid-fee-calculator` | SUBSTANTIAL | 78.0 |
| `nid-download-copy` | SUBSTANTIAL | 77.5 |
| `nid-card-info-correction` | SUBSTANTIAL | 76.5 |
| `nid-combined-correction` | SUBSTANTIAL | 76.5 |
| `nid-other-info-correction` | SUBSTANTIAL | 76.5 |
| `nid-photo-signature-appointment` | PARTIAL | 72.0 |
| `nid-expatriate-registration` | PARTIAL | 69.5 |
| `identity-voter-slip-download` | PARTIAL | 64.8 |

### Civil registration / BDRIS / marriage–divorce (14)

| Service ID | Research status | KQS |
|------------|-----------------|----:|
| `civil-birth-death-verify` | SUBSTANTIAL | 75.2 |
| `civil-birth-registration` | SUBSTANTIAL | 71.8 |
| `civil-bdris-application-print` | PARTIAL | 70.2 |
| `civil-marriage-registration` | PARTIAL | 70.5 |
| `civil-death-registration` | PARTIAL | 69.5 |
| `civil-birth-registration-copy` | PARTIAL | 69.2 |
| `civil-death-registration-copy` | PARTIAL | 69.2 |
| `civil-marriage-registrar-muslim-list` | PARTIAL | 67.2 |
| `civil-marriage-registrar-hindu-list` | PARTIAL | 67.2 |
| `civil-birth-registration-correction` | PARTIAL | 65.8 |
| `civil-death-registration-correction` | PARTIAL | 65.8 |
| `civil-divorce-registration` | PARTIAL | 63.0 |
| `civil-birth-registration-duplicate-cancel` | PARTIAL | 60.5 |
| `civil-death-registration-duplicate-cancel` | PARTIAL | 60.5 |

### Local / DC identity-adjacent certificates (7)

| Service ID | Research status | KQS |
|------------|-----------------|----:|
| `local-character-certificate` | PARTIAL | 52.2 |
| `local-death-certificate-union` | PARTIAL | 52.2 |
| `local-nationality-certificate` | PARTIAL | 52.2 |
| `local-passport-attestation` | PARTIAL | 52.2 |
| `local-voter-transfer-attestation` | PARTIAL | 52.2 |
| `dc-guardianship-certificate` | PARTIAL | 52.2 |
| `dc-attestation-photocopy` | PARTIAL | 52.2 |

---

## 3. Research completeness summary

| Metric | Value |
|--------|------:|
| Services researched | 34 |
| Fully researched (`COMPLETE` / publication-ready with no critical gaps) | **0** |
| SUBSTANTIAL (strong Tier-1 coverage; remaining gaps documented) | **12** |
| PARTIAL (identity/URLs known; docs/fees/geo incomplete) | **22** |
| Average Knowledge Quality Score | **67.7** |

No service is marked fully researched. Even high-KQS NID services still lack a retrieved EC fee gazette PDF and/or hard SLA text.

---

## 4. Structured knowledge storage

Primary database is structured JSON (not prose):

```
data/knowledge/batch-01/
├── metadata.json
├── sources.json
├── claims.json
├── conflicts.json
├── services_index.json
└── services/<service_id>.json
```

Each service record supports (where populated): identity fields, eligibility, requirements with **MUST / CONDITIONAL / RECOMMENDED / N/A**, fees with conditions, procedures, official vs practical layers on claims, geography hooks, related services, missing_information, manual_review_required, and `knowledge_quality` scoring.

### Document requirement engine

Requirements are **not** flat lists. Example pattern (NID new registration):

- **MUST** — printed online form (always for that path).
- **CONDITIONAL** — SSC *if* applicant has SSC/equivalent; birth registration *if* used as age proof path; guardian docs *if* minor pathway, etc.
- **RECOMMENDED** — extras that help but are not elevated to MUST without Tier-1 proof.
- Practical anecdotes remain tagged `layer: PRACTICAL` with `do_not_promote_to_must: true`.

### Official vs practical

Claims and rejection notes carry an explicit layer:

- **OFFICIAL** — responsible authority (Tier 1–2 preferred).
- **PRACTICAL** — news/guides/community; usable for UX warnings, never auto-MUST.

---

## 5. Sources used

| Metric | Count |
|--------|------:|
| Total sources stored | **21** |
| Official Tier 1–2 | **15** (Tier 1: 14, Tier 2: 1) |
| Practical / community / news / blogs (Tier 5+) | **6** |

### Primary Tier-1 / Tier-2 authorities

- Bangladesh Election Commission NID portal — `services.nidw.gov.bd` (FAQ, fees calculator, account registration)
- NID Wing — `nidw.gov.bd` (including duplicate NID page)
- BDRIS — `bdris.gov.bd` (birth application, home, verify flows)
- Office of the Registrar General — `orgbdr.gov.bd` (helpline **16152**)
- Marriage portal — `marriage.gov.bd` (+ CRVS user manual PDF referenced; text not fully extracted this pass)
- MOFA mission notice republishing LGD-referenced BDR fee schedule (Tier 2 proxy for LGD schedule)

### Supporting Tier 5–6

- News: TBS (NID correction friction), Dhaka Tribune / similar reapply windows, secondary NID fee reporting
- Professional guides / blogs: LegalClarity (birth fees — **conflict**), Eshoi/rejection guides, secondary fee tables

Bright Data scrape tools returned HTTP 401 in this environment; research used direct fetches / search retrieval instead. Source URLs and retrieval dates are stored per source record (`retrieved_at`: 2026-08-24).

---

## 6. Verified information (high confidence)

Non-exhaustive; full claim→evidence chains are in `claims.json` + per-service files.

### NID / EC

- Online account registration and application pathway via `services.nidw.gov.bd`.
- Age pathway: NID from age 10+; voter inclusion rules tied to age ≥18 as of 1 January (FAQ).
- Correction / reissue / area change are distinct portal workflows; incomplete applications may be cancelled (FAQ).
- Fee calculator is the official fee surface; static amounts were **not** treated as official MUST from news.
- Helpline / NID Wing existence confirmed via official sites.

### Birth & death (BDRIS / ORGBDR)

- Online birth application at BDRIS; uploads typically JPG/PNG with size limits noted on application UI.
- Helpline **16152** associated with ORGBDR communications.
- Domestic late-registration fee schedule preferred from LGD-referenced / MOFA-republished table:
  - Free within 45 days
  - BDT 25 after 45 days up to 5 years
  - BDT 50 after 5 years
- Correction fee distinction preferred: DOB correction BDT 100 vs other corrections BDT 50 (MOFA English notice) — see conflicts.

### Marriage

- National marriage registration portal exists (`marriage.gov.bd`); Muslim/Hindu registrar lists are catalogue services with portal anchors.
- Detailed citizen fee/document matrix remains incomplete pending full CRVS manual / UI extraction.

### Local certificates

- Confirmed as real service *types* delivered by Union Parishad / Pourashava / City Corporation / DC offices.
- **No nationally uniform fee/document schedule** verified — geographic variance is the correct model.

---

## 7. Uncertain / unverified information

| Area | Status |
|------|--------|
| Exact NID correction/reissue fee amounts (230/345/460 news figures) | UNVERIFIED as official; use calculator |
| First-time NID issuance fee (if any) beyond calculator | Missing / needs EC gazette |
| Full BDRIS Guidelines 2021 document matrix | Not extracted this pass |
| Payment channels for domestic BDR fees (cash vs online) | Incomplete |
| Marriage/divorce citizen fee schedules | Incomplete |
| Expatriate NID biometric mission workflows | Partial |
| Per-LGI character/nationality/attestation checklists | Local-only; not nationally verified |
| Voter slip dedicated download URL/steps | Incomplete beyond account benefits notes |
| Processing SLAs for many correction paths | Often absent on Tier-1 pages |

**Claims requiring manual verification:** **5** (`verification_status: UNVERIFIED` in `claims.json`).

---

## 8. Conflicts found

**6 conflict records** in `conflicts.json` (some topic-duplicated across sibling services):

| Conflict ID | Topic | Resolution |
|-------------|-------|------------|
| `conf-br-fee-10y` | Birth late fee after 10 years: LGD/MOFA BDT 50 after 5y vs LegalClarity BDT 500 after 10y | **UNRESOLVED** — prefer LGD-referenced schedule; do **not** publish 500 as official |
| `conf-bdris-corr-other-fee` (birth + death correction) | Other-info correction BDT 50 vs secondary BDT 100 claims | Prefer MOFA DOB-100 / other-50 split; mark blog noise |
| `conf-nid-*-correction-fee-amount` (3 services) | Official calculator vs news BDT 230/345/460 | **UNRESOLVED** — advise calculator; do not hardcode news as MUST |

No silent winner was chosen where Tier-1 static confirmation was missing.

---

## 9. Practical findings (not promoted to MUST)

- NID correction applicants report long waits, repeated office visits, and document mismatch friction (TBS / guides) — **PRACTICAL**.
- Common rejection anecdotes: blurred scans, cross-document name mismatch, missing birth certificate, unpaid/unverified fees — stored as PRACTICAL with `do_not_promote_to_must`.
- Office staff may request extras beyond published lists for local certificates — must stay geographic/practical until LGI schedule verified.
- Secondary sites sometimes inflate or invent fee tiers; treated as conflict/noise.

---

## 10. Missing information (major)

1. EC official fee schedule gazette / calculator output capture for NID corrections & reissue.
2. BDRIS Guidelines 2021 full extraction (documents, fees, duplicate cancel rules).
3. Marriage.gov.bd / CRVS manual citizen-facing fee & document matrix.
4. Divorce registration document/fee checklist.
5. Geographic_availability instances for all local certificate services (per UP/CC/DC).
6. Expatriate NID mission checklists.
7. Authoritative processing-time statements where FAQ is silent.
8. Payment method matrices (bKash, bank, cash counters) per service path.

---

## 11. Knowledge Quality Score

### Formula (aligned to `docs/KNOWLEDGE_QUALITY_FRAMEWORK.md`)

```
KQS = 0.25×Coverage + 0.25×Authority + 0.20×Freshness + 0.15×Consistency + 0.15×Usability
```

Dimensions are 0–100. Usability cold-start uses neutral **50** (no eval harness feedback yet).

Builder notes document per-service dimension inputs under `knowledge_quality` in each service JSON.

| Aggregate | Value |
|-----------|------:|
| Average KQS | **67.7** |
| Highest | 80.5 (`nid-new-voter-registration`) |
| Lowest | 52.2 (local/DC certificate cluster) |

High KQS does **not** hide missing evidence: `missing_information` and `manual_review_required` remain populated on stronger services.

---

## 12. Manual-review requirements

Services with explicit `manual_review_required` notes include (representative):

- Attach Guidelines 2021 + official BDR fee gazette PDF (`civil-birth-registration`).
- Confirm EC fee schedule via gazette or controlled calculator capture (NID correction trio).
- Confirm first-time NID issuance fee vs correction/reissue-only fees.
- Populate `geographic_availability` with verified LGI URLs/fees before publishing local certificates as authoritative national answers.

**Publication gate recommendation:** do not mark any Batch 1 service ACTIVE for hard MUST answers until listed manual reviews for that service are closed.

---

## 13. Safety compliance checklist

- [x] No fabricated fees/URLs/procedures/evidence
- [x] UNVERIFIED catalogue services not researched as authoritative
- [x] Tier 7 / practical not auto-converted to MUST
- [x] Conflicts recorded, not silently resolved
- [x] Structured knowledge primary; report is secondary
- [x] Batch 2 not started; UI/architecture not redesigned

---

## 14. Batch stop condition

**STOP after Batch 1.** No Batch 2 research was performed.

---

## Appendix A — End-of-batch metrics (requested)

1. **Services researched:** 34  
2. **Services fully researched:** 0  
3. **Services with missing information:** 22+ with explicit `missing_information` entries (all 34 have at least residual gaps vs full checklist)  
4. **Conflicts found:** 6  
5. **Number of sources:** 21  
6. **Number of official sources (Tier 1–2):** 15  
7. **Number of practical/community sources (Tier 5+):** 6  
8. **Claims requiring manual verification:** 5  
9. **Average Knowledge Quality Score:** 67.7  
10. **Major research gaps:** EC fee gazette; BDRIS Guidelines 2021 full extract; marriage/divorce fee-doc matrices; per-LGI certificate schedules; expatriate NID workflows; processing SLAs
