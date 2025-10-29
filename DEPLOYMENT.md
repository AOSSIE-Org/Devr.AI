# Deployment

## Environment
- Copy `env.example` to `.env` and set real values:
  - `SUPABASE_URL`, `SUPABASE_KEY`
  - Any integration keys (optional)

## Docker (services)
```bash
# From repo root
cd backend
docker-compose up -d  # Weaviate, FalkorDB, RabbitMQ
```

## Backend
```bash
# Local run
poetry run start  # uses uvicorn main:api
```

## Frontend
```bash
cd frontend
npm run build
npm run preview  # or deploy via your hosting provider
```

## Health Checks
- Backend health: `GET /health`
- OpenAPI: `http://localhost:8000/docs`

## Notes
- Ensure required databases/services are reachable from the backend.
