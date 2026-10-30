import React, { useEffect, useState } from 'react';
import {
  X,
  ExternalLink,
  Building2,
  MapPin,
  Briefcase,
  DollarSign,
  Calendar,
  CheckCircle2,
  AlertTriangle,
  Lightbulb,
  Award,
  Bookmark,
  Send,
} from 'lucide-react';
import { Job, JobMatch } from '../types';
import { matchService, shortlistService, applicationService } from '../services/api';
import { ScoreBadge } from './ScoreBadge';
import { SourceBadge } from './SourceBadge';

interface JobDetailModalProps {
  job: Job | null;
  onClose: () => void;
  onUpdate?: () => void;
}

export const JobDetailModal: React.FC<JobDetailModalProps> = ({ job, onClose, onUpdate }) => {
  const [match, setMatch] = useState<JobMatch | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [shortlistStatus, setShortlistStatus] = useState<string>('idle');
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  useEffect(() => {
    if (!job) return;
    setLoading(true);
    setActionSuccess(null);
    matchService
      .getMatches({ limit: 100 })
      .then((matches) => {
        const found = matches.find((m) => m.job_id === job.id);
        if (found) setMatch(found);
      })
      .catch((err) => console.error('Error fetching match details:', err))
      .finally(() => setLoading(false));
  }, [job]);

  if (!job) return null;

  const handleShortlist = async (status: string) => {
    try {
      await shortlistService.addToShortlist(job.id, { status });
      setActionSuccess(`Job marked as ${status}!`);
      if (onUpdate) onUpdate();
    } catch (err) {
      console.error(err);
    }
  };

  const handleTrackApplication = async () => {
    try {
      await applicationService.createOrUpdateApplication({
        job_id: job.id,
        application_status: 'Applied',
        applied_at: new Date().toISOString(),
      });
      setActionSuccess('Added to Application Tracker as Applied!');
      if (onUpdate) onUpdate();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs overflow-y-auto">
      <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="p-6 border-b border-slate-100 flex items-start justify-between bg-slate-50/50">
          <div>
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              <SourceBadge source={job.source} />
              <span className="text-xs px-2.5 py-0.5 rounded-md font-medium bg-slate-100 text-slate-600 border border-slate-200">
                {job.work_mode || 'Hybrid'}
              </span>
              <span className="text-xs px-2.5 py-0.5 rounded-md font-medium bg-slate-100 text-slate-600 border border-slate-200">
                {job.employment_type || 'Full-time'}
              </span>
            </div>
            <h2 className="text-2xl font-bold text-slate-900 leading-tight">{job.title}</h2>
            <div className="flex items-center gap-4 mt-2 text-sm text-slate-600 flex-wrap">
              <span className="flex items-center gap-1.5 font-medium text-slate-800">
                <Building2 className="w-4 h-4 text-slate-400" />
                {job.company}
              </span>
              <span className="flex items-center gap-1.5">
                <MapPin className="w-4 h-4 text-slate-400" />
                {job.location || 'Bengaluru, India'}
              </span>
              {job.minimum_experience !== null && job.minimum_experience !== undefined && (
                <span className="flex items-center gap-1.5">
                  <Briefcase className="w-4 h-4 text-slate-400" />
                  {job.minimum_experience}
                  {job.maximum_experience ? `–${job.maximum_experience}` : '+'} yrs exp
                </span>
              )}
              {job.salary_min && (
                <span className="flex items-center gap-1.5 font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">
                  <DollarSign className="w-3.5 h-3.5 text-emerald-600" />
                  ₹{(job.salary_min / 100000).toFixed(1)}L – ₹{((job.salary_max || job.salary_min) / 100000).toFixed(1)}L PA
                </span>
              )}
            </div>
          </div>
          <div className="flex items-center gap-3">
            <ScoreBadge score={match?.overall_score || job.match_score} size="lg" />
            <button
              onClick={onClose}
              className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {actionSuccess && (
          <div className="bg-emerald-50 border-b border-emerald-200 px-6 py-2.5 text-xs text-emerald-800 font-medium flex items-center justify-between">
            <span>{actionSuccess}</span>
            <button onClick={() => setActionSuccess(null)} className="text-emerald-600 hover:underline">
              Dismiss
            </button>
          </div>
        )}

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Match Score Breakdown Cards */}
          {match && (
            <div className="bg-indigo-50/60 rounded-xl p-5 border border-indigo-100">
              <div className="flex items-center gap-2 text-indigo-900 font-semibold mb-3">
                <Award className="w-5 h-5 text-indigo-600" />
                <span>Explainable Match Breakdown & AI Assessment</span>
              </div>
              <p className="text-sm text-slate-700 mb-4">{match.explanation.summary}</p>

              {/* 6 Dimension Grid */}
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-4">
                <div className="bg-white p-3 rounded-lg border border-indigo-100 text-center shadow-xs">
                  <div className="text-xs text-slate-500 font-medium">Tech Skills (35%)</div>
                  <div className="text-lg font-bold text-slate-800 mt-1">{match.skill_score}%</div>
                </div>
                <div className="bg-white p-3 rounded-lg border border-indigo-100 text-center shadow-xs">
                  <div className="text-xs text-slate-500 font-medium">Semantic (25%)</div>
                  <div className="text-lg font-bold text-slate-800 mt-1">{match.semantic_score}%</div>
                </div>
                <div className="bg-white p-3 rounded-lg border border-indigo-100 text-center shadow-xs">
                  <div className="text-xs text-slate-500 font-medium">Experience (15%)</div>
                  <div className="text-lg font-bold text-slate-800 mt-1">{match.experience_score}%</div>
                </div>
                <div className="bg-white p-3 rounded-lg border border-indigo-100 text-center shadow-xs">
                  <div className="text-xs text-slate-500 font-medium">Title Fit (10%)</div>
                  <div className="text-lg font-bold text-slate-800 mt-1">{match.title_score}%</div>
                </div>
                <div className="bg-white p-3 rounded-lg border border-indigo-100 text-center shadow-xs">
                  <div className="text-xs text-slate-500 font-medium">Location (10%)</div>
                  <div className="text-lg font-bold text-slate-800 mt-1">{match.location_score}%</div>
                </div>
                <div className="bg-white p-3 rounded-lg border border-indigo-100 text-center shadow-xs">
                  <div className="text-xs text-slate-500 font-medium">Education (5%)</div>
                  <div className="text-lg font-bold text-slate-800 mt-1">{match.education_score}%</div>
                </div>
              </div>

              {/* Strengths & Gaps */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                <div className="bg-emerald-50/70 p-3.5 rounded-lg border border-emerald-100">
                  <div className="font-semibold text-emerald-900 flex items-center gap-1.5 mb-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    Key Strengths in Candidate Profile
                  </div>
                  <ul className="space-y-1 text-emerald-800 list-disc list-inside">
                    {match.explanation.strengths.map((str, i) => (
                      <li key={i}>{str}</li>
                    ))}
                  </ul>
                </div>
                <div className="bg-amber-50/70 p-3.5 rounded-lg border border-amber-100">
                  <div className="font-semibold text-amber-900 flex items-center gap-1.5 mb-2">
                    <AlertTriangle className="w-4 h-4 text-amber-600" />
                    Areas to Address or Highlight
                  </div>
                  <ul className="space-y-1 text-amber-800 list-disc list-inside">
                    {match.explanation.gaps.length > 0 ? (
                      match.explanation.gaps.map((g, i) => <li key={i}>{g}</li>)
                    ) : (
                      <li>No critical skill gaps identified for this role.</li>
                    )}
                  </ul>
                </div>
              </div>

              {/* Suggested Keywords to Emphasize */}
              {match.explanation.suggested_keywords.length > 0 && (
                <div className="mt-4 pt-3 border-t border-indigo-100 flex items-center gap-2 flex-wrap">
                  <span className="text-xs font-semibold text-indigo-900 flex items-center gap-1">
                    <Lightbulb className="w-3.5 h-3.5 text-amber-500" />
                    Suggested resume keywords:
                  </span>
                  {match.explanation.suggested_keywords.map((kw, i) => (
                    <span
                      key={i}
                      className="px-2 py-0.5 text-xs bg-white text-indigo-700 font-medium rounded-md border border-indigo-200"
                    >
                      +{kw}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Skills Breakdown */}
          <div className="space-y-3">
            <h3 className="text-base font-semibold text-slate-900">Technical Skills Analysis</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="border border-slate-200 rounded-xl p-4 bg-slate-50/50">
                <div className="text-xs font-semibold text-emerald-700 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  Matched Skills ({match?.matched_skills.length || 0})
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {(match?.matched_skills || job.required_skills).map((skill, idx) => (
                    <span
                      key={idx}
                      className="px-2.5 py-1 text-xs font-medium rounded-md bg-emerald-50 text-emerald-700 border border-emerald-200"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>

              <div className="border border-slate-200 rounded-xl p-4 bg-slate-50/50">
                <div className="text-xs font-semibold text-amber-700 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
                  <AlertTriangle className="w-4 h-4 text-amber-600" />
                  Missing Skills ({match?.missing_skills.required.length || 0} required,{' '}
                  {match?.missing_skills.preferred.length || 0} preferred)
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {match?.missing_skills.required.map((skill, idx) => (
                    <span
                      key={`req-${idx}`}
                      className="px-2.5 py-1 text-xs font-medium rounded-md bg-red-50 text-red-700 border border-red-200"
                    >
                      {skill} (Required)
                    </span>
                  ))}
                  {match?.missing_skills.preferred.map((skill, idx) => (
                    <span
                      key={`pref-${idx}`}
                      className="px-2.5 py-1 text-xs font-medium rounded-md bg-amber-50 text-amber-700 border border-amber-200"
                    >
                      {skill} (Preferred)
                    </span>
                  ))}
                  {(!match ||
                    (match.missing_skills.required.length === 0 && match.missing_skills.preferred.length === 0)) && (
                    <span className="text-xs text-slate-500">All required skills accounted for!</span>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Full Job Description */}
          <div className="space-y-3">
            <h3 className="text-base font-semibold text-slate-900">Job Description</h3>
            <div className="bg-slate-50 p-5 rounded-xl border border-slate-200 text-sm text-slate-700 leading-relaxed whitespace-pre-line font-mono text-xs">
              {job.description}
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="p-4 bg-slate-50 border-t border-slate-200 flex items-center justify-between gap-4 flex-wrap">
          <div className="flex items-center gap-2">
            <button
              onClick={() => handleShortlist('shortlisted')}
              className="inline-flex items-center gap-1.5 px-3 py-2 bg-indigo-50 text-indigo-700 hover:bg-indigo-100 font-medium rounded-lg text-sm transition"
            >
              <Bookmark className="w-4 h-4" />
              Shortlist
            </button>
            <button
              onClick={() => handleShortlist('rejected')}
              className="inline-flex items-center gap-1.5 px-3 py-2 bg-slate-100 text-slate-600 hover:bg-red-50 hover:text-red-600 font-medium rounded-lg text-sm transition"
            >
              Not Interested
            </button>
            <button
              onClick={handleTrackApplication}
              className="inline-flex items-center gap-1.5 px-3 py-2 bg-blue-50 text-blue-700 hover:bg-blue-100 font-medium rounded-lg text-sm transition"
            >
              <Send className="w-4 h-4" />
              Mark as Applied
            </button>
          </div>

          <div className="flex items-center gap-3">
            {job.job_url && (
              <a
                href={job.job_url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 text-xs text-slate-600 hover:text-slate-900 underline font-medium"
              >
                Original Job Listing
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            )}
            {job.application_url && (
              <a
                href={job.application_url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 px-4 py-2 bg-indigo-600 text-white font-medium rounded-lg text-sm hover:bg-indigo-700 shadow-xs transition"
              >
                Apply on Official Site
                <ExternalLink className="w-4 h-4" />
              </a>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

