import React, { useEffect, useState, useRef } from 'react';
import {
  UploadCloud,
  FileText,
  CheckCircle2,
  AlertCircle,
  Briefcase,
  GraduationCap,
  Award,
  FolderGit2,
  Edit3,
  Save,
  Trash2,
  Plus,
  RefreshCw,
  User,
} from 'lucide-react';
import { resumeService } from '../services/api';
import { Resume, ResumeParsedData } from '../types';

export const ResumePage: React.FC = () => {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [activeResume, setActiveResume] = useState<Resume | null>(null);
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [editForm, setEditForm] = useState<ResumeParsedData | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [newSkill, setNewSkill] = useState<string>('');
  const [statusMsg, setStatusMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchResumes = async () => {
    try {
      const data = await resumeService.getResumes();
      setResumes(data);
      const active = data.find((r) => r.is_active) || data[0] || null;
      setActiveResume(active);
      if (active) {
        setEditForm(JSON.parse(JSON.stringify(active.parsed_data)));
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchResumes();
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setStatusMsg(null);
    try {
      const uploaded = await resumeService.uploadResume(file);
      setStatusMsg({ type: 'success', text: `Successfully parsed and activated ${file.name}!` });
      await fetchResumes();
    } catch (err: any) {
      setStatusMsg({
        type: 'error',
        text: err.response?.data?.detail || 'Failed to upload and parse resume file.',
      });
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleSelectResume = async (resume: Resume) => {
    try {
      await resumeService.updateResume(resume.id, { is_active: true });
      await fetchResumes();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteResume = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this resume version?')) return;
    try {
      await resumeService.deleteResume(id);
      await fetchResumes();
    } catch (err) {
      console.error(err);
    }
  };

  const handleSaveProfile = async () => {
    if (!activeResume || !editForm) return;
    try {
      await resumeService.updateResume(activeResume.id, { parsed_data: editForm });
      setIsEditing(false);
      setStatusMsg({ type: 'success', text: 'Resume profile updated successfully!' });
      await fetchResumes();
    } catch (err) {
      setStatusMsg({ type: 'error', text: 'Failed to update resume profile.' });
    }
  };

  const handleAddSkill = () => {
    if (!newSkill.trim() || !editForm) return;
    if (!editForm.skills.includes(newSkill.trim())) {
      setEditForm({
        ...editForm,
        skills: [...editForm.skills, newSkill.trim()],
      });
    }
    setNewSkill('');
  };

  const handleRemoveSkill = (skill: string) => {
    if (!editForm) return;
    setEditForm({
      ...editForm,
      skills: editForm.skills.filter((s) => s !== skill),
    });
  };

  return (
    <div className="space-y-6">
      {/* Page Title & Actions */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Resume & Candidate Profile</h1>
          <p className="text-xs text-slate-500">
            Manage your parsed resume data, technical skills, and active version for matching
          </p>
        </div>

        <div className="flex items-center gap-3">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            accept=".pdf,.docx"
            className="hidden"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="inline-flex items-center gap-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold shadow-xs transition"
          >
            <UploadCloud className="w-4 h-4" />
            {uploading ? 'Extracting text...' : 'Upload PDF / DOCX'}
          </button>
        </div>
      </div>

      {statusMsg && (
        <div
          className={`p-4 rounded-xl text-xs font-medium flex items-center justify-between border ${
            statusMsg.type === 'success'
              ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
              : 'bg-red-50 text-red-800 border-red-200'
          }`}
        >
          <div className="flex items-center gap-2">
            {statusMsg.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            ) : (
              <AlertCircle className="w-4 h-4 text-red-600 shrink-0" />
            )}
            <span>{statusMsg.text}</span>
          </div>
          <button onClick={() => setStatusMsg(null)} className="text-xs hover:underline">
            Dismiss
          </button>
        </div>
      )}

      {/* Resume Versions Shelf */}
      {resumes.length > 0 && (
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs flex items-center gap-3 overflow-x-auto">
          <span className="text-xs font-semibold text-slate-500 shrink-0">Resume Versions:</span>
          {resumes.map((r) => (
            <div
              key={r.id}
              onClick={() => handleSelectResume(r)}
              className={`cursor-pointer px-3.5 py-2 rounded-lg border text-xs font-medium flex items-center gap-2 shrink-0 transition ${
                r.is_active
                  ? 'bg-indigo-50 border-indigo-300 text-indigo-700 font-bold shadow-xs'
                  : 'bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100'
              }`}
            >
              <FileText className="w-3.5 h-3.5" />
              <span>
                {r.filename} (v{r.version})
              </span>
              {r.is_active && (
                <span className="bg-indigo-600 text-white text-[10px] px-1.5 py-0.2 rounded-full">
                  Active
                </span>
              )}
              {resumes.length > 1 && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteResume(r.id);
                  }}
                  className="p-1 hover:text-red-600 text-slate-400"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {activeResume && editForm ? (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
          {/* Header Card */}
          <div className="p-6 border-b border-slate-100 bg-slate-50/50 flex items-start justify-between flex-wrap gap-4">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-2xl bg-indigo-600 text-white flex items-center justify-center font-bold text-2xl shadow-sm">
                {editForm.full_name?.charAt(0) || 'A'}
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-xl font-bold text-slate-900">{editForm.full_name}</h2>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 font-semibold">
                    Active Profile
                  </span>
                </div>
                <div className="text-sm font-medium text-indigo-600">{editForm.headline}</div>
                <div className="text-xs text-slate-500 mt-1 flex items-center gap-3 flex-wrap">
                  <span>{editForm.email}</span>
                  <span>•</span>
                  <span>{editForm.phone}</span>
                  <span>•</span>
                  <span>{editForm.location}</span>
                  <span>•</span>
                  <span className="font-semibold text-slate-700">
                    {editForm.years_of_experience || 5} Years Experience
                  </span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {isEditing ? (
                <>
                  <button
                    onClick={() => setIsEditing(false)}
                    className="px-3.5 py-1.5 border border-slate-300 text-slate-700 rounded-lg text-xs font-semibold hover:bg-slate-50 transition"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleSaveProfile}
                    className="inline-flex items-center gap-1.5 px-4 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold shadow-xs transition"
                  >
                    <Save className="w-4 h-4" />
                    Save Changes
                  </button>
                </>
              ) : (
                <button
                  onClick={() => setIsEditing(true)}
                  className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-indigo-50 text-indigo-700 hover:bg-indigo-100 rounded-lg text-xs font-semibold border border-indigo-200 transition"
                >
                  <Edit3 className="w-4 h-4" />
                  Edit Extracted Details
                </button>
              )}
            </div>
          </div>

          <div className="p-6 space-y-6">
            {/* Summary */}
            <div>
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-2">
                Professional Summary
              </h3>
              {isEditing ? (
                <textarea
                  rows={3}
                  value={editForm.summary || ''}
                  onChange={(e) => setEditForm({ ...editForm, summary: e.target.value })}
                  className="w-full p-3 text-xs border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 font-sans"
                />
              ) : (
                <p className="text-xs text-slate-600 leading-relaxed bg-slate-50 p-4 rounded-xl border border-slate-200">
                  {editForm.summary || 'No summary provided in resume.'}
                </p>
              )}
            </div>

            {/* Technical Skills */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                  Technical Skills ({editForm.skills.length})
                </h3>
              </div>

              {isEditing && (
                <div className="flex items-center gap-2 mb-3">
                  <input
                    type="text"
                    placeholder="Add a new skill (e.g. Redis, GraphQL)..."
                    value={newSkill}
                    onChange={(e) => setNewSkill(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleAddSkill()}
                    className="px-3 py-1.5 text-xs border border-slate-300 rounded-lg w-64 focus:ring-2 focus:ring-indigo-500"
                  />
                  <button
                    onClick={handleAddSkill}
                    className="px-3 py-1.5 bg-indigo-600 text-white rounded-lg text-xs font-semibold hover:bg-indigo-700 inline-flex items-center gap-1"
                  >
                    <Plus className="w-3.5 h-3.5" /> Add
                  </button>
                </div>
              )}

              <div className="flex flex-wrap gap-1.5">
                {editForm.skills.map((skill, i) => (
                  <span
                    key={i}
                    className="px-2.5 py-1 text-xs font-medium rounded-md bg-indigo-50 text-indigo-700 border border-indigo-200 flex items-center gap-1"
                  >
                    {skill}
                    {isEditing && (
                      <button
                        onClick={() => handleRemoveSkill(skill)}
                        className="hover:text-red-600 ml-1 text-indigo-400"
                      >
                        ×
                      </button>
                    )}
                  </span>
                ))}
              </div>
            </div>

            {/* Employment Experience */}
            <div>
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-3 flex items-center gap-2">
                <Briefcase className="w-4 h-4 text-indigo-600" />
                Employment History
              </h3>
              <div className="space-y-3">
                {editForm.experience.map((exp, idx) => (
                  <div key={idx} className="p-4 rounded-xl border border-slate-200 bg-slate-50/50">
                    <div className="flex items-start justify-between flex-wrap gap-2">
                      <div>
                        <h4 className="text-sm font-bold text-slate-900">{exp.title}</h4>
                        <div className="text-xs font-semibold text-indigo-600">{exp.company}</div>
                      </div>
                      <div className="text-xs text-slate-500 font-medium">
                        {exp.dates} {exp.location && `• ${exp.location}`}
                      </div>
                    </div>
                    {exp.highlights.length > 0 && (
                      <ul className="mt-2.5 space-y-1 text-xs text-slate-600 list-disc list-inside">
                        {exp.highlights.map((h, i) => (
                          <li key={i}>{h}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Key Projects */}
            <div>
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-3 flex items-center gap-2">
                <FolderGit2 className="w-4 h-4 text-indigo-600" />
                Featured Projects
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {editForm.projects.map((proj, idx) => (
                  <div key={idx} className="p-4 rounded-xl border border-slate-200 bg-slate-50/50">
                    <h4 className="text-sm font-bold text-slate-900">{proj.name}</h4>
                    {proj.technologies.length > 0 && (
                      <div className="flex flex-wrap gap-1 my-1.5">
                        {proj.technologies.map((t, i) => (
                          <span
                            key={i}
                            className="px-1.5 py-0.5 text-[10px] font-semibold bg-white text-indigo-600 border border-indigo-200 rounded"
                          >
                            {t}
                          </span>
                        ))}
                      </div>
                    )}
                    <p className="text-xs text-slate-600 mt-1">{proj.description}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Education & Certifications */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-3 flex items-center gap-2">
                  <GraduationCap className="w-4 h-4 text-indigo-600" />
                  Education
                </h3>
                {editForm.education.map((edu, idx) => (
                  <div key={idx} className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/50">
                    <div className="text-xs font-bold text-slate-900">{edu.degree}</div>
                    <div className="text-xs text-slate-600">{edu.institution}</div>
                    <div className="text-[11px] text-slate-400 mt-1">
                      {edu.year} {edu.details && `• ${edu.details}`}
                    </div>
                  </div>
                ))}
              </div>

              <div>
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-3 flex items-center gap-2">
                  <Award className="w-4 h-4 text-indigo-600" />
                  Certifications
                </h3>
                <div className="space-y-2">
                  {editForm.certifications.map((cert, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-xl border border-slate-200 bg-slate-50/50 text-xs font-semibold text-slate-800 flex items-center gap-2"
                    >
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                      <span>{cert}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-2xl border-2 border-dashed border-slate-200 p-12 text-center max-w-lg mx-auto">
          <UploadCloud className="w-12 h-12 text-indigo-600 mx-auto mb-3" />
          <h3 className="text-lg font-bold text-slate-900">Upload Your Resume</h3>
          <p className="text-xs text-slate-500 mt-1 mb-5">
            Supported formats: PDF (.pdf) and Microsoft Word (.docx). Automatic skill extraction & ranking.
          </p>
          <button
            onClick={() => fileInputRef.current?.click()}
            className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl text-xs shadow-xs transition"
          >
            Select Document
          </button>
        </div>
      )}
    </div>
  );
};

