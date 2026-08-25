# Master Service Discovery Report — Bangladesh Government & Public Services

**Phase:** Discovery (inventory only — no requirements, fees, or procedures)  
**Catalogue version:** `0.1.0-discovery`  
**Discovery date:** 2026-08-24  
**Branch:** `cursor/service-catalogue-discovery-3400`

---

## 1. Executive summary

This phase produced a **machine-readable master service catalogue** under `/data/service_catalogue/`. The inventory captures citizen- and business-facing services discovered across Bangladesh ministries, departments, directorates, authorities, local government tiers, and major government portals.

**We do not claim this list contains all Bangladesh government services.** External registries cite hundreds to thousands of government bodies (e.g., policy research citing ~1,009 public institutions). This catalogue is a **broad first-pass inventory** with explicit status labels and measurable coverage metrics.

| Metric | Count |
|--------|------:|
| **Canonical services** | 432 |
| **Duplicate / alias entries** (tracked separately) | 14 |
| **Total catalogue entries** | 446 |
| **Status: CONFIRMED** | 393 (91.0%) |
| **Status: LIKELY** | 33 (7.6%) |
| **Status: NEEDS_VERIFICATION** | 6 (1.4%) |
| **Taxonomy categories** | 34 |
| **Responsible authorities (indexed)** | 98 |

---

## 2. Deliverables

| Path | Purpose |
|------|---------|
| `data/service_catalogue/services.json` | Primary canonical catalogue |
| `data/service_catalogue/duplicates.json` | Alias/MVP slugs merged into canonical IDs |
| `data/service_catalogue/authorities.json` | Authority index with service counts |
| `data/service_catalogue/metadata.json` | Aggregate statistics |
| `data/service_catalogue/schema.json` | JSON Schema for catalogue entries |
| `data/service_catalogue/by_category/*.json` | Per-category splits (34 files) |
| `data/service_catalogue/sources/*.json` | Raw discovery batches (pre-dedup) |
| `scripts/build_service_catalogue.py` | Build, normalize, deduplicate pipeline |
| `docs/SERVICE_DISCOVERY_REPORT.md` | This report |

Each service entry includes at minimum:

`service_id`, `service_name_bn`, `service_name_en`, `aliases`, `category`, `subcategory`, `responsible_authority`, `target_user`, `geographic_scope`, `official_source`, `discovery_sources`, `status`

Optional fields: `authority_id`, `lifecycle_stage`, `uuid`, `notes`, `canonical_service_id` (for duplicates).

---

## 3. Discovery methodology

### 3.1 Research lenses

Discovery was organized around the **citizen lifecycle** (birth → childhood → education → employment → marriage → property → business → vehicle → tax → healthcare → family → social protection → retirement → death) **plus** services outside that arc (utilities, trade, disaster relief, expatriate labour, ICT, etc.).

### 3.2 Source types

| Source type | Examples used |
|-------------|---------------|
| **National portals** | myGov.bd sector listings, e-passport (DIP), BSP/BRTA, BDRIS, EC NID, e-TIN/NBR |
| **Ministry / division sites** | Social Welfare SSPS programme registry, Land (DLRMS), Health (DGHS), Education boards |
| **Statutory bodies** | BRTA, BIDA, RJSC, BMET, BTRC, DESCO/WASA-style utilities |
| **Local government** | Union Parishad certificates, city corporation services, DC office attestations |
| **Structured batch research** | Curated JSON batches from systematic web research |
| **Prior MVP seeds** | Five seed services merged as duplicate aliases where overlapping |

### 3.3 Status assignment rules

| Status | Meaning |
|--------|---------|
| **CONFIRMED** | Official URL or authoritative government page confirms the service exists |
| **LIKELY** | Strong indirect evidence (portal menu, ministry programme list) but not yet individually verified |
| **NEEDS_VERIFICATION** | Plausible service; official link weak, broken, or generic portal only |
| **DUPLICATE** | Same service as another entry; stored in `duplicates.json` with `canonical_service_id` |
| **DEPRECATED** | Reserved; none assigned in this pass |

### 3.4 Deduplication approach

Aggressive deduplication was applied for naming variants that refer to the same underlying service or closely coupled process:

- **Birth registration / birth certificate / জন্ম নিবন্ধন** → `civil-birth-registration`
- **Death registration (BDRIS) vs union death certificate** → kept as related but distinct entries where delivery authority differs
- **e-Passport re-issue / passport renewal / MRP reissue** → separate canonical entries only where delivery channel or passport generation genuinely differs; MVP aliases merged
- **NID correction / voter registration (new)** → mapped to EC NID canonical services
- **e-TIN registration / TIN registration** → `tax-etin-registration`

Slug-level alias map is defined in `scripts/build_service_catalogue.py` (`DUPLICATE_ALIASES`).

---

## 4. Category breakdown

| Category | Services | Notes |
|----------|----------:|-------|
| SOCIAL_PROTECTION | 147 | Dominated by SSPS/NSSS programme names (allowances, pensions, stipends) |
| UTILITIES | 27 | Power, gas, water connections and billing |
| TRANSPORT | 25 | BRTA licensing, registration, fitness |
| PASSPORT_IMMIGRATION | 17 | e-Passport, visa, immigration |
| CIVIL_REGISTRATION | 15 | Birth, death, marriage registration |
| LAND | 14 | Mutation, khatian, map, land tax |
| POST | 13 | Postal savings, remittance, EMS |
| CERTIFICATES | 12 | Educational, character, income certificates |
| EDUCATION | 12 | Board registration, scholarships, equivalency |
| HEALTH | 12 | DGHS, hospital, medical council |
| IDENTITY | 12 | NID, voter ID services |
| LOCAL_GOVERNMENT | 10 | Union/city/DC-facing certificates |
| AGRICULTURE | 8 | Farmer registration, extension |
| DISASTER_RELIEF | 8 | Relief, rehabilitation programmes |
| HOUSING | 8 | BHBFC, PWD, allotments |
| INVESTMENT | 8 | BIDA OSS, industrial services |
| WOMEN_CHILDREN | 8 | MoWCA programmes |
| ICT | 9 | BTRC, digital centres |
| LICENCES | 6 | Arms, explosives, trade licences |
| EXPATRIATE | 6 | BMET, expatriate welfare |
| ENVIRONMENT | 6 | DoE clearance, EIA |
| FISHERIES | 6 | DoF registration |
| LEGAL_AID | 6 | NLASO legal aid |
| POLICE | 6 | Verification, clearance |
| RELIGIOUS_AFFAIRS | 6 | Hajj, waqf (partial verification) |
| BUSINESS | 4 | Trade licence, RJSC |
| REGISTRATIONS | 5 | Misc. registrations |
| CUSTOMS | 3 | Import/export declarations |
| TAX | 3 | e-TIN, return filing |
| TRADE | 3 | Export promotion |
| VAT | 2 | VAT registration |
| RAILWAYS | 3 | BR ticketing, pass |
| DIGITAL_GOVERNMENT | 1 | Aggregator entry (myGov) |
| GOVERNMENT_PAYMENTS | 1 | Chalan/payment gateway |

**Observation:** Social protection accounts for **34%** of canonical services because the official SSPS registry enumerates programmes individually rather than as a single “social safety net” meta-service.

---

## 5. Responsible authorities (top 20 by service count)

| Authority | Services |
|-----------|----------:|
| Bangladesh Road Transport Authority (BRTA) | 25 |
| Ministry of Social Welfare | 23 |
| Local Government Division, MoLGRD&C | 22 |
| Ministry of Land (DLRMS) | 14 |
| Bangladesh Post Office (Directorate of Posts) | 13 |
| Ministry of Women & Children Affairs | 13 |
| Bangladesh Election Commission (NID Wing) | 12 |
| Ministry of Disaster Management & Relief | 12 |
| Union Parishad | 11 |
| Office of the Registrar General, Birth and Death Registration | 10 |
| Department of Immigration and Passports (DIP) | 10 |
| Ministry of Health & Family Welfare | 10 |
| Dhaka Electric Supply Company Limited (DESCO) | 9 |
| Ministry of Education | 9 |
| Rural Development & Cooperatives Division | 9 |
| Bureau of Manpower, Employment and Training (BMET) | 8 |
| Bangladesh Investment Development Authority (BIDA) | 8 |
| National Board of Revenue (NBR) | 7 |
| Bangladesh Police | 6 |
| Department of Agricultural Extension (DAE) | 5 |

Full authority index: `data/service_catalogue/authorities.json` (98 authorities).

**Gap:** Many entries have `authority_id: null` — human-readable authority names are present but not all are slug-linked yet.

---

## 6. Lifecycle coverage

Lifecycle tagging is **partial** in this discovery pass (intentionally deferred for breadth-first inventory):

| Lifecycle stage | Tagged services |
|-----------------|----------------:|
| social_protection | 146 |
| family | 6 |
| property | 6 |
| employment | 3 |
| business | 2 |
| retirement | 2 |
| childhood | 1 |
| education | 1 |
| **Untagged** | **273 (63%)** |

**Interpretation:** Most services are categorized by domain (TRANSPORT, LAND, etc.) rather than lifecycle stage. A future pass should tag high-traffic citizen journeys (birth → NID → marriage → property → death) for personalized requirement engines.

---

## 7. Duplicate and overlapping services

### 7.1 Tracked duplicates (14)

These MVP/legacy/alternate slugs are recorded in `duplicates.json` and point to canonical services:

| Alias slug | Canonical service |
|------------|-------------------|
| `passport-renewal`, `passport-reissue`, `e-passport-renewal` | `epassport-reissue` |
| `e-passport-application` | `epassport-new-application` |
| `mrp-passport-initial` | `passport-mrp-initial` |
| `mrp-passport-reissue` | `passport-mrp-reissue` |
| `driving-licence-renewal` | `brta-driving-license-renewal` |
| `nid-correction` | `nid-card-info-correction` |
| `birth-registration`, `birth-certificate` | `civil-birth-registration` |
| `death-certificate-bris` | `civil-death-registration` |
| `death-certificate-union` | `local-death-certificate-union` |
| `voter-registration` | `nid-new-voter-registration` |
| `tin-registration` | `tax-etin-registration` |

### 7.2 Known overlaps (not yet merged)

These pairs may be the same service or parent/child variants — require editorial review before merging:

| Service A | Service B | Issue |
|---------|-----------|-------|
| `civil-birth-registration` | Union/city birth certificate issuance | BDRIS vs local delivery channel |
| `civil-death-registration` | `local-death-certificate-union` | National register vs local certificate |
| `civil-marriage-registration` | `local-marriage-certificate-union` | Registration vs certificate copy |
| Multiple BRTA “learner / amateur / professional” licence types | Overlapping renewal paths | Variant vs duplicate |
| SSPS individual allowance programmes | Similar allowances under different ministries | Programme-level granularity |

---

## 8. Services needing verification (6)

| service_id | Name | Authority | Concern |
|------------|------|-----------|---------|
| `agri-livestock-registration` | Livestock Registration and Services | DLS | Official portal path unconfirmed |
| `agri-seed-certification` | Seed Certification and Registration | BADC/Seed Wing | Weak direct URL |
| `dc-armed-forces-property-noc` | Armed Forces Property NOC | DC Office | Niche DC circular; needs circular reference |
| `expatriate-bmet-demand-verification` | Foreign Job Demand/Offer Verification | BMET | Service name inferred from expatriate protection context |
| `religious-mora-portal` | MoRA Services Overview | Ministry of Religious Affairs | Generic portal aggregator |
| `religious-waqf-services` | Waqf Property Management | Islamic Foundation / Waqf | Portal structure unclear |

---

## 9. Coverage gaps and missing areas

The following areas are **under-represented or absent** relative to a full national inventory:

### 9.1 Institutional coverage

- **Per-ministry exhaustive scrape** — Cabinet Division Rules of Business list 50+ ministries; not every attached department was traversed.
- **myGov.bd full service index** — Sector pages reviewed; complete machine-readable service list not ingested.
- **District / upazila / pourashava** — Generic patterns captured (DC attestation, union certificates); not expanded per district (64 districts × local variants).
- **City corporations** — DNCC/DSCC samples only; other city corporations (Chattogram, Sylhet, etc.) partially missing.
- **Public universities & autonomous bodies** — Limited (education board focus); UGC-affiliated university admin services largely absent.
- **Judiciary & courts** — Case filing, certified copy, legal records not systematically covered (NLASO legal aid only).
- **Defence & security** — Civilian-facing MOD services largely absent (except one DC NOC entry).
- **Parliament, EC election ops beyond NID** — Candidate nomination, election dispute processes not covered.
- **Bangladesh Bank / financial regulation** — Consumer banking complaints, forex—not covered.
- **Professional councils** — Bar, engineering, nursing councils partially or missing.
- **Cooperatives & microfinance** — Beyond RDCD division samples.

### 9.2 Service-type gaps

- **Permits & environmental clearance variants** (DoE, forest, wetland)
- **Court / police / prison** records and certificates
- **Municipal building plan approval** (RAJUK vs other development authorities)
- **Agricultural credit** (Bangladesh Bank refinance, Krishi Bank loans as schemes)
- **Rail / air / sea port** operational permits (beyond BR passenger tickets)
- **Telecom consumer complaints** (beyond BTRC licence-facing services)
- **Freedom fighter / special status** certificates beyond BFFWT programmes

### 9.3 Data quality gaps

- **Bangla names** — Some entries have `service_name_bn: null` where English-only sources were used.
- **Lifecycle tags** — 63% untagged.
- **authority_id linkage** — Incomplete slug normalization.
- **DEPRECATED services** — Legacy MRP-only passport flows not explicitly marked deprecated vs e-Passport successors.

---

## 10. Discovery sources (primary)

| Source | URL / reference | Contribution |
|--------|-----------------|--------------|
| SSPS Social Security Programmes | [ssps.gov.bd](https://ssps.gov.bd) | 142 programmes → 147 social protection entries |
| Birth & Death Registration (BDRIS) | [bdris.gov.bd](https://bdris.gov.bd) | Civil registration cluster |
| e-Passport | [epassport.gov.bd](https://epassport.gov.bd) | Passport/immigration cluster |
| BRTA BSP | [bsp.brta.gov.bd](https://bsp.brta.gov.bd) | Transport/licensing cluster |
| EC NID | [services.nidw.gov.bd](https://services.nidw.gov.bd) | Identity cluster |
| e-TIN / NBR | [nbr.gov.bd](https://nbr.gov.bd) | Tax cluster |
| DLRMS / Land Ministry | [land.gov.bd](https://land.gov.bd) | Land services |
| myGov.bd | [mygov.bd](https://mygov.bd) | Cross-sector discovery |
| BIDA OSS | [bida.gov.bd](https://bida.gov.bd) | Investment/business |
| BMET | [bmet.gov.bd](https://bmet.gov.bd) | Expatriate labour |
| Curated batch files | `data/service_catalogue/sources/*.json` | 291 pre-normalized discovery records |

---

## 11. Completeness statement

| Claim | Supported? |
|-------|------------|
| “All Bangladesh government services” | **No** — evidence does not support this |
| “Broad discovery-phase inventory” | **Yes** |
| “432 canonical services with 91% CONFIRMED status” | **Yes** — per `metadata.json` |
| “Social protection programmes well represented” | **Yes** — SSPS-backed |
| “Local government exhaustively covered” | **No** — pattern-based samples only |

**Suggested completeness metrics for future phases:**

1. **Authority coverage ratio** — authorities with ≥1 service / estimated total gov bodies  
2. **myGov service parity** — catalogue entries matched to myGov service IDs  
3. **Lifecycle journey coverage** — % of life events with ≥1 CONFIRMED service chain  
4. **Verification debt** — count of LIKELY + NEEDS_VERIFICATION trending down over time  

---

## 12. Recommended next steps

1. **Verification sprint** — Resolve 6 NEEDS_VERIFICATION and 33 LIKELY entries against primary official pages.  
2. **myGov alignment pass** — Scrape or obtain official myGov service manifest; map IDs.  
3. **Lifecycle tagging** — Tag all high-frequency citizen services.  
4. **Authority normalization** — Complete `authority_id` slugs; align with ministry/agency registry.  
5. **Requirements phase (separate)** — Only after catalogue stabilization: fees, documents, steps per `SERVICE_CATALOGUE_SPECIFICATION.md`.  
6. **MVP curation** — Select 5–20 priority services for full knowledge ingestion (per implementation roadmap).

---

## 13. Rebuild instructions

```bash
# From repository root
python3 scripts/build_service_catalogue.py
```

This regenerates `services.json`, `duplicates.json`, `authorities.json`, `metadata.json`, and `by_category/*.json` from `data/service_catalogue/sources/`.

---

*Report generated for Bangladeshi Assistant knowledge foundation — discovery phase.*
