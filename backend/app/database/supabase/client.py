from app.core.config import settings
from supabase._async.client import AsyncClient

_client: AsyncClient | None = None

def get_supabase_client() -> AsyncClient:
    global _client
    """
    Returns a shared asynchronous Supabase client instance.
    """
    if _client is None:
        if not settings.supabase_url or not settings.supabase_key:
            missing = []
            if not settings.supabase_url:
                missing.append("SUPABASE_URL")
            if not settings.supabase_key:
                missing.append("SUPABASE_KEY")
            raise RuntimeError(
                f"Supabase misconfigured. Missing: {', '.join(missing)}"
            )
        _client = AsyncClient(
            settings.supabase_url,
            settings.supabase_key,
        )
    return _client
