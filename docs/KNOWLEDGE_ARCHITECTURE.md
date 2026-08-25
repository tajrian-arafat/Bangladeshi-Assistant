# Knowledge Architecture — Bangladeshi Assistant

**Version:** 1.0 (design)  
**Date:** 2026-08-24  
**Principle:** The verified knowledge layer is the source of truth; the LLM interprets, retrieves, personalizes, and communicates — it does not invent facts.

---

## 1. Architectural Vision

Bangladeshi Assistant evolves from a **template chatbot** into a **continuously maintained, verified, Bangladesh-specific public-service knowledge system** with a conversational interface.

```
┌─────────────────────────────────────────────────────────────────┐
│                        CONVERSATIONAL LAYER                      │
│  (Next.js UI, clarifications, Bengali/English/Banglish)         │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                     REASONING & ORCHESTRATION                    │
│  Intent → Service ID → Context → Retrieval → Validation → LLM   │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                   VERIFIED KNOWLEDGE LAYER (SoT)                 │
│  Services │ Claims │ Evidence │ Sources │ Versions │ Reviews    │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│              INGESTION, DISCOVERY & MAINTENANCE                  │
│  Crawl │ Extract │ Normalize │ Verify │ Publish │ Monitor        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. End-to-End Request Flow

```
USER MESSAGE
     │
     ▼
┌─────────────────┐
│ Language detect │  bn / en / banglish
└────────┬────────┘
         ▼
┌─────────────────┐
│ Banglish norm   │  Gazetteer + transliteration rules
└────────┬────────┘
         ▼
┌─────────────────┐
│ Intent detect   │  document_list, procedure, fee, office, eligibility, …
└────────┬────────┘
         ▼
┌─────────────────┐
│ Service ID      │  Catalogue match + disambiguation
└────────┬────────┘
         ▼
┌─────────────────┐
│ User context    │  District, applicant type, prior clarifications
└────────┬────────┘
         ▼
┌─────────────────┐
│ Structured      │  Service record, procedures, requirements (typed fields)
│ retrieval       │
└────────┬────────┘
         ▼
┌─────────────────┐
│ Evidence        │  Chunks + claims linked to source versions
│ retrieval       │
└────────┬────────┘
         ▼
┌─────────────────┐
│ Authority eval  │  Tier weighting, official-only for hard requirements
└────────┬────────┘
         ▼
┌─────────────────┐
│ Freshness eval  │  Staleness thresholds, scheduled recheck flags
└────────┬────────┘
         ▼
┌─────────────────┐
│ Conflict detect │  Cross-source disagreement → suppress or warn
└────────┬────────┘
         ▼
┌─────────────────┐
│ Personalization │  Conditional requirements, minimal questions
└────────┬────────┘
         ▼
┌─────────────────┐
│ LLM reasoning   │  Natural language ONLY over approved fact bundle
└────────┬────────┘
         ▼
┌─────────────────┐
│ Citation /      │  Every surfaced fact maps to evidence_id(s)
│ provenance val  │
└────────┬────────┘
         ▼
    ANSWER + CITATIONS + CONFIDENCE + WARNINGS
```

---

## 3. Master Service Catalogue

The **master service catalogue** is the authoritative inventory of public services the system knows about — not necessarily all services that exist in Bangladesh.

### 3.1 Catalogue principles

- **Discoverability over completeness claims:** Never mark the catalogue "complete" without justified coverage metrics.
- **Stable IDs:** Each service has an immutable `service_id` (UUID) and human slug.
- **Hierarchy:** Ministry → agency → service → procedure variant → localized variant.
- **Aliases:** Bangla, English, Banglish, acronyms, common misspellings.
- **Lifecycle:** `DISCOVERED → DRAFT → UNDER_REVIEW → ACTIVE → DEPRECATED`.

### 3.2 Relationship to existing `services` table

Extend the current `Service` model rather than replace it. Add normalized tables for variants, localization, and catalogue metadata (see SERVICE_CATALOGUE_SPECIFICATION.md).

---

## 4. Service Taxonomy

Multi-axis taxonomy (a service can have primary + secondary tags):

| Axis | Examples |
|------|----------|
| Domain | Identity, Transport, Tax, Land, Education, Health, … |
| Service type | Registration, renewal, correction, licence, permit, certificate, payment |
| Delivery channel | Online, in-person, hybrid, mail |
| Jurisdiction | National, division, district, upazila, city corporation |
| Audience | Citizen, business, student, expatriate, disabled, senior |

Taxonomy drives browse UI, discovery crawlers, and intent routing.

---

## 5. Service Database (Structured Knowledge)

**Do not store government services as plain paragraphs.**

Each service is a structured document composed of typed sub-records:

| Field group | Storage approach |
|-------------|------------------|
| Identity | `service_id`, names, aliases, slug, category, subcategory |
| Ownership | `ministry_id`, `agency_id`, responsible offices |
| Scope | `target_users[]`, `geographic_scope`, `application_methods[]` |
| Requirements | Requirement engine (MUST / CONDITIONAL / RECOMMENDED / N/A) |
| Process | Procedure graph with steps, dependencies, URLs |
| Costs | Fee records with effective dates + evidence |
| Legal | `legal_basis[]` with citations |
| Meta | `verification_status`, `confidence`, `freshness`, `version`, `effective_date` |

Paragraph text exists only as **evidence excerpts** attached to claims, not as the canonical store.

---

## 6. Source Database

Parallel catalogue of **information sources** (not services):

```
Source
  ├── domain, tier, agency_id, crawl policy
  └── SourceVersion[] (url, content_hash, fetched_at, published_at)
        └── KnowledgeDocument[]
              └── KnowledgeChunk[] (for retrieval)
```

Sources are registered before crawling. Each source has parser profile, rate limits, robots policy, and allowed paths.

---

## 7. Evidence & Provenance

Every **claim** is a atomic fact (e.g., "Renewal fee is X BDT", "NID is required").

```
Claim
  ├── claim_type (fee, document, step, eligibility, duration, url, …)
  ├── value (structured JSON)
  ├── information_class: OFFICIAL | PRACTICAL | DISCOVERY
  ├── service_id (optional)
  └── ClaimEvidence[]
        ├── evidence_id → KnowledgeChunk or structured field snapshot
        ├── source_version_id
        ├── excerpt, locator (page, section, selector)
        ├── retrieved_at
        └── verified_at (nullable until approved)
```

**Traceability chain:** Answer bullet → Claim → Evidence → SourceVersion → Source → Tier.

---

## 8. Verification System

See [VERIFICATION_FRAMEWORK.md](./VERIFICATION_FRAMEWORK.md).

States per claim:

| State | Meaning |
|-------|---------|
| `DISCOVERED` | Extracted, untrusted |
| `NORMALIZED` | Mapped to schema |
| `PENDING_REVIEW` | Awaiting human |
| `VERIFIED` | Approved for OFFICIAL class |
| `REJECTED` | Not publishable |
| `STALE` | Was verified; source changed |

Service-level `status` aggregates claim states — a service cannot be `ACTIVE` if critical claims are unverified.

---

## 9. Source Authority

See [SOURCE_AUTHORITY_MODEL.md](./SOURCE_AUTHORITY_MODEL.md).

Retrieval and answer assembly **weight** evidence by tier. Hard requirements (MUST documents, fees, legal steps) may only come from **Tier 1–2 OFFICIAL** claims unless explicitly marked practical with disclaimer.

---

## 10. Service Versioning

- **Service.version** increments on any published change to official fields.
- **Procedure.version** and **Fee.version** track sub-resource changes.
- **SourceVersion** captures each fetch snapshot.
- **ChangeEvent** records diffs for review queue.
- Users can query `effective_date` for time-travel ("what was true in 2024?") — future capability.

---

## 11. Freshness

| Signal | Action |
|--------|--------|
| `source_updated_at` from page | Update freshness clock |
| Scheduled recrawl (tier-based) | Tier 1: weekly–monthly; Tier 5–7: manual |
| User report / broken link job | Flag STALE |
| `max_age_days` per field type | Fees: 90d; URLs: 30d; steps: 180d (configurable) |

Freshness feeds **confidence** and triggers warnings in answers.

---

## 12. Conflict Detection

When two verified claims disagree (e.g., different fees):

1. Prefer **higher authority tier**.
2. If same tier, prefer **newer source_version**.
3. If unresolvable, **suppress fact** and surface conflict to user + review queue.

Existing `detect_conflicts()` in code operates on evidence metadata — extend to **claim-level** comparison.

---

## 13. Personalized Requirements

See [PERSONALIZED_REQUIREMENT_ENGINE.md](./PERSONALIZED_REQUIREMENT_ENGINE.md).

The assistant asks the **minimum** clarifying questions to resolve CONDITIONAL items, then emits a personalized checklist.

---

## 14. Procedure / Workflow Engine

Extend current `ProcedureEngine`:

- Support **multiple procedure variants** per service (online vs. in-person, first-time vs. renewal).
- Step preconditions as evaluable rules (same condition DSL as requirements).
- **Dependencies** between steps and between services ("need NID before passport").
- District-specific step overrides via `ServiceOffice` + localization layer.

Intent `procedure_inquiry` returns steps; `document_list` returns checklist; `fee_inquiry` returns fees — not all sections every time.

---

## 15. Knowledge Quality Score

See [KNOWLEDGE_QUALITY_FRAMEWORK.md](./KNOWLEDGE_QUALITY_FRAMEWORK.md).

Composite score per service (0–100):

- Coverage (% of required fields populated with verified claims)
- Authority (% Tier 1–2 sourced)
- Freshness (age-weighted)
- Consistency (no open conflicts)
- User feedback (helpful/not helpful)

Scores drive admin prioritization and public confidence display.

---

## 16. Knowledge Gaps

Explicit `KnowledgeGap` records:

```
service_id, field_name, gap_type, priority, discovered_by, notes
```

Gaps are created when:

- User query cannot be answered from verified data
- Crawler finds service mention without catalogue entry
- Evaluation harness fails golden query

Feeds catalogue discovery and editorial backlog — **never hallucinate to close a gap**.

---

## 17. Human / Admin Review

Roles (existing seed):

| Role | Capability |
|------|------------|
| `knowledge_editor` | CRUD drafts, link evidence |
| `reviewer` | Approve/reject claims, publish versions |
| `ops_admin` | Crawls, feature flags |
| `auditor` | Read-only audit trail |

Workflow: ChangeEvent → ReviewQueueItem → approve → publish → bump version → re-embed chunks.

Admin UI fixes are implementation-phase; architecture assumes **no auto-publish** for Tier 1–2 claims without reviewer action.

---

## 18. RAG Integration

RAG is **retrieval over verified chunks**, not open-domain generation.

### 18.1 Indexing

- Chunk official documents at semantic boundaries (section, table row, list item).
- Store metadata: `service_id`, `claim_ids[]`, `language`, `tier`, `information_class`.
- Embed with configured model (`BAAI/bge-m3` or successor); pgvector index.

### 18.2 Retrieval pipeline

1. **Structured pull:** Load verified claims for matched service + intent.
2. **Hybrid search:** BM25/FTS + vector + RRF over chunks.
3. **Filter:** `information_class=OFFICIAL` for requirements; include PRACTICAL only in labeled section.
4. **Pack context:** JSON fact bundle for LLM (not raw HTML).

### 18.3 Generation constraints

- LLM receives: user message, language, fact bundle, allowed citation IDs.
- LLM must not introduce IDs/URLs/fees not in bundle.
- Post-validate output against bundle (implementation-phase guardrail).

---

## 19. Bengali / English / Banglish Support

| Layer | Approach |
|-------|----------|
| Detection | Existing `detect_language()` |
| Banglish | Expand `normalize_banglish()` gazetteer from catalogue aliases |
| UI | next-intl bn/en |
| Knowledge | Parallel `name_bn`, `label_bn`, `description_bn` on all user-facing records |
| Retrieval | Query in any language; search across bn/en alias index |
| Generation | LLM prompt specifies response language; structured fields pre-localized |

Banglish variants stored as aliases, not as duplicate services.

---

## 20. District / Upazila Localization

Phased geography model:

```
Division → District → Upazila → Union / Ward (future)
City Corporation (orthogonal overlay)
```

Localized overrides:

- Office locations (`ServiceOffice.district_id`, future `upazila_id`)
- Step text ("Submit at local union parishad")
- Conditional requirements (district-specific forms)

User context from entities + clarifications selects applicable override set.

---

## 21. Official vs. Practical Information

Mandatory separation in answers:

| Section | Source class | Citation rule |
|---------|--------------|---------------|
| Official requirements | OFFICIAL, Tier 1–2 | Required |
| Steps & fees (official) | OFFICIAL | Required |
| Practical tips | PRACTICAL, Tier 5–7 | Labeled "community report", never promoted to MUST |

Example structure in UI:

> **Official:** X is required. [cite]  
> **Commonly reported:** Some applicants mention Y. [cite, practical] — not verified as universal.

---

## 22. Mapping to Existing Codebase

| Target component | Current module | Action |
|------------------|----------------|--------|
| Orchestrator | `ai/orchestrator.py` | Add stages, intent-driven sections |
| Retrieval | `retrieval/hybrid_search.py` | Implement real hybrid + claim retrieval |
| Checklist | `engines/checklist_engine.py` | Extend condition DSL |
| Procedure | `engines/procedure_engine.py` | Variants + localization |
| Models | `domain/models/knowledge.py` | Add Claim, KnowledgeGap tables |
| Workers | `workers/tasks.py` | Real crawl/embed pipeline |
| Admin | `api/v1/endpoints/admin.py` | Auth, approve, CRUD |

---

## 23. Non-Goals (This Phase)

- Mass ingestion of unverified content
- UI redesign
- Claiming catalogue completeness
- Fabricating URLs, fees, or requirements

---

## Related Documents

- [CURRENT_SYSTEM_AUDIT.md](./CURRENT_SYSTEM_AUDIT.md)
- [SERVICE_CATALOGUE_SPECIFICATION.md](./SERVICE_CATALOGUE_SPECIFICATION.md)
- [SOURCE_AUTHORITY_MODEL.md](./SOURCE_AUTHORITY_MODEL.md)
- [VERIFICATION_FRAMEWORK.md](./VERIFICATION_FRAMEWORK.md)
- [PERSONALIZED_REQUIREMENT_ENGINE.md](./PERSONALIZED_REQUIREMENT_ENGINE.md)
- [KNOWLEDGE_QUALITY_FRAMEWORK.md](./KNOWLEDGE_QUALITY_FRAMEWORK.md)
- [DATA_INGESTION_PIPELINE.md](./DATA_INGESTION_PIPELINE.md)
- [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md)
