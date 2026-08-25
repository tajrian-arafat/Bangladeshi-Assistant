# Partial Knowledge Depth Analysis

Generated: 2026-08-25T03:49:30.366793+00:00

## Executive Summary

- **PARTIAL services audited:** 416
- **Primary bottleneck (evidence-based):** RESEARCH
- **Aggregate user-value supported coverage:** 54.3%

Step 30 eliminated false completion. Step 31 investigates why services remain PARTIAL despite service-specific sources existing.

## 1. Partial-Knowledge Taxonomy (416 services)

### Top partial reasons

| Reason | Count |
|--------|------:|
| MISSING_E2E_SUPPORTED_COVERAGE | 416 |
| MISSING_MUST_NEED_DOCUMENTS | 408 |
| MISSING_CLAIM_DENSITY | 406 |
| MISSING_CONDITIONAL_DOCUMENTS | 377 |
| MISSING_FEES | 252 |
| MISSING_GEOGRAPHIC_VARIATION | 200 |
| LOCAL_VARIATION | 42 |
| MISSING_PAYMENT | 41 |
| MISSING_FRESHNESS | 27 |
| MISSING_ELIGIBILITY | 26 |

### Dimension gap percentages

| Dimension | % PARTIAL services |
|-----------|-------------------:|
| fees | 60.6% |
| documents | 98.1% |
| procedure | 5.3% |
| official_url | 5.8% |
| eligibility | 6.2% |
| e2e_supported | 100.0% |

## 2. Critical vs Non-Critical Gaps

Critical gaps are profile-specific (from `service_research_profiles.json`), not a universal checklist.
Each service record in `data/audit/partial-knowledge-taxonomy.json` includes `critical_missing`, `noncritical_missing`, `unresolvable_gaps`, and `resolvable_gaps`.

## 3. User-Value Model

Aggregate supported-answer coverage across 416 PARTIAL services: **54.3%**

Full matrix: `data/audit/service-user-value-matrix.json`

## 4. Biggest Knowledge Bottleneck

**Primary bottleneck:** `RESEARCH`

### Bottleneck scores

| Layer | Score |
|-------|------:|
| RESEARCH | 428 |
| RETRIEVAL | 416 |
| E2E | 416 |
| VERIFICATION | 139 |
| DATA_MODEL | 42 |
| SOURCE_ACCESS | 31 |
| SOURCE_DISCOVERY | 24 |
| GOVERNMENT_INFO_AVAILABILITY | 11 |

### Source limitations

- Official source unavailable: 2.6%
- JS rendering limitation: 4.8%
- Calculator-required fees: 0.0%

_Primary bottleneck inferred as RESEARCH based on aggregated partial-reason frequencies, not guesswork. High rates of MISSING_E2E_SUPPORTED_COVERAGE indicate retrieval/E2E gap even when basic service-specific sources exist post-wave rerun._

## 5. Deep-Research Pilot (12 services)

### Pilot selection

| Role | Service ID |
|------|------------|
| high_usage | `nid-new-voter-registration` |
| high_usage | `education-ssc-certificate` |
| high_risk | `tax-income-return-file` |
| high_risk | `business-company-incorporation` |
| land | `land-mutation-apply` |
| land | `land-khatian-certified-copy` |
| education | `education-foreign-equivalency` |
| education | `education-duplicate-certificate` |
| social_protection | `snp-old-age-allowance` |
| disability | `disability-dis-registration` |
| health | `health-bmdc-full-registration` |
| judiciary | `judiciary-supreme-court-e-filing` |

### Supported-answer coverage: before vs after

| Service | Before | After | Verified claims |
|---------|-------:|------:|----------------:|
| `nid-new-voter-registration` | 0.0% | 75.0% | 6 |
| `education-ssc-certificate` | 0.0% | 75.0% | 5 |
| `tax-income-return-file` | 0.0% | 75.0% | 6 |
| `business-company-incorporation` | 0.0% | 75.0% | 5 |
| `land-mutation-apply` | 0.0% | 75.0% | 6 |
| `land-khatian-certified-copy` | 0.0% | 75.0% | 5 |
| `education-foreign-equivalency` | 0.0% | 75.0% | 5 |
| `education-duplicate-certificate` | 0.0% | 75.0% | 5 |
| `snp-old-age-allowance` | 0.0% | 75.0% | 6 |
| `disability-dis-registration` | 0.0% | 75.0% | 6 |
| `health-bmdc-full-registration` | 0.0% | 75.0% | 5 |
| `judiciary-supreme-court-e-filing` | 0.0% | 75.0% | 6 |

- **Average supported coverage before:** 0.0%
- **Average supported coverage after:** 75.0%
- **Average verified claims after:** 5.5

## 6. Pilot Success Criteria Answers

1. **Dominant PARTIAL reasons:** Missing E2E supported coverage, missing fees/documents/procedure, claim density — see taxonomy.
2. **Obtainable dimensions:** Procedure, eligibility, documents (via deeper official portal/PDF investigation).
3. **Structurally unavailable:** Calculator-derived fees, JS-only portals without browser render, rare local variation rules.
4. **Deep research impact:** Supported-answer coverage improved for pilot services with curated deep hints + verification.
5. **COMPLETE definition:** Do not lower threshold yet — improvement signal exists but E2E supported coverage still below COMPLETE bar for most pilots.

## 7. Runtime & Regression

- Runtime DB: `/workspace/backend/data/bda.db` — RUNTIME_DB_ACCESSIBLE
- Regression passed: **True**

## 8. Recommendation for 416-service backlog

Do NOT rerun all 379 services blindly. Instead:

1. Prioritize high-usage PARTIAL services for deep-research protocol.
2. Add browser-rendered retrieval for JS portal services (Land mutation, NID, e-Courts).
3. Treat calculator-derived fees as CALCULATOR_DERIVED — not static COMPLETE blockers.
4. Expand conditional knowledge (IF/THEN) rather than flattening requirements.
5. Wire deep-research staging into runtime publication path for verified claims only.
6. Keep COMPLETE threshold — measure supported-answer coverage improvement first.

## Safety

- deployment_allowed = false
- auto_merge = false
- No full 379-service rerun started

