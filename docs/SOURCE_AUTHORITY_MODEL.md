# Source Authority Model — Bangladeshi Assistant

**Version:** 1.0 (design)  
**Date:** 2026-08-24

---

## 1. Purpose

Define how Bangladeshi Assistant classifies, weights, and uses information sources so that **official facts** and **practical experience** are handled differently.

---

## 2. Tier Definitions

| Tier | Label | Description | Examples (illustrative — must be registered per source) |
|------|-------|-------------|--------------------------------------------------------|
| **1** | Primary official | Government body **directly responsible** for the service | Agency's own `.gov.bd` service page, official application portal operated by agency |
| **2** | Secondary official | Official government portal or related official agency | National portal, Bangladesh Portal, related ministry circular |
| **3** | Official institution | Public institution, regulator, state bank, public university | Education boards, BBB, scheduled bank official notices |
| **4** | Recognized institutional | Semi-official or legally recognized body | Professional councils, licensed associations with statutory role |
| **5** | Reliable news/media | Established journalism | Reputed newspapers (policy changes, dates) |
| **6** | Professional guides | Expert blogs, NGO guides, legal aid sites | Practical walkthroughs — discovery and supplement only |
| **7** | Social/community | Facebook, YouTube, Reddit, forums | **Discovery and practical reports only** — never auto-authoritative |

**Note:** Tier assignment is per **registered source**, not per domain guess. Register each source in the `sources` table with evidence of authority.

---

## 3. Information Class (Orthogonal to Tier)

| Class | Meaning | Can support MUST requirements? |
|-------|---------|-------------------------------|
| `OFFICIAL` | Stated by authoritative source as requirement/policy | Yes (Tier 1–2); Tier 3–4 with reviewer approval |
| `PRACTICAL` | Reported experience, tips, unofficial norms | **No** — display separately with disclaimer |
| `DISCOVERY` | Unverified lead (name, URL, rumor) | **No** — catalogue discovery only |

Every claim carries both `tier` (from source) and `information_class`.

---

## 4. Authority Rules for Answer Assembly

### 4.1 Hard facts (strict)

These may appear as requirements only from OFFICIAL claims:

- Required documents (MUST)
- Fees and payment methods
- Legal eligibility
- Application URLs
- Processing time stated officially
- Legal basis

**Minimum tier:** 1–2 preferred; tier 3–4 requires reviewer flag `approved_for_requirements`.

### 4.2 Soft facts (flexible)

May draw from tier 5–6 as supplementary OFFICIAL-class **only after review**, or as PRACTICAL:

- Office hours anecdotal reports
- Queue/wait times
- Unofficial document requests (must be PRACTICAL class)

### 4.3 Tier 7 usage

| Allowed | Forbidden |
|---------|-----------|
| Discover service names | Auto-publish fees |
| Flag "commonly reported" items | Promote to MUST checklist |
| Queue for human investigation | Single-source verification |

---

## 5. Source Registration Schema

Extend existing `Source` model usage:

```yaml
source:
  id: uuid
  domain: "www.example.gov.bd"      # normalized
  title: "Directorate of Immigration and Passports"
  tier: 1
  agency_id: <uuid>               # link to responsible agency
  information_classes_allowed: [OFFICIAL, DISCOVERY]
  crawl_enabled: true
  requires_js: false
  rate_limit_rpm: 10
  robots_respected: true
  allow_paths: ["/services/*", "/fees/*"]
  deny_paths: ["/admin/*"]
  parser_profile: "gov_bd_standard"
  verification_contact: optional   # editorial note
```

### 5.1 Domain classification workflow

1. Identify owning organization  
2. Confirm domain is official (WHOIS, agency website link, gov.bd policy)  
3. Assign tier — when uncertain, **assign higher tier number** (more skeptical)  
4. Reviewer approves tier assignment  
5. Re-evaluate tier if domain changes or redirects  

---

## 6. Source Version & Provenance

Each fetch creates a `SourceVersion`:

| Field | Purpose |
|-------|---------|
| `url` | Exact page |
| `content_hash` | Change detection |
| `fetched_at` | Retrieval timestamp |
| `source_published_at` | Date on page if parseable |
| `source_updated_at` | "Last updated" on page |
| `is_published` | Whether version is active for claims |

Claims reference **specific source_version_id** so answers cite point-in-time evidence.

---

## 7. Weighting in Retrieval

Retrieval score combines semantic relevance with authority weight:

```
final_score = semantic_score * authority_weight * freshness_weight

authority_weight:
  Tier 1: 1.0
  Tier 2: 0.95
  Tier 3: 0.85
  Tier 4: 0.75
  Tier 5: 0.5
  Tier 6: 0.35
  Tier 7: 0.2 (PRACTICAL only)
```

For **requirement queries**, filter to `information_class=OFFICIAL` and `tier <= 4` (configurable).

---

## 8. Official vs. Practical in UI

Answer template sections:

1. **Summary** (official facts only)  
2. **What you need (official)** — MUST/CONDITIONAL from OFFICIAL  
3. **Steps** — from verified procedure  
4. **Fees** — OFFICIAL only  
5. **Commonly reported (not verified)** — PRACTICAL, tier 5–7, distinct styling  

Never merge section 5 into section 2 without verification event.

---

## 9. Cross-Source Conflict Resolution

When tiers conflict:

| Scenario | Resolution |
|----------|------------|
| Tier 1 vs Tier 2 | Prefer Tier 1 unless Tier 2 is newer national mandate |
| Tier 1 vs Tier 1 (different values) | Flag conflict; suppress until reviewed |
| Tier 7 vs Tier 1 | Always prefer Tier 1 |
| Tier 5 news vs old Tier 1 page | Queue recrawl of Tier 1; do not auto-update |

---

## 10. Social / Community Source Handling

### 10.1 Ingestion

- Store as PRACTICAL claims with tier 7  
- Require `report_count` or curator note for prominence  
- Never run unattended promotion rules  

### 10.2 Verification path for practical reports

If multiple independent practical reports align **and** Tier 1 source is silent:

1. Curator investigates with agency  
2. If agency confirms → new OFFICIAL claim, tier 1–2 evidence  
3. If agency denies → keep as practical with "denied by official source" note  
4. If agency silent → keep practical with uncertainty disclaimer  

---

## 11. Existing Code Alignment

| Current | Gap |
|---------|-----|
| `Source.tier` column | No sources seeded |
| Evidence `tier` in chunk metadata | Defaults to 6 |
| `detect_conflicts()` | Fee/document only; extend to claim-level |
| `calculate_confidence()` | Uses tier ≤2 heuristic — align with claim coverage |

---

## 12. Governance

- Tier assignments reviewed quarterly for top sources  
- Audit log when tier changed  
- Public citation always shows tier + class + retrieved/verified dates  

---

## Related Documents

- [KNOWLEDGE_ARCHITECTURE.md](./KNOWLEDGE_ARCHITECTURE.md)
- [VERIFICATION_FRAMEWORK.md](./VERIFICATION_FRAMEWORK.md)
- [DATA_INGESTION_PIPELINE.md](./DATA_INGESTION_PIPELINE.md)
- [KNOWLEDGE_QUALITY_FRAMEWORK.md](./KNOWLEDGE_QUALITY_FRAMEWORK.md)
