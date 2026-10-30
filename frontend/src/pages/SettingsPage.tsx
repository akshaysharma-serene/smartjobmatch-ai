import React, { useEffect, useState } from 'react';
import {
  Save,
  Sliders,
  MapPin,
  Briefcase,
  Layers,
  Clock,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Plus,
  X,
  Key,
} from 'lucide-react';
import { preferenceService, matchService, jobService } from '../services/api';
import { JobSearchPreferences, SyncStatus } from '../types';

export const SettingsPage: React.FC = () => {
  const [prefs, setPrefs] = useState<JobSearchPreferences | null>(null);
  const [syncStatus, setSyncStatus] = useState<SyncStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);
  const [savedBanner, setSavedBanner] = useState<string | null>(null);

  // New item inputs
  const [newRole, setNewRole] = useState<string>('');
  const [newLocation, setNewLocation] = useState<string>('');

  const loadSettings = async () => {
    setLoading(true);
    try {
      const [p, s] = await Promise.all([
        preferenceService.getPreferences(),
        jobService.getSyncStatus(),
      ]);
      setPrefs(p);
      setSyncStatus(s);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSettings();
  }, []);

  const handleWeightChange = (key: string, value: number) => {
    if (!prefs) return;
    setPrefs({
      ...prefs,
      scoring_weights: {
        ...prefs.scoring_weights,
        [key]: value,
      },
    });
  };

  const handleAddRole = () => {
    if (!newRole.trim() || !prefs) return;
    if (!prefs.keywords.includes(newRole.trim())) {
      setPrefs({ ...prefs, keywords: [...prefs.keywords, newRole.trim()] });
    }
    setNewRole('');
  };

  const handleRemoveRole = (role: string) => {
    if (!prefs) return;
    setPrefs({ ...prefs, keywords: prefs.keywords.filter((r) => r !== role) });
  };

  const handleAddLocation = () => {
    if (!newLocation.trim() || !prefs) return;
    if (!prefs.locations.includes(newLocation.trim())) {
      setPrefs({ ...prefs, locations: [...prefs.locations, newLocation.trim()] });
    }
    setNewLocation('');
  };

  const handleRemoveLocation = (loc: string) => {
    if (!prefs) return;
    setPrefs({ ...prefs, locations: prefs.locations.filter((l) => l !== loc) });
  };

  const toggleWorkMode = (mode: string) => {
    if (!prefs) return;
    const current = prefs.work_modes;
    if (current.includes(mode)) {
      if (current.length > 1) {
        setPrefs({ ...prefs, work_modes: current.filter((m) => m !== mode) });
      }
    } else {
      setPrefs({ ...prefs, work_modes: [...current, mode] });
    }
  };

  const handleSave = async () => {
    if (!prefs) return;
    setSaving(true);
    try {
      await preferenceService.updatePreferences(prefs);
      // Re-trigger matches with new weights & thresholds
      await matchService.runMatches();
      setSavedBanner('Preferences and scoring weights saved successfully! Matches re-evaluated.');
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  if (loading || !prefs) {
    return <div className="p-16 text-center text-xs text-slate-400">Loading settings...</div>;
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Job Preferences & Engine Settings</h1>
          <p className="text-xs text-slate-500">
            Customize target roles, location constraints, scoring weights, and external job sources
          </p>
        </div>

        <button
          onClick={handleSave}
          disabled={saving}
          className="inline-flex items-center gap-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold shadow-xs transition disabled:opacity-50"
        >
          <Save className="w-4 h-4" />
          {saving ? 'Saving...' : 'Save Preferences'}
        </button>
      </div>

      {savedBanner && (
        <div className="p-4 rounded-xl text-xs font-medium bg-emerald-50 text-emerald-800 border border-emerald-200 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>{savedBanner}</span>
          </div>
          <button onClick={() => setSavedBanner(null)} className="hover:underline">
            Dismiss
          </button>
        </div>
      )}

      {/* Target Roles */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
        <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
          <Briefcase className="w-4 h-4 text-indigo-600" />
          Target Job Roles
        </h2>
        <p className="text-xs text-slate-500">
          The matching engine prioritizes these specific roles and keywords for title scoring.
        </p>

        <div className="flex items-center gap-2">
          <input
            type="text"
            placeholder="Add target role (e.g. Cloud-Native Java Engineer)..."
            value={newRole}
            onChange={(e) => setNewRole(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleAddRole()}
            className="px-3 py-2 text-xs border border-slate-300 rounded-lg w-72 focus:ring-2 focus:ring-indigo-500"
          />
          <button
            onClick={handleAddRole}
            className="px-3 py-2 bg-indigo-600 text-white rounded-lg text-xs font-semibold hover:bg-indigo-700 inline-flex items-center gap-1"
          >
            <Plus className="w-4 h-4" /> Add Role
          </button>
        </div>

        <div className="flex flex-wrap gap-2 pt-1">
          {prefs.keywords.map((role, idx) => (
            <span
              key={idx}
              className="px-3 py-1.5 rounded-lg text-xs font-medium bg-indigo-50 text-indigo-800 border border-indigo-200 flex items-center gap-2"
            >
              {role}
              <button
                onClick={() => handleRemoveRole(role)}
                className="hover:text-red-600 text-indigo-400"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </span>
          ))}
        </div>
      </div>

      {/* Target Locations & Work Modes */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <MapPin className="w-4 h-4 text-indigo-600" />
            Preferred Locations
          </h2>
          <div className="flex items-center gap-2">
            <input
              type="text"
              placeholder="e.g. Bengaluru, Remote..."
              value={newLocation}
              onChange={(e) => setNewLocation(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAddLocation()}
              className="px-3 py-2 text-xs border border-slate-300 rounded-lg flex-1 focus:ring-2 focus:ring-indigo-500"
            />
            <button
              onClick={handleAddLocation}
              className="px-3 py-2 bg-indigo-600 text-white rounded-lg text-xs font-semibold hover:bg-indigo-700"
            >
              Add
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {prefs.locations.map((loc, idx) => (
              <span
                key={idx}
                className="px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-100 text-slate-800 border border-slate-200 flex items-center gap-2"
              >
                {loc}
                <button
                  onClick={() => handleRemoveLocation(loc)}
                  className="hover:text-red-600 text-slate-400"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </span>
            ))}
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Layers className="w-4 h-4 text-indigo-600" />
            Work-Mode Preferences
          </h2>
          <p className="text-xs text-slate-500">Select acceptable arrangements:</p>
          <div className="flex items-center gap-2">
            {['Remote', 'Hybrid', 'On-site'].map((mode) => {
              const active = prefs.work_modes.includes(mode);
              return (
                <button
                  key={mode}
                  type="button"
                  onClick={() => toggleWorkMode(mode)}
                  className={`px-4 py-2 rounded-xl text-xs font-semibold border transition ${
                    active
                      ? 'bg-indigo-600 text-white border-indigo-600'
                      : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                  }`}
                >
                  {mode}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Auto-Shortlist Threshold & Scoring Weights */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-5">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Sliders className="w-4 h-4 text-indigo-600" />
              Matching Weights & Shortlist Threshold
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Adjust how the matching algorithm scores jobs against your resume.
            </p>
          </div>
          <div className="text-right">
            <div className="text-xs text-slate-500">Auto-Shortlist At:</div>
            <div className="text-lg font-bold text-indigo-600">{prefs.minimum_match_score}%</div>
          </div>
        </div>

        {/* Threshold Slider */}
        <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-700 mb-2">
            <span>Minimum Match Score Threshold for Automatic Shortlisting</span>
            <span>{prefs.minimum_match_score}%</span>
          </div>
          <input
            type="range"
            min="50"
            max="90"
            step="5"
            value={prefs.minimum_match_score}
            onChange={(e) => setPrefs({ ...prefs, minimum_match_score: Number(e.target.value) })}
            className="w-full accent-indigo-600 cursor-pointer"
          />
          <div className="flex justify-between text-[10px] text-slate-400 mt-1">
            <span>50% (Permissive)</span>
            <span>70% (Recommended)</span>
            <span>90% (Strict)</span>
          </div>
        </div>

        {/* Weights Sliders */}
        <div className="space-y-3 pt-2">
          <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
            Scoring Dimensions Distribution
          </h3>

          {[
            { key: 'technical_skills', label: 'Technical Skills Overlap', default: 35 },
            { key: 'semantic_similarity', label: 'Responsibilities & Semantic Similarity (TF-IDF)', default: 25 },
            { key: 'experience', label: 'Seniority & Experience Alignment', default: 15 },
            { key: 'job_title', label: 'Target Job Title Relevance', default: 10 },
            { key: 'location_work_mode', label: 'Location & Work-Mode Compatibility', default: 10 },
            { key: 'education_certifications', label: 'Education & Certifications Fit', default: 5 },
          ].map((w) => {
            const rawVal = prefs.scoring_weights[w.key] ?? w.default / 100;
            const pct = Math.round(rawVal * 100);
            return (
              <div key={w.key} className="flex items-center justify-between gap-4 text-xs">
                <span className="w-1/2 font-medium text-slate-700">{w.label}</span>
                <input
                  type="range"
                  min="0"
                  max="60"
                  step="5"
                  value={pct}
                  onChange={(e) => handleWeightChange(w.key, Number(e.target.value) / 100)}
                  className="w-1/3 accent-indigo-600 cursor-pointer"
                />
                <span className="w-12 text-right font-bold text-slate-900">{pct}%</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Job Sources & Credential Status */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
        <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
          <Key className="w-4 h-4 text-indigo-600" />
          Job Source Adapters & Integration Status
        </h2>
        <p className="text-xs text-slate-500">
          Real-time LinkedIn job scraper discovers live postings matching your search keywords and locations.
        </p>

        <div className="space-y-3">
          {syncStatus?.sources.map((src, i) => (
            <div key={i} className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 space-y-2">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-sm text-slate-900 capitalize">{src.source}</span>
                  <span
                    className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase tracking-wider ${
                      src.status === 'connected' || src.status === 'ready'
                        ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                        : 'bg-blue-50 text-blue-700 border border-blue-200'
                    }`}
                  >
                    {src.status}
                  </span>
                </div>
                <div className="text-[11px] text-slate-400">
                  {src.total_fetched} listings indexed
                </div>
              </div>
              <p className="text-xs text-slate-600">{src.message}</p>
              {src.required_permissions && src.required_permissions.length > 0 && (
                <div className="text-[11px] text-slate-500 font-mono bg-white p-2 rounded border border-slate-200">
                  Configuration: {src.required_permissions.join(', ')}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

