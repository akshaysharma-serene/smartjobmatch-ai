import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import httpx
from app.integrations.base import BaseJobSource
from app.core.config import settings

logger = logging.getLogger(__name__)


class LeverJobSource(BaseJobSource):
    source_name = "lever"

    def __init__(self):
        super().__init__()
        self.site_name = settings.LEVER_SITE_NAME or "netflix"

    def get_connection_status(self) -> Dict[str, Any]:
        return {
            "source": "lever",
            "status": "connected" if self.site_name else "unconfigured",
            "is_mock": False,
            "message": f"Lever Public Postings API active (site: '{self.site_name}').",
            "required_permissions": ["Company Public Site Handle"],
            "last_sync": self.last_sync_time.isoformat() if self.last_sync_time else None,
            "total_fetched": self.total_fetched,
        }

    async def fetch_jobs(
        self,
        keywords: List[str],
        locations: List[str],
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        if not self.site_name:
            return []

        url = f"https://api.lever.co/v0/postings/{self.site_name}?mode=json"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    jobs_raw = resp.json()
                    results = []
                    lower_kw = [k.lower() for k in keywords]
                    for j in jobs_raw:
                        title = j.get("text", "")
                        desc = j.get("descriptionPlain", "") or j.get("description", "")
                        categories = j.get("categories", {})
                        loc = categories.get("location", "")
                        work_type = categories.get("commitment", "Full-time")

                        if lower_kw and not any(k in title.lower() or k in desc.lower() for k in lower_kw):
                            continue

                        results.append({
                            "source": "lever",
                            "external_job_id": str(j.get("id")),
                            "title": title,
                            "company": self.site_name.capitalize(),
                            "description": desc,
                            "location": loc,
                            "employment_type": work_type,
                            "job_url": j.get("hostedUrl"),
                            "application_url": j.get("applyUrl") or j.get("hostedUrl"),
                        })
                        if len(results) >= limit:
                            break
                    self.last_sync_time = datetime.now(timezone.utc)
                    self.total_fetched += len(results)
                    return results
                else:
                    self.last_error = f"Lever HTTP {resp.status_code}"
                    return []
        except Exception as e:
            self.last_error = str(e)
            return []

