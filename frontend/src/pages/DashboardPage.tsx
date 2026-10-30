import React, { useEffect, useState } from 'react';
import {
  Briefcase,
  Award,
  BookmarkCheck,
  Send,
  TrendingUp,
  Sparkles,
  ArrowRight,
  RefreshCw,
  Search,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { matchService, jobService, shortlistService, applicationService } from '../services/api';
import { MatchAnalytics, Job } from '../types';
import { JobCard } from '../components/JobCard';
import { JobDetailModal } from '../components/JobDetailModal';

export const DashboardPage: React.FC = () => {
  const [analytics, setAnalytics] = useState<MatchAnalytics | null>(null);
  const [recentJobs, setRecentJobs] = useState<Job[]>([]);
  const [shortlistCount, setShortlistCount] = useState<number>(0);
  const [appCount, setAppCount] = useState<number>(0);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const [anData, jobsData, slData, appData] = await Promise.all([
        matchService.getAnalytics(),
        jobService.getJobs({ page: 1, page_size: 6, sort_by: 'match_score', sort_order: 'desc' }),
        shortlistService.getShortlist(),
        applicationService.getApplications(),
      ]);
      setAnalytics(anData);
      setRecentJobs(jobsData.items);
      setShortlistCount(slData.length);
      setAppCount(appData.length);
    } catch (err) {
      console.error('Error loading dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const barColors = ['#10B981', '#3B82F6', '#6366F1', '#F59E0B', '#EF4444', '#94A3B8'];

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-indigo-700 via-indigo-600 to-blue-600 rounded-2xl p-6 text-white shadow-md relative overflow-hidden">
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-white/20 backdrop-blur-xs mb-3">
            <Sparkles className="w-3.5 h-3.5" />
            AI Compatibility Engine Active
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Discover Bengaluru & Remote Java Roles
          </h1>
          <p className="mt-2 text-indigo-100 text-sm leading-relaxed">
            Continuously analyzing active job listings against your Full-Stack Software Engineer resume.
            Ranked by multi-factor score: skills, semantic fit, 5+ years experience, and location.
          </p>
          <div className="mt-5 flex items-center gap-3">
            <Link
              to="/jobs"
              className="px-4 py-2 bg-white text-indigo-900 font-semibold rounded-lg text-xs hover:bg-indigo-50 shadow-xs transition inline-flex items-center gap-1.5"
            >
              <Search className="w-4 h-4" />
              Explore All Jobs
            </Link>
            <Link
              to="/shortlist"
              className="px-4 py-2 bg-indigo-500/40 hover:bg-indigo-500/60 text-white font-semibold rounded-lg text-xs backdrop-blur-xs transition inline-flex items-center gap-1.5 border border-white/20"
            >
              <BookmarkCheck className="w-4 h-4" />
              View Shortlist ({shortlistCount})
            </Link>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <div className="text-xs font-medium text-slate-500 flex items-center justify-between">
            Discovered Jobs
            <Briefcase className="w-4 h-4 text-slate-400" />
          </div>
          <div className="text-2xl font-bold text-slate-900 mt-2">
            {analytics?.total_matched || 0}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">Across 4 adapters</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <div className="text-xs font-medium text-slate-500 flex items-center justify-between">
            Excellent Matches
            <Award className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="text-2xl font-bold text-emerald-600 mt-2">
            {analytics?.excellent_matches || 0}
          </div>
          <div className="text-[11px] text-emerald-600 font-medium mt-1">Score &ge; 85%</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <div className="text-xs font-medium text-slate-500 flex items-center justify-between">
            Strong Matches
            <TrendingUp className="w-4 h-4 text-blue-500" />
          </div>
          <div className="text-2xl font-bold text-blue-600 mt-2">
            {analytics?.strong_matches || 0}
          </div>
          <div className="text-[11px] text-blue-600 font-medium mt-1">Score 70% – 84%</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <div className="text-xs font-medium text-slate-500 flex items-center justify-between">
            Average Match
            <Sparkles className="w-4 h-4 text-indigo-500" />
          </div>
          <div className="text-2xl font-bold text-indigo-600 mt-2">
            {analytics?.average_score || 0}%
          </div>
          <div className="text-[11px] text-slate-500 mt-1">Weighted profile fit</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <div className="text-xs font-medium text-slate-500 flex items-center justify-between">
            Shortlisted
            <BookmarkCheck className="w-4 h-4 text-purple-500" />
          </div>
          <div className="text-2xl font-bold text-purple-600 mt-2">
            {shortlistCount}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">Auto & manual saves</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <div className="text-xs font-medium text-slate-500 flex items-center justify-between">
            Applied
            <Send className="w-4 h-4 text-cyan-500" />
          </div>
          <div className="text-2xl font-bold text-cyan-600 mt-2">
            {appCount}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">Tracked applications</div>
        </div>
      </div>

      {/* Analytics & Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Score Distribution Chart */}
        <div className="lg:col-span-2 bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-bold text-slate-900">Compatibility Score Distribution</h2>
              <p className="text-xs text-slate-500">Distribution of all active jobs against your resume</p>
            </div>
            <span className="text-xs font-medium text-indigo-600 bg-indigo-50 px-2.5 py-1 rounded-md border border-indigo-100">
              Target Threshold: 70%
            </span>
          </div>

          <div className="h-64 w-full">
            {analytics && analytics.score_distribution && analytics.score_distribution.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={analytics.score_distribution}>
                  <XAxis dataKey="range" stroke="#94A3B8" fontSize={11} tickLine={false} />
                  <YAxis stroke="#94A3B8" fontSize={11} tickLine={false} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1E293B',
                      color: '#F8FAFC',
                      borderRadius: '8px',
                      fontSize: '12px',
                    }}
                  />
                  <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                    {analytics.score_distribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={barColors[index % barColors.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-400">
                Loading score analytics...
              </div>
            )}
          </div>
        </div>

        {/* Top In-Demand & Missing Skills */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900 mb-1">Market Skill Alignment</h2>
            <p className="text-xs text-slate-500 mb-4">Frequency of skills requested across target roles</p>

            <div className="space-y-4">
              <div>
                <div className="text-xs font-semibold text-emerald-800 uppercase tracking-wider mb-2">
                  Top Matched Strengths
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {analytics?.top_matched_skills.slice(0, 6).map((item, i) => (
                    <span
                      key={i}
                      className="px-2 py-1 bg-emerald-50 text-emerald-700 text-xs font-medium rounded border border-emerald-200 flex items-center gap-1"
                    >
                      <span>{item.skill}</span>
                      <span className="text-[10px] bg-emerald-200/60 px-1 rounded-full font-bold">
                        {item.count}
                      </span>
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <div className="text-xs font-semibold text-amber-800 uppercase tracking-wider mb-2">
                  Frequent Market Gaps
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {analytics?.top_missing_skills.slice(0, 6).map((item, i) => (
                    <span
                      key={i}
                      className="px-2 py-1 bg-amber-50 text-amber-700 text-xs font-medium rounded border border-amber-200 flex items-center gap-1"
                    >
                      <span>{item.skill}</span>
                      <span className="text-[10px] bg-amber-200/60 px-1 rounded-full font-bold">
                        {item.count}
                      </span>
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] text-slate-400">
            Tip: Highlighting missing preferred skills in project highlights can raise scores by up to 15%.
          </div>
        </div>
      </div>

      {/* Top Matching Opportunities */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-bold text-slate-900">Top Matching Opportunities</h2>
            <p className="text-xs text-slate-500">Highest compatibility roles discovered for your profile</p>
          </div>
          <Link
            to="/jobs"
            className="text-xs font-semibold text-indigo-600 hover:text-indigo-800 flex items-center gap-1"
          >
            View all ({analytics?.total_matched || 0})
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {recentJobs.map((job) => (
            <JobCard
              key={job.id}
              job={job}
              onViewDetails={(j) => setSelectedJob(j)}
            />
          ))}
        </div>
      </div>

      {/* Detail Modal */}
      <JobDetailModal
        job={selectedJob}
        onClose={() => setSelectedJob(null)}
        onUpdate={loadData}
      />
    </div>
  );
};

