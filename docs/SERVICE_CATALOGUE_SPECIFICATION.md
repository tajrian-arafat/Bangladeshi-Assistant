# Service Catalogue Specification — Bangladeshi Assistant

**Version:** 1.0 (design)  
**Date:** 2026-08-24

---

## 1. Purpose

Define how Bangladeshi Assistant discovers, identifies, registers, and maintains a **master service catalogue** — the inventory of public/government services the system can answer about.

**This document specifies methodology and schema — not a list of services.** No completeness claims until coverage metrics justify them.

---

## 2. Catalogue Object Definition

A **catalogue entry** represents one citizen-facing public service or distinct service variant (e.g., "Passport renewal" vs. "Passport reissue for lost passport").

Each entry must have:

| Field | Required | Description |
|-------|----------|-------------|
| `service_id` | Yes | UUID, immutable |
| `slug` | Yes | URL-safe unique key |
| `name_bn` | Yes | Official or standard Bangla name |
| `name_en` | Yes | English name |
| `aliases` | Yes | Array: Banglish, acronyms, colloquial terms |
| `category` | Yes | Primary taxonomy domain |
| `subcategory` | Recommended | Finer classification |
| `ministry_id` | Recommended | Parent ministry |
| `agency_id` | Yes | Responsible agency |
| `target_users` | Recommended | e.g., citizen, business, student |
| `geographic_scope` | Yes | national / division / district / local |
| `service_type` | Yes | registration, renewal, correction, licence, … |
| `status` | Yes | Lifecycle state |
| `verification_status` | Yes | Aggregate verification |
| `confidence` | Yes | 0.0–1.0 editorial confidence |
| `freshness` | Yes | Last verified timestamp + score |
| `version` | Yes | Integer, increments on publish |
| `effective_date` | Optional | When this version became active |

Extended fields (stored as structured sub-records, not prose):

- eligibility, prerequisites, application methods, application URL
- official information URLs, forms, fees, payment methods, processing time
- steps (procedure graph), office locations, dependencies, legal basis
- source references (claim/evidence links)

---

## 3. Service Identity Rules

### 3.1 One service vs. multiple entries

Create **separate catalogue entries** when:

- Different agencies own the process
- Different application portals/forms
- Mutually exclusive eligibility (individual vs. business TIN)
- Distinct fee schedules and legal basis

Use **procedure variants** under one entry when:

- Same agency and outcome, different paths (online vs. in-office)
- Same core documents with conditional extras

### 3.2 Slug conventions

```
{domain}-{action}[-{variant}]

Examples:
  passport-renewal
  passport-reissue-lost
  nid-correction-name
  tin-registration-individual
  tin-registration-business
  driving-licence-renewal-professional
```

### 3.3 Aliases

Maintain alias types:

| Type | Example |
|------|---------|
| `en` | "passport renew" |
| `bn` | "পাসপোর্ট নবায়ন" |
| `banglish` | "passport renew korte", "e-passport update" |
| `acronym` | "DIP", "BRTA" |
| `misspelling` | "liscence renew" |

Aliases feed fuzzy matching and Banglish normalization.

---

## 4. Taxonomy

### 4.1 Primary domains (minimum set)

1. Identity & Civil Registration  
2. Passport & Immigration  
3. Police  
4. BRTA & Transport  
5. Land  
6. Tax  
7. VAT  
8. Customs  
9. Business & Trade  
10. Education  
11. Health  
12. Agriculture / Fisheries / Livestock  
13. Employment & Labour  
14. Expatriate / Migration  
15. Social Protection  
16. Disability Services  
17. Women & Children  
18. Elderly Services  
19. Disaster Relief  
20. Legal / Public Services  
21. Local Government  
22. Certificates / Licences / Registrations / Permits  
23. Government Payments  
24. Public Utilities  
25. Environment  

Services may have **secondary tags** (e.g., "Transport" + "Licence").

### 4.2 Service type enum

`REGISTRATION | RENEWAL | CORRECTION | REPLACEMENT | LICENCE | PERMIT | CERTIFICATE | PAYMENT | INFORMATION | COMPLAINT | OTHER`

---

## 5. Discovery Methodology

Catalogue growth is **systematic**, not random scraping.

### 5.1 Discovery sources (priority order)

| Priority | Source type | Method |
|----------|-------------|--------|
| P1 | Official agency service lists | Manual + assisted crawl of ministry/agency sites |
| P2 | National portals | a2i, Bangladesh Portal, e-Gov service indexes |
| P3 | Statutory mandates | Act/regulation schedules of services |
| P4 | Division/district admin sites | Regional service pages |
| P5 | City corporations / municipalities | Local service matrices |
| P6 | Public institution sites | Boards, universities, regulators |
| P7 | Tier 5–7 discovery | News, guides, social — **discovery only**, not auto-publish |

### 5.2 Discovery workflow

```
1. SCAN    → Crawler/manual review of source sitemap
2. EXTRACT → Service name, agency, URL (minimal metadata)
3. REGISTER→ Create DISCOVERED entry with source reference
4. DEDUPE  → Match against existing slugs/aliases/fuzzy name
5. PRIORITIZE → Score by demand (queries, population impact)
6. CURATE  → Full structured curation (separate pipeline)
```

### 5.3 Deduplication signals

- Same `agency_id` + high name similarity (>90)
- Same official application URL
- Shared form code
- Manual reviewer merge

### 5.4 Coverage metrics (when reporting progress)

| Metric | Definition |
|--------|------------|
| `registered_services` | Count in catalogue any status |
| `active_verified_services` | ACTIVE + quality score ≥ threshold |
| `domain_coverage` | % of taxonomy domains with ≥1 ACTIVE service |
| `agency_coverage` | % of registered agencies with ≥1 service |
| `query_coverage` | % golden queries answerable with citations |

**Never claim "complete catalogue"** unless methodology + metrics are published and audited.

---

## 6. Organizational Hierarchy

```
Ministry (new table: ministries)
  └── Agency (existing: agencies)
        └── Service (existing: services)
              └── ProcedureVariant (extend procedures)
                    └── LocalizedVariant (district/upazila overrides)
```

### 6.1 Ministry table (proposed)

| Field | Description |
|-------|-------------|
| `ministry_id` | UUID |
| `slug` | e.g., `home-affairs` |
| `name_bn`, `name_en` | Official names |
| `website_url` | Primary portal |

Agencies link to ministries. Services inherit ministry through agency.

---

## 7. Geographic Scope Model

| Scope | Meaning |
|-------|---------|
| `NATIONAL` | Same process nationwide |
| `DIVISION` | Varies by division |
| `DISTRICT` | Varies by district |
| `UPAZILA` | Varies by upazila |
| `CITY_CORPORATION` | Urban body specific |

Geographic applicability stored on service or variant. Office locations (`service_offices`) attach to district/upazila when known.

---

## 8. Lifecycle States

```
DISCOVERED → DRAFT → UNDER_REVIEW → ACTIVE → DEPRECATED → ARCHIVED
```

| State | Public visibility | Chat answers |
|-------|-------------------|--------------|
| DISCOVERED | Hidden | "Service identified but not yet available" |
| DRAFT | Hidden | No |
| UNDER_REVIEW | Optional stub page | Template + strong disclaimers (current MVP) |
| ACTIVE | Full | Verified answers with citations |
| DEPRECATED | Page with notice | Redirect to successor service |
| ARCHIVED | Hidden | No |

Promotion to `ACTIVE` requires minimum quality score (see KNOWLEDGE_QUALITY_FRAMEWORK.md).

---

## 9. Catalogue Entry Template (Curation)

When curators create/complete an entry, they fill structured sections — **not a wiki article**.

### Required for ACTIVE (minimum viable verified service)

- [ ] Unique service_id + slug  
- [ ] Bangla + English names  
- [ ] Agency + category  
- [ ] ≥1 OFFICIAL source (Tier 1–2) registered  
- [ ] Application method(s) with verified URL(s)  
- [ ] MUST requirement list with evidence each  
- [ ] Procedure with ≥1 verified step  
- [ ] Fee OR explicit "no fee" with evidence  
- [ ] Processing time OR "not stated officially"  
- [ ] Reviewer approval + `last_verified_at`  

### Recommended

- CONDITIONAL requirements with rules  
- Forms with URLs  
- Office locator data  
- Legal basis citations  
- Practical section (clearly separated)  

---

## 10. Relationship to Seed Data

Current MVP (`data/seeds/mvp_services.json`):

| Slug | Status | Action |
|------|--------|--------|
| passport-renewal | UNDER_REVIEW | Keep slug; replace content via verification |
| nid-correction | UNDER_REVIEW | Same |
| driving-licence-renewal | UNDER_REVIEW | Same |
| birth-registration | UNDER_REVIEW | Same |
| tin-registration | UNDER_REVIEW | Same |

These are **catalogue placeholders**, not verified facts.

---

## 11. API & Admin (Future)

| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/services` | Public browse (existing) |
| `GET /api/v1/services/{slug}` | Detail (existing) |
| `POST /api/v1/admin/services` | Create draft |
| `PATCH /api/v1/admin/services/{id}` | Edit draft |
| `POST /api/v1/admin/services/{id}/publish` | Bump version, ACTIVE |
| `GET /api/v1/admin/catalogue/gaps` | Knowledge gaps |
| `GET /api/v1/admin/catalogue/coverage` | Metrics dashboard |

---

## 12. Research Methodology (Catalogue Phase)

When expanding the catalogue:

1. **Start from agency list** — seed ministries/agencies from official directories (manually verified).
2. **Per agency:** locate "services", "citizen charter", "forms", "fees" pages.
3. **Extract service names only** — register DISCOVERED entries.
4. **Prioritize top 50–100** by estimated demand before deep curation.
5. **Log gaps** when official info is missing — do not infer.

---

## Related Documents

- [KNOWLEDGE_ARCHITECTURE.md](./KNOWLEDGE_ARCHITECTURE.md)
- [SOURCE_AUTHORITY_MODEL.md](./SOURCE_AUTHORITY_MODEL.md)
- [VERIFICATION_FRAMEWORK.md](./VERIFICATION_FRAMEWORK.md)
- [DATA_INGESTION_PIPELINE.md](./DATA_INGESTION_PIPELINE.md)
- [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md)
