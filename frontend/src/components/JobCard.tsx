import React from 'react';
import {
  Building2,
  MapPin,
  Briefcase,
  DollarSign,
  Bookmark,
  CheckCircle2,
  AlertTriangle,
  ExternalLink,
  Info,
  Calendar,
} from 'lucide-react';
import { Job } from '../types';
import { ScoreBadge } from './ScoreBadge';
import { SourceBadge } from './SourceBadge';

interface JobCardProps {
  job: Job;
  isShortlisted?: boolean;
  onViewDetails: (job: Job) => void;
  onToggleShortlist?: (job: Job) => void;
  onApplyTracker?: (job: Job) => void;
}

export const JobCard: React.FC<JobCardProps> = ({
  job,
  isShortlisted = false,
  onViewDetails,
  onToggleShortlist,
  onApplyTracker,
}) => {
  const formattedDate = job.posted_at
    ? new Date(job.posted_at).toLocaleDateString('en-IN', {
        month: 'short',
        day: 'numeric',
      })
    : null;

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs hover:shadow-md transition duration-150 flex flex-col justify-between group">
      <div>
        {/* Top badges & Score */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex items-center gap-2 flex-wrap">
            <SourceBadge source={job.source} />
            {job.work_mode && (
              <span className="text-xs px-2 py-0.5 rounded font-medium bg-slate-100 text-slate-600 border border-slate-200">
                {job.work_mode}
              </span>
            )}
            {formattedDate && (
              <span className="text-xs text-slate-400 flex items-center gap-1">
                <Calendar className="w-3 h-3" />
                {formattedDate}
              </span>
            )}
          </div>
          <ScoreBadge score={job.match_score} size="md" />
        </div>

        {/* Title & Company */}
        <h3
          onClick={() => onViewDetails(job)}
          className="text-base font-bold text-slate-900 group-hover:text-indigo-600 cursor-pointer transition line-clamp-1"
        >
          {job.title}
        </h3>

        <div className="flex items-center gap-3 text-xs text-slate-600 mt-1.5 flex-wrap">
          <span className="flex items-center gap-1 font-medium text-slate-800">
            <Building2 className="w-3.5 h-3.5 text-slate-400" />
            {job.company}
          </span>
          <span className="flex items-center gap-1">
            <MapPin className="w-3.5 h-3.5 text-slate-400" />
            {job.location || 'Bengaluru, India'}
          </span>
          {job.minimum_experience !== null && job.minimum_experience !== undefined && (
            <span className="flex items-center gap-1">
              <Briefcase className="w-3.5 h-3.5 text-slate-400" />
              {job.minimum_experience}
              {job.maximum_experience ? `–${job.maximum_experience}` : '+'} yrs
            </span>
          )}
          {job.salary_min && (
            <span className="font-semibold text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded">
              ₹{(job.salary_min / 100000).toFixed(1)}L PA
            </span>
          )}
        </div>

        {/* Snippet / Description */}
        <p className="text-xs text-slate-500 mt-2.5 line-clamp-2 leading-relaxed">
          {job.description}
        </p>

        {/* Skill badges */}
        <div className="mt-3.5 pt-3 border-t border-slate-100 flex flex-wrap gap-1.5 items-center">
          {job.required_skills.slice(0, 5).map((skill, i) => (
            <span
              key={i}
              className="px-2 py-0.5 text-xs font-medium rounded bg-slate-100 text-slate-700 hover:bg-slate-200"
            >
              {skill}
            </span>
          ))}
          {job.required_skills.length > 5 && (
            <span className="text-xs text-slate-400 font-medium">
              +{job.required_skills.length - 5} more
            </span>
          )}
        </div>
      </div>

      {/* Card Actions */}
      <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
        <button
          onClick={() => onViewDetails(job)}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-600 hover:text-indigo-800 transition"
        >
          <Info className="w-3.5 h-3.5" />
          View Compatibility
        </button>

        <div className="flex items-center gap-2">
          {onToggleShortlist && (
            <button
              onClick={() => onToggleShortlist(job)}
              title={isShortlisted ? 'In Shortlist' : 'Add to Shortlist'}
              className={`p-1.5 rounded-lg border text-xs transition ${
                isShortlisted
                  ? 'bg-indigo-600 text-white border-indigo-600'
                  : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
              }`}
            >
              <Bookmark className="w-4 h-4" />
            </button>
          )}

          {job.application_url && (
            <a
              href={job.application_url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 px-2.5 py-1.5 bg-slate-900 text-white hover:bg-indigo-600 text-xs font-medium rounded-lg transition"
            >
              Apply
              <ExternalLink className="w-3 h-3" />
            </a>
          )}
        </div>
      </div>
    </div>
  );
};

