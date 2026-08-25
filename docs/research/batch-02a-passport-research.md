# Batch 2A Research Report — Passport Services

**Batch ID:** `batch-02a-passport`  
**Researched at:** 2026-08-24  
**Catalogue version:** `1.0.0-finalized` (464 CONFIRMED services)  
**Phase:** RESEARCH ONLY — verification and publication **not started**  
**Raw artifacts:** `data/research/raw/batch-02a-passport/`  
**Generator:** `scripts/generate_batch02a_research_artifacts.py`

> **Guardrail:** All claims in this batch carry `pipeline_status: DISCOVERED` and
> `verification_status: PENDING_INDEPENDENT_VERIFICATION`. Nothing from Batch 2A
> is publication-ready. Community/practical sources are tagged separately and
> must not be promoted to MUST_NEED without Tier 1–2 verification.

---

## 1. Scope and selection method

Batch 2A was selected from the **finalized canonical catalogue**
(`data/service_catalogue/final/services.json`), not from an illustrative example list.

### Inclusion rules

- Status must be **CONFIRMED**.
- Service must be **passport issuance, renewal, status, fee payment, biometric enrollment,
  urgent processing, or police verification on the passport pathway**.
- Sub-processes without separate catalogue entries (lost, damaged, minors, expatriates,
  correction) are mapped to existing catalogue services via `scope.json`.

### Exclusion rules (noted, not researched as passport issuance)

| Service ID | Reason |
|------------|--------|
| `local-passport-attestation` | Union-level attestation; not DIP passport issuance |
| `migration-visa-application-dip` | Visa service; deferred to immigration batch |
| `migration-e-apostille` | MOFA document authentication |
| `mofa-document-attestation` | MOFA consular attestation |
| `mofa-csat` | MOFA appointment portal |
| `mofa-education-attestation-chain` | Education attestation chain |
| `mofa-nv-loi-application` | Note Verbale / LOI |

### Catalogue scan result

A full-text scan of the 464-service catalogue for passport-related keywords
(`passport`, `epassport`, `e-passport`, MRP subcategories) identified **12 in-scope
CONFIRMED services**. No additional CONFIRMED passport issuance services were found
beyond this set. Passport **cancellation** has no dedicated catalogue entry.

**Responsible authority (all DIP passport services):** Ministry of Home Affairs →
Department of Immigration and Passports (DIP). Police verification services fall under
Bangladesh Police (Special Branch / district verification per citizen charter).

---

## 2. Passport services identified and researched

### e-Passport channel (DIP — `epassport.gov.bd`)

| Service ID | Bangla name (catalogue) | English name | Research status |
|------------|-------------------------|--------------|-----------------|
| `epassport-new-application` | নতুন ই-পাসপোর্ট আবেদন | New e-Passport Application | SUBSTANTIAL |
| `epassport-reissue` | ই-পাসপোর্ট পুন:ইssue/রি-ইস্যু | e-Passport Re-issue | SUBSTANTIAL |
| `epassport-fee-payment` | ই-পাসপোর্ট ফি পরিশোধ | e-Passport Fee Payment | SUBSTANTIAL |
| `epassport-enrollment-appointment` | বায়োমেট্রিক এনরোলমেন্ট/অ্যাপয়েন্টমেন্ট | Biometric Enrollment Appointment | SUBSTANTIAL |
| `epassport-application-status` | ই-পাসপোর্ট আবেদনের অবস্থা | e-Passport Application Status Check | PARTIAL |
| `epassport-urgent-super-express` | সুপার এক্সপ্রেস (জরুরি) ই-পাসপোর্ট | Super Express (Urgent) e-Passport | SUBSTANTIAL |
| `epassport-rpo-secretariat` | বাংলাদেশ সচিবালয় আঞ্চলিক পাসপোর্ট অফিসে আবেদন | Application at RPO Bangladesh Secretariat | PARTIAL |

### Legacy MRP channel (DIP — `passport.gov.bd`)

| Service ID | Bangla name (catalogue) | English name | Research status |
|------------|-------------------------|--------------|-----------------|
| `passport-mrp-initial` | পাসপোর্ট প্রাথমিক/নতুন আবেদন (MRP) | Machine Readable Passport — Initial Application | SUBSTANTIAL |
| `passport-mrp-reissue` | পাসপোর্ট পুন:ইssue/সংশোধন (MRP) | MRP Reissue/Correction | PARTIAL |
| `passport-application-status` | পাসপোর্ট আবেদনের অবস্থা | Passport Application Status Check | PARTIAL |

### Police verification pathway

| Service ID | Bangla name (catalogue) | English name | Research status |
|------------|-------------------------|--------------|-----------------|
| `police-passport-police-verification` | পাসপোর্ট পুলিশ ভেরিফিকেশন | Passport Police Verification (SB pathway) | PARTIAL |
| `police-passport-verification` | পাসপোর্ট ভেরিফিকেশন | Passport Verification (district charter) | PARTIAL |

**Research status key:** SUBSTANTIAL = multiple Tier 1–2 sources and ≥5 atomic claims;
PARTIAL = official URL/role known but gaps in fees, SLA, or mission-specific rules.

### Sub-process coverage (no separate catalogue entry)

| Citizen topic | Mapped catalogue services |
|---------------|---------------------------|
| First-time application | `epassport-new-application`, `passport-mrp-initial` |
| Renewal / reissue | `epassport-reissue`, `passport-mrp-reissue` |
| Information correction | `epassport-reissue`, `passport-mrp-reissue` |
| Lost passport | `epassport-reissue` (+ GD / mission lost report) |
| Damaged passport | `epassport-reissue` (rules not separately enumerated) |
| Minor applicants | `epassport-new-application`, `epassport-reissue` |
| Expatriate applicants | `epassport-new-application`, `epassport-reissue`, `epassport-fee-payment` |
| Biometric enrollment | `epassport-enrollment-appointment` |
| Fee payment | `epassport-fee-payment` |
| Status checking | `epassport-application-status`, `passport-application-status` |
| Urgent processing | `epassport-urgent-super-express` |
| Police verification | `police-passport-police-verification`, `police-passport-verification` |
| Passport cancellation | *(none — gap)* |

---

## 3. Research completeness summary

| Metric | Value |
|--------|------:|
| Services in scope | 12 |
| Services researched | 12 |
| SUBSTANTIAL | 7 |
| PARTIAL | 5 |
| Sources captured | 20 |
| Tier 1–2 sources | 19 |
| Tier 6 (practical only) | 1 |
| Atomic claims (DISCOVERED) | 55 |
| OFFICIAL claims | 51 |
| PRACTICAL claims | 2 |
| DISCOVERY claims | 2 |
| Unresolved conflicts | 3 |
| Knowledge gaps | 6 |
| Independent verification | **NOT STARTED** |
| Publication | **NOT STARTED** |

No service is marked fully researched (`COMPLETE`). Fee schedules, mission-specific
document lists, and police-verification SLAs require independent verification and/or
live portal capture before publication.

---

## 4. Workflow stages completed (this step)

Per `docs/research/BATCH_RESEARCH_TEMPLATE.md`:

| Stage | Status | Notes |
|-------|--------|-------|
| DISCOVERY | ✅ Complete | 12 services from canonical catalogue |
| STAGING | ⏸ Raw only | Artifacts in `data/research/raw/batch-02a-passport/`; formal staging dir not created |
| NORMALIZATION | ⏸ Not started | Awaits verification |
| CLAIM EXTRACTION | ✅ Complete | 55 atomic claims in `claims.json` |
| CROSS-CHECK | ✅ Partial | 3 conflicts logged |
| INDEPENDENT VERIFICATION | ❌ **Stopped per scope** | Explicitly out of scope for this turn |
| CLAIM-LEVEL PUBLICATION | ❌ Not started | |
| E2E EVALUATION | ❌ Not started | |
| HARDENING | ❌ Not started | |

---

## 5. Sources

### Tier 1 — DIP / official portals (primary)

| Source ID | URL | Last updated (on page) | Used for |
|-----------|-----|------------------------|----------|
| `src-epassport-fees` | https://epassport.gov.bd/instructions/passport-fees | 8 March 2023 | Fees, VAT, delivery tiers, ekpay/A-Challan, regular SLA |
| `src-epassport-instructions` | https://epassport.gov.bd/instructions/instructions | — | No attestation, NID/BRC, minors, govt NOC, lost GD |
| `src-epassport-urgent` | https://epassport.gov.bd/instructions/urgent-applications | 22 October 2022 | Super Express 2-day, Agargaon pickup, mission exclusion |
| `src-epassport-enrollment-docs` | https://www.epassport.gov.bd/landing/notices/34 | **7 May 2025** | Enrollment document checklist |
| `src-epassport-onboarding` | https://www.epassport.gov.bd/onboarding | — | District/police station, domestic vs abroad |
| `src-epassport-status` | https://www.epassport.gov.bd/authorization/application-status | — | Status check portal |
| `src-epassport-landing` | https://epassport.gov.bd/landing | — | Apply / Re-Issue entry |
| `src-epassport-five-steps` | https://epassport.gov.bd/instructions/five-step-to-your-epassport | — | End-to-end workflow |
| `src-epassport-app-form` | https://epassport.gov.bd/instructions/application-form | — | RPO Secretariat |
| `src-mrp-home` | http://passport.gov.bd/ | — | MRP Form 1, email credentials, biometric visit |
| `src-mrp-reissue` | http://passport.gov.bd/UserHome.aspx | — | MRP Form 2 reissue/correction |
| `src-mrp-status` | http://passport.gov.bd/OnlineStatus.aspx | — | MRP status check |
| `src-mrp-form-pdf` | http://passport.gov.bd/Reports/MRP_Application_Form[Hard%20Copy].pdf | — | MRP hard-copy form requirements |
| `src-dip-home` | https://www.dip.gov.bd/ | — | Parent authority |

### Tier 2 — Missions / police (secondary official)

| Source ID | URL | Used for |
|-----------|-----|----------|
| `src-mofa-dubai-epassport` | https://bcgdubai.gov.bd/e-passport/ | Expatriate eligibility, docs, lost report, MRP validity rule |
| `src-mofa-singapore-epassport` | https://singapore.mofa.gov.bd/en/site/page/E-passport-application-rules | Mission docs, NETS payment, hours |
| `src-mofa-abudhabi-epassport` | https://abudhabi.mofa.gov.bd/en/site/page/E-Passport-Issue--Reissue: | BRC everify, WEWB 10% surcharge, mission selection |
| `src-police-charter` | https://www.police.gov.bd/index.php/en/citizen_charter | PV SLA (discovery only — needs live verification) |
| `src-police-sb` | https://www.police.gov.bd/en/special_branch | SB passport verification pathway |

### Tier 6 — Practical only (not evidence for MUST_NEED)

| Source ID | URL | Notes |
|-----------|-----|-------|
| `src-practical-qna-fees` | https://en.qnabangla.com/passport-fee-bangladesh/ | Community fee summary; cross-check only |

### Source retrieval limitations

- **e-Passport SPA:** Direct `curl` to `epassport.gov.bd` returns Angular shell HTML only;
  instructional content was captured via search-indexed excerpts citing official URLs.
  Full page snapshots were **not** archived in this pass.
- **Bright Data MCP:** Unavailable (HTTP 401) in this environment.
- **MRP portal:** Server-rendered HTML retrieved successfully for home/UserHome pages;
  PDF forms partially readable.

---

## 6. Claims summary

All 55 claims live in `data/research/raw/batch-02a-passport/claims.json`.

### By service (claim count)

| Service ID | Claims | Highlights |
|------------|-------:|------------|
| `epassport-fee-payment` | 14 | Domestic BDT tiers (48/64 p × 5/10 y × regular/express/super-express); mission USD tiers; ekpay/A-Challan; 15% VAT; regular SLA |
| `epassport-new-application` | 11 | Online onboarding; no attestation; NID/BRC; minor parent NID; under-6 photo; police station; expatriate flow |
| `epassport-reissue` | 8 | Re-issue portal; previous passport; lost GD; correction docs; mission lost report; Dubai MRP validity |
| `epassport-urgent-super-express` | 5 | 2 working days; Agargaon only; not at missions; MRP-without-address-change restriction |
| `passport-mrp-initial` | 6 | Form 1; email ID/password; biometric visit; attested copies (contrasts e-Passport) |
| `epassport-enrollment-appointment` | 2 | Appointment + original ID at enrollment |
| `police-passport-police-verification` | 3 | SB pathway; police station selection |
| `epassport-application-status` | 2 | OID + DOB status check |
| `passport-mrp-reissue` | 2 | Form 2; 5-day appointment validity |
| `passport-application-status` | 1 | MRP OnlineStatus portal |
| `epassport-rpo-secretariat` | 1 | Secretariat application-form page |
| `police-passport-verification` | 2 | Charter SLA (discovery); district scope |

### Requirement classification pattern (research-phase)

Claims use structured `condition` fields where evidence supports branching:

| Classification | Examples discovered |
|----------------|---------------------|
| **MUST_NEED** (when verified) | Printed application summary; original NID/BRC; printed application form |
| **CONDITIONAL** | Parent NID if minor &lt;18 without own NID; 3R photo if &lt;6; GO/NOC if government employee; previous passport if reissue; GD copy if lost; payment slip if offline payment; mission lost report if abroad; BRC everify if BRC used |
| **RECOMMENDED** | Correction supporting docs per correction type (official notice defers to nature of application) |
| **NOT_APPLICABLE** | Attestation at online apply stage (e-Passport explicitly not required) |

### High-risk claim categories (pending verification)

- All **fee amounts** (domestic BDT and mission USD)
- **Super Express eligibility** restriction vs headline text
- **Regular delivery SLA** (15 working days / 21 days)
- **Police verification SLA** (15–21 normal / 7 urgent from charter snippet)
- **Official application URLs** (live portal availability)
- **Payment gateway enumeration** (ekpay confirmed; full list not captured from live JS)

---

## 7. Conflicts (unresolved — do not publish)

| Conflict ID | Topic | Description |
|-------------|-------|-------------|
| `conflict-super-express-eligibility` | Super Express eligibility | Urgent page says any citizen may apply, but NOTE restricts current service to existing MRP holders **without permanent address change** |
| `conflict-mrp-vs-epassport-primary` | Primary channel | Both MRP and e-Passport portals remain active; national primary channel for new applicants needs DIP circular confirmation |
| `conflict-fee-freshness` | Fee schedule date | Official fee page last updated 8 March 2023; possible stale fees if revised by gazette without page update |

---

## 8. Knowledge gaps

| Gap ID | Priority | Description |
|--------|----------|-------------|
| `MISSING_MRP_FEE_SCHEDULE_MACHINE_READABLE` | HIGH | MRP bank-deposit fee table not extracted from official live source |
| `MISSING_EXPATRIATE_UNIFIED_NATIONAL_PROCEDURE` | HIGH | Mission-specific rules (Dubai, Singapore, Abu Dhabi sampled); no single DIP consolidation page |
| `MISSING_PASSPORT_CANCELLATION_SERVICE` | MEDIUM | No canonical catalogue entry; may be embedded in lost/reissue workflows |
| `MISSING_POLICE_PV_DEDICATED_OFFICIAL_URL` | MEDIUM | No standalone SB passport PV procedure page captured |
| `MISSING_PAYMENT_GATEWAY_OFFICIAL_ENUM` | MEDIUM | Full online gateway list not captured from live JS portal |
| `MISSING_DAMAGED_PASSPORT_DISTINCT_RULES` | MEDIUM | Lost GD rules found; damaged passport not separately enumerated on Tier-1 pages |

---

## 9. Practical findings (separate from OFFICIAL)

These are **community or secondary observations** — not promoted to requirements:

1. **Processing delays:** Mission pages and expatriate forums frequently cite police
   verification timing as a bottleneck; treat as PRACTICAL until SB/DIP SLA verified.
2. **BRC/NID data mismatch:** Singapore and Abu Dhabi missions warn that mismatches
   between passport, NID, and everify.bdris.gov.bd BRC data cause delays — aligns with
   official mission text (Tier 2), not mere forum rumor.
3. **ekpay payment flow:** Third-party guides describe ekpay redirect and e-Challan
   verification; official fee page confirms ekpay — gateway UX details remain PRACTICAL.
4. **UAE expatriate routing:** Property/travel blogs describe Dubai vs Abu Dhabi mission
   routing by emirate; official mission pages are authoritative for document lists only.
5. **YouTube / Facebook / Reddit:** Not systematically harvested in this pass; deferred
   to practical-ingestion only after official baseline verification.

---

## 10. Services with substantial gaps

| Service ID | Gap severity | Primary missing elements |
|------------|--------------|--------------------------|
| `epassport-rpo-secretariat` | HIGH | Only landing/instruction URL captured; Secretariat-specific workflow steps, hours, document variants |
| `passport-mrp-reissue` | HIGH | Form 2 URL confirmed; reissue/lost/damaged/correction document matrix not fully extracted |
| `passport-application-status` | MEDIUM | Status portal URL only; input fields and output semantics not captured |
| `epassport-application-status` | MEDIUM | OID/DOB requirement cited; live portal behavior not snapshotted |
| `police-passport-police-verification` | HIGH | Pathway inferred from onboarding + SB page; no dedicated PV procedure |
| `police-passport-verification` | HIGH | Charter SLA cited as DISCOVERY; needs live charter text verification |
| `epassport-fee-payment` | MEDIUM | Fee amounts captured from indexed excerpts; freshness conflict open |
| `epassport-reissue` | MEDIUM | Damaged-passport rules not distinct; cancellation pathway unknown |

---

## 11. Key research findings by domain

### Application methods

- **e-Passport (current):** Online at `www.epassport.gov.bd/onboarding` → fee payment →
  appointment → biometric enrollment at Regional Passport Office → collection.
- **MRP (legacy):** Online Form 1/2 at `passport.gov.bd` → email Application ID/Password →
  print PDF → in-person biometric enrollment with **attested** document copies.

### Fees (DISCOVERED — verify before publish)

**Inside Bangladesh (incl. 15% VAT), from official fee page excerpts:**

| Pages | Validity | Regular (BDT) | Express (BDT) | Super Express (BDT) |
|------:|---------:|--------------:|--------------:|--------------------:|
| 48 | 5 yr | 4,025 | 6,325 | 8,625 |
| 48 | 10 yr | 5,750 | 8,050 | 10,350 |
| 64 | 5 yr | 6,325 | 8,625 | 12,075 |
| 64 | 10 yr | 8,050 | 10,350 | 13,800 |

Mission fees published separately in USD for **General** and **Labor/Student** categories
(regular and express tiers per page count/validity).

### Biometrics and appointments

- Enrollment requires printed application summary **including appointment** (when scheduled).
- Original NID or Birth Certificate required at enrollment.
- Super Express: application at any domestic office; **collection only at Agargaon** DPVO.

### Lost / damaged

- **Lost:** GD copy required (official instructions); mission may require **local police lost report**.
- **Damaged:** Prompt GD advised in instructions; distinct damaged-passport document list **not found** on Tier-1 pages.

### Minors

- Under 18 without own NID: father or mother NID number required in application.
- Under 6: 3R lab-print photo at enrollment.
- Mission newborn rules (Dubai/Singapore): parent passports/NID/BRC, marriage certificate, etc.

### Expatriates

- Onboarding Step 1: select **No** for applying from Bangladesh; choose mission.
- Dubai: e-Passport not accepted if MRP validity &gt;1 year remaining (mission rule).
- Abu Dhabi: 10% WEWB surcharge on consular fees.
- Singapore: NETS payment at counter; weekday enrollment 9:00–12:30, collection 14:00–16:30.

### Legal basis

- Passport issuance authority: Department of Immigration and Passports under Ministry of Home Affairs.
- Wage Earners' Welfare Board Act 2018 §14(e) cited on Abu Dhabi mission page for fee surcharge.
- Full Passport Rules / gazette citations **not extracted** in this pass — gap for verification stage.

---

## 12. Artifact inventory

```
data/research/raw/batch-02a-passport/
├── metadata.json           # batch stats
├── services_index.json     # 12 services from catalogue
├── scope.json              # in/out of scope + subprocess map
├── sources.json            # 20 sources with tiers
├── claims.json             # 55 DISCOVERED claims
├── conflicts.json          # 3 unresolved
├── knowledge_gaps.json     # 6 gaps
└── services/
    └── {service_id}.json   # per-service claim bundles (12 files)

scripts/generate_batch02a_research_artifacts.py
docs/research/batch-02a-passport-research.md   # this report
```

---

## 13. Next steps (explicitly NOT done in this turn)

1. **Independent verification** — live fetch/snapshot of Tier 1 pages; second-source cross-check for fees and SLAs.
2. **Staging normalization** — `data/research/staging/batch-02a-passport/` with requirements.json, fees.json, procedure_steps.json.
3. **Conflict resolution** — Super Express eligibility, MRP vs e-Passport primary channel, fee freshness.
4. **Gap closure** — MRP fee schedule, damaged passport rules, passport cancellation, SB PV dedicated procedure.
5. **Claim-level publication** — only after verification gate passes.

---

## 14. Stop statement

**Batch 2A research phase is complete.** Verification, publication, frontend changes, RAG
implementation, deployment, and Batch 2B are **not started** per scope instructions.
