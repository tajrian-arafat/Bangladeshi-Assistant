# Service-Specific Research Pipeline Fix — Step 29 Report

**Date:** 2026-08-25  
**Verdict:** Pipeline fix implemented; **10-service pilot PASSED**  
**Remaining 379 false-completion services:** Eligible for autonomous re-research **after human review of this report** — not auto-launched.

---

## Executive Summary

The final global audit (`KNOWLEDGE_INCOMPLETE`) identified **389 services at FALSE_COMPLETION_RISK** because batches 04–14 were processed by a generic builder that emitted boilerplate catalogue metadata (`c-application-portal`, `c-responsible-authority`, `c-official-source`) — including incorrect NBR portal references on land and health services.

This step **freezes generic builder output as non-authoritative scaffolding**, introduces a data-driven research quality model, blocks batch completion on false completion, builds a 389-service re-research queue, and validates the new pipeline on a **10-service cross-category pilot**.

**Do not run the full 389-service queue yet.** Deployment remains locked; auto-merge disabled.

---

## False-Completion Root Causes

| Cause | Impact |
|-------|--------|
| Generic `ResearchBuilder` treated artefact existence as research complete | 389 services marked researched with 2–3 boilerplate claims |
| Hardcoded NBR portal fallback for all services | Land/health/education services received tax portal URLs |
| `check_research_complete()` only checked file existence | No service-level quality gate |
| Generic verification marked catalogue claims VERIFIED on URL reachability | Inflated verification counts without service specificity |
| Overnight orchestrator advanced batches on phase artefact success | BATCH_COMPLETE without per-service evaluation |

Example: `land-deed-registration` received claim text *"associated with NBR e-service portal"* despite Department of Registration / land.gov.bd being the correct authority.

---

## New Research Quality Model

### Claim classes

| Class | Counts toward completeness? |
|-------|----------------------------|
| `SERVICE_SPECIFIC` | Yes — meaningful, authority-matched evidence |
| `CATALOGUE_METADATA` | No — scaffolding only |
| `DISCOVERY_ONLY` | No — discovery hints only |

### Service status

A service is `RESEARCH_COMPLETE` only when its profile requirements are met:

- Minimum meaningful service-specific claims
- At least one authoritative service-specific source (authority/domain matched)
- Required research dimensions attempted (identity, authority, official URL, procedure — profile-specific)
- No metadata-only completion pattern
- Verified claims per profile minimum (where applicable)

Implementation: `automation/orchestrator/research_quality.py`

### Completeness scoring (documented weights)

From `data/research/service_research_profiles.json`:

```
completeness = research_quality (0.25)
             + verification_quality (0.20)
             + knowledge_coverage (0.20)
             + e2e_supported_coverage (0.15)
             + source_quality (0.10)
             + citation_integrity (0.10)
```

Pipeline phase count is **not** used as a proxy for completeness.

---

## Configuration

| File | Purpose |
|------|---------|
| `data/research/service_research_profiles.json` | Service-type profiles (LAND, HEALTH, TAX, …) |
| `data/audit/generic-claim-detection.json` | 389 FALSE_COMPLETION_RISK + 65 VALID |
| `data/research/rerun_queue.json` | 389 services → `RESEARCH_REQUIRED` with priorities |
| `data/audit/runtime-database-diagnostic.json` | Runtime DB path diagnosis |

---

## Pipeline Changes

| Component | Change |
|-----------|--------|
| `research_builder.py` | Scaffolding only; claims tagged `CATALOGUE_METADATA`; NBR bleed removed |
| `service_research_builder.py` | **New** — per-service authoritative research |
| `research_quality.py` | **New** — classification, scoring, batch gate |
| `task_factory.py` | Per-service research briefs: **RESEARCH THIS EXACT SERVICE** |
| `phase_completion.py` | Quality gate integrated into research completion |
| `cloud_worker.py` | Returns PARTIAL when quality gate fails |
| `phase_runner.py` / `overnight_runner.py` | Block BATCH_COMPLETE on false completion |

Hand-researched batches 01–03 are exempt from false-completion blocking (preserved verified knowledge).

---

## 10-Service Pilot

| # | Service | Category | Profile | Status | Score |
|---|---------|----------|---------|--------|-------|
| 1 | `land-deed-registration` | land | LAND | RESEARCH_COMPLETE | 1.0 |
| 2 | `education-class-registration` | education | EDUCATION | RESEARCH_COMPLETE | 1.0 |
| 3 | `health-16263-telemedicine` | health | HEALTH | RESEARCH_COMPLETE | 1.0 |
| 4 | `ff-g2p-electronic-payment` | social_protection | SOCIAL_PROTECTION | RESEARCH_COMPLETE | 1.0 |
| 5 | `disability-dis-registration` | disability | DISABILITY | RESEARCH_COMPLETE | 1.0 |
| 6 | `vat-bin-registration` | vat | TAX | RESEARCH_COMPLETE | 1.0 |
| 7 | `dc-attestation-photocopy` | local_government | LOCAL_GOVERNMENT | RESEARCH_COMPLETE | 1.0 |
| 8 | `judiciary-case-status-tracking` | judiciary | JUDICIARY | RESEARCH_COMPLETE | 1.0 |
| 9 | `agri-bamis-farmer-registration` | agriculture | AGRICULTURE | RESEARCH_COMPLETE | 1.0 |
| 10 | `employment-boesl-overseas-recruitment` | employment | EMPLOYMENT | RESEARCH_COMPLETE | 1.0 |

**Pilot verdict:** `PILOT_PASSED` — all 10 services:

- Not `FALSE_COMPLETION_RISK`
- Service-specific sources with authority-matched domains (no NBR on land)
- Meaningful verified claims (2–4 per service)
- Critical dimensions covered
- Zero hallucinations / citation failures in pilot E2E checks

Pilot artefacts: `data/research/pilot/{service_id}/`  
Full results: `data/audit/service-specific-research-pilot.json`

**Note:** Pilot E2E used artifact-quality evaluation because canonical audit path `data/bda.db` is empty; see runtime DB diagnosis below.

---

## Runtime Database Diagnosis

| Path | Size | Status |
|------|------|--------|
| `data/bda.db` | 0 bytes | Empty — audit path |
| `backend/data/bda.db` | ~3.4 MB | Populated |

**Diagnosis code:** `D_WRONG_AUDIT_PATH`

The final audit inspected `data/bda.db` (empty). Runtime knowledge exists at `backend/data/bda.db`. Publication path alignment is required before claiming end-to-end runtime consistency. **Do not silently claim runtime knowledge is unavailable** — it exists at the backend path but not the audit path.

---

## Regression Results

| Suite | Result |
|-------|--------|
| Automation tests | **72/72 passed** |
| Backend pytest | **62/62 passed** |
| Batch 01–03 knowledge | Unchanged (hand-researched) |
| Publication gates | Not weakened |
| Deployment | Locked |

---

## Re-Research Queue

- **389 services** queued in `data/research/rerun_queue.json`
- All marked `RESEARCH_REQUIRED` (not COMPLETE)
- Prioritized by citizen usage, harm risk, false-source bleed
- `do_not_autorun_until_pilot_passes: true` — pilot now passed

### Are the remaining 379 safe to rerun?

**Conditionally yes** — the pilot demonstrates the new pipeline produces genuine service-specific knowledge across diverse categories. Recommended before autonomous queue:

1. Align runtime DB publication path
2. Human approval of pilot artefacts (especially procedure/document hints)
3. Run overnight orchestrator in service-by-service mode using `ServiceResearchBuilder` + per-service task briefs
4. Keep deployment locked until a second audit confirms false-completion count → 0

**Do not launch all 389 in one unattended run without monitoring.**

---

## What Was NOT Done (per instructions)

- Full 389-service autonomous queue **not started**
- No deploy / merge
- No weakening of publication gates
- No changes to verified Batch 01–03 knowledge
- No threshold lowering

---

## Next Steps (human decision)

1. Review pilot artefacts under `data/research/pilot/`
2. Approve re-research queue processing strategy
3. Fix canonical runtime DB path (`data/bda.db` vs `backend/data/bda.db`)
4. After approval: process `rerun_queue.json` service-by-service via updated orchestrator
