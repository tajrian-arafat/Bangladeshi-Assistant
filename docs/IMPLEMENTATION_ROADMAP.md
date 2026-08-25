# Implementation Roadmap — Bangladeshi Assistant Knowledge Foundation

**Version:** 1.0 (design)  
**Date:** 2026-08-24  
**Scope:** Knowledge layer only — no UI redesign, no mass ingestion until Phase 2 gates pass

---

## 1. Guiding Principles

1. **Verified knowledge is the source of truth** — not the LLM.  
2. **Reuse existing schema and orchestrator** — extend, don't rebuild.  
3. **Five MVP services first** — fully verified end-to-end before scaling catalogue.  
4. **No fabricated government data** — gaps stay open until sourced.  
5. **Measure quality** — eval harness + KQS before declaring success.

---

## 2. Phase Overview

| Phase | Focus | Outcome |
|-------|-------|---------|
| **0** | Documentation & audit | This document set ✓ |
| **1** | Schema + claim layer + admin auth | Curators can approve claims |
| **2** | MVP curation (5 services) | ACTIVE services with citations |
| **3** | Retrieval + grounding | True hybrid RAG, honest answers |
| **4** | Personalization + clarifications | Minimal questions, correct checklists |
| **5** | Catalogue expansion | Systematic discovery, prioritized growth |
| **6** | Operations | Monitoring, eval CI, freshness at scale |

**STOP after Phase 0** until stakeholder review — **current status**.

---

## 3. Phase 0: Foundation (Complete)

Deliverables:

- [x] [CURRENT_SYSTEM_AUDIT.md](./CURRENT_SYSTEM_AUDIT.md)
- [x] [KNOWLEDGE_ARCHITECTURE.md](./KNOWLEDGE_ARCHITECTURE.md)
- [x] [SERVICE_CATALOGUE_SPECIFICATION.md](./SERVICE_CATALOGUE_SPECIFICATION.md)
- [x] [SOURCE_AUTHORITY_MODEL.md](./SOURCE_AUTHORITY_MODEL.md)
- [x] [VERIFICATION_FRAMEWORK.md](./VERIFICATION_FRAMEWORK.md)
- [x] [PERSONALIZED_REQUIREMENT_ENGINE.md](./PERSONALIZED_REQUIREMENT_ENGINE.md)
- [x] [KNOWLEDGE_QUALITY_FRAMEWORK.md](./KNOWLEDGE_QUALITY_FRAMEWORK.md)
- [x] [DATA_INGESTION_PIPELINE.md](./DATA_INGESTION_PIPELINE.md)
- [x] [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md)

**Gate to Phase 1:** Stakeholder approval of architecture + verification rules.

---

## 4. Phase 1: Schema & Curation Infrastructure

### 4.1 Database migrations

- Add `claims`, `claim_evidence`, `knowledge_gaps`, `ministries` tables  
- Extend `checklist_items` with `claim_id`, `information_class`  
- Add upazila geography table (optional defer to Phase 5)  

### 4.2 Admin authentication

- Implement `POST /api/v1/admin/login` (JWT)  
- Enforce RBAC on all `/admin/*` mutations  
- Align frontend API paths (`/admin/reviews` ↔ `/admin/review-queue`)  
- Fix dashboard schema mismatch  

### 4.3 Admin curation APIs

- CRUD draft services  
- Claim approve/reject  
- Service publish endpoint  
- Review queue actions  

### 4.4 Honest messaging

- Remove "verified" copy when `status != ACTIVE`  
- Confidence driven by KQS band  

### 4.5 Tests

- Auth + RBAC tests  
- Claim lifecycle unit tests  

**Exit criteria:** Curator can log in, approve a test claim, see audit log.

---

## 5. Phase 2: MVP Service Verification (5 Services)

### 5.1 Source registration

For each MVP agency (DIP, EC-NID, BRTA, DGFP, NBR):

1. Register Tier 1–2 sources (manually verified domains — **no fabrication**)  
2. Fetch specific official pages via crawl pipeline  
3. Store SourceVersions  

### 5.2 Claim curation

Per service:

- MUST documents with evidence  
- Fees or verified absence  
- Application URL or in-person confirmation  
- Procedure steps from official source  
- Processing time if stated  

### 5.3 Seed script upgrade

- Seed sources (not content) from curator-approved registry  
- Remove placeholder claims from auto-seed OR keep UNDER_REVIEW with honest labels  
- Wire fees, forms, service_links when verified  

### 5.4 Publish

- Promote to ACTIVE only when KQS ≥ 70  
- Run golden eval for 5 services  

**Exit criteria:** Each MVP service answers golden queries with Tier 1–2 citations.

---

## 6. Phase 3: Retrieval & Grounding

### 6.1 Hybrid search

- PostgreSQL FTS (tsvector) + pgvector  
- RRF fusion  
- Service-scoped retrieval  

### 6.2 Answer assembly refactor

- Build answer from VERIFIED claims, not templates alone  
- LLM summary only over fact bundle  
- Persist citations on messages  

### 6.3 Workers

- Real `batch_embed`  
- Real `run_crawl` (HTTP first, Playwright behind flag)  

### 6.4 Citation validation

- Post-check LLM output IDs against bundle  

**Exit criteria:** Retrieval uses chunks; answers differ when evidence removed (regression test).

---

## 7. Phase 4: Personalization & Clarifications

### 7.1 Condition DSL upgrade

- Replace flat `_conditions_match`  
- Align orchestrator keys with seed conditions  

### 7.2 Question planner

- Information-gain ranking  
- Persist clarifications on conversation  

### 7.3 Frontend clarification UX

- Render `clarifications_needed`  
- Resubmit with `ChatRequest.clarifications`  

### 7.4 Intent-driven sections

- Fee queries → fees block  
- Office queries → offices block  

**Exit criteria:** Passport renewal checklist changes when lost vs renewal selected.

---

## 8. Phase 5: Catalogue Expansion

### 8.1 Discovery pipeline

- Agency-by-agency service name extraction  
- DISCOVERED entries + dedupe  

### 8.2 Priority queue

- Top 50–100 services by demand metrics  
- Gap-driven prioritization  

### 8.3 Geography

- Upazila table + office overrides  

**Exit criteria:** Coverage dashboard shows domain/agency metrics; no completeness claims.

---

## 9. Phase 6: Operations & Quality at Scale

- Nightly eval harness in CI  
- Freshness recrawl schedules  
- Broken link monitoring  
- Feedback loop → gaps  
- Public changelog for service version updates  

---

## 10. Risk Register

| Risk | Mitigation |
|------|------------|
| Official sources lack structured info | Human curation + honest gaps |
| Source website changes frequently | Hash monitoring + stale workflow |
| Over-reliance on LLM | Fact bundle + validation |
| Catalogue scope creep | Priority queue + KQS gates |
| Fabrication pressure | Verification framework + audits |
| Admin security gap | Phase 1 auth mandatory before publish |

---

## 11. What Stays Unchanged (All Phases)

- Modular monolith (Next.js + FastAPI)  
- Public UI layout  
- Conversation API contract (extended, not broken)  
- Docker compose topology  
- Feature flag pattern  
- Geography seed (extended later)  

---

## 12. What Gets Replaced (Gradually)

| Current | Target |
|---------|--------|
| ILIKE retrieval | Hybrid FTS + vector |
| Template-only answers | Claim-grounded answers |
| Stub workers | Real pipeline |
| Unauthenticated admin | JWT + RBAC |
| Misleading "verified" copy | Status-driven messaging |

---

## 13. Success Metrics (Long-Term)

| Metric | Target |
|--------|--------|
| Golden query pass rate | ≥90% on ACTIVE services |
| Citation rate | 100% answers include ≥1 Tier 1–2 cite for ACTIVE |
| Hallucinated URL rate | 0 in eval harness |
| User helpful ratio | ≥70% |
| Mean KQS (ACTIVE) | ≥80 |

---

## 14. Immediate Next Steps (After Approval)

1. Review this document set with stakeholders  
2. Approve verification rules (especially Tier 7 handling)  
3. Begin Phase 1 migration + admin auth  
4. Assign curators for MVP 5 services  
5. Register real official sources (manual verification)  

**Do not begin mass ingestion until Phase 1 exit criteria met.**

---

## Related Documents

- [CURRENT_SYSTEM_AUDIT.md](./CURRENT_SYSTEM_AUDIT.md)
- [KNOWLEDGE_ARCHITECTURE.md](./KNOWLEDGE_ARCHITECTURE.md)
- [Architecture blueprint](./architecture/bangladesh-digital-assistant-architecture.md)
