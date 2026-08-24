# Operations

## Initial setup

```bash
pip install -e ".[dev]"   # repo root — automation package
python -m automation.orchestrator.main init
```

## Manual single step

```bash
python -m automation.orchestrator.main run
python -m automation.orchestrator.main status
```

## Offline simulation (required before real batches)

```bash
python -m automation.orchestrator.main simulate
```

Runs 10 cases without touching the research queue.

## Continuous mode

```bash
python -m automation.orchestrator.main daemon --interval 60
```

Stops on HUMAN_APPROVAL_REQUIRED, BLOCKED, or COMPLETE.

## Environment variables

| Variable | Purpose |
|----------|---------|
| `CURSOR_API_KEY` | Cloud Agents API |
| `BDA_GITHUB_REPO` | Repository URL for cloud agents |
| `BDA_GIT_BRANCH` | Branch for cloud agents |
| `BDA_AUTOMATION_PREFER_CLOUD` | Default `1` |
| `BDA_HUMAN_APPROVAL_TOKEN` | Required for `approve` |
| `BDA_DEPLOYMENT_UNLOCK` | Required for deployment unlock |

## Cursor hooks

Configured in `.cursor/hooks.json` — defense in depth alongside Python gates.

## Pilot: BATCH_03A

After simulation passes:

```bash
python -m automation.orchestrator.main run
```

Creates `data/research/raw/batch-03a-brta-driving-licence/scope.json` and dispatches research prompt.
