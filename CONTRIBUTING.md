# Contributing to Devr.AI

## Quick Start
- Fork, create a branch: `git checkout -b feat/short-name`.
- Install tools: `poetry install` (backend), `npm i` in `frontend/`.
- Run locally: `poetry run start` (backend), `npm run dev` (frontend).
- Tests: `pytest` (backend), `npm run test` (frontend).
- Quality: `black`, `isort`, `flake8`, `mypy`, `eslint`, `prettier`.
- Commit small, clear messages (e.g., `fix:`, `feat:`, `docs:`).
- Open a PR with context and checklist; link issues.

## PR Rules
- Keep PRs focused; include tests and docs updates.
- CI must pass (tests, lint, type-check).
- Do not commit secrets.

## Code Style
- Python: type hints, `black` + `isort`, `flake8`, `mypy` clean.
- TS/JS: `eslint`, `prettier`, `tsc` clean.

## Security
- Report vulnerabilities privately via security advisory or email.
