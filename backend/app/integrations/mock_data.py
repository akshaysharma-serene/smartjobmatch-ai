import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any
from app.integrations.base import BaseJobSource

MOCK_JOBS_FIXTURES: List[Dict[str, Any]] = [
    {
        "source": "curated_feed",
        "external_job_id": "feed-blr-101",
        "title": "Senior Java Developer",
        "company": "Target Tech India",
        "location": "Bengaluru, Karnataka, India",
        "work_mode": "Hybrid",
        "employment_type": "Full-time",
        "description": """Target Tech is seeking a Senior Java Developer in Bengaluru to build resilient e-commerce microservices.
Key Responsibilities:
- Design and implement distributed microservices using Java 17+, Spring Boot, and Spring MVC.
- Deploy high-throughput event-driven architectures with Apache Kafka and MySQL.
- Containerize services with Docker and deploy to Kubernetes on AWS Cloud.
- Lead CI/CD automation pipelines with Jenkins and Terraform.
- Collaborate with frontend engineers using ReactJS to deliver seamless guest checkout workflows.
Qualifications:
- 5+ years of software development experience with Java, Spring Boot, and Microservices.
- Solid experience with REST APIs, SQL databases, Docker, and Kubernetes.
- Excellent background in cloud platforms (AWS or Azure).""",
        "required_skills": ["Java", "Spring Boot", "Microservices", "REST APIs", "SQL", "Kafka", "Docker", "AWS"],
        "preferred_skills": ["Kubernetes", "ReactJS", "Terraform", "Jenkins", "CI/CD"],
        "minimum_experience": 5.0,
        "maximum_experience": 8.0,
        "salary_min": 2400000.0,
        "salary_max": 3500000.0,
        "salary_currency": "INR",
        "job_url": "https://careers.target.com/jobs/senior-java-developer-bengaluru",
        "application_url": "https://careers.target.com/jobs/apply/senior-java-developer-bengaluru",
    },
    {
        "source": "linkedin_mock",
        "external_job_id": "li-mock-202",
        "title": "Full-Stack Developer — Java + React",
        "company": "Flipkart Internet",
        "location": "Bengaluru, Karnataka, India",
        "work_mode": "Hybrid",
        "employment_type": "Full-time",
        "description": """Flipkart is hiring a Full-Stack Developer (Java + React) for the Marketplace Platform team in Bangalore.
Role Overview:
- Build high-scale microservices using Java, Spring Boot, and RESTful APIs.
- Develop interactive, responsive merchant management web portals using ReactJS, JavaScript (ES6+), HTML5, and CSS3.
- Manage state, optimize client bundle sizes, and tune backend database queries on MySQL and MongoDB.
- Ensure end-to-end telemetry and monitoring for SLO compliance (<50ms response times).
- Work with Docker containers and AWS/Azure cloud infrastructure.
Requirements:
- 4 to 7 years of full stack web development experience.
- Strong command of Java, Spring Boot, ReactJS, and REST APIs.
- Experience with databases: MySQL, MongoDB, and caching solutions.""",
        "required_skills": ["Java", "Spring Boot", "ReactJS", "JavaScript", "Microservices", "REST APIs", "MySQL", "MongoDB"],
        "preferred_skills": ["Docker", "AWS", "CI/CD", "HTML5", "CSS3"],
        "minimum_experience": 4.0,
        "maximum_experience": 7.0,
        "salary_min": 2600000.0,
        "salary_max": 3800000.0,
        "salary_currency": "INR",
        "job_url": "https://www.flipkartcareers.com/jobs/fullstack-java-react-blr",
        "application_url": "https://www.flipkartcareers.com/jobs/apply/fullstack-java-react-blr",
    },
    {
        "source": "curated_feed",
        "external_job_id": "feed-blr-303",
        "title": "Microservices Engineer (Java & Cloud-Native)",
        "company": "Intuit India",
        "location": "Bengaluru, Karnataka, India",
        "work_mode": "Remote",
        "employment_type": "Full-time",
        "description": """Intuit is looking for a talented Microservices Engineer to power TurboTax and QuickBooks backend platforms.
What you'll do:
- Architect, build, and deploy fault-tolerant microservices with Java, Spring Boot, and Kubernetes.
- Leverage AWS services (EC2, EKS, RDS, S3) and Terraform for infrastructure as code.
- Implement streaming pipelines using Apache Kafka for real-time compliance and transaction events.
- Drive automated CI/CD releases via Jenkins and GitHub Actions.
- Ensure 99.99% system availability and enforce security compliance.
Requirements:
- 5+ years of backend engineering experience with Java and Spring.
- In-depth knowledge of Microservices patterns, REST APIs, and container orchestration (Kubernetes, Docker).
- Hands-on experience with Kafka and AWS.""",
        "required_skills": ["Java", "Spring Boot", "Microservices", "Kubernetes", "Docker", "AWS", "Kafka", "REST APIs"],
        "preferred_skills": ["Terraform", "Jenkins", "CI/CD", "MySQL"],
        "minimum_experience": 5.0,
        "maximum_experience": 9.0,
        "salary_min": 2800000.0,
        "salary_max": 4200000.0,
        "salary_currency": "INR",
        "job_url": "https://jobs.intuit.com/job/bengaluru/microservices-engineer/503",
        "application_url": "https://jobs.intuit.com/job/bengaluru/microservices-engineer/apply/503",
    },
    {
        "source": "linkedin_mock",
        "external_job_id": "li-mock-404",
        "title": "Java Backend Developer",
        "company": "Walmart Global Tech India",
        "location": "Bengaluru, Karnataka, India",
        "work_mode": "Hybrid",
        "employment_type": "Full-time",
        "description": """Walmart Global Tech is hiring a Java Backend Developer in Bengaluru.
Responsibilities:
- Build high-scale backend services in Java, Spring Boot, and Spring MVC.
- Optimize SQL queries and schema performance for high volume retail catalogs.
- Implement distributed caching with Redis and async queues with Kafka.
- Containerize backend workloads using Docker and deploy into private/hybrid clouds.
- Write thorough unit and integration tests (JUnit, Mockito).
Qualifications:
- 4-8 years experience in core Java backend development.
- Strong problem-solving, data structures, and database optimization skills.""",
        "required_skills": ["Java", "Spring Boot", "Spring MVC", "REST APIs", "SQL", "MySQL"],
        "preferred_skills": ["Kafka", "Docker", "Redis", "AWS"],
        "minimum_experience": 4.0,
        "maximum_experience": 8.0,
        "salary_min": 2200000.0,
        "salary_max": 3200000.0,
        "salary_currency": "INR",
        "job_url": "https://careers.walmart.com/jobs/java-backend-dev-blr",
        "application_url": "https://careers.walmart.com/jobs/apply/java-backend-dev-blr",
    },
    {
        "source": "curated_feed",
        "external_job_id": "feed-blr-505",
        "title": "Cloud-Native Java Engineer",
        "company": "Cisco Systems",
        "location": "Bengaluru, Karnataka, India",
        "work_mode": "Hybrid",
        "employment_type": "Full-time",
        "description": """Cisco Cloud Engineering is looking for a Cloud-Native Java Engineer in Bangalore.
Key Tasks:
- Design microservices architectures on AWS and Azure with Java and Spring Boot.
- Implement infrastructure as code using Terraform and automated CI/CD pipelines via Jenkins.
- Manage Docker containers running on Kubernetes clusters.
- Integrate Kafka message brokers and secure REST API endpoints.
Qualifications:
- 5+ years of software development.
- Strong skills in Java, Docker, Kubernetes, Terraform, AWS, and Spring Boot.""",
        "required_skills": ["Java", "Spring Boot", "AWS", "Azure", "Docker", "Kubernetes", "Terraform", "CI/CD"],
        "preferred_skills": ["Kafka", "Jenkins", "REST APIs", "SQL"],
        "minimum_experience": 5.0,
        "maximum_experience": 9.0,
        "salary_min": 2500000.0,
        "salary_max": 3700000.0,
        "salary_currency": "INR",
        "job_url": "https://jobs.cisco.com/jobs/cloud-native-java-engineer-blr",
        "application_url": "https://jobs.cisco.com/jobs/apply/cloud-native-java-engineer-blr",
    },
    {
        "source": "curated_feed",
        "external_job_id": "feed-rem-606",
        "title": "Spring Boot Developer",
        "company": "Zeta Suite",
        "location": "Bengaluru, Karnataka, India",
        "work_mode": "Remote",
        "employment_type": "Full-time",
        "description": """Zeta is building next-generation banking tech platforms.
We need a Spring Boot Developer with experience in:
- High-frequency financial transaction processing in Java and Spring Boot.
- Microservice event architectures with Kafka and MySQL.
- Strictly idempotent transaction processing and compliance auditing.
- AWS cloud deployments, Docker, and automated CI/CD.
Requirements:
- 3 to 6 years of experience.
- Deep expertise in Spring Boot, REST APIs, and SQL.""",
        "required_skills": ["Java", "Spring Boot", "REST APIs", "SQL", "MySQL", "Kafka"],
        "preferred_skills": ["AWS", "Docker", "CI/CD", "Microservices"],
        "minimum_experience": 3.0,
        "maximum_experience": 6.0,
        "salary_min": 2000000.0,
        "salary_max": 3000000.0,
        "salary_currency": "INR",
        "job_url": "https://zeta.tech/careers/spring-boot-developer",
        "application_url": "https://zeta.tech/careers/apply/spring-boot-developer",
    },
    {
        "source": "linkedin_mock",
        "external_job_id": "li-mock-707",
        "title": "Full-Stack Software Engineer",
        "company": "Swiggy",
        "location": "Bengaluru, Karnataka, India",
        "work_mode": "On-site",
        "employment_type": "Full-time",
        "description": """Swiggy Food Delivery Core team is looking for a Full-Stack Software Engineer in Bangalore.
Build frontend applications in ReactJS and backend microservices using Java/NodeJS.
Required: 5+ years experience with Java, Spring Boot, React, JavaScript, SQL, and REST APIs.
Experience with cloud deployments on AWS and containerization using Docker is strongly preferred.""",
        "required_skills": ["Java", "ReactJS", "JavaScript", "Spring Boot", "SQL", "REST APIs"],
        "preferred_skills": ["AWS", "Docker", "Kafka", "Microservices"],
        "minimum_experience": 5.0,
        "maximum_experience": 8.0,
        "salary_min": 2500000.0,
        "salary_max": 3600000.0,
        "salary_currency": "INR",
        "job_url": "https://careers.swiggy.com/jobs/fullstack-swe-blr",
        "application_url": "https://careers.swiggy.com/jobs/apply/fullstack-swe-blr",
    },
    {
        "source": "curated_feed",
        "external_job_id": "feed-div-808",
        "title": "Senior Python & ML Engineer",
        "company": "DataCorp Analytics",
        "location": "Bengaluru, Karnataka, India",
        "work_mode": "Remote",
        "employment_type": "Full-time",
        "description": """DataCorp is seeking a Senior Python & ML Engineer to build LLM pipelines, PyTorch models, and FastAPI microservices.
Requirements:
- 5+ years with Python, PyTorch, LangChain, Pandas, NumPy, and Docker.
- Experience training machine learning models on GPUs.
- Java or SQL knowledge is a mild bonus.""",
        "required_skills": ["Python", "FastAPI", "Docker", "SQL"],
        "preferred_skills": ["Java", "AWS"],
        "minimum_experience": 5.0,
        "maximum_experience": 8.0,
        "salary_min": 2800000.0,
        "salary_max": 4000000.0,
        "salary_currency": "INR",
        "job_url": "https://datacorp.ai/careers/python-ml-engineer",
        "application_url": "https://datacorp.ai/careers/apply/python-ml-engineer",
    },
    {
        "source": "curated_feed",
        "external_job_id": "feed-div-909",
        "title": "Lead iOS Swift Developer",
        "company": "MobileStudio Apps",
        "location": "Bengaluru, Karnataka, India",
        "work_mode": "On-site",
        "employment_type": "Full-time",
        "description": """MobileStudio is seeking a Lead iOS Swift Developer to build native consumer apps using Swift, SwiftUI, Combine, and Xcode.
Requirements: 6+ years in iOS mobile application development.""",
        "required_skills": ["Swift", "iOS", "SwiftUI", "Xcode"],
        "preferred_skills": ["REST APIs"],
        "minimum_experience": 6.0,
        "maximum_experience": 10.0,
        "salary_min": 3000000.0,
        "salary_max": 4500000.0,
        "salary_currency": "INR",
        "job_url": "https://mobilestudio.io/careers/ios-swift-lead",
        "application_url": "https://mobilestudio.io/careers/apply/ios-swift-lead",
    }
]


class MockJobSource(BaseJobSource):
    source_name = "mock"

    def get_connection_status(self) -> Dict[str, Any]:
        return {
            "source": "mock_curated",
            "status": "ready",
            "is_mock": True,
            "message": "Curated offline job fixtures & mock provider active for local development.",
            "required_permissions": [],
            "last_sync": self.last_sync_time.isoformat() if self.last_sync_time else None,
            "total_fetched": self.total_fetched,
        }

    async def fetch_jobs(
        self,
        keywords: List[str],
        locations: List[str],
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        self.last_sync_time = datetime.now(timezone.utc)
        self.total_fetched += len(MOCK_JOBS_FIXTURES)
        return MOCK_JOBS_FIXTURES[:limit]

