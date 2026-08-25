# Local Setup

## Prerequisites

- Python 3.12+
- Node.js 22+
- (Optional) Docker for full production stack

## Quick start (local)

```bash
cp .env.example .env
make install
make migrate
make seed
make dev          # API on http://localhost:8000
```

In another terminal:

```bash
cd frontend
npm ci
npm run dev       # UI on http://localhost:3000
```

Default admin (seed): `admin@bda.local` / `Admin123!ChangeMe`

## Verify

```bash
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/services
```
