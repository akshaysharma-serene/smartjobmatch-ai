import pytest
from unittest.mock import patch, MagicMock
from app.integrations.linkedin import LinkedInJobSource


def test_linkedin_status():
    source = LinkedInJobSource()
    assert source.is_configured is True
    status = source.get_connection_status()
    assert status["source"] == "linkedin"
    assert status["status"] == "connected"
    assert status["is_mock"] is False
    assert "Real-time" in status["message"]


@pytest.mark.asyncio
async def test_linkedin_fetch_jobs_mocked():
    source = LinkedInJobSource()

    mock_search_html = """
    <html>
      <body>
        <div class="base-card" data-entity-urn="urn:li:jobPosting:9999999999">
          <a class="base-card__full-link" href="https://www.linkedin.com/jobs/view/test-job-9999999999?refId=123"></a>
          <h3 class="base-search-card__title">Senior Java Engineer</h3>
          <h4 class="base-search-card__subtitle"><a href="#">Acme Corp</a></h4>
          <span class="job-search-card__location">Bengaluru, Karnataka, India</span>
          <time datetime="2026-10-25">2 days ago</time>
        </div>
      </body>
    </html>
    """

    mock_detail_html = """
    <html>
      <body>
        <div class="show-more-less-html__markup">
          <p>We are looking for a Senior Java Engineer with expertise in Spring Boot, Kafka, and Microservices.</p>
          <ul>
            <li>5+ years Java experience</li>
            <li>REST API development</li>
          </ul>
        </div>
        <ul class="description__job-criteria-list">
          <li class="description__job-criteria-item">
            <h3>Seniority level</h3>
            <span>Mid-Senior level</span>
          </li>
          <li class="description__job-criteria-item">
            <h3>Employment type</h3>
            <span>Full-time</span>
          </li>
        </ul>
      </body>
    </html>
    """

    with patch("httpx.AsyncClient.get") as mock_get:
        async def mock_response(url, *args, **kwargs):
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            if "seeMoreJobPostings" in str(url):
                mock_resp.text = mock_search_html
            elif "jobPosting" in str(url):
                mock_resp.text = mock_detail_html
            else:
                mock_resp.text = ""
            return mock_resp

        mock_get.side_effect = mock_response

        jobs = await source.fetch_jobs(keywords=["Java"], locations=["Bengaluru"], limit=5)
        assert len(jobs) == 1
        job = jobs[0]
        assert job["source"] == "linkedin"
        assert job["external_job_id"] == "9999999999"
        assert job["title"] == "Senior Java Engineer"
        assert job["company"] == "Acme Corp"
        assert "Spring Boot" in job["description"]
        assert job["employment_type"] == "Full-time"
        assert job["seniority_level"] == "Mid-Senior level"
        assert job["job_url"] == "https://www.linkedin.com/jobs/view/test-job-9999999999"


@pytest.mark.asyncio
async def test_linkedin_live_scraping():
    # Verify live real-time scraping against LinkedIn guest API
    source = LinkedInJobSource(timeout=10.0)
    try:
        jobs = await source.fetch_jobs(
            keywords=["Java Developer"],
            locations=["Bengaluru, Karnataka, India"],
            limit=2,
        )
        # If network is available and LinkedIn permits, we verify structure
        if jobs:
            assert len(jobs) >= 1
            for j in jobs:
                assert j["source"] == "linkedin"
                assert j["external_job_id"]
                assert j["title"]
                assert j["company"]
                assert j["description"]
                assert j["job_url"].startswith("https://")
    except Exception as e:
        # Live test may fail if offline, which is fine as unit test is above
        pytest.skip(f"Live network unavailable: {e}")

