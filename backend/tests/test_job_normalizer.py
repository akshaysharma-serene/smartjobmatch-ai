from app.services.job_normalizer import JobNormalizerService


def test_calculate_content_hash():
    h1 = JobNormalizerService.calculate_content_hash(
        "Senior Java Developer", "Target Tech", "Building microservices with Spring Boot"
    )
    h2 = JobNormalizerService.calculate_content_hash(
        "senior java developer  ", "TARGET TECH", "building microservices with spring boot  "
    )
    assert h1 == h2
    assert len(h1) == 64


def test_extract_skills_from_text():
    text = "We require strong Java, Spring Boot, React, and AWS experience with Kafka and Docker."
    skills = JobNormalizerService.extract_skills_from_text(text)
    assert "Java" in skills
    assert "Spring Boot" in skills
    assert "ReactJS" in skills
    assert "AWS" in skills
    assert "Kafka" in skills
    assert "Docker" in skills


def test_extract_experience_requirements():
    min_exp, max_exp = JobNormalizerService.extract_experience_requirements("5 to 8 years experience required.")
    assert min_exp == 5.0
    assert max_exp == 8.0

    min_exp2, max_exp2 = JobNormalizerService.extract_experience_requirements("Candidate must have 5+ years experience.")
    assert min_exp2 == 5.0
    assert max_exp2 is None


def test_infer_work_mode():
    assert JobNormalizerService.infer_work_mode("This is a 100% remote position") == "Remote"
    assert JobNormalizerService.infer_work_mode("Hybrid setup in our Bengaluru office") == "Hybrid"
    assert JobNormalizerService.infer_work_mode("Work on site at headquarters") == "On-site"


def test_normalize_job_dict():
    raw = {
        "title": "Java Backend Engineer",
        "company": "Amazon",
        "description": "5+ years developing Java Spring Boot microservices on AWS.",
        "location": "Bangalore",
    }
    normalized = JobNormalizerService.normalize_job_dict(raw)
    assert normalized["title"] == "Java Backend Engineer"
    assert normalized["location"] == "Bengaluru, Karnataka, India"
    assert normalized["minimum_experience"] == 5.0
    assert "Java" in normalized["required_skills"]
    assert len(normalized["content_hash"]) == 64

