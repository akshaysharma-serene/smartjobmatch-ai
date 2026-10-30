import React, { useEffect, useState } from 'react';
import {
  Search,
  Filter,
  RefreshCw,
  Plus,
  MapPin,
  Briefcase,
  DollarSign,
  Building2,
  X,
  ChevronLeft,
  ChevronRight,
  Sparkles,
} from 'lucide-react';
import { jobService, shortlistService } from '../services/api';
import { Job, SyncStatus } from '../types';
import { JobCard } from '../components/JobCard';
import { JobDetailModal } from '../components/JobDetailModal';

export const JobSearchPage: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [page, setPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(true);

  // Filters
  const [keyword, setKeyword] = useState<string>('');
  const [location, setLocation] = useState<string>('');
  const [workMode, setWorkMode] = useState<string>('');
  const [source, setSource] = useState<string>('');
  const [minScore, setMinScore] = useState<number | undefined>(undefined);
  const [sortBy, setSortBy] = useState<string>('match_score');
  const [sortOrder, setSortOrder] = useState<string>('desc');

  // Modal states
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [isImportOpen, setIsImportOpen] = useState<boolean>(false);
  const [importForm, setImportForm] = useState({
    title: '',
    company: '',
    description: '',
    location: 'Bengaluru, Karnataka, India',
    work_mode: 'Hybrid',
    job_url: '',
  });
  const [syncStatus, setSyncStatus] = useState<SyncStatus | null>(null);

  const fetchJobs = async () => {
    setLoading(true);
    try {
      const data = await jobService.getJobs({
        keyword: keyword || undefined,
        location: location || undefined,
        work_mode: workMode || undefined,
        source: source || undefined,
        min_score: minScore,
        page,
        page_size: 12,
        sort_by: sortBy,
        sort_order: sortOrder,
      });
      setJobs(data.items);
      setTotal(data.total);
      setTotalPages(data.total_pages);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
    jobService.getSyncStatus().then((s) => setSyncStatus(s)).catch(console.error);
  }, [page, minScore, workMode, source, sortBy, sortOrder]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchJobs();
  };

  const handleToggleShortlist = async (job: Job) => {
    try {
      await shortlistService.addToShortlist(job.id);
      fetchJobs();
    } catch (err) {
      console.error(err);
    }
  };

  const handleImportJob = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await jobService.importJob(importForm);
      setIsImportOpen(false);
      setImportForm({
        title: '',
        company: '',
        description: '',
        location: 'Bengaluru, Karnataka, India',
        work_mode: 'Hybrid',
        job_url: '',
      });
      fetchJobs();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Title & Import Trigger */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Job Discovery & Search</h1>
          <p className="text-xs text-slate-500">
            {total} opportunities indexed across LinkedIn (Real-time), Greenhouse, Lever, and Verified Feeds
          </p>
        </div>

        <button
          onClick={() => setIsImportOpen(true)}
          className="inline-flex items-center gap-1.5 px-3.5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold shadow-xs transition"
        >
          <Plus className="w-4 h-4" />
          Import Job Listing / URL
        </button>
      </div>

      {/* Sources Health Pill Shelf */}
      {syncStatus && (
        <div className="bg-slate-50 p-3 rounded-xl border border-slate-200 flex items-center gap-4 overflow-x-auto text-xs">
          <span className="font-semibold text-slate-500 shrink-0">Connected Adapters:</span>
          {syncStatus.sources.map((s, idx) => (
            <div
              key={idx}
              className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-white border border-slate-200 rounded-md shrink-0 shadow-2xs"
            >
              <span
                className={`w-2 h-2 rounded-full ${
                  s.status === 'connected' || s.status === 'ready' ? 'bg-emerald-500' : 'bg-blue-400'
                }`}
              />
              <span className="font-medium text-slate-800 capitalize">{s.source}</span>
              <span className="text-[10px] text-slate-400">
                ({s.is_mock ? 'Mock Mode' : 'Real-time Scraper'})
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Search & Filter Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-3">
        <form onSubmit={handleSearchSubmit} className="flex items-center gap-3 flex-wrap sm:flex-nowrap">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by title, skills, keyword, or company (e.g. Spring Boot, Target, React)..."
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>

          <div className="relative w-full sm:w-56">
            <MapPin className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Location (e.g. Bengaluru)..."
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="w-full pl-9 pr-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <button
            type="submit"
            className="px-5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs rounded-lg shadow-xs transition"
          >
            Search
          </button>
        </form>

        {/* Quick Dropdown Filters */}
        <div className="flex items-center justify-between gap-3 flex-wrap pt-2 border-t border-slate-100 text-xs">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-slate-400 font-medium">Filters:</span>

            {/* Work Mode */}
            <select
              value={workMode}
              onChange={(e) => {
                setWorkMode(e.target.value);
                setPage(1);
              }}
              className="px-2.5 py-1.5 border border-slate-200 rounded-md bg-slate-50 text-slate-700 text-xs focus:ring-1 focus:ring-indigo-500"
            >
              <option value="">All Work Modes</option>
              <option value="Remote">Remote</option>
              <option value="Hybrid">Hybrid</option>
              <option value="On-site">On-site</option>
            </select>

            {/* Min Match Score */}
            <select
              value={minScore || ''}
              onChange={(e) => {
                setMinScore(e.target.value ? Number(e.target.value) : undefined);
                setPage(1);
              }}
              className="px-2.5 py-1.5 border border-slate-200 rounded-md bg-slate-50 text-slate-700 text-xs focus:ring-1 focus:ring-indigo-500"
            >
              <option value="">Any Match Score</option>
              <option value="85">Excellent (85%+)</option>
              <option value="70">Strong (70%+)</option>
              <option value="55">Potential (55%+)</option>
            </select>

            {/* Source */}
            <select
              value={source}
              onChange={(e) => {
                setSource(e.target.value);
                setPage(1);
              }}
              className="px-2.5 py-1.5 border border-slate-200 rounded-md bg-slate-50 text-slate-700 text-xs focus:ring-1 focus:ring-indigo-500"
            >
              <option value="">All Sources</option>
              <option value="linkedin">LinkedIn (Real-time)</option>
              <option value="curated_feed">Verified Feed</option>
              <option value="linkedin_mock">LinkedIn (Mock)</option>
              <option value="greenhouse">Greenhouse</option>
              <option value="lever">Lever</option>
              <option value="manual">Manual Import</option>
            </select>

            {(keyword || location || workMode || source || minScore) && (
              <button
                onClick={() => {
                  setKeyword('');
                  setLocation('');
                  setWorkMode('');
                  setSource('');
                  setMinScore(undefined);
                  setPage(1);
                  fetchJobs();
                }}
                className="text-xs text-indigo-600 hover:underline font-medium"
              >
                Reset Filters
              </button>
            )}
          </div>

          {/* Sort By */}
          <div className="flex items-center gap-2">
            <span className="text-slate-400 font-medium">Sort by:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-2.5 py-1.5 border border-slate-200 rounded-md bg-slate-50 text-slate-700 text-xs"
            >
              <option value="match_score">Match Compatibility</option>
              <option value="posted_at">Posting Date</option>
              <option value="created_at">Discovered Date</option>
            </select>
          </div>
        </div>
      </div>

      {/* Job Grid */}
      {loading ? (
        <div className="p-16 text-center text-xs text-slate-400">Loading discovered jobs...</div>
      ) : jobs.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {jobs.map((job) => (
            <JobCard
              key={job.id}
              job={job}
              onViewDetails={(j) => setSelectedJob(j)}
              onToggleShortlist={handleToggleShortlist}
            />
          ))}
        </div>
      ) : (
        <div className="bg-white p-12 text-center rounded-2xl border border-slate-200 max-w-md mx-auto">
          <Search className="w-10 h-10 text-slate-400 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-900">No matching jobs found</h3>
          <p className="text-xs text-slate-500 mt-1 mb-4">
            Try broadening your search keywords or resetting your minimum match threshold.
          </p>
          <button
            onClick={() => {
              setKeyword('');
              setLocation('');
              setWorkMode('');
              setMinScore(undefined);
              fetchJobs();
            }}
            className="px-4 py-2 bg-indigo-50 text-indigo-700 font-semibold text-xs rounded-lg hover:bg-indigo-100"
          >
            Clear Filters
          </button>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between bg-white px-4 py-3 border border-slate-200 rounded-xl shadow-xs text-xs">
          <div className="text-slate-500">
            Showing Page <span className="font-bold text-slate-800">{page}</span> of{' '}
            <span className="font-bold text-slate-800">{totalPages}</span> ({total} total results)
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="p-1.5 rounded border border-slate-200 disabled:opacity-40 hover:bg-slate-50"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="p-1.5 rounded border border-slate-200 disabled:opacity-40 hover:bg-slate-50"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Details Modal */}
      <JobDetailModal
        job={selectedJob}
        onClose={() => setSelectedJob(null)}
        onUpdate={fetchJobs}
      />

      {/* Manual Import Modal */}
      {isImportOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl w-full max-w-xl p-6">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <h2 className="text-lg font-bold text-slate-900">Import Job Listing</h2>
              <button onClick={() => setIsImportOpen(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleImportJob} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Job Title *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Senior Java Backend Developer"
                  value={importForm.title}
                  onChange={(e) => setImportForm({ ...importForm, title: e.target.value })}
                  className="w-full p-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Company Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Target, Infosys, Flipkart"
                  value={importForm.company}
                  onChange={(e) => setImportForm({ ...importForm, company: e.target.value })}
                  className="w-full p-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Location</label>
                  <input
                    type="text"
                    value={importForm.location}
                    onChange={(e) => setImportForm({ ...importForm, location: e.target.value })}
                    className="w-full p-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Work Mode</label>
                  <select
                    value={importForm.work_mode}
                    onChange={(e) => setImportForm({ ...importForm, work_mode: e.target.value })}
                    className="w-full p-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="Hybrid">Hybrid</option>
                    <option value="Remote">Remote</option>
                    <option value="On-site">On-site</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Original Listing URL</label>
                <input
                  type="url"
                  placeholder="https://www.linkedin.com/jobs/view/..."
                  value={importForm.job_url}
                  onChange={(e) => setImportForm({ ...importForm, job_url: e.target.value })}
                  className="w-full p-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Job Description *</label>
                <textarea
                  required
                  rows={5}
                  placeholder="Paste job description requirements and technical stack here..."
                  value={importForm.description}
                  onChange={(e) => setImportForm({ ...importForm, description: e.target.value })}
                  className="w-full p-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 font-mono text-xs"
                />
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setIsImportOpen(false)}
                  className="px-4 py-2 border border-slate-300 text-slate-700 rounded-lg font-semibold hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold shadow-xs"
                >
                  Normalize & Save Job
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

