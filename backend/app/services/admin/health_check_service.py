import logging
import asyncio
import aiohttp
from urllib.parse import urlparse
from datetime import datetime, timezone
from typing import Dict, Any, List
from dataclasses import dataclass, field

from app.core.config import settings
from app.database.supabase.client import get_supabase_client

logger = logging.getLogger(__name__)


@dataclass
class ServiceHealth:
    name: str
    status: str  # healthy, unhealthy, degraded
    latency_ms: float
    error: str = ""


@dataclass
class SystemHealth:
    overall_status: str
    services: List[ServiceHealth] = field(default_factory=list)
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class HealthCheckService:
    def __init__(self, queue_manager=None):
        self.queue_manager = queue_manager
        self.timeout = 10.0

    async def check_supabase(self) -> ServiceHealth:
        start = datetime.now()
        try:
            supabase = get_supabase_client()
            await asyncio.wait_for(
                supabase.table("users").select("id").limit(1).execute(),
                timeout=self.timeout
            )
            latency = (datetime.now() - start).total_seconds() * 1000
            return ServiceHealth("Supabase", "healthy", round(latency, 2))
        except asyncio.TimeoutError:
            return ServiceHealth("Supabase", "unhealthy", self.timeout * 1000, "Timeout")
        except Exception as e:
            latency = (datetime.now() - start).total_seconds() * 1000
            return ServiceHealth("Supabase", "unhealthy", round(latency, 2), str(e)[:100])

    async def check_rabbitmq(self) -> ServiceHealth:
        start = datetime.now()
        try:
            if not self.queue_manager or not self.queue_manager.connection:
                return ServiceHealth("RabbitMQ", "unhealthy", 0, "Not connected")

            if self.queue_manager.connection.is_closed:
                return ServiceHealth("RabbitMQ", "unhealthy", 0, "Connection closed")

            latency = (datetime.now() - start).total_seconds() * 1000
            return ServiceHealth("RabbitMQ", "healthy", round(latency, 2))
        except Exception as e:
            latency = (datetime.now() - start).total_seconds() * 1000
            return ServiceHealth("RabbitMQ", "unhealthy", round(latency, 2), str(e)[:100])

    async def check_weaviate(self) -> ServiceHealth:
        start = datetime.now()
        try:
            weaviate_url = getattr(settings, 'weaviate_url', 'http://localhost:8080')
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{weaviate_url}/v1/.well-known/ready",
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as resp:
                    latency = (datetime.now() - start).total_seconds() * 1000
                    if resp.status == 200:
                        return ServiceHealth("Weaviate", "healthy", round(latency, 2))
                    return ServiceHealth("Weaviate", "unhealthy", round(latency, 2), f"Status {resp.status}")
        except asyncio.TimeoutError:
            return ServiceHealth("Weaviate", "unhealthy", self.timeout * 1000, "Timeout")
        except Exception as e:
            latency = (datetime.now() - start).total_seconds() * 1000
            return ServiceHealth("Weaviate", "unhealthy", round(latency, 2), str(e)[:100])

    async def check_falkordb(self) -> ServiceHealth:
        start = datetime.now()
        client = None
        try:
            import redis.asyncio as redis

            falkor_url = getattr(settings, 'falkordb_url', None) or "redis://localhost:6379"

            # Normalize non-redis URLs (e.g., http://localhost:6379) to redis://
            parsed = urlparse(falkor_url)
            if parsed.scheme not in ("redis", "rediss"):
                host = parsed.hostname or "localhost"
                port = parsed.port or 6379
                falkor_url = f"redis://{host}:{port}"

            client = redis.from_url(falkor_url, decode_responses=True)
            pong = await asyncio.wait_for(client.ping(), timeout=self.timeout)

            latency = (datetime.now() - start).total_seconds() * 1000
            if pong is True or pong == "PONG":
                return ServiceHealth("FalkorDB", "healthy", round(latency, 2))
            return ServiceHealth("FalkorDB", "degraded", round(latency, 2), f"Unexpected ping reply: {pong}")
        except asyncio.TimeoutError:
            return ServiceHealth("FalkorDB", "degraded", self.timeout * 1000, "Timeout")
        except Exception as e:
            latency = (datetime.now() - start).total_seconds() * 1000
            return ServiceHealth("FalkorDB", "degraded", round(latency, 2), str(e)[:50])
        finally:
            if client is not None:
                try:
                    await client.aclose()
                except Exception:
                    try:
                        await client.close()
                    except Exception:
                        pass

    async def check_gemini_api(self) -> ServiceHealth:
        start = datetime.now()
        try:
            if not getattr(settings, 'gemini_api_key', None):
                return ServiceHealth("Gemini API", "unhealthy", 0, "No API key")

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://generativelanguage.googleapis.com/v1/models",
                    params={"key": settings.gemini_api_key},
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as resp:
                    latency = (datetime.now() - start).total_seconds() * 1000
                    if resp.status == 200:
                        return ServiceHealth("Gemini API", "healthy", round(latency, 2))
                    return ServiceHealth("Gemini API", "unhealthy", round(latency, 2), f"Status {resp.status}")
        except asyncio.TimeoutError:
            return ServiceHealth("Gemini API", "degraded", self.timeout * 1000, "Timeout")
        except Exception as e:
            latency = (datetime.now() - start).total_seconds() * 1000
            return ServiceHealth("Gemini API", "unhealthy", round(latency, 2), str(e)[:100])

    async def get_all_health(self) -> SystemHealth:
        checks = await asyncio.gather(
            self.check_supabase(),
            self.check_rabbitmq(),
            self.check_weaviate(),
            self.check_falkordb(),
            self.check_gemini_api(),
            return_exceptions=True
        )

        services = []
        for check in checks:
            if isinstance(check, Exception):
                services.append(ServiceHealth("Unknown", "unhealthy", 0, str(check)[:100]))
            else:
                services.append(check)

        unhealthy = sum(1 for s in services if s.status == "unhealthy")
        degraded = sum(1 for s in services if s.status == "degraded")

        if unhealthy > 0:
            overall = "unhealthy"
        elif degraded > 0:
            overall = "degraded"
        else:
            overall = "healthy"

        return SystemHealth(overall_status=overall, services=services)
