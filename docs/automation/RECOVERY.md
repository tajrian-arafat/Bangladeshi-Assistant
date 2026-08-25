# Recovery

## Commands

```bash
python -m automation.orchestrator.main status   # current state
python -m automation.orchestrator.main resume   # after pause/stop
python -m automation.orchestrator.main pause
python -m automation.orchestrator.main stop
```

## Crash recovery / idempotency

Each run has:

- `run_id`
- `batch_id`
- `phase`
- `idempotency_key`

Restarting after a completed phase must **not**:

- duplicate claims/sources/publications
- duplicate PRs
- restart the same batch from scratch

Check `.automation/current_run.json` and `.automation/runs/<run_id>/result.json`.

## If validation fails

1. Fix `result.json` or re-run phase
2. `resume` after fixing
3. If retries exhausted → check `.automation/decisions/`

## If regression fails

1. STOP next batch
2. Root-cause fix in routing/knowledge
3. Re-run regression scripts
4. Escalate if unresolved

## Reset (human only)

Delete `.automation/current_run.json` and set `workflow_status` to `READY` in `project_state.json` — only when you understand the partial run state.
