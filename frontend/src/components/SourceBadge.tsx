import React from 'react';

interface SourceBadgeProps {
  source: string;
}

export const SourceBadge: React.FC<SourceBadgeProps> = ({ source }) => {
  const s = source.toLowerCase();

  if (s.includes('linkedin')) {
    const isMock = s.includes('mock');
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-medium bg-[#0A66C2]/10 text-[#0A66C2] border border-[#0A66C2]/20">
        <span className="w-1.5 h-1.5 rounded-full bg-[#0A66C2]"></span>
        LinkedIn {isMock ? '(Mock)' : '(Real-time)'}
      </span>
    );
  }

  if (s.includes('greenhouse')) {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
        Greenhouse
      </span>
    );
  }

  if (s.includes('lever')) {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-medium bg-indigo-50 text-indigo-700 border border-indigo-200">
        <span className="w-1.5 h-1.5 rounded-full bg-indigo-500"></span>
        Lever
      </span>
    );
  }

  if (s.includes('manual')) {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-medium bg-purple-50 text-purple-700 border border-purple-200">
        Manual Import
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200">
      Verified Feed
    </span>
  );
};

