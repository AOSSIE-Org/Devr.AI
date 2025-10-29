# API Documentation

Base URL (local): `http://localhost:8000`

- OpenAPI UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Auth
- POST `/api/v1/auth/login`

Example:
```bash
curl -X POST \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"secret"}' \
  http://localhost:8000/api/v1/auth/login
```

## Health
- GET `/health`

Example:
```bash
curl http://localhost:8000/health
```

## Notes
- Some endpoints require valid environment configuration (e.g., Supabase keys).
- See `DEVELOPMENT.md` for running locally.
