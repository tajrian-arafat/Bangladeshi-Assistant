# Supervisor Protocol

With Cursor Pro only, **Cursor is both executor and supervisor** — no external OpenAI supervisor API.

## Escalation triggers

- Critical official fee conflict
- Legal ambiguity
- Hallucination or citation failure in E2E
- Regression after new batch
- Malformed `result.json` after max retries
- Unresolved material verification conflict

## Human decision records

Written to `.automation/decisions/<decision_id>.json`:

```json
{
  "status": "HUMAN_APPROVAL_REQUIRED",
  "batch": "03A",
  "issue": "Conflicting official fees",
  "severity": "CRITICAL",
  "publication_blocked": true
}
```

When escalated:

1. **STOP** automation
2. Do **not** guess
3. Do **not** publish
4. Do **not** start next batch

Resolve with:

```bash
BDA_HUMAN_APPROVAL_TOKEN=<token> python -m automation.orchestrator.main approve <decision_id>
```

## Merge policy

- PR creation may be automated
- **Merge to main is always manual**
- Never auto-merge
