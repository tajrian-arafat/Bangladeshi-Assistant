# Batch 3C Research Report — BRTA Fitness / Tax Token / Route Permit

**Batch ID:** `BATCH_03C`  
**Slug:** `batch-03c-brta-fitness-tax-permit`  
**Phase completed:** RESEARCH → VERIFICATION → GAP_CLOSURE  
**Researched at:** 2026-08-25  
**Catalogue version:** 1.0.0-finalized (464 canonical services)

---

## Executive summary

Batch 3C covers **15 CONFIRMED catalogue services** in the BRTA fitness, tax token, route permit, and related portal/modification domain. Research produced **121 atomic claims** from **15 sources** (Tier 1–2). Vehicle-type, usage-class, procedure-action, and route/permit-type variants are modeled explicitly — rules are **not** flattened into generic checklists.

**Critical cross-batch dependency (BATCH_03B → BATCH_03C):** Fitness validity by vehicle class was deferred from Batch 3B. Gap-closure browser probe verified the portal page title (`ফিটনেস নবায়ন`) but **no authoritative validity-by-class matrix** was captured in the CMS render. Resolution status: **PARTIALLY_RESOLVED** — validity periods remain **UNVERIFIED** (no invented durations such as "private car 5 years").

**Next automatic transition:** `GAP_CLOSURE → PUBLICATION → E2E → REGRESSION` (orchestrator autonomous loop).

---

## 1. Scope discovery

### In scope (15 services — batch queue)

| Service ID | Focus |
|---|---|
| `brta-fitness-certificate` | Fitness issue/renewal, E-Fitness, inspection |
| `brta-tax-token` | Tax token issue/renewal |
| `brta-mv-tax-payment` | Motor vehicle tax (MV tax) payment portal |
| `brta-advance-income-tax` | Advance income tax (motor vehicle) |
| `brta-route-permit` | Route permit issue/renewal (portal) |
| `transport-route-permit` | Route permit (BSP operator service) |
| `brta-fee-calculator` | BSP fee calculator (cross-cutting) |
| `brta-bsp-user-registration` | BSP account prerequisite |
| `brta-e-document-verification` | E-tax token / e-license verification |
| `brta-payment-verification` | BSP payment verification |
| `brta-color-change` | Vehicle color modification |
| `brta-engine-change` | Engine replacement registration |
| `brta-tire-size-change` | Tyre width modification |
| `brta-driving-school-registration` | Driving training school registration |
| `transport-driving-school-licence` | Driving school / training centre licence |

### Related services — out of scope (cross-referenced only)

| Service ID | Reason |
|---|---|
| `brta-new-vehicle-registration` | BATCH_03B — fitness/tax may be bundled at first registration |
| `brta-ownership-transfer` | BATCH_03B — may require current fitness/tax as prerequisites |

---

## 2. Sources (Tier 1–2)

| Tier | Source | URL / notes |
|---|---|---|
| 1 | BSP fee calculator | https://bsp.brta.gov.bd/feeCalculator — CALCULATOR_DERIVED fees |
| 1 | BSP home / roadSafety | https://bsp.brta.gov.bd/ — operating context, driving school |
| 1 | BSP register | https://bsp.brta.gov.bd/register — owner account prerequisite |
| 2 | BRTA fitness portal | …/6922db91933eb65569e0af12 — title verified; CMS body empty |
| 2 | BRTA tax token portal | …/6922e0ab933eb65569e281ad |
| 2 | BRTA route permit portal | …/6922df7a933eb65569e2240e |
| 2 | BRTA AIT portal | …/6922e058933eb65569e269cd |
| 2 | Modification portals | color / engine / tyre static pages |
| 2 | MV tax portal (catalogue) | https://brta.cnsbd.com/mvtax_brta — DNS fetch failed at probe |
| 2 | Canonical catalogue | `data/service_catalogue/services.json` |

Full source registry: `data/research/raw/batch-03c-brta-fitness-tax-permit/sources.json`

---

## 3. Fitness validity resolution (BATCH_03B dependency)

| Requirement | Status | Evidence |
|---|---|---|
| Validity period by vehicle class | **UNVERIFIED** | Portal render has title only; no class matrix |
| Commercial vs private inspection rules | **UNVERIFIED** | Not in authoritative capture |
| Renewal interval / grace rules | **UNVERIFIED** | Not in authoritative capture |
| Portal page identity | **VERIFIED** | Title `ফিটনেস নবায়ন`; last-updated metadata captured |

**Cross-batch resolution:** `dep-03b-fitness-validity-03c` → **PARTIALLY_RESOLVED**  
Artifact: `data/research/verification/batch-03c-brta-fitness-tax-permit-gap-closure/cross_batch_dependency_resolution.json`

Historical BATCH_03B claims are **not rewritten**; supersession records link deferral claim to gap-closure resolution claims.

---

## 4. Claims summary

| Metric | Count |
|---|---|
| Research claims | 121 |
| Gap-closure claims | 7 |
| Total after verification | 128 |
| VERIFIED | 21 |
| PARTIALLY_VERIFIED | 99 |
| UNVERIFIED | 8 |
| Fitness validity UNVERIFIED | 2 |
| Blocking knowledge gaps | 0 (documented gaps: 6) |

---

## 5. Fee handling

All vehicle-type-dependent fees are **`CALCULATOR_DERIVED`** via BSP feeCalculator. Interactive matrix not fully captured — **no static numeric amounts invented**. Staged fee records: `data/research/staging/batch-03c-brta-fitness-tax-permit/fees.json` (12 CALCULATOR_DERIVED entries).

---

## 6. Conflicts detected

1. **Portal CMS empty body** vs expected procedural checklists (Tier 2 pages render `কন্টেন্ট: পাতা` placeholder)
2. **Calculator-derived fees** vs blog/static fee tables (reject unverified static amounts)
3. **brta-route-permit** (portal page) vs **transport-route-permit** (BSP) — distinct official entry points
4. **MV tax portal** catalogue URL vs DNS resolution failure at probe time
5. **Private vs commercial** validity rules — insufficient authoritative evidence to resolve

---

## 7. Knowledge gaps (documented, non-blocking)

| Gap ID | Classification |
|---|---|
| `MISSING_FITNESS_VALIDITY_BY_CLASS` | cross_batch_dependency — UNRESOLVED |
| `MISSING_FEE_MATRIX` | missing_fee_schedule — UNRESOLVED |
| `MISSING_ROUTE_PERMIT_TYPE_MATRIX` | insufficient_evidence — UNRESOLVED |
| `MISSING_MV_TAX_PORTAL_SNAPSHOT` | availability — UNRESOLVED |
| `MISSING_PORTAL_JS_BODY` | insufficient_evidence — PARTIALLY_RESOLVED |
| `MISSING_BSP_CALCULATOR_INTERACTION` | missing_fee_schedule — PARTIALLY_RESOLVED |

---

## 8. Practical findings

- BSP fee calculator and home pages **rendered** during 03C probe (vs 404 off-hours in 03B)
- BRTA portal static pages consistently show **verified titles** but **empty CMS instructional bodies**
- E-Fitness results viewable on BSP per catalogue notes on `brta-fitness-certificate`
- Commercial route permit workflows require fitness and tax prerequisites (conditional claims — detail UNVERIFIED)
- Vehicle modification services (color/engine/tyre) are **separate procedures** from fitness renewal and tax token

---

## 9. Evidence limitations

- No authoritative fitness validity schedule captured from Tier 1–2 sources
- Fee amounts require live BSP calculator session with vehicle class selected
- MV tax portal external host unreachable at probe (`brta.cnsbd.com` DNS failure)
- Route permit route-type matrix not published in captured portal renders

---

## 10. Explicit non-actions

- Did not invent fitness validity periods
- Did not deploy or merge
- Did not approve legacy seed replacements
- Did not start Batch 4

---

## Artifact paths

| Artifact | Path |
|---|---|
| Raw research | `data/research/raw/batch-03c-brta-fitness-tax-permit/` |
| Verification | `data/research/verification/batch-03c-brta-fitness-tax-permit/` |
| Gap closure | `data/research/verification/batch-03c-brta-fitness-tax-permit-gap-closure/` |
| Staging | `data/research/staging/batch-03c-brta-fitness-tax-permit/` |
| Gap-closure doc | `docs/research/batch-03c-brta-fitness-tax-permit-gap-closure.md` |
