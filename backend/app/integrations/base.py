from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime


class BaseJobSource(ABC):
    source_name: str
    is_live_authorized: bool = False

    def __init__(self, timeout: float = 10.0, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.last_sync_time: Optional[datetime] = None
        self.last_error: Optional[str] = None
        self.total_fetched: int = 0

    @abstractmethod
    def get_connection_status(self) -> Dict[str, Any]:
        """Returns connection status, credential health, and configuration notes."""
        pass

    @abstractmethod
    async def fetch_jobs(
        self,
        keywords: List[str],
        locations: List[str],
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Fetches jobs from the source, returning raw job dictionaries."""
        pass

