# Deployment Guide

## Docker Compose (recommended)

```bash
cp .env.example .env
# Edit .env for production secrets

docker compose up -d postgres redis minio api worker scheduler frontend
docker compose exec api alembic upgrade head
docker compose exec api python /scripts/seed_database.py
```

Optional LLM profile:

```bash
# Place GGUF model in ./models/model.gguf
docker compose --profile llm up -d llm
```

Production with Caddy TLS:

```bash
docker compose --profile prod up -d
```

## Environment

See `.env.example` for all variables. Required for production:

- `APP_SECRET_KEY`
- `JWT_SECRET`
- `DATABASE_URL` (PostgreSQL + pgvector)
- `REDIS_URL`
- `CORS_ORIGINS`

## Health checks

- Liveness: `GET /api/v1/health`
- Readiness: `GET /api/v1/readiness`
