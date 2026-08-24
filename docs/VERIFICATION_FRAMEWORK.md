# Verification Framework — Bangladeshi Assistant

**Version:** 1.0 (design)  
**Date:** 2026-08-24

---

## 1. Core Principle

**Never scrape and trust.** Every important fact passes through a defined pipeline before it can power user-facing answers as OFFICIAL truth.

---

## 2. Verification Pipeline

```
DISCOVERY
    ↓
EXTRACTION
    ↓
NORMALIZATION
    ↓
SOURCE CLASSIFICATION (tier + information_class)
    ↓
CROSS-CHECK (multi-source where available)
    ↓
CONFLICT DETECTION
    ↓
VERIFICATION (human and/or rule-based)
    ↓
APPROVAL
    ↓
PUBLICATION
    ↓
MONITORING (freshness, change detection)
```

Each stage produces auditable records. Failures loop back or create `KnowledgeGap` entries — never silent invention.

---

## 3. Traceability Chain

Every user-facing claim must trace:

```
Claim (atomic fact)
  ↓
ClaimEvidence (link + excerpt + locator)
  ↓
SourceVersion (url, hash, fetched_at)
  ↓
Source (domain, tier, agency)
  ↓
Retrieved date / Verified date / Verifier identity
```

If any link is missing, the fact cannot be OFFICIAL in answers.

---

## 4. Claim Model (Proposed)

```yaml
claim:
  id: uuid
  service_id: uuid
  claim_type: document_required | fee | step | eligibility | url | duration | legal | other
  claim_key: structured identifier (e.g., fee.renewal.standard)
  value_json: structured payload
  information_class: OFFICIAL | PRACTICAL | DISCOVERY
  status: DISCOVERED | NORMALIZED | PENDING_REVIEW | VERIFIED | REJECTED | STALE
  confidence: 0.0-1.0
  created_at, updated_at
  verified_at: nullable
  verified_by: admin_user_id nullable
  effective_from: date nullable
  effective_to: date nullable
```

Multiple evidence rows per claim allowed (corroboration).

---

## 5. Stage Definitions

### 5.1 Discovery

**Input:** Crawl, manual research, user feedback, catalogue scan  
**Output:** Raw mention + source URL + DISCOVERY class  
**Automated:** Yes  
**Publishable:** No  

### 5.2 Extraction

**Input:** HTML/PDF/text from SourceVersion  
**Output:** Candidate fact spans with locators (CSS selector, page, table cell)  
**Automated:** Parser profiles + optional LLM assist (extract only, not verify)  
**Publishable:** No  

### 5.3 Normalization

**Input:** Candidate spans  
**Output:** Claims mapped to schema (`claim_type`, `value_json`)  
**Automated:** Rules + human QA  
**Publishable:** No (status → NORMALIZED)  

Examples:
- "Tk 3,000/-" → `{amount: 3000, currency: "BDT"}`
- "National ID card" → `{document_code: "nid", label_bn: "...", label_en: "..."}`

### 5.4 Source Classification

**Input:** SourceVersion  
**Output:** Tier + information_class on each claim  
**Automated:** Tier from registered Source; class from extraction context  
**Human:** Approve tier for new domains  

### 5.5 Cross-Check

**Input:** Claims for same `claim_key` from multiple sources  
**Output:** Corroboration score, conflict flags  
**Rules:**
- 2+ Tier 1–2 agreeing → high corroboration
- Any Tier 1 contradicting Tier 6 → ignore Tier 6 for OFFICIAL
- Tier 1 vs Tier 1 conflict → PENDING_REVIEW, block publish

### 5.6 Conflict Detection

Extend existing `detect_conflicts()` logic:

| Conflict type | Detection |
|---------------|-------------|
| Fee mismatch | Different amounts same fee key |
| Document mismatch | MUST vs NOT listed |
| URL mismatch | Different official portals |
| Step count/order | Structural diff |
| Eligibility | Contradictory rules |

Conflicts create `ChangeEvent` + `ReviewQueueItem`.

### 5.7 Verification

**Human reviewer** (required for OFFICIAL Tier 1–2 MUST requirements):

- Compare evidence excerpt to claim value  
- Confirm source still live  
- Confirm applies to service variant  
- Mark VERIFIED or REJECTED  

**Rule-based auto-verify** (limited):

- Tier 1 source unchanged re-fetch, same hash → extend freshness  
- Exact duplicate claim from same source_version  

### 5.8 Approval

Reviewer action:

```
POST /admin/claims/{id}/approve
POST /admin/claims/{id}/reject
POST /admin/services/{id}/publish   # promotes service version
```

Approval writes `AuditLog`, sets `verified_at`, `verified_by`.

### 5.9 Publication

On publish:

1. Bump `service.version`  
2. Sync structured fields from VERIFIED claims  
3. Rebuild knowledge chunks + embeddings  
4. Set `service.status = ACTIVE` if quality threshold met  
5. Invalidate retrieval cache  

### 5.10 Monitoring

- Scheduled recrawl per source tier  
- Hash change → STALE claims → review queue  
- Broken link job → flag URLs  
- User "not helpful" feedback → sample review  

---

## 6. Verification Status Matrix

| Claim status | In OFFICIAL answers? | In PRACTICAL section? |
|--------------|---------------------|----------------------|
| DISCOVERED | No | No |
| NORMALIZED | No | No |
| PENDING_REVIEW | No | Optional stub |
| VERIFIED | Yes | If class=PRACTICAL |
| REJECTED | No | No |
| STALE | No (show warning if was public) | No |

---

## 7. Service-Level Gates

Service cannot be `ACTIVE` unless:

| Gate | Rule |
|------|------|
| G1 | ≥1 Tier 1–2 OFFICIAL source registered |
| G2 | All MUST document claims VERIFIED |
| G3 | Fees VERIFIED or explicit verified "contact office" |
| G4 | Primary application URL VERIFIED or in-person only confirmed |
| G5 | No unresolved Tier 1–1 conflicts |
| G6 | Reviewer sign-off |
| G7 | Quality score ≥ minimum (see KNOWLEDGE_QUALITY_FRAMEWORK.md) |

---

## 8. Human Review Queue

Uses existing `ReviewQueueItem` + `ChangeEvent`:

| Trigger | Priority |
|---------|----------|
| New Tier 1 claim | High |
| Conflict detected | High |
| Source hash change | Medium |
| User correction feedback | Medium |
| Stale threshold exceeded | Medium |
| New Tier 7 practical cluster | Low |

Admin UI shows: claim diff, evidence excerpt, source screenshot/archive (future), approve/reject.

---

## 9. LLM Role in Verification

| Allowed | Forbidden |
|---------|-----------|
| Extract candidates from HTML | Approve claims autonomously |
| Suggest claim_type mapping | Invent fees/documents |
| Summarize verified bundle for user | Replace missing data |

LLM outputs in ingestion are always `DISCOVERY` or `NORMALIZED` — never `VERIFIED`.

---

## 10. Audit & Compliance

`AuditLog` records:

- claim approve/reject  
- tier changes  
- service publish  
- source registration  
- manual edits to structured fields  

Retention: indefinite for published claims; raw crawls per storage policy.

---

## 11. Current System Gaps

| Capability | Status |
|------------|--------|
| Claim table | Not implemented |
| Review workflow | Schema only |
| Cross-check | Not implemented |
| Auto stale detection | Not implemented |
| Citation persistence | Partial |

---

## Related Documents

- [SOURCE_AUTHORITY_MODEL.md](./SOURCE_AUTHORITY_MODEL.md)
- [KNOWLEDGE_ARCHITECTURE.md](./KNOWLEDGE_ARCHITECTURE.md)
- [DATA_INGESTION_PIPELINE.md](./DATA_INGESTION_PIPELINE.md)
- [KNOWLEDGE_QUALITY_FRAMEWORK.md](./KNOWLEDGE_QUALITY_FRAMEWORK.md)
