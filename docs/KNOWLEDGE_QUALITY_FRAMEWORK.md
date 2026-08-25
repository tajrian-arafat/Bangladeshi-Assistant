# Knowledge Quality Framework — Bangladeshi Assistant

**Version:** 1.0 (design)  
**Date:** 2026-08-24

---

## 1. Purpose

Measure, monitor, and improve the quality of the verified knowledge layer. Quality scores drive publication gates, admin prioritization, and user-facing confidence.

---

## 2. Quality Dimensions

| Dimension | Weight | Description |
|-----------|--------|-------------|
| **Coverage** | 25% | Required fields populated with VERIFIED claims |
| **Authority** | 25% | Share of facts from Tier 1–2 OFFICIAL sources |
| **Freshness** | 20% | Age of evidence vs field-specific thresholds |
| **Consistency** | 15% | Absence of unresolved conflicts |
| **Usability** | 15% | User feedback + eval harness pass rate |

Composite **Knowledge Quality Score (KQS):** 0–100 per service.

---

## 3. Coverage Scoring

### 3.1 Required fields (checklist)

| Field | Points |
|-------|--------|
| Names (bn + en) | 5 |
| Agency + category | 5 |
| MUST requirements (≥3 typical) | 15 |
| Procedure steps (≥3) | 15 |
| Verified application URL or in-person official confirmation | 15 |
| Fees verified OR verified "no fee" statement | 10 |
| Processing time or official silence documented | 5 |
| Forms (if applicable) | 5 |
| Office locator (if in-person) | 10 |
| Legal basis (optional bonus) | 5 |

**Coverage %** = earned / possible × 100, capped at 100.

### 3.2 Penalties

| Issue | Penalty |
|-------|---------|
| Placeholder text in seed | -10 |
| NULL official_url on all steps | -5 |
| MUST item without evidence_id | -5 each |

---

## 4. Authority Scoring

```
authority_score = (weighted_claims_official / total_claims_surface) × 100

Weight per claim:
  Tier 1 OFFICIAL: 1.0
  Tier 2 OFFICIAL: 0.95
  Tier 3-4 OFFICIAL: 0.8
  PRACTICAL any tier: 0 (excluded from authority numerator)
```

Surface = all claims shown in default answer template.

**Minimum for ACTIVE:** authority_score ≥ 80.

---

## 5. Freshness Scoring

Per-field max age (days):

| Field type | Max age |
|------------|---------|
| URLs | 30 |
| Fees | 90 |
| Steps/procedure | 180 |
| Eligibility | 180 |
| Legal basis | 365 |

```
freshness_score = mean(field_freshness) × 100

field_freshness = max(0, 1 - (age_days / max_age_days))
```

If `source_updated_at` newer than `verified_at`, trigger recheck — freshness 0 until re-verified.

---

## 6. Consistency Scoring

```
consistency_score = 100 - (penalties)

Penalties:
  Open Tier 1 conflict: -40 each
  Open Tier 2 conflict: -20 each
  STALE MUST claim still displayed: -30
  Broken primary URL: -25
```

---

## 7. Usability Scoring

```
usability_score = 0.6 × eval_pass_rate + 0.4 × helpful_ratio

eval_pass_rate = passed golden queries / total for service
helpful_ratio = helpful feedback / (helpful + not_helpful)
```

Cold start: neutral 50 until ≥20 feedback samples or eval run.

---

## 8. Composite KQS

```
KQS = 0.25×Coverage + 0.25×Authority + 0.20×Freshness 
    + 0.15×Consistency + 0.15×Usability
```

| Band | Range | Public label |
|------|-------|--------------|
| A | 85–100 | High confidence |
| B | 70–84 | Medium confidence |
| C | 50–69 | Limited — verify with office |
| D | <50 | Not ready — should not be ACTIVE |

Align with existing `confidence` field in chat responses: map KQS band to low/medium/high.

---

## 9. Knowledge Gaps

### 9.1 Gap record (proposed table)

```yaml
knowledge_gap:
  id: uuid
  service_id: uuid nullable
  field_name: string          # e.g., "fees", "application_url"
  gap_type: missing | stale | conflict | user_reported | discovery
  priority: 1-5
  discovered_by: system | user | crawler | evaluator
  query_text: nullable       # triggering user query
  status: open | in_progress | resolved | wont_fix
  notes: text
  created_at, resolved_at
```

### 9.2 Gap creation triggers

| Trigger | Example |
|---------|---------|
| User query, no service match | Golden query failure |
| Intent=fee_inquiry, no verified fees | Missing fee gap |
| Crawl hash change | Stale gap |
| Conflict detector | Conflict gap |
| Coverage below threshold | Field gap |
| "Not helpful" feedback | Review gap |

### 9.3 Gap prioritization

```
priority = f(user_demand, field_criticality, gap_age)

Critical fields: MUST docs, fees, application URL
```

Admin dashboard: gaps by priority, domain, agency.

---

## 10. Publication Gates (Recap)

Service `ACTIVE` requires:

- KQS ≥ 70  
- Coverage ≥ 80%  
- Authority ≥ 80%  
- Zero open Tier 1 conflicts  
- Reviewer approval  

---

## 11. Monitoring & Dashboards

### 11.1 Admin metrics

- Services by KQS band  
- Open gaps by type  
- Mean freshness by agency  
- Eval pass rate trend  
- Citation coverage (% answers with ≥1 Tier 1–2 cite)  

### 11.2 Alerts

- KQS drop >10 points after crawl  
- Primary URL broken  
- Spike in not_helpful for service  

---

## 12. Evaluation Harness (Golden Queries)

Existing: `data/evaluation/golden_queries.jsonl`

Extend harness to measure:

| Metric | Pass criteria |
|--------|---------------|
| Service match | Expected slug |
| Intent | Expected intent |
| Citations | require_citations when true |
| MUST items | Expected subset present |
| No hallucinated URL | URL in answer ⊆ verified URLs |

Wire to `EvaluationRun` model (schema exists, unused).

---

## 13. Current Baseline (MVP Seed)

Estimated KQS for seeded services (all UNDER_REVIEW):

| Dimension | Approx score |
|-----------|--------------|
| Coverage | ~40 (structure without verified fields) |
| Authority | ~0 (no sources) |
| Freshness | 0 |
| Consistency | 100 (no conflicting claims) |
| Usability | 50 (neutral) |
| **KQS** | **~30 (D band)** |

**Correct behavior:** strong disclaimers, not ACTIVE — current code still claims "verified" in summary text (bug to fix in implementation phase).

---

## Related Documents

- [VERIFICATION_FRAMEWORK.md](./VERIFICATION_FRAMEWORK.md)
- [SERVICE_CATALOGUE_SPECIFICATION.md](./SERVICE_CATALOGUE_SPECIFICATION.md)
- [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md)
- [CURRENT_SYSTEM_AUDIT.md](./CURRENT_SYSTEM_AUDIT.md)
