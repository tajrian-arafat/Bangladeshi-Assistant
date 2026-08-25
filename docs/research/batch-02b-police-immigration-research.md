# Batch 2B Research Report — Police + Immigration Services

**Batch ID:** `batch-02b-police-immigration`  
**Researched at:** 2026-08-24  
**Catalogue version:** `1.0.0-finalized` (464 CONFIRMED services)  
**Phase:** RESEARCH ONLY — verification and publication **not started**  
**Raw artifacts:** `data/research/raw/batch-02b-police-immigration/`  
**Generator:** `scripts/generate_batch02b_police_immigration_research_artifacts.py`

> **Guardrail:** All claims carry `pipeline_status: DISCOVERED` and
> `verification_status: PENDING_INDEPENDENT_VERIFICATION`. Nothing from Batch 2B
> is publication-ready. OFFICIAL SLA and PRACTICAL wait-time/community experience
> are kept separate. Police verification rules are scoped per service — not
> generalized from the e-Passport pathway.

---

## 1. Scope and selection method

Batch 2B was selected from the **finalized canonical catalogue**
(`data/service_catalogue/final/services.json`), covering confirmed police,
police clearance, GD, police verification, Special Branch citizen services, and
Bangladesh-government immigration (visa) services.

### Inclusion rules

- Status must be **CONFIRMED**.
- Service must relate to: police clearance, GD, police verification, SB/citizen
  charter police services, expatriate police support, firearms licensing (SB), or
  DIP visa application (Bangladesh as issuing authority).
- Passport-pathway police verification services are included with **extended**
  batch-2B research cross-referencing batch-2A partial claims.

### Exclusion rules (noted, not researched in this batch)

| Service ID | Reason |
|------------|--------|
| `epassport-*`, `passport-mrp-*` | Passport issuance; batch-02a |
| `migration-e-apostille`, `mofa-*` | MOFA attestation; separate batch |
| `bida-work-permit-security-clearance` | BIDA digital work-permit clearance |
| `expatriate-emigration-clearance` | BMET emigration clearance |

### Catalogue scan result

**11 in-scope CONFIRMED services** across `police` (8), `passport_immigration`
(1 visa), `expatriate` (1), and `licences` (1 firearms). No new canonical
services were created. `police-general-diary` and `police-general-diary-online`
share the same portal URL — flagged as a catalogue relationship gap, not resolved
in research phase.

---

## 2. Services researched

| Service ID | English name | Category | Research status | Claims |
|------------|--------------|----------|-----------------|-------:|
| `police-clearance-certificate` | Police Clearance Certificate (PCC) | police | SUBSTANTIAL | 22 |
| `police-general-diary` | Online General Diary (GD) | police | PARTIAL | 6 |
| `police-general-diary-online` | Online GD Filing | police | SUBSTANTIAL | 10 |
| `police-cyber-support-women` | Police Cyber Support for Women (PCSW) | police | SUBSTANTIAL | 5 |
| `police-employment-verification` | Employment Verification | police | PARTIAL | 5 |
| `police-nid-address-verification` | Address/NID-based Police Verification | police | PARTIAL | 3 |
| `police-passport-police-verification` | Passport Police Verification (SB) | police | PARTIAL | 4 |
| `police-passport-verification` | Passport Verification (district charter) | police | PARTIAL | 5 |
| `migration-visa-application-dip` | Visa Application (DIP) | passport_immigration | PARTIAL | 7 |
| `police-expatriate-services` | Expatriate Cell Services | expatriate | SUBSTANTIAL | 5 |
| `police-firearms-license` | Firearms License | licences | PARTIAL | 4 |

**Responsible authorities:** Ministry of Home Affairs → Bangladesh Police (PCC,
GD, verification, PCSW, Expatriate Cell, firearms) and Department of
Immigration and Passports (visa/MRV).

---

## 3. Sources

### Tier 1–2 (official — primary for high-risk claims)

| Source ID | Tier | URL / artifact | Used for |
|-----------|-----:|----------------|----------|
| `src-pcc-portal` | 1 | https://pcc.police.gov.bd/ords/r/pcc/pcc/9 | Online PCC fees, eligibility, workflow, documents |
| `src-gd-portal` | 1 | https://gd.police.gov.bd/ | GD portal URL (snapshot failed — gap) |
| `src-dip-home` | 1 | https://www.dip.gov.bd/ | Visa e-service links |
| `src-dip-visa-online` | 1 | DIP Apply Visa Online page | visa.gov.bd portal reference |
| `src-visa-gov-bd` | 1 | https://www.visa.gov.bd/ | MRV application portal (snapshot failed — gap) |
| `src-dip-visa-types` | 1 | DIP visa types/documents page | Visa document matrix (stale 2022) |
| `src-dip-mrv-fees` | 1 | DIP MRV fee page | Fee schedule reference |
| `src-police-charter` | 2 | Citizen charter | SLAs, fees (where stated), service list |
| `src-police-pcc-offline-page` | 2 | police.gov.bd PCC page | Offline/paper PCC procedure |
| `src-police-sb` | 2 | Special Branch page | SB role context |
| `src-batch-02a-passport-research` | 2 | batch-02a artifacts | e-Passport PV cross-reference |

**Tier 1–2 count:** 11 sources in metadata (of 14 total).

### Tier 5–6 (discovery / practical only)

| Source ID | Tier | Role |
|-----------|-----:|------|
| `src-bss-online-gd-rollout` | 5 | Online GD nationwide rollout timing (Sep 2025) |
| `src-tbs-online-gd-expansion` | 5 | All-types GD vs lost-and-found-only history |
| `src-unb-pcc-guide` | 5 | PRACTICAL — older Tk 500 fee reference |

### Source snapshots captured

`data/research/raw/batch-02b-police-immigration/source_snapshots/`:

- `pcc_portal_home.html` — full online PCC terms, fees, steps
- `police_pcc_page.html` — offline PCC instructions
- `police_charter.html` — citizen charter
- `police_sb.html`, `dip_home.html`, `dip_visa_online.html`, `dip_visa_types.html`, `dip_mrv_fees.html`

**Not captured:** `gd.police.gov.bd`, `visa.gov.bd` (SSL/connectivity failure in research environment).

---

## 4. Claims summary

| Metric | Count |
|--------|------:|
| **Total atomic claims** | **77** |
| OFFICIAL | 67 |
| DISCOVERY | 9 |
| PRACTICAL | 1 |
| Conflicts recorded | 5 |
| Knowledge gaps | 10 |

All claims: `pipeline_status: DISCOVERED`, `verification_status: PENDING_INDEPENDENT_VERIFICATION`.

### High-risk claim coverage

| Topic | Primary official sources | Notes |
|-------|-------------------------|-------|
| PCC online fee | PCC portal | BDT 1,500 + code 1-7301-0001-2681 |
| PCC offline fee | police.gov.bd PCC page | BDT 500 + code 1-2201-0001-2681 — **conflict** |
| PCC official SLA | Citizen charter | 3–7 days (online clearance row) |
| Passport verification SLA | Citizen charter | Normal 15–21 days; urgent 7 days |
| GD official SLA | Citizen charter | 1–7 days; free |
| GD online scope | Tier 5 PHQ statements | All-types expansion 2025 — pending Tier 1 snapshot |
| Visa application URL | DIP → visa.gov.bd | Portal workflow not snapshotted |
| Employment/firearms fees | Citizen charter | "Government fee" without numeric amount — **gap** |

### Conditional requirements (examples)

| Condition | Requirement class | Service |
|-----------|-------------------|---------|
| Passport lacks address | CONDITIONAL | NID/birth/ward councillor certificate |
| Applicant abroad (BD national) | CONDITIONAL | High Commission attested passport |
| Applicant abroad (foreign passport) | CONDITIONAL | Justice of Peace attestation |
| Representative collection | CONDITIONAL | Authorization letter + collector NID |
| Purpose = domestic employment in BD | CONDITIONAL / restriction | Use DSB/CSB — not online PCC portal |
| Destination = Spain | CONDITIONAL | Extra photos to Home Ministry |
| Urgent passport verification | CONDITIONAL | 7-day charter SLA |

### Police verification scope classification

| Service | Scope | Rationale |
|---------|-------|-----------|
| `police-passport-police-verification` | SERVICE_SPECIFIC | e-Passport onboarding / SB pathway only |
| `police-passport-verification` | LOCATION_SPECIFIC | District/metro SB charter service |
| `police-employment-verification` | SERVICE_SPECIFIC | Employer-driven; no universal doc list |
| `police-nid-address-verification` | CONDITIONAL | When passport lacks address |
| Online PCC vs charter PV | SERVICE_SPECIFIC | Distinct purposes and SLAs |

---

## 5. Conflicts detected

| Conflict ID | Topic | Summary |
|-------------|-------|---------|
| `conflict-pcc-fee-online-vs-offline` | PCC fee | BDT 1,500 (online portal) vs BDT 500 (offline police page) |
| `conflict-pcc-treasury-code` | Treasury code | 1-7301-0001-2681 vs 1-2201-0001-2681 |
| `conflict-gd-online-scope-timeline` | GD scope | All-types online (2025 announcements) vs historical lost-and-found-only |
| `conflict-passport-verification-vs-pcc` | Service boundaries | Charter PV 15–21 days vs PCC 3–7 days |
| `conflict-pcc-portal-url-variants` | Application URL | Multiple APEX entry paths on police domains |

**None silently resolved** — all marked `UNRESOLVED` for verification phase.

---

## 6. Practical findings (non-official)

- Community/secondary guides (e.g. UNB 2023) still cite **Tk 500** PCC fee — likely
  stale relative to current online portal (**PRACTICAL**, not promoted to MUST_NEED).
- Third-party notary/guide sites describe courier delivery for PCC — **not**
  confirmed on Tier 1 pages captured; gap recorded.
- Online GD rollout press coverage (BSS Sep 2025, TBS Jun–Jul 2025) provides
  practical registration requirements (NID, live photo, hotline 01320001428) but
  requires Tier 1 portal verification.

---

## 7. Knowledge gaps

| Priority | Gap |
|----------|-----|
| HIGH | GD portal (`gd.police.gov.bd`) live snapshot / complaint-type matrix |
| HIGH | `visa.gov.bd` application workflow, fees, document rules |
| HIGH | MRV fee table extraction from DIP fee page |
| HIGH | Visa types/documents matrix (page last updated **March 2022**) |
| MEDIUM | Numeric fees for employment/passport verification |
| MEDIUM | PCC collection/delivery (courier) official rules |
| MEDIUM | PCC correction/reissue process |
| MEDIUM | Firearms license document checklist |
| LOW | Resolve `police-general-diary` vs `police-general-diary-online` catalogue duplication |

---

## 8. Evidence limitations

1. **Environment connectivity:** SSL failures prevented direct snapshots of
   `gd.police.gov.bd` and `visa.gov.bd` despite successful fetches for police
   and DIP static pages.
2. **Stale official pages:** DIP visa types page last updated 2022; offline PCC
   page may predate online BDT 1,500 fee revision.
3. **Citizen charter granularity:** Charter provides SLAs and free/fee flags but
   often omits numeric fees for verification services.
4. **Dynamic portals:** PCC Oracle APEX portal content captured from home/login
   page; post-login payment gateway enumeration not performed in research phase.
5. **Cross-batch dependency:** Passport PV onboarding claims partially rely on
   batch-02a research; batch-2B adds scope boundaries and domestic-employment PCC
   routing — batch-02a claims not re-verified here.
6. **Geographic variation:** DMP token collection, Spain destination rule, and
   district/metro SB routing captured as location/destination-specific conditions;
   full district-wise variation not mapped.

---

## 9. Phase status

| Step | Status |
|------|--------|
| Research / discovery | **COMPLETE** |
| Independent verification | NOT STARTED |
| Staging normalization | NOT STARTED |
| Publication to knowledge DB | NOT STARTED |
| Frontend / RAG changes | NOT STARTED (explicitly out of scope) |

---

## 10. Final metrics (Step 17 stop report)

| Metric | Value |
|--------|------:|
| Services researched | **11** |
| Sources captured | **14** |
| Tier 1–2 sources | **11** |
| Atomic claims | **77** |
| Conflicts | **5** |
| Knowledge gaps | **10** |

**Major evidence limitations:** missing Tier 1 snapshots for GD and visa portals;
PCC fee/channel conflict unresolved; visa document/fee pages stale or not
machine-readable; verification service fees not numerically specified on charter.

**STOP — research phase complete. Do not verify, publish, or deploy.**
