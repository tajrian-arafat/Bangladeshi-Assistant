# Deep Research Runtime Integration (Step 32)

Generated: 2026-08-25T04:38:41+00:00

## Executive summary

Step 32 productionized the deep-research pipeline with full runtime integration: **research → staging → sync → publish → retrieval audit → E2E → regression**. The 20-service pilot **did not pass the quality gate** — not because research failed, but because **publication and runtime retrieval remain the dominant bottlenecks**, confirming Step 31 findings at scale.

| Metric | Result | Target | Status |
|--------|--------|--------|--------|
| Supported-answer coverage (simulated E2E) | **71.7%** | ≥75% | Close — up from 0% baseline |
| Runtime retrieval accuracy | **5.0%** | ≥95% | Failed — publication gate blocks most claims |
| Verified deep-research claims | **109** | — | Research layer working |
| Claims synced to runtime DB | **113** | — | Storage path working |
| Regression (149 tests) | **GREEN** | GREEN | Passed |

**Pilot passed: false** — scaling to 396+ services remains blocked.

## Pipeline implemented

```
SERVICE PROFILE → DISCOVERY → DEEP OFFICIAL RETRIEVAL → BROWSER/JS WHEN NEEDED
→ CLAIM EXTRACTION → CONDITIONAL RULES → INDEPENDENT VERIFICATION → GAP CLOSURE
→ LOCAL PUBLICATION (staging) → sync → publish → RUNTIME VALIDATION → E2E → REGRESSION
```

Key modules:
- `automation/orchestrator/deep_research_pipeline.py` — canonical orchestrator
- `automation/orchestrator/deep_research_staging.py` — publisher-ready staging
- `automation/orchestrator/runtime_validator.py` — DB + ClaimRetrieval probes
- `automation/orchestrator/claim_density.py` — complexity-tier density scoring
- `automation/orchestrator/task_factory.py` — `DEEP RESEARCH THIS EXACT SERVICE` tasks
- `scripts/run_deep_research_pilot_20.py` — 2-wave pilot runner

## Selected services (20 — excludes Step 31's 12)

| Role | Service ID | Domain |
|------|------------|--------|
| high_usage | `nid-download-copy` | identity |
| high_usage | `education-hsc-certificate` | education |
| high_usage | `local-passport-attestation` | certificates |
| high_usage | `tax-etin-registration` | tax |
| high_risk | `customs-import-export-control-licence` | customs |
| high_risk | `permits-fire-noc-enoc` | permits |
| high_risk | `nid-combined-correction` | identity |
| land | `land-deed-registration` | land |
| land | `land-khatian-online-copy` | land |
| education | `education-class-registration` | education |
| health | `health-16263-telemedicine` | health |
| agriculture | `agri-bamis-farmer-registration` | agriculture |
| employment | `employment-boesl-overseas-recruitment` | employment |
| local_gov | `dc-attestation-photocopy` | local_government |
| utilities | `ff-g2p-electronic-payment` | social_protection |
| tax | `vat-bin-registration` | vat |
| judiciary | `judiciary-case-status-tracking` | judiciary |
| geographic | `dc-citizen-charter-dhaka` | local_government |
| js_heavy | `customs-asycuda-declaration` | customs |
| professional | `health-bmdc-eligibility-certificate` | health |

## Deep-research results

- **109 verified claims** extracted across 20 services
- Document knowledge: MUST_NEED / CONDITIONAL / RECOMMENDED preserved in claim `condition.requirement_class`
- Conditional rules stored structurally (not flattened)
- JS-rendered portals flagged with `JS_RENDERING_LIMITATION` gaps
- Calculator-derived fees marked `CALCULATOR_DERIVED` / `UNVERIFIED`

Artifacts: `data/research/deep-research-pilot-20/`, `data/evaluation/deep-research-pilot-20/`

## Runtime publication

- Staging batch: `data/research/staging/deep-research-pilot-20/`
- Verification: `data/research/verification/deep-research-pilot-20/`
- **113 claims synced** to `backend/data/bda.db`
- Publication gate outcome: most services **RED / KNOWLEDGE_GAP** — claims synced but not published to answer layer
- Partial success: `nid-download-copy` published 7 verified claims; `nid-combined-correction` partial (seed replacement pending)

## Retrieval audit

See `data/audit/deep-research-runtime-consistency.json`.

Probe classification:
- **PUBLICATION_GAP** — verified claims in DB but `is_published=false` (gate blocked)
- **RETRIEVAL_BUG** — published claims exist but `ClaimRetrieval` misses them (e.g. procedure claim_type mismatch)
- **OK** — published claim retrieved for intent

Aggregate retrieval accuracy: **5.0%** (dominated by publication gaps, not research gaps).

## Bottleneck quantification

| Layer | Count / finding |
|-------|-----------------|
| RESEARCH | 109 verified claims — **working** |
| VERIFICATION | Independent verifier applied — **working** |
| PUBLICATION | ~18/20 services blocked by `KNOWLEDGE_GAP` or seed replacement — **primary bottleneck** |
| RUNTIME STORAGE | 113 claims synced — **working** |
| RETRIEVAL | 5% when publication blocks; isolated RETRIEVAL_BUG on published services |
| E2E (simulated) | 71.7% supported — **near target** |
| REGRESSION | 149/149 green — **working** |

**Primary bottleneck: PUBLICATION** (gate + knowledge readiness), co-primary: **RETRIEVAL** (downstream of publication).

## Orchestrator integration

- `rerun_queue.json` updated: **384 services** marked `DEEP_RESEARCH_REQUIRED`, `do_not_autorun_until_pilot_passes: true`
- `overnight_runner.py` blocks autorun when deep-research queue is pending pilot gate
- `cloud_executor.py` routes `DEEP_RESEARCH` phase to `create_deep_research_task`

## Regression

All baseline suites green after Step 32 changes:
- Batch 1, Passport, Batch 2B, Batch 3A–3C, routing, cross-domain
- **149/149** automation + backend tests

## Constraints preserved

- COMPLETE thresholds **not lowered**
- **396+ PARTIAL services not launched** — queued only
- **No deploy, no merge**
- Verification gates **not weakened**

## Next steps (blocked until publication path fixed)

1. Fix publication gate / knowledge readiness for deep-research staging packs
2. Resolve seed replacement blocking for services like `nid-combined-correction`
3. Fix RETRIEVAL_BUG cases where published claims miss intent→claim_type mapping
4. Re-run 20-service pilot gate; only then scale `DEEP_RESEARCH_REQUIRED` queue
