# Research data (staging) — not the runtime knowledge SoT

This directory holds the **research → evidence → verification → publication** pipeline
artifacts. It is intentionally separate from the production database and from
`data/seeds/`.

## Hard rules

1. **Nothing here is served to users as authoritative** until a dedicated
   verification/publication phase writes approved facts into the runtime DB
   (`services`, `checklist_items`, `fees`, `procedures`, …).
2. Finding a source does **not** make a claim `VERIFIED`.
3. Practical / social / news findings stay `information_class: PRACTICAL` and
   must never auto-populate official MUST requirements.
4. Do **not** load these files via `scripts/seed_database.py`.
5. Do **not** implement RAG/embeddings solely because architecture docs mention them.

## Layout

```
data/research/
  README.md
  catalogue_runtime_mappings.json   ← catalogue_service_id → runtime slug
  raw/                              ← discovery dumps
  staging/                          ← normalized Source→…→Claim chains
    schema.json
    batch-01/
  publication/                      ← reserved; empty until verification phase
```

## Runtime publish CLI

```bash
python scripts/publish_verified_knowledge.py --batch batch-01 --dry-run
python scripts/publish_verified_knowledge.py --batch batch-01 --sync-claims --dry-run
python scripts/publish_verified_knowledge.py --batch batch-01 --publish --commit
```

See `docs/RESEARCH_TO_RUNTIME_PIPELINE.md` and `docs/KNOWLEDGE_PUBLICATION_GATE.md`.

## Pipeline states (claim / fact)

`DISCOVERED` → `EXTRACTED` → `NORMALIZED` → `CROSS_CHECKED` → `PENDING_REVIEW`
→ `VERIFIED` | `CONFLICTING` | `OUTDATED` | `REJECTED`

Only `VERIFIED` (after human/process verification) may publish into runtime
official answer fields.
