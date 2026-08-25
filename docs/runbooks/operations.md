# Operations Runbook

## Daily checks

1. `GET /api/v1/readiness` — all dependencies green
2. Grafana dashboard — API latency, crawl failures
3. Review queue — pending fee/document changes

## Common issues

### LLM unavailable

System degrades to deterministic mode automatically. Check `llm` container logs. Set `FEATURE_LLM_ENABLED=false` to skip LLM calls.

### Database connection errors

Verify `DATABASE_URL`, PostgreSQL health, connection pool size.

### Stale knowledge

Trigger crawl: `POST /api/v1/admin/sources/{id}/crawl` (admin auth required).

## Backups

Nightly `pg_dump` to MinIO backup bucket. See `docs/runbooks/backup-restore.md`.
