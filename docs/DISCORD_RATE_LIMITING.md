Discord Rate Limiting System
Overview

This implementation adds robust Discord API rate limit handling with:

Automatic 429 detection

Exponential backoff retry logic (2^n + jitter)

Configurable maximum retry attempts (default: 3)

Redis-based distributed rate limit tracking

Per-channel bucket isolation

Command queueing using per-channel asyncio locks

Minimal performance overhead when not rate limited

This ensures improved bot resilience and production readiness.

Architecture

Flow:

User Message
→ DiscordBot
→ Per-channel Lock (Queueing)
→ DiscordRateLimiter
→ Redis (Bucket Tracking)
→ Discord API

Retry Mechanism

When a 429 HTTPException occurs:

Extract retry_after from Discord response

Store reset timestamp in Redis:

discord_ratelimit:<channel_id>

Calculate exponential backoff:

delay = (2^attempt × retry_after) + jitter

Retry up to max_retries times (default = 3)

If retries are exhausted, an exception is raised.

Distributed Rate Limit Tracking

Redis is used to coordinate rate limits across multiple bot instances.

Key format:

discord_ratelimit:<bucket>

Where:

bucket = Discord channel ID

This ensures:

Only the affected channel waits

Other channels continue operating normally

Safe multi-instance deployments

Command Queueing

Per-channel asyncio.Lock ensures:

Sequential message processing per channel

No concurrent retry storms

Clean isolation of channel traffic

This acts as a lightweight queue system.

Performance Characteristics

When NOT rate limited:

Single Redis GET

No artificial sleep

Direct execution

Negligible overhead (<1ms)

When rate limited:

Controlled exponential backoff

Shared distributed coordination via Redis

Configuration

Environment variable required:

REDIS_URL=redis://localhost:6379

Ensure Redis service is running before starting the bot.

Testing

Unit tests cover:

Successful execution without rate limit

Retry behavior on 429

Exponential backoff growth

Maximum retry exhaustion

Redis key storage on 429

Delay enforcement

Run tests:

pytest tests/test_rate_limiter.py

Future Improvements

Per-endpoint bucket parsing from Discord headers

Prometheus metrics integration

Advanced distributed worker queue

Rate limit analytics dashboard

Issue Reference

Implements Issue #284

Adds production-grade Discord rate limiting with exponential backoff and distributed coordination.