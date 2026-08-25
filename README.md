# Bangladesh Digital Assistant

Bangladesh-focused digital information layer for government services, procedures, and citizen guidance.

## Status

Deployment-ready MVP implementation (not production-deployed).

## Quick start

```bash
make install && make migrate && make seed
make dev                    # API :8000
cd frontend && npm ci && npm run dev   # UI :3000
```

## Architecture

- [Full architecture blueprint (MD)](docs/architecture/bangladesh-digital-assistant-architecture.md)
- [PDF version](docs/architecture/bangladesh-digital-assistant-architecture.pdf)
- [Local setup](docs/local-setup.md)
- [Deployment guide](docs/deployment.md)

## Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 15, React 19, Tailwind, next-intl |
| Backend | FastAPI, SQLAlchemy, Alembic |
| Database | SQLite (dev) / PostgreSQL + pgvector (prod) |
| Queue | Celery + Redis |
| AI | Local LLM optional; deterministic fallback always on |

## MVP domains

Passport, NID, birth registration, BRTA, TIN, service discovery, 64 districts, forms/links, basic education.

## Tests

```bash
make test
cd frontend && npm run build
```

## License

See `docs/attribution/licenses.md`
