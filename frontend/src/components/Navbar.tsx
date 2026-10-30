import React, { useEffect, useState } from 'react';
import { RefreshCw, Sparkles, CheckCircle2, AlertCircle, Briefcase } from 'lucide-react';
import { jobService } from '../services/api';
import { SyncStatus } from '../types';

interface NavbarProps {
  onSyncTriggered?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onSyncTriggered }) => {
  const [syncing, setSyncing] = useState<boolean>(false);
  const [syncStatus, setSyncStatus] = useState<SyncStatus | null>(null);

  const fetchStatus = () => {
    jobService
      .getSyncStatus()
      .then((status) => setSyncStatus(status))
      .catch((err) => console.error(err));
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleSync = async () => {
    setSyncing(true);
    try {
      await jobService.triggerSync();
      fetchStatus();
      if (onSyncTriggered) onSyncTriggered();
    } catch (e) {
      console.error(e);
    } finally {
      setSyncing(false);
    }
  };

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between sticky top-0 z-40">
      {/* Brand */}
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-blue-500 flex items-center justify-center text-white shadow-xs">
          <Briefcase className="w-5 h-5" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-extrabold text-slate-900 text-lg tracking-tight">SmartJobMatch</span>
            <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200 uppercase tracking-wider">
              AI Platform
            </span>
          </div>
          <div className="text-[11px] text-slate-500 hidden sm:block">Bengaluru & Remote Job Discovery</div>
        </div>
      </div>

      {/* Sync Status & Action */}
      <div className="flex items-center gap-4">
        {syncStatus && (
          <div className="hidden md:flex items-center gap-2 text-xs text-slate-500 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-200">
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span>LinkedIn Real-Time Scraper + Greenhouse/Lever Active</span>
          </div>
        )}

        <button
          onClick={handleSync}
          disabled={syncing}
          className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold shadow-xs transition disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${syncing ? 'animate-spin' : ''}`} />
          <span>{syncing ? 'Synchronizing...' : 'Sync Jobs'}</span>
        </button>

        {/* User Avatar */}
        <div className="flex items-center gap-2.5 pl-3 border-l border-slate-200">
          <div className="w-8 h-8 rounded-full bg-slate-900 text-white text-xs font-bold flex items-center justify-center">
            AS
          </div>
          <div className="hidden sm:block text-left">
            <div className="text-xs font-semibold text-slate-900 leading-tight">Akshay Sharma</div>
            <div className="text-[10px] text-slate-500">Full-Stack Engineer</div>
          </div>
        </div>
      </div>
    </header>
  );
};

