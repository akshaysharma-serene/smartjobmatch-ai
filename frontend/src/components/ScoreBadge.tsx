import React from 'react';
import { Award, CheckCircle2, AlertCircle } from 'lucide-react';

interface ScoreBadgeProps {
  score?: number | null;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

export const ScoreBadge: React.FC<ScoreBadgeProps> = ({ score, size = 'md', showLabel = true }) => {
  if (score === null || score === undefined) {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-600 border border-slate-200">
        Not calculated
      </span>
    );
  }

  const s = Math.round(score);

  let badgeColor = 'bg-slate-100 text-slate-700 border-slate-200';
  let label = 'Low Match';
  let icon = <AlertCircle className="w-3.5 h-3.5 text-slate-500" />;

  if (s >= 85) {
    badgeColor = 'bg-emerald-50 text-emerald-700 border-emerald-200';
    label = 'Excellent Match';
    icon = <Award className="w-3.5 h-3.5 text-emerald-600" />;
  } else if (s >= 70) {
    badgeColor = 'bg-blue-50 text-blue-700 border-blue-200';
    label = 'Strong Match';
    icon = <CheckCircle2 className="w-3.5 h-3.5 text-blue-600" />;
  } else if (s >= 55) {
    badgeColor = 'bg-amber-50 text-amber-700 border-amber-200';
    label = 'Potential Match';
    icon = <AlertCircle className="w-3.5 h-3.5 text-amber-600" />;
  }

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-2.5 py-1',
    lg: 'text-base px-3 py-1.5 font-bold',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-semibold rounded-full border shadow-xs ${badgeColor} ${sizeClasses[size]}`}
    >
      {icon}
      <span>{s}%</span>
      {showLabel && <span className="font-normal opacity-90 text-xs">({label})</span>}
    </span>
  );
};

