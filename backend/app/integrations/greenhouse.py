import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import httpx
from app.integrations.base import BaseJobSource
from app.core.config import settings

logger = logging.getLogger(__name__)


class GreenhouseJobSource(BaseJobSource):
    source_name = "greenhouse"

    def __init__(self):
        super().__init__()
        self.board_token = settings.GREENHOUSE_BOARD_TOKEN or "stripe"  # Sample active tech company board

    def get_connection_status(self) -> Dict[str, Any]:
        return {
            "source": "greenhouse",
            "status": "connected" if self.board_token else "unconfigured",
            "is_mock": False,
            "message": f"Greenhouse Public Board API active (board: '{self.board_token}').",
            "required_permissions": ["Public Board Token"],
            "last_sync": self.last_sync_time.isoformat() if self.last_sync_time else None,
            "total_fetched": self.total_fetched,
        }

    async def fetch_jobs(
        self,
        keywords: List[str],
        locations: List[str],
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        if not self.board_token:
            return []

        url = f"https://boards-api.greenhouse.io/v1/boards/{self.board_token}/jobs?content=true"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    jobs_raw = data.get("jobs", [])
                    results = []
                    lower_kw = [k.lower() for k in keywords]
                    for j in jobs_raw:
                        title = j.get("title", "")
                        desc = j.get("content", "")
                        loc = j.get("location", {}).get("name", "")
                        # Filter by keyword if any
                        if lower_kw and not any(k in title.lower() or k in desc.lower() for k in lower_kw):
                            continue
                        results.append({
                            "source": "greenhouse",
                            "external_job_id": str(j.get("id")),
                            "title": title,
                            "company": self.board_token.capitalize(),
                            "description": desc,
                            "location": loc,
                            "job_url": j.get("absolute_url"),
                            "application_url": j.get("absolute_url"),
                        })
                        if len(results) >= limit:
                            break
                    self.last_sync_time = datetime.now(timezone.utc)
                    self.total_fetched += len(results)
                    return results
                else:
                    self.last_error = f"Greenhouse HTTP {resp.status_code}"
                    return []
        except Exception as e:
            self.last_error = str(e)
            return []

