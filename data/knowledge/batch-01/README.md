# LEGACY DISCOVERY DUMP — NOT VERIFIED SoT

**Path:** `data/knowledge/batch-01/`

This folder is the **original Batch 1 discovery dump**. It incorrectly used
`verification_status: VERIFIED` for many claims merely because a source URL was
found. That label is **not** valid for publication.

## Use instead

| Purpose | Path |
|---------|------|
| Immutable raw copy | `data/research/raw/batch-01/` |
| Normalized staging (provenance chain) | `data/research/staging/batch-01/` |
| Pipeline status report | `docs/research/batch-01-pipeline-status.md` |

## Rules

- Do **not** load these files into the runtime database.
- Do **not** treat `VERIFIED` in this dump as verified.
- Do **not** overwrite `data/seeds` or live `services` / `fees` / `checklist_items`.
- Prefer staging JSON produced by `scripts/normalize_batch01_to_staging.py`.
