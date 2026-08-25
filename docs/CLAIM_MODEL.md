# Claim Model

**Version:** 1.0  
**Date:** 2026-08-24  
**Runtime table:** `claims`  
**ORM:** `backend/app/domain/models/claims.py::Claim`

---

## Purpose

A **Claim** is one atomic factual assertion about a service (fee amount, required document, URL, step, etc.). Claims are the unit of verification and publication.

Finding a source does **not** make a claim `VERIFIED`.

---

## Fields

| Field | Description |
|-------|-------------|
| `id` | UUID primary key |
| `service_id` | FK → `services` |
| `research_claim_key` | Stable key from research staging (e.g. `civil-birth-registration::c-br-fee-late`) |
| `claim_type` | See enum below |
| `subject` / `predicate` / `value` | Triple-style assertion |
| `structured_value` | JSON payload (amount, condition, order, …) |
| `information_class` | `OFFICIAL` \| `PRACTICAL` \| `DISCOVERY` |
| `pipeline_status` | See Claim Pipeline Status |
| `confidence` | 0–1 research/review confidence |
| `created_at` / `updated_at` | Timestamps |
| `verified_at` / `verified_by_admin_id` | Set only on successful verification |
| `effective_from` / `effective_until` | Optional validity window |
| `supersedes_claim_id` / `superseded_by_claim_id` | Version lineage |
| `review_notes` | Human notes |
| `is_published` / `published_at` | Published into runtime Fee/Checklist/Step |

---

## claim_type

`eligibility`, `document`, `conditional_document`, `fee`, `procedure_step`, `processing_time`, `application_url`, `office`, `payment_method`, `deadline`, `legal_basis`, `availability`, `restriction`, `practical_tip`, `other`

---

## Pipeline status

`DISCOVERED` → `EXTRACTED` → `NORMALIZED` → `CROSS_CHECKED` → `PENDING_REVIEW` → `VERIFIED`  
Also: `PARTIALLY_VERIFIED`, `CONFLICTING`, `OUTDATED`, `REJECTED`, `UNVERIFIED`

**VERIFIED** means: evidence passed project verification rules and is approved for official publication — not merely that a URL was found.

**PARTIALLY_VERIFIED** means: some part of the claim is supported, but the complete claim cannot yet be established for authoritative publication.

**UNVERIFIED** means: insufficient evidence after independent inspection.

---

## Traceability

```
Claim → ClaimEvidence → SourceVersion → Source (authority tier)
```

See `docs/CLAIM_EVIDENCE_MODEL.md` and `docs/KNOWLEDGE_PUBLICATION_GATE.md`.
