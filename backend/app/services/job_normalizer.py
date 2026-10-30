import hashlib
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any
from app.services.resume_parser import KNOWN_SKILLS


class JobNormalizerService:
    @staticmethod
    def calculate_content_hash(title: str, company: str, description: str) -> str:
        """Computes a deterministic SHA-256 hash for duplicate detection."""
        # Normalize text: lowercase, remove excess whitespace
        clean_title = re.sub(r"\s+", " ", title.lower().strip())
        clean_company = re.sub(r"\s+", " ", company.lower().strip())
        # Use first 800 chars of normalized description
        clean_desc = re.sub(r"\s+", " ", description.lower().strip())[:800]
        payload = f"{clean_title}::{clean_company}::{clean_desc}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @staticmethod
    def extract_skills_from_text(text: str) -> List[str]:
        """Extracts recognizable technical skills from a job description."""
        found = set()
        lowered = text.lower()
        for pattern, canonical in KNOWN_SKILLS.items():
            escaped = re.escape(pattern)
            if re.search(rf"(?<![a-zA-Z0-9]){escaped}(?![a-zA-Z0-9])", lowered):
                found.add(canonical)
        return sorted(list(found))

    @staticmethod
    def extract_experience_requirements(text: str) -> Tuple[Optional[float], Optional[float]]:
        """Extracts minimum and maximum years of experience from job text."""
        # e.g. "5-8 years", "5 to 8 years", "5+ years", "minimum 4 years"
        range_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)\s*(?:years|yrs)", text, re.IGNORECASE)
        if range_match:
            try:
                return float(range_match.group(1)), float(range_match.group(2))
            except ValueError:
                pass

        min_match = re.search(r"(?:minimum|at least|\bmin\.?)\s*(\d+(?:\.\d+)?)\s*(?:years|yrs)", text, re.IGNORECASE)
        if min_match:
            try:
                val = float(min_match.group(1))
                return val, None
            except ValueError:
                pass

        plus_match = re.search(r"(\d+(?:\.\d+)?)\+\s*(?:years|yrs)", text, re.IGNORECASE)
        if plus_match:
            try:
                val = float(plus_match.group(1))
                return val, None
            except ValueError:
                pass

        return None, None

    @staticmethod
    def infer_work_mode(text: str, location: Optional[str] = None) -> str:
        """Infers work mode: Remote, Hybrid, or On-site."""
        combined = f"{location or ''} {text[:500]}".lower()
        if "remote" in combined or "work from home" in combined or "wfh" in combined:
            if "hybrid" in combined:
                return "Hybrid"
            return "Remote"
        if "hybrid" in combined:
            return "Hybrid"
        return "On-site"

    @classmethod
    def normalize_job_dict(cls, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes raw job dict from any connector into standard schema."""
        title = raw.get("title", "").strip()
        company = raw.get("company", "").strip()
        description = raw.get("description", "").strip()
        source = raw.get("source", "unknown").strip()
        external_id = str(raw.get("external_job_id", "")).strip()

        location = raw.get("location")
        if location:
            location = location.strip()
            if "bangalore" in location.lower() or "bengaluru" in location.lower():
                location = "Bengaluru, Karnataka, India"

        work_mode = raw.get("work_mode") or cls.infer_work_mode(description, location)
        
        # Skills extraction
        required_skills = raw.get("required_skills") or []
        preferred_skills = raw.get("preferred_skills") or []
        if not required_skills and description:
            all_extracted = cls.extract_skills_from_text(description)
            # Partition: core skills as required
            required_skills = all_extracted[:10]
            preferred_skills = all_extracted[10:15]

        # Experience extraction
        min_exp = raw.get("minimum_experience")
        max_exp = raw.get("maximum_experience")
        if min_exp is None and description:
            inferred_min, inferred_max = cls.extract_experience_requirements(description)
            min_exp = inferred_min
            max_exp = inferred_max

        # Content hash
        content_hash = raw.get("content_hash") or cls.calculate_content_hash(title, company, description)

        now = datetime.now(timezone.utc)
        return {
            "source": source,
            "external_job_id": external_id or content_hash[:16],
            "title": title,
            "company": company,
            "description": description,
            "location": location,
            "work_mode": work_mode,
            "employment_type": raw.get("employment_type", "Full-time"),
            "required_skills": required_skills,
            "preferred_skills": preferred_skills,
            "minimum_experience": min_exp,
            "maximum_experience": max_exp,
            "salary_min": raw.get("salary_min"),
            "salary_max": raw.get("salary_max"),
            "salary_currency": raw.get("salary_currency", "INR"),
            "posted_at": raw.get("posted_at") or now,
            "job_url": raw.get("job_url"),
            "application_url": raw.get("application_url") or raw.get("job_url"),
            "content_hash": content_hash,
            "status": raw.get("status", "active"),
            "first_seen_at": raw.get("first_seen_at") or now,
            "last_seen_at": raw.get("last_seen_at") or now,
        }

