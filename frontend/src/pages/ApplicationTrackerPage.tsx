import React, { useEffect, useState } from 'react';
import {
  KanbanSquare,
  Building2,
  Calendar,
  ExternalLink,
  Plus,
  Clock,
  CheckCircle2,
  AlertCircle,
  FileText,
  ChevronRight,
  MoreVertical,
} from 'lucide-react';
import { applicationService, jobService } from '../services/api';
import { JobApplication, ApplicationStatus, Job } from '../types';
import { ScoreBadge } from '../components/ScoreBadge';

const STATUS_COLUMNS: { key: ApplicationStatus; label: string; color: string; border: string }[] = [
  { key: 'To Apply', label: 'To Apply', color: 'bg-slate-100 text-slate-800', border: 'border-slate-300' },
  { key: 'Applied', label: 'Applied', color: 'bg-blue-50 text-blue-800', border: 'border-blue-300' },
  { key: 'Assessment', label: 'Assessment / OA', color: 'bg-purple-50 text-purple-800', border: 'border-purple-300' },
  { key: 'Interview', label: 'Interviewing', color: 'bg-amber-50 text-amber-800', border: 'border-amber-300' },
  { key: 'Offer', label: 'Offer Received', color: 'bg-emerald-50 text-emerald-800', border: 'border-emerald-300' },
  { key: 'Rejected', label: 'Rejected', color: 'bg-rose-50 text-rose-800', border: 'border-rose-300' },
];

export const ApplicationTrackerPage: React.FC = () => {
  const [applications, setApplications] = useState<JobApplication[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [isAddOpen, setIsAddOpen] = useState<boolean>(false);
  const [availableJobs, setAvailableJobs] = useState<Job[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<number | ''>('');
  const [newStatus, setNewStatus] = useState<ApplicationStatus>('Applied');
  const [newNotes, setNewNotes] = useState<string>('');

  const fetchApplications = async () => {
    setLoading(true);
    try {
      const data = await applicationService.getApplications();
      setApplications(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApplications();
    jobService.getJobs({ page_size: 50 }).then((res) => setAvailableJobs(res.items)).catch(console.error);
  }, []);

  const handleStatusChange = async (appId: number, nextStatus: ApplicationStatus) => {
    try {
      await applicationService.updateApplication(appId, { application_status: nextStatus });
      fetchApplications();
    } catch (err) {
      console.error(err);
    }
  };

  const handleAddApplication = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedJobId) return;
    try {
      await applicationService.createOrUpdateApplication({
        job_id: Number(selectedJobId),
        application_status: newStatus,
        notes: newNotes,
        applied_at: newStatus === 'Applied' ? new Date().toISOString() : undefined,
      });
      setIsAddOpen(false);
      setSelectedJobId('');
      setNewNotes('');
      fetchApplications();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Application Pipeline Tracker</h1>
          <p className="text-xs text-slate-500">
            Track interview rounds, assessments, and offers for your target applications
          </p>
        </div>

        <button
          onClick={() => setIsAddOpen(true)}
          className="inline-flex items-center gap-1.5 px-3.5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold shadow-xs transition"
        >
          <Plus className="w-4 h-4" />
          Add Tracked Job
        </button>
      </div>

      {/* Kanban Board */}
      {loading ? (
        <div className="p-16 text-center text-xs text-slate-400">Loading applications...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 items-start">
          {STATUS_COLUMNS.map((col) => {
            const colApps = applications.filter((a) => a.application_status === col.key);
            return (
              <div key={col.key} className="bg-slate-100/70 rounded-2xl p-3 border border-slate-200 min-h-[480px]">
                {/* Column Header */}
                <div className="flex items-center justify-between mb-3 px-1">
                  <div className="flex items-center gap-1.5">
                    <span className="font-bold text-xs text-slate-800">{col.label}</span>
                    <span className="text-[11px] font-bold px-1.5 py-0.2 rounded-full bg-slate-200 text-slate-700">
                      {colApps.length}
                    </span>
                  </div>
                </div>

                {/* Column Cards */}
                <div className="space-y-2.5">
                  {colApps.map((app) => (
                    <div
                      key={app.id}
                      className="bg-white rounded-xl p-3.5 border border-slate-200 shadow-xs hover:shadow-md transition text-xs space-y-2"
                    >
                      <div className="flex items-start justify-between gap-1">
                        <h4 className="font-bold text-slate-900 line-clamp-1">{app.job.title}</h4>
                        <ScoreBadge score={app.job.match_score} size="sm" showLabel={false} />
                      </div>

                      <div className="flex items-center gap-1 text-[11px] font-medium text-slate-600">
                        <Building2 className="w-3 h-3 text-slate-400 shrink-0" />
                        <span className="truncate">{app.job.company}</span>
                      </div>

                      {app.applied_at && (
                        <div className="text-[10px] text-slate-400 flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          Applied {new Date(app.applied_at).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' })}
                        </div>
                      )}

                      {app.notes && (
                        <div className="p-2 bg-slate-50 rounded text-[11px] text-slate-600 line-clamp-2 border border-slate-100">
                          {app.notes}
                        </div>
                      )}

                      {/* Transition Dropdown / Quick Mover */}
                      <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                        <select
                          value={app.application_status}
                          onChange={(e) => handleStatusChange(app.id, e.target.value as ApplicationStatus)}
                          className="text-[10px] bg-slate-50 border border-slate-200 rounded px-1.5 py-1 text-slate-700 font-medium"
                        >
                          {STATUS_COLUMNS.map((c) => (
                            <option key={c.key} value={c.key}>
                              &rarr; {c.label}
                            </option>
                          ))}
                        </select>

                        {app.job.application_url && (
                          <a
                            href={app.job.application_url}
                            target="_blank"
                            rel="noreferrer"
                            className="text-slate-400 hover:text-indigo-600 p-1"
                            title="Open application URL"
                          >
                            <ExternalLink className="w-3.5 h-3.5" />
                          </a>
                        )}
                      </div>
                    </div>
                  ))}

                  {colApps.length === 0 && (
                    <div className="p-6 text-center text-[11px] text-slate-400 border border-dashed border-slate-200 rounded-xl">
                      Empty
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Add Tracked Job Modal */}
      {isAddOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl w-full max-w-md p-6">
            <h2 className="text-lg font-bold text-slate-900 mb-4">Track Job Application</h2>

            <form onSubmit={handleAddApplication} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Select Discovered Job *</label>
                <select
                  required
                  value={selectedJobId}
                  onChange={(e) => setSelectedJobId(Number(e.target.value))}
                  className="w-full p-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">Choose a job...</option>
                  {availableJobs.map((j) => (
                    <option key={j.id} value={j.id}>
                      {j.title} — {j.company} ({j.match_score || 0}% match)
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Status</label>
                <select
                  value={newStatus}
                  onChange={(e) => setNewStatus(e.target.value as ApplicationStatus)}
                  className="w-full p-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                >
                  {STATUS_COLUMNS.map((c) => (
                    <option key={c.key} value={c.key}>
                      {c.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Notes</label>
                <textarea
                  rows={3}
                  placeholder="Referral name, recruiter contact, interview date..."
                  value={newNotes}
                  onChange={(e) => setNewNotes(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setIsAddOpen(false)}
                  className="px-3.5 py-1.5 border border-slate-300 text-slate-700 rounded-lg font-semibold hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold shadow-xs"
                >
                  Add to Pipeline
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

