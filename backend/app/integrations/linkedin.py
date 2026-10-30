import asyncio
from datetime import datetime, timezone
import logging
import re
from typing import Dict, List, Optional, Any
import httpx
from lxml import html

from app.integrations.base import BaseJobSource
from app.core.config import settings

logger = logging.getLogger(__name__)

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)


class LinkedInJobSource(BaseJobSource):
    source_name = "linkedin"

    def __init__(self, timeout: float = 12.0, max_retries: int = 2):
        super().__init__(timeout=timeout, max_retries=max_retries)
        self.client_id = settings.LINKEDIN_CLIENT_ID
        self.client_secret = settings.LINKEDIN_CLIENT_SECRET
        self.api_token = settings.LINKEDIN_API_TOKEN
        self.headers = {
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

    @property
    def is_configured(self) -> bool:
        # Real-time web scraping is always ready and requires no enterprise credentials
        return True

    def get_connection_status(self) -> Dict[str, Any]:
        has_api_keys = bool(self.api_token or (self.client_id and self.client_secret))
        if has_api_keys:
            message = "LinkedIn live integration active (Real-time Web Scraper + Official API credentials configured)."
        else:
            message = "Real-time LinkedIn Guest Scraping Engine active (live postings fetched directly from LinkedIn)."

        return {
            "source": "linkedin",
            "status": "connected",
            "is_mock": False,
            "message": message,
            "required_permissions": [
                "Real-time Guest Web Scraping (Active)",
                "Official API Credentials (Optional)",
            ],
            "last_sync": self.last_sync_time.isoformat() if self.last_sync_time else None,
            "total_fetched": self.total_fetched,
            "manual_import_supported": True,
        }

    async def _fetch_official_api(
        self,
        keywords: List[str],
        locations: List[str],
        limit: int = 25,
    ) -> List[Dict[str, Any]]:
        """Optional query via official LinkedIn API if credentials are provided."""
        if not self.api_token:
            return []

        url = "https://api.linkedin.com/v2/jobSearch"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "X-Restli-Protocol-Version": "2.0.0",
        }
        params = {
            "keywords": " ".join(keywords[:2]),
            "location": locations[0] if locations else "Bengaluru",
            "count": min(limit, 25),
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url, headers=headers, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    elements = data.get("elements", [])
                    results = []
                    for el in elements:
                        results.append({
                            "source": "linkedin",
                            "external_job_id": str(el.get("id")),
                            "title": el.get("title", ""),
                            "company": el.get("companyName", ""),
                            "description": el.get("description", {}).get("text", ""),
                            "location": el.get("formattedLocation", "Bengaluru, Karnataka, India"),
                            "job_url": f"https://www.linkedin.com/jobs/view/{el.get('id')}",
                            "application_url": el.get("applyUrl") or f"https://www.linkedin.com/jobs/view/{el.get('id')}",
                        })
                    return results
                else:
                    logger.warning(f"LinkedIn Official API error: {resp.status_code} - {resp.text}")
                    return []
        except Exception as e:
            logger.warning(f"LinkedIn Official API request failed: {e}")
            return []

    async def _fetch_job_detail(
        self,
        client: httpx.AsyncClient,
        job_id: str,
        sem: asyncio.Semaphore,
    ) -> Dict[str, Any]:
        """Fetches detailed job description and criteria from the LinkedIn guest job API."""
        url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
        async with sem:
            try:
                resp = await client.get(url, headers=self.headers, timeout=self.timeout)
                if resp.status_code == 200:
                    tree = html.fromstring(resp.text)
                    desc_elements = tree.xpath("//div[contains(@class, 'show-more-less-html__markup')]")
                    description = ""
                    if desc_elements:
                        desc_el = desc_elements[0]
                        # Preserve linebreaks and bullet points
                        for br in desc_el.xpath(".//br"):
                            br.tail = "\n" + (br.tail or "")
                        for li in desc_el.xpath(".//li"):
                            li.text = "• " + (li.text or "")
                            li.tail = "\n" + (li.tail or "")
                        raw_text = desc_el.text_content().strip()
                        description = re.sub(r"\n\s*\n+", "\n\n", raw_text)

                    employment_type = "Full-time"
                    seniority_level = None
                    criteria_items = tree.xpath("//li[contains(@class, 'description__job-criteria-item')]")
                    for item in criteria_items:
                        hdr = item.xpath(".//h3")
                        val = item.xpath(".//span")
                        if hdr and val:
                            h_text = hdr[0].text_content().strip().lower()
                            v_text = val[0].text_content().strip()
                            if "employment type" in h_text:
                                employment_type = v_text
                            elif "seniority level" in h_text:
                                seniority_level = v_text

                    return {
                        "description": description,
                        "employment_type": employment_type,
                        "seniority_level": seniority_level,
                    }
                else:
                    logger.debug(f"LinkedIn detail fetch status {resp.status_code} for job {job_id}")
            except Exception as e:
                logger.debug(f"LinkedIn detail fetch error for {job_id}: {e}")

        return {"description": "", "employment_type": "Full-time", "seniority_level": None}

    async def fetch_jobs(
        self,
        keywords: List[str],
        locations: List[str],
        limit: int = 30,
    ) -> List[Dict[str, Any]]:
        """
        Scrapes real-time jobs from LinkedIn public guest endpoint.
        Falls back to official API if configured and scraper yields no results.
        """
        collected_jobs: Dict[str, Dict[str, Any]] = {}
        target_kw = keywords if keywords else ["Senior Java Developer", "Java Developer"]
        target_locs = locations if locations else ["Bengaluru, Karnataka, India"]
        search_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                for kw in target_kw[:3]:
                    if len(collected_jobs) >= limit:
                        break
                    for loc in target_locs[:2]:
                        if len(collected_jobs) >= limit:
                            break
                        start = 0
                        # Paginate up to 3 pages per keyword/location combo
                        while len(collected_jobs) < limit and start < 30:
                            params = {
                                "keywords": kw,
                                "location": loc,
                                "start": start,
                            }
                            try:
                                resp = await client.get(search_url, headers=self.headers, params=params)
                                if resp.status_code != 200:
                                    logger.warning(
                                        f"LinkedIn search returned HTTP {resp.status_code} for '{kw}' in '{loc}' (start={start})"
                                    )
                                    break

                                tree = html.fromstring(resp.text)
                                cards = tree.xpath("//div[contains(@class, 'base-card')]")
                                if not cards:
                                    # Alternate xpath if LinkedIn structure differs
                                    cards = tree.xpath("//li")

                                if not cards:
                                    break

                                for card in cards:
                                    urn = card.xpath("./@data-entity-urn") or card.xpath(".//div/@data-entity-urn")
                                    job_id = urn[0].split(":")[-1] if urn else ""

                                    link_el = card.xpath(".//a[contains(@class, 'base-card__full-link')]")
                                    job_link = ""
                                    if link_el:
                                        raw_href = link_el[0].get("href", "")
                                        job_link = raw_href.split("?")[0] if raw_href else ""

                                    if not job_id and job_link:
                                        id_match = re.search(r"(\d{8,})", job_link)
                                        if id_match:
                                            job_id = id_match.group(1)

                                    if not job_id or job_id in collected_jobs:
                                        continue

                                    title_el = card.xpath(".//h3[contains(@class, 'base-search-card__title')]")
                                    company_el = card.xpath(".//h4[contains(@class, 'base-search-card__subtitle')]")
                                    loc_el = card.xpath(".//span[contains(@class, 'job-search-card__location')]")
                                    time_el = card.xpath(".//time")

                                    title = title_el[0].text_content().strip() if title_el else ""
                                    company = company_el[0].text_content().strip() if company_el else ""
                                    job_location = loc_el[0].text_content().strip() if loc_el else loc
                                    
                                    if not title:
                                        continue

                                    clean_link = job_link or f"https://www.linkedin.com/jobs/view/{job_id}"

                                    posted_dt = datetime.now(timezone.utc)
                                    if time_el:
                                        raw_date = time_el[0].get("datetime")
                                        if raw_date:
                                            try:
                                                posted_dt = datetime.fromisoformat(raw_date).replace(tzinfo=timezone.utc)
                                            except Exception:
                                                pass

                                    collected_jobs[job_id] = {
                                        "source": "linkedin",
                                        "external_job_id": job_id,
                                        "title": title,
                                        "company": company,
                                        "location": job_location,
                                        "job_url": clean_link,
                                        "application_url": clean_link,
                                        "posted_at": posted_dt,
                                        "description": "",
                                        "employment_type": "Full-time",
                                    }

                                    if len(collected_jobs) >= limit:
                                        break

                                start += 10
                            except Exception as e:
                                logger.warning(f"Error scraping LinkedIn search page start={start}: {e}")
                                break

                # Concurrently fetch detailed job descriptions for all discovered listings
                if collected_jobs:
                    sem = asyncio.Semaphore(4)
                    detail_tasks = [
                        self._fetch_job_detail(client, jid, sem)
                        for jid in collected_jobs.keys()
                    ]
                    details = await asyncio.gather(*detail_tasks, return_exceptions=True)

                    for (jid, job), det in zip(collected_jobs.items(), details):
                        if isinstance(det, dict) and det.get("description"):
                            job["description"] = det["description"]
                            if det.get("employment_type"):
                                job["employment_type"] = det["employment_type"]
                            if det.get("seniority_level"):
                                job["seniority_level"] = det["seniority_level"]
                        else:
                            # Fallback informative description if detail fetch was rate-limited or blank
                            job["description"] = (
                                f"{job['title']} at {job['company']}. Location: {job['location']}. "
                                f"Live posting discovered via real-time LinkedIn search. "
                                f"Apply and view complete specifications at {job['job_url']}"
                            )

        except Exception as e:
            self.last_error = str(e)
            logger.error(f"LinkedIn real-time scraping encountered error: {e}")

        # If scraper gathered no jobs (e.g. rate limit / network block) and official API is configured, try official API
        if not collected_jobs and (self.api_token or (self.client_id and self.client_secret)):
            logger.info("Attempting fallback to official LinkedIn API...")
            api_results = await self._fetch_official_api(keywords, locations, limit=limit)
            for j in api_results:
                collected_jobs[j["external_job_id"]] = j

        results = list(collected_jobs.values())
        if results:
            self.last_sync_time = datetime.now(timezone.utc)
            self.total_fetched += len(results)
            logger.info(f"LinkedIn real-time scraper successfully retrieved {len(results)} live jobs.")

        return results
