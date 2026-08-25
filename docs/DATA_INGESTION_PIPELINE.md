# Data Ingestion Pipeline — Bangladeshi Assistant

**Version:** 1.0 (design)  
**Date:** 2026-08-24

---

## 1. Purpose

Define how external information enters the verified knowledge layer — from discovery through publication — **without mass untrusted ingestion**.

**This phase:** pipeline design only. No bulk import execution.

---

## 2. Pipeline Overview

```
┌─────────────┐   ┌─────────────┐   ┌──────────────┐   ┌─────────────┐
│  DISCOVER   │──▶│    FETCH    │──▶│   PARSE /    │──▶│  NORMALIZE  │
│  (sources)  │   │  (crawl)    │   │   EXTRACT    │   │   (claims)  │
└─────────────┘   └─────────────┘   └──────────────┘   └──────┬──────┘
                                                              │
┌─────────────┐   ┌─────────────┐   ┌──────────────┐         │
│  PUBLISH    │◀──│   APPROVE   │◀──│   REVIEW     │◀────────┘
│  (index)    │   │  (human)    │   │  (queue)     │
└─────────────┘   └─────────────┘   └──────────────┘
       │
       ▼
┌─────────────┐   ┌─────────────┐
│   EMBED     │   │   MONITOR   │
│  (chunks)   │   │ (freshness) │
└─────────────┘   └─────────────┘
```

---

## 3. Stage 1: Discovery

### 3.1 Inputs

- Registered `Source` records  
- Manual URL submission by editors  
- Catalogue gap analysis  
- Tier 5–7 discovery (names only)  

### 3.2 Outputs

- New URLs queued in crawl job  
- New `DISCOVERED` catalogue entries (name + agency only)  
- `KnowledgeGap` records  

### 3.3 Rules

- Do not fetch unregistered domains without ops approval  
- Respect `robots.txt` (`robots_respected=true`)  
- Rate limit per source (`rate_limit_rpm`)  

---

## 4. Stage 2: Fetch (Crawl)

### 4.1 Components (to implement)

| Component | Role |
|-----------|------|
| `CrawlJob` / `CrawlAttempt` | Existing models — wire to worker |
| HTTP fetcher | Static pages, PDFs |
| Playwright fetcher | JS-heavy (`FEATURE_PLAYWRIGHT_CRAWL`) |
| Storage | Raw HTML/PDF → object storage (MinIO in compose) |

### 4.2 Celery tasks (replace stubs)

```python
run_crawl(source_id)      # enqueue URLs from source config
fetch_url(url)            # single page, write SourceVersion
check_broken_links()      # periodic link validation
```

### 4.3 Fetch metadata

Each successful fetch creates:

```yaml
SourceVersion:
  url, content_hash, fetched_at
  source_published_at, source_updated_at  # parsed if present
  metadata_json: { content_type, language, http_status }
```

Duplicate hash → skip re-extraction unless forced.

---

## 5. Stage 3: Parse & Extract

### 5.1 Parser profiles

| Profile | Use case |
|---------|----------|
| `gov_bd_standard` | Common .gov.bd layout |
| `pdf_table` | Fee schedules in PDF |
| `portal_form` | Application portal pages |
| `generic_article` | Fallback |

### 5.2 Extraction outputs

- `KnowledgeDocument` (full text, language, `untrusted_content=true`)  
- Candidate `Claim` rows (status DISCOVERED)  
- Locators for human review  

### 5.3 LLM-assisted extraction (optional)

- Input: page section + schema template  
- Output: candidate JSON only  
- Always `information_class=DISCOVERY` until reviewed  

---

## 6. Stage 4: Normalize

Map candidates to canonical schema:

| Raw | Normalized |
|-----|------------|
| "৩,০০০ টাকা" | `{amount: 3000, currency: "BDT"}` |
| "জাতীয় পরিচয়পত্র" | `{document_code: "nid"}` |
| Step lists | ProcedureStep candidates linked to service |

Status → `NORMALIZED`. Attach to `service_id` when match confidence high; else queue for curator linking.

---

## 7. Stage 5: Review Queue

Auto-route to `ReviewQueueItem`:

| Condition | Route |
|-----------|-------|
| Tier 1–2 new MUST claim | Priority high |
| Fee or URL claim | Priority high |
| Tier 7 only | Low — practical bucket |
| Parser confidence < threshold | Human required |

Review UI shows side-by-side: excerpt ↔ normalized claim.

---

## 8. Stage 6: Approve & Publish

On claim approval:

1. Set `status=VERIFIED`, `verified_at`, `verified_by`  
2. Update structured service fields from claims  
3. Create `ChangeEvent` audit  

On service publish:

1. Bump version  
2. Trigger chunking + embedding  
3. Set ACTIVE if KQS gate passes  

---

## 9. Stage 7: Chunk & Embed

### 9.1 Chunking strategy

- Chunk at semantic boundaries (headings, list items, table rows)  
- Attach metadata: `service_id`, `claim_ids`, `language`, `tier`, `information_class`  
- Target 200–500 tokens per chunk  

### 9.2 Embedding

Replace stub `batch_embed`:

```
batch_embed(document_ids):
  load KnowledgeDocument chunks without embedding
  compute vectors (BAAI/bge-m3 or API)
  store in knowledge_chunks.embedding (pgvector)
  update search_vector for FTS
```

### 9.3 Index types (PostgreSQL)

- `pgvector` cosine index on embeddings  
- GIN index on `search_vector` (tsvector)  

SQLite dev: FTS-only fallback, no vector (degraded mode).

---

## 10. Stage 8: Monitor

| Job | Frequency |
|-----|-----------|
| Recrawl Tier 1 sources | Weekly–monthly |
| Recrawl Tier 2 | Monthly |
| Broken link check | Weekly |
| Stale claim scanner | Daily |
| Eval harness | On publish + nightly |

Hash change → mark claims STALE → review queue.

---

## 11. Data Stores

| Store | Contents |
|-------|----------|
| PostgreSQL | Structured knowledge, claims, metadata |
| MinIO | Raw HTML, PDFs, screenshots |
| Redis | Celery queue, rate limits |
| pgvector | Embeddings |

---

## 12. What NOT to Ingest (Yet)

- Bulk Wikipedia or random blog scraping  
- Unverified social media posts as OFFICIAL  
- Fabricated fee/URL lists  
- Complete service catalogue in one batch  

**Phased approach:** MVP 5 services fully verified first, then expand by priority.

---

## 13. Research Methodology (Editorial)

For each priority service:

1. Register Tier 1–2 sources (manual domain verification)  
2. Fetch specific pages (application guide, fee schedule, forms)  
3. Extract + normalize claims  
4. Cross-check 2 sources minimum for fees and MUST docs  
5. Reviewer approve  
6. Publish + eval golden queries  

Document sources used in audit trail — no fabricated URLs.

---

## 14. Mapping to Current Code

| Component | File | Status |
|-----------|------|--------|
| Crawl models | `domain/models/operations.py` | Schema ✓ |
| Source models | `domain/models/knowledge.py` | Schema ✓ |
| Workers | `workers/tasks.py` | **Stub** |
| Hybrid search | `retrieval/hybrid_search.py` | ILIKE only |
| Seed script | `scripts/seed_database.py` | No sources/chunks |

---

## 15. Idempotency & Safety

- Content hash deduplication  
- Crawl rate limits per domain  
- No auto-publish  
- `untrusted_content=true` default on documents  
- Full audit log on publish  

---

## Related Documents

- [VERIFICATION_FRAMEWORK.md](./VERIFICATION_FRAMEWORK.md)
- [SOURCE_AUTHORITY_MODEL.md](./SOURCE_AUTHORITY_MODEL.md)
- [SERVICE_CATALOGUE_SPECIFICATION.md](./SERVICE_CATALOGUE_SPECIFICATION.md)
- [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md)
