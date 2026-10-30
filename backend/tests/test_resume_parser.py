import os
from pathlib import Path
import pytest
from app.services.resume_parser import ResumeParserService
from app.schemas.resume import ResumeParsedData

SAMPLE_RESUME_TEXT = """
Akshay Sharma
Full-Stack Software Engineer
Bangalore, Karnataka
akshaysharma2aug@gmail.com
+91 8088498674

PROFESSIONAL SUMMARY
Results-driven Full-Stack Software Engineer with 5+ years of experience designing and deploying scalable enterprise
applications using Java, Spring Boot, Microservices, and ReactJS. Proven expertise in cloud deployments (AWS, Azure),
and CI/CD DevOps pipelines.

PROFESSIONAL EXPERIENCE
Senior Software - Full Stack Engineer | TCS
May 2026 – Present | Bangalore
Developed full-stack enterprise applications integrating Spring Boot microservices with interactive ReactJS frontends.
Deployed scalable containerized applications onto AWS Cloud using automated CI/CD pipelines.

Software Engineer - Java | Accenture
Nov 2024 – Apr 2026 | Bangalore
Designed and built enterprise backend services using Java and Spring Boot.
Managed cloud infrastructure and application lifecycles on Azure Cloud.

KEY PROJECTS
PageTurn Bookstore – Cloud Native DevOps Platform
Java, Spring Boot, React, AWS, K8s
Designed a microservices-based e-commerce platform.

TECHNICAL SKILLS
Languages: Java, JavaScript (ES6+), SQL
Backend: Spring Boot, Spring MVC, Microservices, REST APIs
Cloud: AWS, Azure, Docker, Kubernetes, Jenkins, Terraform, CI/CD
Databases: MySQL, MongoDB, Kafka

EDUCATION & CERTIFICATIONS
B.Tech - Electrical & Electronics Engineering | Guru Gobind Science / GGSIPU (2015–2019) – CGPA: 8.2/10
Certifications: AWS Certified Solutions Architect – Associate | Infosys Java Readability Certification
"""


def test_resume_parser_extracts_contact_info():
    name, headline, email, phone = ResumeParserService.extract_contact_info(SAMPLE_RESUME_TEXT)
    assert name == "Akshay Sharma"
    assert "Full-Stack Software Engineer" in headline
    assert email == "akshaysharma2aug@gmail.com"
    assert phone is not None


def test_resume_parser_extracts_skills():
    skills, categorized = ResumeParserService.extract_skills(SAMPLE_RESUME_TEXT)
    assert "Java" in skills
    assert "Spring Boot" in skills
    assert "ReactJS" in skills
    assert "Microservices" in skills
    assert "AWS" in skills
    assert "Docker" in skills
    assert "Kubernetes" in skills
    assert "Kafka" in skills
    assert len(categorized) >= 3


def test_resume_parser_experience_years():
    years = ResumeParserService.extract_experience_years(SAMPLE_RESUME_TEXT)
    assert years == 5.0


def test_resume_parser_full_model_validation():
    parsed = ResumeParserService.parse_resume(SAMPLE_RESUME_TEXT, "sample.pdf")
    assert isinstance(parsed, ResumeParsedData)
    assert parsed.full_name == "Akshay Sharma"
    assert len(parsed.experience) >= 2
    assert any("TCS" in exp.company for exp in parsed.experience)
    assert any("Accenture" in exp.company for exp in parsed.experience)
    assert any("AWS Certified" in c for c in parsed.certifications)


def test_real_pdf_parsing_if_available():
    root_pdf = Path(__file__).resolve().parent.parent.parent / "Full_Stack_Software_Engineer.pdf"
    if root_pdf.exists():
        text = ResumeParserService.extract_text_from_pdf(root_pdf.read_bytes())
        assert len(text) > 100
        parsed = ResumeParserService.parse_resume(text, root_pdf.name)
        assert parsed.full_name == "Akshay Sharma"
        assert "Java" in parsed.skills
        assert "Spring Boot" in parsed.skills

