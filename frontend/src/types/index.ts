export interface ExperienceItem {
  title: string;
  company: string;
  location?: string;
  dates?: string;
  is_current?: boolean;
  highlights: string[];
}

export interface EducationItem {
  degree: string;
  institution: string;
  year?: string;
  details?: string;
}

export interface ProjectItem {
  name: string;
  technologies: string[];
  description: string;
  highlights: string[];
}

export interface ResumeParsedData {
  full_name?: string;
  headline?: string;
  email?: string;
  phone?: string;
  location?: string;
  summary?: string;
  years_of_experience?: number;
  skills: string[];
  skills_by_category: Record<string, string[]>;
  experience: ExperienceItem[];
  education: EducationItem[];
  certifications: string[];
  projects: ProjectItem[];
}

export interface Resume {
  id: number;
  user_id: number;
  filename: string;
  extracted_text: string;
  parsed_data: ResumeParsedData;
  version: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Job {
  id: number;
  source: string;
  external_job_id: string;
  title: string;
  company: string;
  description: string;
  location?: string;
  work_mode?: string;
  employment_type?: string;
  required_skills: string[];
  preferred_skills: string[];
  minimum_experience?: number;
  maximum_experience?: number;
  salary_min?: number;
  salary_max?: number;
  salary_currency?: string;
  posted_at?: string;
  job_url?: string;
  application_url?: string;
  status: string;
  content_hash: string;
  first_seen_at: string;
  last_seen_at: string;
  created_at: string;
  updated_at: string;
  match_score?: number;
}

export interface MissingSkills {
  required: string[];
  preferred: string[];
}

export interface MatchExplanation {
  summary: string;
  strengths: string[];
  gaps: string[];
  experience_compatibility: string;
  location_compatibility: string;
  suggested_keywords: string[];
  breakdown_notes: Record<string, string>;
}

export interface JobMatch {
  id: number;
  user_id: number;
  resume_id: number;
  job_id: number;
  overall_score: number;
  skill_score: number;
  semantic_score: number;
  experience_score: number;
  title_score: number;
  location_score: number;
  education_score: number;
  matched_skills: string[];
  missing_skills: MissingSkills;
  explanation: MatchExplanation;
  calculated_at: string;
  job?: Job;
}

export interface ShortlistedJob {
  id: number;
  user_id: number;
  job_id: number;
  resume_id?: number;
  status: string;
  match_score: number;
  notes?: string;
  shortlisted_at: string;
  updated_at: string;
  job: Job;
  match?: JobMatch;
}

export type ApplicationStatus =
  | 'Saved'
  | 'To Apply'
  | 'Applied'
  | 'Assessment'
  | 'Interview'
  | 'Offer'
  | 'Rejected'
  | 'Withdrawn';

export interface JobApplication {
  id: number;
  user_id: number;
  job_id: number;
  application_status: ApplicationStatus;
  applied_at?: string;
  follow_up_date?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
  job: Job;
}

export interface JobSearchPreferences {
  id: number;
  user_id: number;
  keywords: string[];
  locations: string[];
  work_modes: string[];
  minimum_experience?: number;
  maximum_experience?: number;
  minimum_match_score: number;
  scoring_weights: Record<string, number>;
  sync_frequency: string;
  created_at: string;
  updated_at: string;
}

export interface MatchAnalytics {
  total_matched: number;
  excellent_matches: number;
  strong_matches: number;
  potential_matches: number;
  low_matches: number;
  average_score: number;
  top_matched_skills: { skill: string; count: number }[];
  top_missing_skills: { skill: string; count: number }[];
  score_distribution: { range: string; count: number }[];
}

export interface SourceStatus {
  source: string;
  status: string;
  is_mock: boolean;
  message: string;
  required_permissions: string[];
  last_sync?: string;
  total_fetched: number;
  manual_import_supported?: boolean;
}

export interface SyncStatus {
  is_running: boolean;
  last_run_time?: string;
  last_stats?: Record<string, any>;
  sources: SourceStatus[];
}

