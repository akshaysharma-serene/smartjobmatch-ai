import React, { useEffect, useState } from 'react';
import {
  BookmarkCheck,
  Building2,
  MapPin,
  Briefcase,
  DollarSign,
  Trash2,
  Send,
  ExternalLink,
  MessageSquare,
  X,
  Save,
  CheckCircle2,
} from 'lucide-react';
import { shortlistService, applicationService } from '../services/api';
import { ShortlistedJob } from '../types';
import { ScoreBadge } from '../components/ScoreBadge';
import { SourceBadge } from '../components/SourceBadge';
import { JobDetailModal } from '../components/JobDetailModal';

export const ShortlistPage: React.FC = () => {
  const [shortlist, setShortlist] = useState<ShortlistedJob[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [activeTab, setActiveTab] = useState<string>('shortlisted');
  const [editingNotesId, setEditingNotesId] = useState<number | null>(null);
  const [notesText, setNotesText] = useState<string>('');
  const [selectedJob, setSelectedJob] = useState<any>(null);
  const [bannerMsg, setBannerMsg] = useState<string | null>(null);

  const fetchShortlist = async () => {
    setLoading(true);
    try {
      const data = await shortlistService.getShortlist(activeTab === 'all' ? undefined : activeTab);
      setShortlist(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchShortlist();
  }, [activeTab]);

  const handleRemove = async (jobId: number) => {
    try {
      await shortlistService.removeFromShortlist(jobId);
      setBannerMsg('Job removed from shortlist.');
      fetchShortlist();
    } catch (err) {
      console.error(err);
    }
  };

  const handleMoveToTracker = async (entry: ShortlistedJob) => {
    try {
      await applicationService.createOrUpdateApplication({
        job_id: entry.job_id,
        application_status: 'To Apply',
        notes: entry.notes || undefined,
      });
      setBannerMsg(`Moved "${entry.job.title}" to Application Tracker!`);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSaveNotes = async (jobId: number) => {
    try {
      await shortlistService.updateShortlist(jobId, { notes: notesText });
      setEditingNotesId(null);
      fetchShortlist();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Smart Shortlist</h1>
          <p className="text-xs text-slate-500">
            Roles meeting your 70%+ compatibility criteria or saved manually for targeted applications
          </p>
        </div>

        {/* Tab Filters */}
        <div className="bg-slate-100 p-1 rounded-xl flex items-center text-xs font-semibold">
          <button
            onClick={() => setActiveTab('shortlisted')}
            className={`px-3 py-1.5 rounded-lg transition ${
              activeTab === 'shortlisted' ? 'bg-white text-indigo-700 shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Active Shortlist
          </button>
          <button
            onClick={() => setActiveTab('saved')}
            className={`px-3 py-1.5 rounded-lg transition ${
              activeTab === 'saved' ? 'bg-white text-indigo-700 shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Saved For Later
          </button>
          <button
            onClick={() => setActiveTab('rejected')}
            className={`px-3 py-1.5 rounded-lg transition ${
              activeTab === 'rejected' ? 'bg-white text-indigo-700 shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Archived / Rejected
          </button>
        </div>
      </div>

      {bannerMsg && (
        <div className="bg-indigo-50 border border-indigo-200 p-3 rounded-xl text-xs font-medium text-indigo-800 flex items-center justify-between">
          <span>{bannerMsg}</span>
          <button onClick={() => setBannerMsg(null)} className="text-indigo-600 hover:underline">
            Dismiss
          </button>
        </div>
      )}

      {/* Shortlist Table / Cards */}
      {loading ? (
        <div className="p-16 text-center text-xs text-slate-400">Loading shortlisted jobs...</div>
      ) : shortlist.length > 0 ? (
        <div className="space-y-4">
          {shortlist.map((item) => (
            <div
              key={item.id}
              className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs hover:shadow-md transition flex flex-col md:flex-row items-start md:items-center justify-between gap-5"
            >
              {/* Job Info Left */}
              <div className="flex-1 space-y-2">
                <div className="flex items-center gap-2 flex-wrap">
                  <SourceBadge source={item.job.source} />
                  <span className="text-xs px-2 py-0.5 rounded font-medium bg-slate-100 text-slate-600 border border-slate-200">
                    {item.job.work_mode || 'Hybrid'}
                  </span>
                  <span className="text-xs text-slate-400">
                    Added {new Date(item.shortlisted_at).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' })}
                  </span>
                </div>

                <div className="flex items-start justify-between">
                  <div>
                    <h3
                      onClick={() => setSelectedJob(item.job)}
                      className="text-base font-bold text-slate-900 hover:text-indigo-600 cursor-pointer transition"
                    >
                      {item.job.title}
                    </h3>
                    <div className="flex items-center gap-3 text-xs text-slate-600 mt-1 flex-wrap">
                      <span className="flex items-center gap-1 font-medium text-slate-800">
                        <Building2 className="w-3.5 h-3.5 text-slate-400" />
                        {item.job.company}
                      </span>
                      <span className="flex items-center gap-1">
                        <MapPin className="w-3.5 h-3.5 text-slate-400" />
                        {item.job.location || 'Bengaluru, India'}
                      </span>
                      {item.job.minimum_experience !== null && item.job.minimum_experience !== undefined && (
                        <span className="flex items-center gap-1">
                          <Briefcase className="w-3.5 h-3.5 text-slate-400" />
                          {item.job.minimum_experience}
                          {item.job.maximum_experience ? `–${item.job.maximum_experience}` : '+'} yrs exp
                        </span>
                      )}
                      {item.job.salary_min && (
                        <span className="font-semibold text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded">
                          ₹{(item.job.salary_min / 100000).toFixed(1)}L PA
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Skills tags */}
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {item.job.required_skills.slice(0, 6).map((skill, i) => (
                    <span
                      key={i}
                      className="px-2 py-0.5 text-xs font-medium rounded-md bg-slate-100 text-slate-700"
                    >
                      {skill}
                    </span>
                  ))}
                </div>

                {/* Notes Display / Edit */}
                <div className="pt-2">
                  {editingNotesId === item.job_id ? (
                    <div className="flex items-center gap-2">
                      <input
                        type="text"
                        placeholder="Add personal notes, referral name, or follow-up date..."
                        value={notesText}
                        onChange={(e) => setNotesText(e.target.value)}
                        className="px-3 py-1.5 text-xs border border-slate-300 rounded-lg flex-1 focus:ring-2 focus:ring-indigo-500"
                      />
                      <button
                        onClick={() => handleSaveNotes(item.job_id)}
                        className="px-3 py-1.5 bg-emerald-600 text-white text-xs font-semibold rounded-lg hover:bg-emerald-700"
                      >
                        Save
                      </button>
                      <button
                        onClick={() => setEditingNotesId(null)}
                        className="px-2 py-1.5 text-slate-500 text-xs hover:underline"
                      >
                        Cancel
                      </button>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2 text-xs text-slate-500">
                      <MessageSquare className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                      <span className="italic">{item.notes || 'No notes added yet.'}</span>
                      <button
                        onClick={() => {
                          setEditingNotesId(item.job_id);
                          setNotesText(item.notes || '');
                        }}
                        className="text-indigo-600 hover:underline font-medium text-[11px] ml-1"
                      >
                        Edit Note
                      </button>
                    </div>
                  )}
                </div>
              </div>

              {/* Match Score & Actions Right */}
              <div className="flex flex-row md:flex-col items-center md:items-end justify-between w-full md:w-auto pt-3 md:pt-0 border-t md:border-t-0 border-slate-100 gap-3">
                <ScoreBadge score={item.match_score} size="lg" />

                <div className="flex items-center gap-2 flex-wrap">
                  <button
                    onClick={() => handleMoveToTracker(item)}
                    className="inline-flex items-center gap-1 px-3 py-1.5 bg-blue-50 text-blue-700 hover:bg-blue-100 font-semibold rounded-lg text-xs transition"
                  >
                    <Send className="w-3.5 h-3.5" />
                    Track
                  </button>

                  {item.job.application_url && (
                    <a
                      href={item.job.application_url}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1 px-3 py-1.5 bg-indigo-600 text-white hover:bg-indigo-700 font-semibold rounded-lg text-xs transition shadow-xs"
                    >
                      Apply
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  )}

                  <button
                    onClick={() => handleRemove(item.job_id)}
                    className="p-1.5 text-slate-400 hover:text-red-600 rounded-lg hover:bg-slate-100 transition"
                    title="Remove from shortlist"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white p-12 text-center rounded-2xl border border-slate-200 max-w-md mx-auto">
          <BookmarkCheck className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-900">No jobs in this shortlist</h3>
          <p className="text-xs text-slate-500 mt-1 mb-4">
            Jobs matching your 70%+ threshold appear here automatically, or you can bookmark them from Job Search.
          </p>
        </div>
      )}

      {/* Details Modal */}
      <JobDetailModal
        job={selectedJob}
        onClose={() => setSelectedJob(null)}
        onUpdate={fetchShortlist}
      />
    </div>
  );
};

