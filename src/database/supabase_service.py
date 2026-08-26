import logging
from typing import List, Dict, Any, Optional
from supabase import create_client, Client

from src.core.config import settings

logger = logging.getLogger(__name__)

class SupabaseService:
    """Service layer for Supabase database operations."""
    
    def __init__(self):
        url: str = settings.SUPABASE_URL
        key: str = settings.SUPABASE_KEY
        if not url or not key or url.startswith("https://your-project"):
            logger.warning("SUPABASE_URL or SUPABASE_KEY is missing or invalid. Supabase functions will fail.")
            self.client: Optional[Client] = None
        else:
            self.client: Client = create_client(url, key)
            logger.info("Supabase client initialized successfully.")
        self._is_loaded = True
        
    def query_rpc(self, rpc_name: str, params: Dict[str, Any]) -> Any:
        """Call a Postgres function (RPC) via Supabase REST API."""
        if not self.client:
            raise ValueError("Supabase client not initialized")
            
        try:
            response = self.client.rpc(rpc_name, params).execute()
            return response.data
        except Exception as e:
            logger.error(f"Supabase RPC error ({rpc_name}): {e}")
            raise

    def query_table(self, table_name: str, filters: Dict[str, Any] = None, select: str = "*") -> List[Dict[str, Any]]:
        """Query a table directly."""
        if not self.client:
            raise ValueError("Supabase client not initialized")
            
        try:
            query = self.client.table(table_name).select(select)
            if filters:
                for k, v in filters.items():
                    query = query.eq(k, v)
            response = query.execute()
            return response.data
        except Exception as e:
            logger.error(f"Supabase Table query error ({table_name}): {e}")
            raise
