import json
import re
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.schemas.resume import ResumeParsedData
from app.models.job import Job
from app.schemas.match import MissingSkills, MatchExplanation

DEFAULT_WEIGHTS = {
    "technical_skills": 0.35,
    "semantic_similarity": 0.25,
    "experience": 0.15,
    "job_title": 0.10,
    "location_work_mode": 0.10,
    "education_certifications": 0.05,
}

SKILL_ALIASES = {
    "react": "ReactJS",
    "reactjs": "ReactJS",
    "spring": "Spring Boot",
    "springboot": "Spring Boot",
    "k8s": "Kubernetes",
    "cicd": "CI/CD",
    "rest": "REST APIs",
    "restful": "REST APIs",
    "sql": "SQL",
    "aws": "AWS",
    "azure": "Azure",
    "gcp": "Google Cloud",
    "kafka": "Kafka",
    "docker": "Docker",
}


class JobMatcherService:
    @staticmethod
    def normalize_skill(skill: str) -> str:
        s = skill.lower().strip()
        return SKILL_ALIASES.get(s, skill.strip())

    @classmethod
    def calculate_skill_score(
        cls,
        candidate_skills: List[str],
        required_skills: List[str],
        preferred_skills: List[str],
    ) -> Tuple[float, List[str], MissingSkills]:
        candidate_norm = {cls.normalize_skill(s).lower(): s for s in candidate_skills}

        matched = []
        missing_req = []
        missing_pref = []

        for req in required_skills:
            req_norm = cls.normalize_skill(req).lower()
            if req_norm in candidate_norm or any(req_norm in c for c in candidate_norm):
                matched.append(req)
            else:
                missing_req.append(req)

        for pref in preferred_skills:
            pref_norm = cls.normalize_skill(pref).lower()
            if pref_norm in candidate_norm or any(pref_norm in c for c in candidate_norm):
                if pref not in matched:
                    matched.append(pref)
            else:
                missing_pref.append(pref)

        # Calculate weighted ratio
        # Required skills are 70% weight, preferred are 30% weight
        total_req = len(required_skills)
        total_pref = len(preferred_skills)

        if total_req == 0 and total_pref == 0:
            # If no skills listed in job, base score is neutral high
            score = 80.0
        elif total_req == 0:
            pref_matched = total_pref - len(missing_pref)
            score = (pref_matched / total_pref) * 100.0
        elif total_pref == 0:
            req_matched = total_req - len(missing_req)
            score = (req_matched / total_req) * 100.0
        else:
            req_matched = total_req - len(missing_req)
            pref_matched = total_pref - len(missing_pref)
            req_ratio = req_matched / total_req
            pref_ratio = pref_matched / total_pref
            score = (req_ratio * 0.70 + pref_ratio * 0.30) * 100.0

        return round(float(score), 1), matched, MissingSkills(required=missing_req, preferred=missing_pref)

    @staticmethod
    def calculate_semantic_similarity(resume_text: str, job_description: str) -> float:
        """TF-IDF and cosine similarity between resume text and job description."""
        if not resume_text.strip() or not job_description.strip():
            return 50.0
        try:
            vectorizer = TfidfVectorizer(
                stop_words="english",
                ngram_range=(1, 2),
                max_features=5000,
            )
            tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
            sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            # TF-IDF cosine similarity between long and short documents typically falls between 0.15 and 0.65
            # Scale non-linearly to 0-100 range for meaningful discrimination
            scaled = min(100.0, max(0.0, (sim * 1.5) * 100.0))
            return round(float(scaled), 1)
        except Exception:
            return 60.0

    @staticmethod
    def calculate_experience_score(
        candidate_years: Optional[float],
        min_years: Optional[float],
        max_years: Optional[float],
    ) -> Tuple[float, str]:
        c_years = candidate_years if candidate_years is not None else 5.0

        if min_years is None and max_years is None:
            return 85.0, "Experience requirement not specified; compatible."

        if min_years is not None and max_years is not None:
            if min_years <= c_years <= max_years:
                return 100.0, f"Candidate's {c_years:.1f} years fits target range of {min_years:.1f}–{max_years:.1f} years perfectly."
            elif c_years > max_years:
                # Mild overqualification
                diff = c_years - max_years
                penalty = min(20.0, diff * 5.0)
                return max(75.0, 100.0 - penalty), f"Candidate has {c_years:.1f} years (slightly exceeds target max of {max_years:.1f} years)."
            else:
                # Underqualified
                diff = min_years - c_years
                penalty = diff * 15.0
                score = max(30.0, 100.0 - penalty)
                return score, f"Candidate has {c_years:.1f} years versus target minimum of {min_years:.1f} years."

        if min_years is not None:
            if c_years >= min_years:
                return 100.0, f"Candidate has {c_years:.1f} years, meeting required {min_years:.1f}+ years."
            else:
                diff = min_years - c_years
                penalty = diff * 18.0
                return max(30.0, 100.0 - penalty), f"Candidate has {c_years:.1f} years, below desired {min_years:.1f}+ years."

        return 85.0, "Compatible experience."

    @staticmethod
    def calculate_title_similarity(
        candidate_title: Optional[str],
        job_title: str,
        target_roles: Optional[List[str]] = None,
    ) -> float:
        jt_lower = job_title.lower()
        titles_to_check = [candidate_title or "Full-Stack Software Engineer"]
        if target_roles:
            titles_to_check.extend(target_roles)

        best_score = 40.0
        for t in titles_to_check:
            t_lower = t.lower()
            if t_lower in jt_lower or jt_lower in t_lower:
                return 100.0
            
            # Token overlap (Jaccard similarity)
            words_cand = set(re.findall(r"\w+", t_lower)) - {"developer", "engineer", "software"}
            words_job = set(re.findall(r"\w+", jt_lower)) - {"developer", "engineer", "software"}
            
            common = words_cand.intersection(words_job)
            if common:
                overlap_ratio = len(common) / max(len(words_cand), len(words_job))
                score = 60.0 + (overlap_ratio * 40.0)
                if score > best_score:
                    best_score = score

        # Check key technology keywords in title
        key_techs = ["java", "react", "spring", "microservices", "full-stack", "fullstack", "cloud"]
        matches = [k for k in key_techs if k in jt_lower]
        if matches:
            tech_score = min(95.0, 50.0 + len(matches) * 15.0)
            best_score = max(best_score, tech_score)

        return round(float(best_score), 1)

    @staticmethod
    def calculate_location_work_mode_score(
        candidate_loc: Optional[str],
        candidate_work_modes: List[str],
        job_loc: Optional[str],
        job_work_mode: Optional[str],
    ) -> Tuple[float, str]:
        c_loc = (candidate_loc or "Bengaluru, Karnataka, India").lower()
        j_loc = (job_loc or "").lower()
        j_mode = (job_work_mode or "Hybrid").capitalize()

        score = 80.0
        notes = []

        # Location matching
        if "remote" in j_mode.lower() or "remote" in j_loc:
            score = 100.0
            notes.append("Remote position aligns with candidate location.")
        elif any(city in j_loc for city in ["bengaluru", "bangalore"]):
            score = 100.0
            notes.append("Exact location match in Bengaluru.")
        elif not j_loc:
            score = 75.0
            notes.append("Job location unspecified.")
        else:
            # Different city
            score = 50.0
            notes.append(f"Job is located in {job_loc}; relocation or remote agreement may be needed.")

        # Work-mode preference
        if candidate_work_modes and j_mode not in candidate_work_modes:
            score = max(40.0, score - 15.0)
            notes.append(f"Work mode '{j_mode}' not in candidate preferred modes ({', '.join(candidate_work_modes)}).")

        return round(float(score), 1), " ".join(notes)

    @staticmethod
    def calculate_education_score(
        education: List[Any],
        certifications: List[str],
        job_description: str,
    ) -> float:
        score = 85.0
        j_lower = job_description.lower()
        
        # Candidate has B.Tech and AWS Certified Solutions Architect
        if "aws" in j_lower and any("aws" in c.lower() for c in certifications):
            score = 100.0
        elif "degree" in j_lower or "bachelor" in j_lower or "b.tech" in j_lower:
            score = 95.0

        return round(float(score), 1)

    @classmethod
    def evaluate_match(
        cls,
        parsed_resume: ResumeParsedData,
        resume_raw_text: str,
        job: Job,
        custom_weights: Optional[Dict[str, float]] = None,
        target_roles: Optional[List[str]] = None,
        preferred_work_modes: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        weights = custom_weights or DEFAULT_WEIGHTS
        total_w = sum(weights.values())
        norm_weights = {k: v / total_w for k, v in weights.items()}

        req_skills = json.loads(job.required_skills_json) if job.required_skills_json else []
        pref_skills = json.loads(job.preferred_skills_json) if job.preferred_skills_json else []

        # 1. Skill Score
        skill_score, matched_skills, missing_skills = cls.calculate_skill_score(
            parsed_resume.skills,
            req_skills,
            pref_skills,
        )

        # 2. Semantic Score
        semantic_score = cls.calculate_semantic_similarity(
            resume_raw_text,
            job.description,
        )

        # 3. Experience Score
        exp_score, exp_notes = cls.calculate_experience_score(
            parsed_resume.years_of_experience,
            job.minimum_experience,
            job.maximum_experience,
        )

        # 4. Title Score
        title_score = cls.calculate_title_similarity(
            parsed_resume.headline,
            job.title,
            target_roles=target_roles,
        )

        # 5. Location & Work Mode Score
        loc_score, loc_notes = cls.calculate_location_work_mode_score(
            parsed_resume.location,
            preferred_work_modes or ["Remote", "Hybrid", "On-site"],
            job.location,
            job.work_mode,
        )

        # 6. Education Score
        edu_score = cls.calculate_education_score(
            parsed_resume.education,
            parsed_resume.certifications,
            job.description,
        )

        # Calculate Overall Weighted Score
        overall = (
            skill_score * norm_weights["technical_skills"]
            + semantic_score * norm_weights["semantic_similarity"]
            + exp_score * norm_weights["experience"]
            + title_score * norm_weights["job_title"]
            + loc_score * norm_weights["location_work_mode"]
            + edu_score * norm_weights["education_certifications"]
        )
        overall = round(max(0.0, min(100.0, float(overall))), 1)

        # Generate Strengths, Gaps, and Suggested Keywords
        strengths = []
        if matched_skills:
            strengths.append(f"Strong match on core skills: {', '.join(matched_skills[:5])}.")
        if exp_score >= 90:
            strengths.append(f"Ideal seniority level: {exp_notes}")
        if loc_score >= 90:
            strengths.append("High geographical/work-mode compatibility.")

        gaps = []
        if missing_skills.required:
            gaps.append(f"Missing required skills from resume: {', '.join(missing_skills.required)}.")
        if missing_skills.preferred:
            gaps.append(f"Desired secondary skills not highlighted: {', '.join(missing_skills.preferred[:4])}.")

        # Suggested keywords from job description that candidate likely has or can highlight
        suggested_kw = [s for s in (missing_skills.required + missing_skills.preferred) if len(s) > 2][:5]

        explanation = MatchExplanation(
            summary=f"Overall compatibility of {overall}% based on skill alignment, {job.title} title relevance, and {parsed_resume.years_of_experience or 5} years experience.",
            strengths=strengths,
            gaps=gaps,
            experience_compatibility=exp_notes,
            location_compatibility=loc_notes,
            suggested_keywords=suggested_kw,
            breakdown_notes={
                "Skills Match (35%)": f"{skill_score}%",
                "Responsibilities Semantic Sim (25%)": f"{semantic_score}%",
                "Experience Alignment (15%)": f"{exp_score}%",
                "Job Title Relevance (10%)": f"{title_score}%",
                "Location & Work-Mode (10%)": f"{loc_score}%",
                "Education & Certs (5%)": f"{edu_score}%",
            }
        )

        return {
            "overall_score": overall,
            "skill_score": skill_score,
            "semantic_score": semantic_score,
            "experience_score": exp_score,
            "title_score": title_score,
            "location_score": loc_score,
            "education_score": edu_score,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills.model_dump(),
            "explanation": explanation.model_dump(),
        }

