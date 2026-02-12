# Development Workflow

## Prerequisites
- Python 3.10+, Poetry
- Node.js LTS, pnpm/npm
- Docker (optional: Weaviate, FalkorDB, RabbitMQ)

## Setup
```bash
# Backend
poetry install
# Frontend
cd frontend && npm i
```

## Run
```bash
# Backend (from repo root)
poetry run start  # or: poetry run python start.py
# Frontend
cd frontend && npm run dev
```

## Tests
```bash
# Backend
pytest
# Frontend
cd frontend && npm run test
```

## Quality
```bash
# Backend
black . && isort . && flake8 && mypy
# Frontend
cd frontend && npm run format && npm run lint && npm run type-check
```

## Notes
- Configure `.env` (see `env.example`). Placeholder values may break startup.
- OpenAPI: `http://localhost:8000/docs`.
