from app.core.config import settings
from supabase._async.client import AsyncClient

supabase_client: AsyncClient = AsyncClient(
    settings.supabase_url,
    settings.supabase_key
)

def get_supabase_client() -> AsyncClient:
    """
    Returns a shared asynchronous Supabase client instance.
    """
    return supabase_client
