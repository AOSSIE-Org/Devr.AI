# Database Connection Management

This document describes the thread-safe database connection management implemented for the Devr.AI backend.

## Overview

We use **SQLAlchemy** (AsyncIO) with **asyncpg** to manage a pool of connections to the Supabase PostgreSQL database. This allows for high-concurrency operations without the limitations of HTTP-based PostgREST calls (which `supabase-py` wraps).

## Configuration

The connection manager reads the `DATABASE_URL` from the application settings (loaded from `.env`).

```env
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname
```

## Key Components

### 1. Engine & Pooling
Located in `backend/app/database/core.py`.
- **Pool Size**: 20 connections maintained open.
- **Max Overflow**: 10 temporary connections allowed during high load.
- **Pool Timeout**: 30 seconds wait time before raising an error.
- **Pre-Ping**: Checked before checkout to ensure connection health.

### 2. Dependency Injection
Use `get_db` in FastAPI routes or other async functions to get a session.

```python
from backend.app.database.core import get_db
from sqlalchemy import text

@router.get("/items")
async def read_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM items"))
    return result.mappings().all()
```

The `get_db` generator ensures:
- A session is created from the pool.
- The session is passed to the function.
- The session is **automatically closed** after the function completes (even on error).
- If an error occurs, the transaction is rolled back.

## Testing
Unit tests in `tests/test_db_pool.py` verify:
- Pool configuration.
- Concurrent session acquisition (simulating 50+ parallel requests).
- Proper cleanup (rollback and close) on errors.
