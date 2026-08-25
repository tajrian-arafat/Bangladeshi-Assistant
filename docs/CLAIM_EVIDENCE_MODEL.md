# Claim Evidence Model

**Version:** 1.0  
**Date:** 2026-08-24  
**Runtime table:** `claim_evidence`  
**ORM:** `backend/app/domain/models/claims.py::ClaimEvidence`

---

## Purpose

`ClaimEvidence` links a claim to durable source material. A claim may have zero (discovery), one, or many evidence rows.

---

## Fields

| Field | Description |
|-------|-------------|
| `claim_id` | FK → `claims` |
| `source_version_id` | FK → `source_versions` (preferred) |
| `knowledge_document_id` | Optional FK → `knowledge_documents` |
| `knowledge_chunk_id` | Optional FK → `knowledge_chunks` |
| `evidence_excerpt` | Supporting text span |
| `locator` / `page_number` / `section` / `selector` | Location hints |
| `retrieved_at` / `verified_at` | Freshness / review |
| `evidence_strength` | `WEAK` \| `MODERATE` \| `STRONG` |

---

## Provenance chain

```
CLAIM
  → CLAIM EVIDENCE
    → SOURCE VERSION (url, content_hash, raw_content_path, retrieved_at)
      → SOURCE (domain, authority tier 1–7)
```

Large raw bodies are stored via `SourceVersion.raw_content_path` / `extracted_text_path` (filesystem or object storage), **not** inline in normal relational columns.

---

## Authority tiers (immutable by LLM)

| Tier | Meaning |
|------|---------|
| 1 | Official authority directly responsible for the service |
| 2 | Other official Bangladesh government source |
| 3 | Official institution / public body |
| 4 | Recognized institutional source |
| 5 | Reliable media / professional |
| 6 | Guides / blogs |
| 7 | Community / social media |

Tier must not be auto-changed by the LLM.
