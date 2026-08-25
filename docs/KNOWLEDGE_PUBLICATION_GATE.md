# Knowledge Publication Gate

**Version:** 1.0  
**Date:** 2026-08-24  
**Code:** `backend/app/application/knowledge/publication_gate.py`

---

## Hard rule

A claim may become **authoritative runtime knowledge** (`VERIFIED` + `OFFICIAL` published into Fee / Checklist / ProcedureStep) only when **all** of the following hold:

1. Evidence exists (excerpt and/or locator / chunk).
2. Source authority is sufficient (Tier 1–2 for OFFICIAL hard facts).
3. Evidence actually supports the claim.
4. No unresolved material conflict for the same fact family.
5. Freshness requirements are satisfied (when `retrieved_at` known).
6. Required reviewer approval / `verified_at` is set.
7. Provenance is complete: Claim → Evidence → SourceVersion → Source.
8. Durable `content_hash` (or equivalent snapshot) is present for auditability.

If any requirement fails: **DO NOT publish.**

---

## Conflict gate

If Claim A says fee=50 and Claim B says fee=500 and the conflict is unresolved:

- Both claims remain stored.
- Neither populates authoritative `fees`.
- Service may be marked `CONFLICTED` / needs review.
- The LLM must not choose arbitrarily.

---

## Requirement / fee / procedure rules

| Target | Rule |
|--------|------|
| MUST NEED checklist | Only `VERIFIED` + `OFFICIAL` document claims |
| CONDITIONAL checklist | Same, plus explicit supported condition |
| Fee | Only `VERIFIED` + `OFFICIAL` fee claims with `structured_value.amount` |
| ProcedureStep | Only verified official procedure claims — never invent boilerplate steps |
| PRACTICAL tips | Never populate official MUST NEED |

---

## Answer support levels

Runtime answers distinguish (internally):

- `VERIFIED`
- `PARTIALLY_SUPPORTED`
- `CONFLICTED`
- `INSUFFICIENT_EVIDENCE`

The orchestrator must **not** say “verified guidance” unless support is `VERIFIED`.

---

## CLI

```bash
python scripts/publish_verified_knowledge.py --batch batch-01 --dry-run
python scripts/publish_verified_knowledge.py --batch batch-01 --sync-claims --dry-run
python scripts/publish_verified_knowledge.py --batch batch-01 --publish --dry-run
python scripts/publish_verified_knowledge.py --batch batch-01 --sync-claims --commit
python scripts/publish_verified_knowledge.py --batch batch-01 --publish --commit
```

`--publish` without `--commit` remains dry-run. Validation failures raise and roll back.
