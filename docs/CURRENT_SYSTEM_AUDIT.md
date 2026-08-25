# Current System Audit — Bangladeshi Assistant

**Date:** 2026-08-24  
**Scope:** Repository audit before knowledge-foundation redesign  
**Status:** Audit complete — no code changes in this phase

---

## Executive Summary

Bangladeshi Assistant (repo: `Bangladeshi-Assistant`) is a **modular monolith** with a Next.js frontend, FastAPI backend, SQLite/PostgreSQL database, and optional local LLM. The **application shell is built**; the **verified knowledge layer is not**.

Today, answers are assembled from **seeded template data** (5 MVP services, all `UNDER_REVIEW`) with **no verified sources, fees, URLs, or knowledge chunks**. Retrieval is **ILIKE substring search**, not true hybrid RAG. The LLM is **disabled by default** and, when enabled, only rewrites the summary — it does not ground checklist, steps, or fees.

**Root cause of poor answers vs. ChatGPT:** ChatGPT draws on broad pretrained knowledge. This assistant has almost no curated Bangladesh-specific knowledge to retrieve or cite. The architecture *anticipates* a verified knowledge system but has not populated or wired it.

---

## 1. Repository Structure

```
/workspace/
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── ai/              # Orchestrator, LLM client, pipeline stages
│   │   ├── api/v1/          # REST endpoints
│   │   ├── application/     # Services, checklist/procedure engines
│   │   ├── domain/models/   # SQLAlchemy models
│   │   ├── retrieval/       # HybridSearchService (ILIKE only)
│   │   └── workers/         # Celery tasks (stubs)
│   ├── alembic/             # Single initial migration
│   └── tests/               # 11 pytest tests
├── frontend/                # Next.js 15, React 19, next-intl
├── data/
│   ├── seeds/               # Geography, agencies, MVP services
│   └── evaluation/          # golden_queries.jsonl (no harness)
├── docs/                    # Setup, deployment, architecture blueprint
├── scripts/seed_database.py
├── docker-compose.yml
└── Makefile
```

---

## 2. Current Architecture

### 2.1 Frontend

| Component | Technology | Notes |
|-----------|------------|-------|
| Framework | Next.js 15, React 19 | App Router with `[locale]` i18n |
| Styling | Tailwind CSS | Public + admin route groups |
| Data fetching | TanStack Query + custom `api.ts` | Proxies to backend |
| Locales | `en`, `bn` via next-intl | Banglish handled server-side |

**Public routes:** home/chat, services catalog, service detail, districts, about.  
**Admin routes:** login, dashboard, services list, review queue — **partially broken** (see §8).

### 2.2 Backend

| Component | Technology | Notes |
|-----------|------------|-------|
| API | FastAPI | `/api/v1/*` |
| ORM | SQLAlchemy 2 (async) | Alembic migrations |
| Validation | Pydantic v2 | Request/response schemas |
| Auth schema | JWT + RBAC models | **Not enforced on admin routes** |
| Queue | Celery + Redis | Worker tasks are stubs |

### 2.3 Database

| Environment | Engine | Vector support |
|-------------|--------|----------------|
| Development default | SQLite (`sqlite+aiosqlite:///./data/bda.db`) | No |
| Production-ready | PostgreSQL + pgvector (docker-compose) | Schema supports `embedding` column |

**Single migration:** `001_initial_schema.py` — full schema including knowledge, geography, auth, operations.

### 2.4 Deployment

- **docker-compose.yml:** postgres (pgvector), redis, minio, api, worker, scheduler, frontend; optional llm (llama.cpp) and caddy profiles.
- **Docs:** `docs/local-setup.md`, `docs/deployment.md`, runbooks under `docs/runbooks/`.
- **Architecture blueprint:** `docs/architecture/bangladesh-digital-assistant-architecture.md` (north-star design; implementation gap remains).

### 2.5 Environment Variables (key)

| Variable | Default | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | SQLite path | Database connection |
| `REDIS_URL` | `redis://localhost:6379/0` | Celery broker |
| `FEATURE_LLM_ENABLED` | `false` | LLM summary rewrite |
| `LLM_BASE_URL` | `http://localhost:8080/v1` | OpenAI-compatible local LLM |
| `EMBEDDING_MODEL` | `BAAI/bge-m3` | Configured but **unused** |
| `FEATURE_PLAYWRIGHT_CRAWL` | `false` | Crawling disabled |
| `JWT_SECRET` | placeholder | Auth (not wired to admin API) |

---

## 3. Current AI / Answer Generation Flow

```
POST /api/v1/chat
        │
        ▼
ChatService.process_chat()
        │
        ├─ Persist user Message
        │
        ▼
Orchestrator.run()
        │
        ├─ detect_language()
        ├─ normalize_banglish()
        ├─ classify_intent()          ← computed but NOT used to shape answer
        ├─ extract_entities()         ← fuzzy service match (threshold 75)
        ├─ _clarifications_needed()   ← passport/driving licence only
        │
        ├─ if clarifications → return prompt (early exit)
        │
        ├─ HybridSearchService        ← ILIKE on knowledge_chunks; fallback to service name
        ├─ detect_conflicts()         ← on evidence metadata (usually empty)
        ├─ ChecklistEngine.build()    ← from DB checklist_items + conditions
        ├─ ProcedureEngine.build_steps() ← from DB procedure_steps
        ├─ load fees from service.fees ← always empty after seed
        ├─ calculate_confidence()
        └─ _build_citations()         ← from evidence list
        │
        ▼
Optional: LLMClient.summarize()       ← only if FEATURE_LLM_ENABLED; summary text only
        │
        ▼
Persist assistant Message (answer_json, no separate citations table)
        │
        ▼
ChatResponse { answer, citations, metadata }
```

**Critical observation:** Checklist, steps, and fees come from **structured DB templates**, not from retrieved evidence. Evidence and citations are **decorative** when chunks are empty — the system falls back to citing the service record itself with tier 2 and no URL.

---

## 4. Current RAG Flow

| Stage | Designed | Implemented |
|-------|----------|-------------|
| Chunk storage | `knowledge_chunks` with embeddings | **0 chunks seeded** |
| Vector search | pgvector `EmbeddingType` column | **Not queried** |
| Full-text search | `search_vector` column | **Not used** |
| Hybrid fusion (BM25 + vector + RRF) | Blueprint describes it | **ILIKE `%query%` only** |
| Re-ranking | Blueprint | **None** |
| Grounding constraint | LLM prompt says "use ONLY evidence" | Evidence is empty; templates fill gap |
| Citation validation | Blueprint | Tier/confidence computed; no claim-level validation |

**HybridSearchService behavior (`backend/app/retrieval/hybrid_search.py`):**

1. `search()`: ILIKE on `KnowledgeChunk.content`; if no hits, fuzzy match services by name/slug.
2. `retrieve_for_service()`: Load chunks for service; if none, return single pseudo-evidence from service name.

There is **no embedding generation worker**, **no web search**, and **no scraping pipeline** despite schema and Celery task stubs.

---

## 5. Current Data Model

### 5.1 Knowledge domain (existing tables)

| Table | Purpose | Populated? |
|-------|---------|------------|
| `agencies` | Responsible organizations | 6 seed agencies |
| `services` | Service catalogue entries | 5 MVP services |
| `procedures` / `procedure_steps` | Workflow steps | Generic 3-step templates |
| `checklist_items` / `checklist_conditions` | Document requirements | Placeholder items |
| `fees` | Fee schedules | **Empty** (seed ignores fees) |
| `forms` | Downloadable forms | **Empty** |
| `service_links` | Official URLs | **Empty** |
| `service_offices` | Office locations | **Empty** |
| `sources` / `source_versions` | Provenance | **Empty** |
| `knowledge_documents` / `knowledge_chunks` | RAG corpus | **Empty** |

### 5.2 Service record fields (current)

Present: `slug`, `name_bn`, `name_en`, `aliases`, `agency_id`, `category`, `status`, `eligibility` (JSON), `required_documents`, `conditional_documents`, `effective_date`, `expiration_date`, `last_verified_at`, `confidence`, `review_state`, `version`, `source_provenance`.

**Missing vs. target schema:** subcategory, Banglish aliases (separate field), target users, geographic scope, application methods, payment methods, processing time, legal basis, official/practical split, ministry hierarchy, upazila localization.

### 5.3 Geography

- 8 divisions, 64 districts seeded from `data/seeds/divisions_districts.json`.
- **No upazila/union/city corporation tables.**

### 5.4 Operations

- `review_queue_items`, `change_events`, `crawl_jobs`, `audit_logs`, `feature_flags`, `evaluation_runs` — schema exists, **minimal runtime use**.

### 5.5 Conversations

- `conversations`, `messages` — chat history stored.
- `answer_json` on assistant messages holds structured answer; **citations not persisted separately** and may be lost on conversation reload depending on UI path.

---

## 6. Current Knowledge Sources

| Source | Location | Verified? |
|--------|----------|-----------|
| MVP service templates | `data/seeds/mvp_services.json` | Explicitly `UNDER_REVIEW`; placeholders |
| Agency metadata | `data/seeds/agencies.json` | Names/acronyms only; URLs not validated |
| Geography | `data/seeds/divisions_districts.json` | Standard admin divisions |
| Live crawled content | — | **None** |
| Official portals | — | **Not ingested** |
| Community/practical reports | — | **Not modeled** |

**Seed script gaps (`scripts/seed_database.py`):**

- Loads procedures and checklist items only.
- **Does not seed:** fees, forms, service_links, sources, knowledge chunks, embeddings.
- All services created with `review_state=DRAFT`, `status=UNDER_REVIEW`.

---

## 7. Current Search / Retrieval Mechanism

### 7.1 Service identification

- `extract_entities()` loads **all services** and fuzzy-matches (rapidfuzz `partial_ratio >= 75`) against slug, English name, and aliases.
- No vector intent classification; no catalogue taxonomy routing.
- District detection: substring match on district name/slug.
- Hardcoded `"mirpur"` location hint.

### 7.2 Intent classification

- Rule-based keywords in `classify_intent()`: fee, office, eligibility, documents, procedure.
- **Intent is returned in metadata but does not change answer composition** (same checklist + steps regardless).

### 7.3 Clarifications

- Orchestrator asks for passport type, application type, licence class.
- Checklist conditions use different keys (`passport_status`, `correction_type`, `licence_class`, `tin_type`, etc.).
- **No UI flow** to collect clarifications and resubmit; `ClarificationState` not persisted.

### 7.4 Public search API

- `GET /api/v1/search?q=` — service name search (separate from chat retrieval).

---

## 8. Authentication & Admin Panel

### 8.1 Auth models

- `admin_users`, `roles`, `permissions`, `role_permissions` — seeded with default admin `admin@example.local` / `change-me-admin`.
- JWT settings configured.

### 8.2 Backend admin API (implemented)

- `GET /admin/dashboard`
- `GET/PATCH /admin/feature-flags`
- `GET /admin/review-queue`

### 8.3 Frontend admin expectations (not implemented)

| Frontend call | Backend status |
|---------------|----------------|
| `POST /api/v1/admin/login` | **Missing** |
| `GET /api/v1/admin/services` | **Missing** |
| `GET /api/v1/admin/reviews` | **Missing** (backend has `/admin/review-queue`) |
| Dashboard field names | **Mismatch** (`services_count` vs `total_services`) |
| Approve/reject actions | **UI stubs only** |

**RBAC:** Comment in admin router: "RBAC to be added" — all admin endpoints are **unauthenticated**.

---

## 9. LLM Provider

| Aspect | Current state |
|--------|---------------|
| Provider | OpenAI-compatible HTTP (llama.cpp in docker profile) |
| Default | **Off** (`feature_llm_enabled=False`) |
| Role | Summary rewrite only via `LLMClient.summarize()` |
| Grounding | Prompt instructs evidence-only; evidence usually empty |
| Fallback | Deterministic template summary in orchestrator |
| Cost | Local/zero when llama.cpp profile used |

The LLM is **not** the source of truth today — but neither is a verified knowledge layer. Users get **generic seeded templates** with disclaimers about unverified fees/URLs.

---

## 10. Workers, Crawling, Embeddings

| Celery task | Status |
|-------------|--------|
| `run_crawl` | Returns `{"status": "queued"}` — no crawler |
| `batch_embed` | Returns count — no embedding logic |
| `check_broken_links` | Returns zeros |
| `purge_temp_documents` | Returns zero |

No Scrapy/Playwright implementation despite feature flags. No scheduled ingestion.

---

## 11. Tests & Evaluation

| Asset | Status |
|-------|--------|
| `backend/tests/test_health.py` | Health/readiness |
| `backend/tests/test_api.py` | Basic API |
| `backend/tests/test_pipeline.py` | Language, banglish, intent unit tests |
| `data/evaluation/golden_queries.jsonl` | 6+ golden queries — **no eval harness** |
| Citation accuracy tests | **None** |
| Regression on verified facts | **None** |

---

## 12. Why Answers Are Weak

### 12.1 Inaccurate

- Checklist items are **curator placeholders**, not extracted from official sources.
- No cross-check or verification pipeline has run.
- Conditional logic may misfire (clarification keys ≠ condition keys).

### 12.2 Incomplete

- No fees, forms, official URLs, office locations, processing times.
- Only **5 services** vs. hundreds of real public services.
- Intent-specific queries (fees, offices) get same generic template.

### 12.3 Outdated

- No crawl schedule, change detection, or freshness tracking in use.
- `last_verified_at` is null for all seeded services.

### 12.4 Generic

- Procedure steps are 3-step boilerplate ("check eligibility → gather documents → submit").
- Summaries claim "verified structured guidance" when status is `UNDER_REVIEW`.

### 12.5 Poorly sourced

- Citations fall back to service name with no URL.
- No `Source` or `SourceVersion` records.
- `evidence_chunk_id` on checklist items always null.

### 12.6 Insufficiently Bangladesh-specific

- No upazila/district office variants.
- No Bengali-first curated content beyond seed labels.
- Banglish normalization exists but glossary is minimal.
- No integration with official portals (e.g., e-passport, BRIS, NID, NBR e-TIN).

---

## 13. What Can Be Reused

| Asset | Reuse recommendation |
|-------|---------------------|
| Database schema (services, sources, chunks, review queue) | **Extend**, don't replace |
| Orchestrator pipeline skeleton | **Keep** — add stages per target flow |
| ChecklistEngine / ProcedureEngine | **Keep** — wire to verified claims + evidence IDs |
| Language/banglish/intent modules | **Keep** — expand gazetteers |
| Frontend chat UI (citations, checklist, steps) | **Keep** — no redesign now |
| Geography seed (divisions/districts) | **Keep** — extend to upazila |
| Agency seed | **Keep** — enrich with official domains |
| Docker/compose topology | **Keep** |
| Architecture blueprint | **Align** implementation to it |
| Golden query dataset | **Wire** to eval harness |
| Admin dashboard concept | **Fix** API alignment + auth |

---

## 14. What Should Be Improved

1. **Populate verified knowledge** through human-in-the-loop curation, not bulk scrape-and-trust.
2. **Implement true hybrid retrieval** (BM25/FTS + vector + RRF) with pgvector.
3. **Ground every fact** in `Claim → Evidence → Source` chain.
4. **Separate official vs. practical** information layers.
5. **Use intent** to shape answer sections (fees-only, offices-only, etc.).
6. **Fix admin/auth** for curation workflow.
7. **Complete seed script** for fees, links, sources — or ban auto-publish until verified.
8. **Clarification UX** end-to-end with persisted state.
9. **Evaluation harness** against golden queries with citation requirements.
10. **Honest confidence/status** — don't imply verification when `UNDER_REVIEW`.

---

## 15. What Should Remain Unchanged (for now)

- Overall modular monolith architecture.
- Next.js + FastAPI stack.
- Public UI layout and chat interaction pattern.
- Conversation/message persistence model.
- Feature flag pattern for LLM/crawl/upload.
- SQLite dev / Postgres prod strategy.
- Existing 5 MVP service slugs as **starting catalogue entries** (content to be replaced/verified, not deleted blindly).

---

## 16. What Should Eventually Be Replaced

| Component | Replace with |
|-----------|--------------|
| ILIKE-only retrieval | Hybrid search + claim-level retrieval |
| Template-only answers | Evidence-grounded structured answers |
| Empty worker stubs | Real ingestion, embed, link-check pipelines |
| Unauthenticated admin | JWT + RBAC enforced on all admin mutations |
| Single JSON eligibility blob | Structured requirement engine with conditions |
| Service-level status only | Field-level verification + versioning |
| Implicit "verified" copy | Status-driven messaging (`DRAFT`, `UNDER_REVIEW`, `ACTIVE`) |

---

## 17. Gap vs. Target Flow

**Today:**
```
User → LLM (optional summary) + DB templates → Answer
```

**Target (see KNOWLEDGE_ARCHITECTURE.md):**
```
User → Intent → Service ID → User Context → Structured Retrieval → Evidence →
Authority → Freshness → Conflict Detection → Personalization → LLM Reasoning →
Citation Validation → Answer
```

---

## 18. Related Documents

- [KNOWLEDGE_ARCHITECTURE.md](./KNOWLEDGE_ARCHITECTURE.md)
- [SERVICE_CATALOGUE_SPECIFICATION.md](./SERVICE_CATALOGUE_SPECIFICATION.md)
- [SOURCE_AUTHORITY_MODEL.md](./SOURCE_AUTHORITY_MODEL.md)
- [VERIFICATION_FRAMEWORK.md](./VERIFICATION_FRAMEWORK.md)
- [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md)
- [Architecture blueprint](./architecture/bangladesh-digital-assistant-architecture.md)

---

*This audit is based on repository inspection as of 2026-08-24. No Bangladesh government facts were fabricated for this document.*
