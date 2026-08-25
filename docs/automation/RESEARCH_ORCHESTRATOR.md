# Research Orchestrator

The BDA **Autonomous Knowledge-Construction Orchestrator** automates:

**RESEARCH → VERIFICATION → GAP CLOSURE → LOCAL PUBLICATION → E2E → REGRESSION → NEXT BATCH**

## Architecture

```
Human
  ↓
Cursor Agent (research / reasoning)
  ↓
Deterministic Python Orchestrator (workflow state authority)
  ↓
Quality Gates
  ↓
Cursor Agent continuation OR human escalation
```

- **Cursor** is the execution and reasoning agent (Cloud Agents API preferred, local prompt fallback).
- **Python orchestrator** is authoritative for workflow state — AI chat prose never transitions state directly.
- Every phase writes `.automation/runs/<run_id>/result.json` validated before transitions.

## Key paths

| Path | Purpose |
|------|---------|
| `automation/orchestrator/` | State machine, gates, phase runner |
| `.automation/project_state.json` | Current batch/phase/status |
| `.automation/deployment.lock` | Hard deployment lock (`false`) |
| `.automation/batch_queue.json` | Catalogue-derived batch queue |
| `.automation/runs/` | Per-run artifacts + `result.json` |

## Commands

```bash
python -m automation.orchestrator.main init
python -m automation.orchestrator.main status
python -m automation.orchestrator.main simulate
python -m automation.orchestrator.main run
python -m automation.orchestrator.main resume
python -m automation.orchestrator.main pause
python -m automation.orchestrator.main stop
python -m automation.orchestrator.main approve <decision_id>
```

## Cursor integration

- **Cloud:** `CURSOR_API_KEY` → Cursor Cloud Agents API v1 (`POST /v1/agents`)
- **Local fallback:** writes `prompt.md` + expects validated `result.json`
- **CLI fallback:** optional via `BDA_AUTOMATION_USE_CLI=1`

## Cost control

- No external paid AI APIs
- Cursor Pro only
- Gap closure only when verification finds real gaps
- Deterministic gates before re-invoking Cursor

See also: [WORKFLOW.md](./WORKFLOW.md), [QUALITY_GATES.md](./QUALITY_GATES.md), [OPERATIONS.md](./OPERATIONS.md)
