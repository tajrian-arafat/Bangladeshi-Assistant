# Backup and Restore

## Backup

```bash
pg_dump "$DATABASE_URL" | gzip > backup-$(date +%Y%m%d).sql.gz
# Upload to MinIO or offsite storage
```

## Restore

```bash
gunzip -c backup-YYYYMMDD.sql.gz | psql "$DATABASE_URL"
cd backend && alembic upgrade head
python ../scripts/seed_database.py  # only if restoring to empty DB
```

## RPO / RTO

- RPO: 24 hours (nightly backup)
- RTO: 4 hours (small deployment)
