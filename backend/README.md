# Bangladesh Digital Assistant — Backend

FastAPI backend for the Bangladesh Digital Assistant modular monolith.

## Quick start

```bash
# From repo root
make install
make migrate
make seed
make dev
```

API docs: http://localhost:8000/docs

Health: http://localhost:8000/api/v1/health  
Readiness: http://localhost:8000/api/v1/readiness

## Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI entry
│   ├── api/v1/              # REST routers and endpoints
│   ├── core/                # config, database, security, logging
│   ├── domain/              # enums and SQLAlchemy models
│   ├── application/         # use-case services
│   └── schemas/             # Pydantic request/response models
├── alembic/                 # Database migrations
├── tests/                   # pytest suite
└── pyproject.toml
```

## Database

- **Dev:** SQLite with JSON text embeddings (`sqlite+aiosqlite:///./data/bda.db`)
- **Prod:** PostgreSQL 16 + pgvector (`postgresql+asyncpg://...`)

Run migrations: `make migrate`  
Load seeds: `make seed`
