import axios from 'axios';
import {
  Resume,
  Job,
  JobMatch,
  ShortlistedJob,
  JobApplication,
  JobSearchPreferences,
  MatchAnalytics,
  SyncStatus,
} from '../types';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const resumeService = {
  uploadResume: async (file: File): Promise<Resume> => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await api.post<Resume>('/resumes/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },
  getResumes: async (): Promise<Resume[]> => {
    const res = await api.get<Resume[]>('/resumes');
    return res.data;
  },
  getResume: async (id: number): Promise<Resume> => {
    const res = await api.get<Resume>(`/resumes/${id}`);
    return res.data;
  },
  updateResume: async (id: number, data: Partial<Resume>): Promise<Resume> => {
    const res = await api.put<Resume>(`/resumes/${id}`, data);
    return res.data;
  },
  deleteResume: async (id: number): Promise<void> => {
    await api.delete(`/resumes/${id}`);
  },
};

export const jobService = {
  getJobs: async (params?: {
    keyword?: string;
    location?: string;
    work_mode?: string;
    source?: string;
    min_score?: number;
    page?: number;
    page_size?: number;
    sort_by?: string;
    sort_order?: string;
  }): Promise<{ items: Job[]; total: number; page: number; total_pages: number }> => {
    const res = await api.get('/jobs', { params });
    return res.data;
  },
  getJob: async (id: number): Promise<Job> => {
    const res = await api.get<Job>(`/jobs/${id}`);
    return res.data;
  },
  triggerSync: async (): Promise<{ status: string; message: string; results: any }> => {
    const res = await api.post('/jobs/sync');
    return res.data;
  },
  getSyncStatus: async (): Promise<SyncStatus> => {
    const res = await api.get<SyncStatus>('/jobs/sync/status');
    return res.data;
  },
  importJob: async (data: any): Promise<Job> => {
    const res = await api.post<Job>('/jobs/import', data);
    return res.data;
  },
};

export const matchService = {
  runMatches: async (data?: { resume_id?: number; job_ids?: number[] }) => {
    const res = await api.post('/matches/run', data || {});
    return res.data;
  },
  getMatches: async (params?: { resume_id?: number; min_score?: number; limit?: number }): Promise<JobMatch[]> => {
    const res = await api.get<JobMatch[]>('/matches', { params });
    return res.data;
  },
  getMatch: async (id: number): Promise<JobMatch> => {
    const res = await api.get<JobMatch>(`/matches/${id}`);
    return res.data;
  },
  getAnalytics: async (): Promise<MatchAnalytics> => {
    const res = await api.get<MatchAnalytics>('/matches/analytics');
    return res.data;
  },
};

export const shortlistService = {
  getShortlist: async (statusFilter?: string): Promise<ShortlistedJob[]> => {
    const res = await api.get<ShortlistedJob[]>('/shortlist', {
      params: { status_filter: statusFilter },
    });
    return res.data;
  },
  addToShortlist: async (jobId: number, data?: { status?: string; notes?: string }): Promise<ShortlistedJob> => {
    const res = await api.post<ShortlistedJob>(`/shortlist/${jobId}`, data || {});
    return res.data;
  },
  updateShortlist: async (jobId: number, data: { status?: string; notes?: string }): Promise<ShortlistedJob> => {
    const res = await api.patch<ShortlistedJob>(`/shortlist/${jobId}`, data);
    return res.data;
  },
  removeFromShortlist: async (jobId: number): Promise<void> => {
    await api.delete(`/shortlist/${jobId}`);
  },
};

export const applicationService = {
  getApplications: async (statusFilter?: string): Promise<JobApplication[]> => {
    const res = await api.get<JobApplication[]>('/applications', {
      params: { status_filter: statusFilter },
    });
    return res.data;
  },
  createOrUpdateApplication: async (data: {
    job_id: number;
    application_status: string;
    applied_at?: string;
    follow_up_date?: string;
    notes?: string;
  }): Promise<JobApplication> => {
    const res = await api.post<JobApplication>('/applications', data);
    return res.data;
  },
  updateApplication: async (
    id: number,
    data: {
      application_status?: string;
      applied_at?: string;
      follow_up_date?: string;
      notes?: string;
    }
  ): Promise<JobApplication> => {
    const res = await api.patch<JobApplication>(`/applications/${id}`, data);
    return res.data;
  },
};

export const preferenceService = {
  getPreferences: async (): Promise<JobSearchPreferences> => {
    const res = await api.get<JobSearchPreferences>('/preferences');
    return res.data;
  },
  updatePreferences: async (data: Partial<JobSearchPreferences>): Promise<JobSearchPreferences> => {
    const res = await api.put<JobSearchPreferences>('/preferences', data);
    return res.data;
  },
};

export const healthService = {
  getHealth: async () => {
    const res = await api.get('/health');
    return res.data;
  },
};

export default api;

