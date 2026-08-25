# Workflow

## Phases (in order)

1. **RESEARCH** — discovery per `docs/research/BATCH_RESEARCH_TEMPLATE.md`
2. **VERIFICATION** — independent claim verdicts
3. **GAP_CLOSURE** — targeted evidence only (optional)
4. **PUBLICATION** — local/dev verified claims only
5. **E2E** — realistic multilingual queries
6. **REGRESSION** — all baseline suites
7. **STABILIZATION** — reusable routing fixes if needed

## State machine

| State | Meaning |
|-------|---------|
| READY | Waiting to start next step |
| RUNNING | Phase executing |
| WAITING_FOR_RESULT | Awaiting Cursor `result.json` |
| VALIDATING_RESULT | Schema + gate checks |
| AUTO_CONTINUE | Passed — advance phase |
| RETRY | Technical failure (max 3) |
| GAP_CLOSURE | Verification found researchable gaps |
| SUPERVISOR_REVIEW | Cursor self-review needed |
| HUMAN_APPROVAL_REQUIRED | Stop — human decision |
| BLOCKED | Safety gate failed |
| COMPLETE | Batch finished |

Illegal transitions raise `ValueError`.

## Batch progression

Next batch only when:

- Current batch complete
- Critical claims safe
- Publication complete (if applicable)
- E2E acceptable
- Regression passes
- No blocking escalation
- No unresolved critical conflict

## Pilot vs continuous

- **Pilot (`pilot_mode: true`):** BATCH_03A with reviewable phase transitions
- **Continuous (`daemon`):** automatic ticks after pilot passes
