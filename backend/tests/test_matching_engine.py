import json
import pytest
from app.services.job_matcher import JobMatcherService
from app.schemas.resume import ResumeParsedData, ExperienceItem, EducationItem
from app.models.job import Job


@pytest.fixture
def candidate_resume():
    return ResumeParsedData(
        full_name="Akshay Sharma",
        headline="Full-Stack Software Engineer",
        email="akshay@test.com",
        location="Bengaluru, Karnataka, India",
        years_of_experience=5.0,
        skills=["Java", "Spring Boot", "Microservices", "REST APIs", "ReactJS", "AWS", "Docker", "Kafka", "SQL", "MySQL"],
        experience=[
            ExperienceItem(title="Senior Software Engineer", company="TCS", dates="2026-Present", is_current=True)
        ],
        education=[EducationItem(degree="B.Tech", institution="GGSIPU", year="2019")],
        certifications=["AWS Certified Solutions Architect – Associate"],
    )


def test_calculate_skill_score_high_overlap(candidate_resume):
    score, matched, missing = JobMatcherService.calculate_skill_score(
        candidate_skills=candidate_resume.skills,
        required_skills=["Java", "Spring Boot", "Microservices", "AWS"],
        preferred_skills=["Docker", "Kafka"],
    )
    assert score == 100.0
    assert len(missing.required) == 0
    assert len(matched) == 6


def test_calculate_skill_score_missing_skills(candidate_resume):
    score, matched, missing = JobMatcherService.calculate_skill_score(
        candidate_skills=candidate_resume.skills,
        required_skills=["Java", "C++", "Rust"],
        preferred_skills=["Kafka"],
    )
    assert score < 70.0
    assert "C++" in missing.required
    assert "Rust" in missing.required


def test_experience_score_ranges(candidate_resume):
    # Candidate has 5.0 years
    # Ideal range 4 to 8 years
    score1, note1 = JobMatcherService.calculate_experience_score(candidate_resume.years_of_experience, 4.0, 8.0)
    assert score1 == 100.0

    # Overqualified: target 1-2 years
    score2, note2 = JobMatcherService.calculate_experience_score(candidate_resume.years_of_experience, 1.0, 2.0)
    assert score2 >= 75.0

    # Underqualified: target 10-15 years
    score3, note3 = JobMatcherService.calculate_experience_score(candidate_resume.years_of_experience, 10.0, 15.0)
    assert score3 < 70.0


def test_evaluate_match_overall(candidate_resume):
    job = Job(
        title="Senior Java Developer",
        company="Target Tech",
        description="Looking for Senior Java Developer with Spring Boot, Microservices, ReactJS, AWS, and Kafka.",
        location="Bengaluru, Karnataka, India",
        work_mode="Hybrid",
        required_skills_json=json.dumps(["Java", "Spring Boot", "Microservices", "AWS"]),
        preferred_skills_json=json.dumps(["ReactJS", "Kafka", "Docker"]),
        minimum_experience=5.0,
        maximum_experience=8.0,
    )
    res = JobMatcherService.evaluate_match(
        parsed_resume=candidate_resume,
        resume_raw_text="Java Spring Boot Microservices ReactJS AWS Kafka Docker Kubernetes 5+ years experience",
        job=job,
    )
    assert res["overall_score"] >= 80.0
    assert "Java" in res["matched_skills"]
    assert len(res["explanation"]["strengths"]) >= 1

