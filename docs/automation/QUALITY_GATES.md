# Quality Gates

## Deployment lock

- `.automation/deployment.lock` = `false` (default)
- Blocks: deploy, production hosting, `npx convex deploy`, PR merge commands
- Unlock only via human: `BDA_DEPLOYMENT_UNLOCK=I_UNDERSTAND_PRODUCTION_RISK` + `approve deployment_unlock`

## Publication gates

Never publish: PARTIALLY_VERIFIED, UNVERIFIED, CONFLICTING, OUTDATED, REJECTED as authoritative.

Blocked when `workflow_status` is `HUMAN_APPROVAL_REQUIRED` or `BLOCKED`.

## Regression baseline (must hold)

| Suite | Required |
|-------|----------|
| Batch 1 E2E | 100% |
| Passport E2E | 100% |
| Batch 2B E2E | 100% normalized |
| Routing benchmark | 100% |
| Hallucinations | 0 |
| Citation failures | 0 |
| Pytest | 58/58 |

## Phase result gates

- `hallucinations > 0` → BLOCK
- `citation_failures > 0` → BLOCK
- `critical_conflicts > 0` at publication → BLOCK
- `regressions > 0` → BLOCK / fix cycle

## Retry policy

Technical failures only (timeout, crash, malformed artifact): max **3** retries, then SUPERVISOR_REVIEW.
