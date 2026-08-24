# Service Catalogue Gap Analysis

**Phase:** Discovery audit (no requirements research)  
**Catalogue version:** `0.1.0-discovery`  
**Audit date:** 2026-08-24  
**Baseline catalogue:** 432 canonical services  
**Post-remediation catalogue:** 492 canonical services (+60 net new)

---

## 1. Executive summary

This audit systematically tested the master service catalogue against **36 citizen-facing dimensions** (ministries through digital government). The catalogue had strong coverage in **social protection (SSPS)**, **transport (BRTA)**, **utilities**, and **core identity/civil registration**, but **critical gaps** in **judiciary**, **disability citizen services**, **employment/labour**, **permits (fire/forest)**, **professional councils**, and **local-government tax/licence variants** outside Dhaka templates.

**60 net-new services** were added from official sources (`gap_audit_services.json`). **We still do not claim completeness.** myGov.bd cites **2,000+ integrated services** across **40 ministries**; this catalogue remains a structured subset with explicit uncertainty labels.

| Metric | Before audit | After remediation |
|--------|-------------:|----------------:|
| Canonical services | 432 | **492** |
| Categories | 34 | **40** |
| Authorities indexed | 98 | **127** |
| Duplicate/alias entries | 14 | **17** |
| CONFIRMED | 393 (91%) | **402 (82%)** |
| LIKELY | 33 | **78** |
| NEEDS_VERIFICATION | 6 | **12** |

The CONFIRMED **percentage** dropped because gap-fill entries were added with honest LIKELY/NEEDS_VERIFICATION labels where portals were not individually verified in this pass.

---

## 2. Audit methodology

### 2.1 Dimensions tested (36)

1. Government ministries  
2. Government departments  
3. Directorates  
4. Authorities  
5. Commissions  
6. Statutory bodies  
7. District administration  
8. Upazila administration  
9. Union/local government  
10. City corporations  
11. Municipalities  
12. Social safety-net programmes  
13. Education  
14. Healthcare  
15. Agriculture  
16. Fisheries  
17. Livestock  
18. Land  
19. Transport  
20. Police  
21. Courts/legal services  
22. Tax/VAT/customs  
23. Business  
24. Employment  
25. Migration  
26. Women/children  
27. Disability  
28. Elderly  
29. Disaster relief  
30. Environment  
31. Public certificates  
32. Licences  
33. Registrations  
34. Permits  
35. Government payments  
36. Digital government services  

### 2.2 Gap severity rubric

| Severity | Meaning |
|----------|---------|
| **CRITICAL** | High-frequency citizen journey with **zero or near-zero** catalogue coverage; official services confirmed to exist |
| **HIGH** | Major service family **under-represented** (<3 entries) or only programme names without citizen-facing application path |
| **MEDIUM** | Partial coverage; generic samples exist but **per-authority/per-district** expansion missing |
| **LOW** | Niche, employer-facing, or low-volume services; or already covered indirectly |

### 2.3 Remediation action

Gap-fill batch: `data/service_catalogue/sources/gap_audit_services.json` (61 entries → **60 net new**, 1 merged as duplicate).

Rebuild: `python3 scripts/build_service_catalogue.py`

---

## 3. Gap findings by dimension

### 3.1 CRITICAL gaps (found & partially remediated)

| Gap | Before | Action taken | Remaining risk |
|-----|--------|--------------|----------------|
| **Judiciary / courts** | 0 court services | +6 JUDICIARY entries (certified copy, e-filing, case tracking, virtual court, family/loan courts) | District/subordinate court services still sparse; no exhaustive court-type matrix |
| **Disability citizen services** | 0 DIS entries; allowance only as SSPS programme name | +1 DIS registration; allowance application via `social-allowance-online-application` | Disability stipend, rehabilitation loan as **application services** not fully split out |
| **Fire permits / NOC** | Mentioned only in BIDA notes | +4 PERMITS (e-fire licence, e-NOC, safety firm registration, forest transit) | Explosives/chemical NOC cross-agency chain incomplete |
| **Employment / labour** | BMET/expatriate only; no domestic labour | +4 EMPLOYMENT (BOESL, trade union, labour ADR, employment exchange) | Employment exchange **NEEDS_VERIFICATION** (2026 rollout) |
| **e-Apostille / Hague authentication** | MOFA attestation yes; e-Apostille missing | +1 `migration-e-apostille` CONFIRMED | Full MOFA document-type matrix not catalogued per document |
| **Cooperative registration** | RDCD programmes only | +1 cooperative society registration (IDSDP) | Cooperative audit/liquidation services not added |
| **Professional councils** | BMDC verification only | +5 PROFESSIONAL (Bar, BMDC reg, nursing, pharmacy, engineer) | Architect, dentist specialist boards, vet council missing |

### 3.2 HIGH gaps (found & partially remediated)

| Gap | Before | Action taken | Remaining risk |
|-----|--------|--------------|----------------|
| **City corporation services** | DNCC/DSCC samples; no CCC | +CCC trade licence & holding tax; DNCC/DSCC holding tax | Sylhet, Rajshahi, Gazipur, Cumilla, etc. **not expanded** |
| **Municipality / pourashava** | 1 trade licence entry | +pourashava holding tax | Birth/death at pourashava level not per-municipality |
| **Upazila administration** | Land office entries only | +UNO digital services; upazila land tax | Upazila NOC/certificates (inheritance, solvency) incomplete |
| **Tax / VAT citizen filing** | e-TIN only | +income tax return, TDS certificate, VAT return | Wealth surcharge, gift tax, appeal services missing |
| **Intellectual property** | None | +trademark, patent (DPDT) | Design registration, GI marks not added |
| **Food / VGF assistance** | None as service | +VGF/food assistance card | OMS/Fair Price Shop operational services not detailed |
| **Health immunization** | Hospital/clinic only | +EPI immunization card, hospital birth notification | DGHS specialist referrals, death medical certification sparse |
| **Police citizen services** | Clearance/verification | +online GD, passport police verification | Traffic case payment, lost property reporting not confirmed |
| **Digital government** | 1 aggregator entry | +myGov registration, Ekpay, aChallan | **No myGov service ID parity** (2000+ services) |
| **Elderly** | `snp-old-age-allowance` programme only | +online allowance application portal | Old-age pension (MOF) vs DSS allowance distinction not fully mapped |
| **NGO registration** | Women NGO only | +NGOAB registration | Foreign NGO branch office renewal not split |

### 3.3 MEDIUM gaps (partially addressed or deferred)

| Gap | Status |
|-----|--------|
| **Development authorities** (CDA, RAJUK, NHA, RAJUK done) | +CDA building permit, NHA allotment; **Khulna, Rajshahi, Cox's Bazar DAP** authorities missing |
| **Education — public universities** | +UGC recognition, public admission (NEEDS_VERIFICATION); **individual university admin services** not enumerated |
| **Election Commission** | +candidate nomination; voter slip added; ** electoral roll correction, observer accreditation** missing |
| **Environment** | ECC strong; +forest clearance; **wetland, wildlife, EIA appeal** incomplete |
| **Transport** | BRTA strong; +route permit, driving school licence; **inland water vessel, port authority** missing |
| **Agriculture / fisheries / livestock** | +fish farm registration; livestock farm registration; **seed certification** still NEEDS_VERIFICATION |
| **Women/children** | +OCC, child helpline 1098; **domestic worker registration, daycare licensing** missing |
| **Disaster relief** | 8 entries; **cyclone shelter registration, relief card** as citizen services not split |
| **Certificates** | +freedom fighter certificate (NEEDS_VERIFICATION); **solvent/non-creditor, succession** partially covered at union level |
| **Customs/trade** | 3 customs entries; **export incentive, EPB registration, bonded warehouse** incomplete |

### 3.4 LOW gaps (deferred)

| Gap | Rationale |
|-----|-----------|
| **Defence / armed forces civilian services** | Very restricted; only DC armed-forces property NOC partially covered |
| **Parliament / legislative services** | Not typical citizen transactional services |
| **Bangladesh Bank retail complaints** | Regulatory, not procedural catalogue fit |
| **Statistics bureau data requests** | Information access, low transactional volume |
| **Cultural ministry artist grants** | Programme-heavy; low universal citizen demand |
| **Rail/air freight operator licences** | B2B/regulatory |

---

## 4. Services added in this audit (60 net new)

New categories introduced: **JUDICIARY**, **DISABILITY**, **EMPLOYMENT**, **PERMITS**, **PROFESSIONAL**, **LIVESTOCK**.

| Category | Added | Examples |
|----------|------:|---------|
| JUDICIARY | 6 | Supreme Court certified copy, e-filing, virtual court |
| PERMITS | 4 | Fire e-licence, e-NOC, safety firm registration |
| EMPLOYMENT | 4 | BOESL, trade union, labour ADR, employment exchange |
| PROFESSIONAL | 5 | Bar Council, BMDC, nursing, pharmacy, engineer |
| LOCAL_GOVERNMENT | 5 | CCC/DNCC/DSCC holding tax, UNO services, pourashava tax |
| SOCIAL_PROTECTION | 2 | Online allowance application, VGF card |
| PASSPORT_IMMIGRATION | 2 | e-Apostille, visa application |
| REGISTRATIONS | 4 | Cooperative, NGOAB, trademark, patent |
| TAX / VAT | 3 | Income return, TDS cert, VAT return |
| HEALTH | 2 | Immunization card, hospital birth notification |
| POLICE | 2 | Online GD, passport verification |
| TRANSPORT | 2 | Route permit, driving school licence |
| HOUSING | 2 | CDA building permit, NHA allotment |
| EDUCATION | 2 | UGC recognition, public university admission |
| WOMEN_CHILDREN | 2 | OCC, child helpline 1098 |
| Others | 13 | Ekpay, myGov registration, land e-stamp, etc. |

Full list: `data/service_catalogue/sources/gap_audit_services.json`

---

## 5. Duplicates removed / merged

| Alias / weak entry | Canonical service | Notes |
|--------------------|-------------------|-------|
| `agri-livestock-registration` | `agriculture-livestock-farm-registration` | Weak URL replaced with DLS-backed entry |
| Prior MVP aliases (14) | unchanged | passport, NID, birth, TIN, etc. |
| **New duplicate records** | 17 total | +3 from explicit alias map and build dedup |

---

## 6. Remaining uncertainty

### 6.1 NEEDS_VERIFICATION (12 total)

Includes pre-audit entries plus new:

| service_id | Concern |
|------------|---------|
| `agri-seed-certification` | Official portal path unconfirmed |
| `dc-armed-forces-property-noc` | Niche DC circular |
| `expatriate-bmet-demand-verification` | Inferred service name |
| `religious-mora-portal` | Generic aggregator |
| `religious-waqf-services` | Portal structure unclear |
| `judiciary-artha-rin-salish` | No primary URL confirmed |
| `judiciary-family-court-services` | No primary URL confirmed |
| `employment-district-employment-exchange` | Announced 2026; may not be live |
| `land-e-stamp-payment` | e-Stamp vendor portal not confirmed |
| `education-public-university-admission` | No single national portal |
| `certificates-freedom-fighter-certificate` | Issuance authority path unclear |
| `police-general-diary-online` | Online GD availability varies by district |

### 6.2 LIKELY (78 total)

Many new gap-fill entries are LIKELY pending individual portal verification. High-priority verification queue: city corporation portals, tax/VAT filing URLs, professional council online application paths.

---

## 7. Coverage limitations (honest statement)

| Claim | Supported? |
|-------|------------|
| "All Bangladesh government services" | **No** |
| "Broad inventory with measured gaps" | **Yes** |
| "myGov parity" | **No** — only ~492 canonical vs 2000+ myGov integrations cited publicly |
| "Per-district local government complete" | **No** — pattern-based samples for 64 districts × tiers |
| "Court system complete" | **No** — 6 high-level judiciary services vs full court hierarchy |
| "Disability & elderly journeys complete" | **Partial** — registration + application portal added; not all benefit types |

### 7.1 Structural limitations

1. **SSPS programme granularity** — 149 social protection entries are mostly **programme names**, not always distinct citizen application workflows.  
2. **Lifecycle tagging** — Still ~63% untagged (not addressed in this audit).  
3. **Authority normalization** — 127 authorities; many ministry names inconsistent across SSPS vs operational services.  
4. **Bangla names** — Some gap-fill entries English-first where official Bangla label not fetched.  
5. **No myGov service ID mapping** — Cannot measure parity until official manifest ingested.

### 7.2 Highest-priority future discovery passes

1. **myGov service manifest scrape** — Map service IDs to catalogue slugs  
2. **Judiciary subordinate courts** — District Judge, Magistrate, Labour Court, Family Court per district  
3. **All 12 city corporations + 495 pourashavas** — Trade licence, holding tax, birth/death delivery  
4. **Ministry Rules of Business sweep** — 50+ ministries → attached departments  
5. **Commission/statutory body registry** — ACC, PSC, SEC, BTRC (partial), ICAB, etc.

---

## 8. Audit scorecard (36 dimensions)

| # | Dimension | Pre-audit | Post-audit | Severity was | Notes |
|---|-----------|-----------|------------|--------------|-------|
| 1 | Ministries | Partial | Partial | MEDIUM | SSPS covers many; operational services uneven |
| 2 | Departments | Partial | Partial | MEDIUM | DSS, DLRMS, DGHS OK; Food, Labour improved |
| 3 | Directorates | Partial | Improved | HIGH→MEDIUM | Fire, Cooperatives, DLS added |
| 4 | Authorities | Partial | Improved | HIGH | RAJUK/CDA/NHA; port authorities missing |
| 5 | Commissions | Weak | Weak | HIGH | EC partial; PSC, SEC, UGC partial |
| 6 | Statutory bodies | Partial | Improved | HIGH | Professional councils added |
| 7 | District admin | Weak | Weak | HIGH | DC attestation exists; NOC matrix incomplete |
| 8 | Upazila admin | Weak | Improved | HIGH | UNO entry added |
| 9 | Union/local gov | Moderate | Moderate | MEDIUM | Union certificates OK |
| 10 | City corporations | Weak | Improved | **CRITICAL→HIGH** | CCC + Dhaka holding tax |
| 11 | Municipalities | Weak | Improved | HIGH | Pourashava holding tax |
| 12 | Social safety-net | Strong | Strong | LOW | 149 programmes; application portal added |
| 13 | Education | Moderate | Improved | MEDIUM | Boards OK; UGC added |
| 14 | Healthcare | Moderate | Improved | MEDIUM | EPI added |
| 15 | Agriculture | Moderate | Moderate | MEDIUM | 7 services |
| 16 | Fisheries | Moderate | Improved | MEDIUM | Fish farm registration |
| 17 | Livestock | Weak | Improved | **CRITICAL→MEDIUM** | DLS farm registration |
| 18 | Land | Strong | Improved | MEDIUM | e-stamp added (NEEDS_VERIFICATION) |
| 19 | Transport | Strong | Improved | LOW | BRTA comprehensive |
| 20 | Police | Moderate | Improved | MEDIUM | GD + passport PV |
| 21 | Courts/legal | **None** | Improved | **CRITICAL→HIGH** | 6 judiciary + 6 legal aid |
| 22 | Tax/VAT/customs | Weak | Improved | **CRITICAL→MEDIUM** | Returns added |
| 23 | Business | Weak | Improved | HIGH | Cooperative, NGOAB, IP |
| 24 | Employment | Weak | Improved | **CRITICAL→MEDIUM** | Labour + BOESL |
| 25 | Migration | Moderate | Improved | HIGH | e-Apostille, visa |
| 26 | Women/children | Moderate | Improved | MEDIUM | OCC, 1098 |
| 27 | Disability | **None** | Improved | **CRITICAL→MEDIUM** | DIS + application |
| 28 | Elderly | Programme-only | Improved | HIGH | Online application portal |
| 29 | Disaster relief | Moderate | Moderate | LOW | 8 services |
| 30 | Environment | Moderate | Improved | MEDIUM | Forest clearance |
| 31 | Public certificates | Moderate | Moderate | MEDIUM | 13 certificates |
| 32 | Licences | Moderate | Improved | MEDIUM | Fire, CCC trade |
| 33 | Registrations | Weak | Improved | HIGH | Coop, NGO, IP |
| 34 | Permits | **None** | Improved | **CRITICAL→MEDIUM** | Fire/forest |
| 35 | Gov payments | Weak | Improved | HIGH | Ekpay, aChallan |
| 36 | Digital gov | Weak | Improved | **CRITICAL→HIGH** | myGov reg; not full index |

---

## 9. Recommended next steps

1. **Verification sprint** — Resolve 12 NEEDS_VERIFICATION and top 30 LIKELY entries.  
2. **myGov alignment** — Ingest official service list; compute **coverage ratio** (catalogue ∩ myGov / myGov).  
3. **Merge SSPS programme vs application** — Distinguish `snp-*` programmes from citizen `apply-*` workflows.  
4. **Lifecycle tagging pass** — Tag high-traffic journeys end-to-end.  
5. **Requirements phase (separate)** — Only after catalogue stabilization.

---

## 10. Final metrics (post-remediation)

| Metric | Value |
|--------|------:|
| **Total canonical services** | **492** |
| **Total categories** | **40** |
| **Total authorities** | **127** |
| **Duplicates removed (tracked)** | **17** alias records |
| **Newly discovered in gap audit** | **60 net new** (61 batch − 1 merge) |
| **CONFIRMED** | 402 |
| **LIKELY** | 78 |
| **NEEDS_VERIFICATION** | 12 |
| **DEPRECATED** | 0 |

**Completeness:** Not claimed. Estimated coverage against publicly cited **2,000+ myGov services** ≈ **25% by count** (492/2000), but many catalogue entries are SSPS programmes while myGov counts transactional integrations — **direct parity requires ID mapping, not raw count comparison**.

---

*Audit performed without detailed requirements, fees, or document research.*
