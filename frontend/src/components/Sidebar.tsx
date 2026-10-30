import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  Search,
  BookmarkCheck,
  KanbanSquare,
  Settings,
  Sparkles,
  ExternalLink,
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const navItems = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/resume', label: 'My Resume', icon: FileText },
    { to: '/jobs', label: 'Job Search', icon: Search },
    { to: '/shortlist', label: 'Smart Shortlist', icon: BookmarkCheck },
    { to: '/applications', label: 'Application Tracker', icon: KanbanSquare },
    { to: '/settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col justify-between shrink-0 min-h-[calc(100vh-4rem)] p-4">
      <div className="space-y-6">
        <div>
          <div className="px-3 text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">
            Navigation
          </div>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === '/'}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition ${
                      isActive
                        ? 'bg-indigo-50 text-indigo-700 font-semibold'
                        : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                    }`
                  }
                >
                  <Icon className="w-4 h-4 shrink-0" />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Target Profile Card */}
        <div className="bg-gradient-to-br from-indigo-50 to-blue-50/50 p-4 rounded-xl border border-indigo-100 text-xs">
          <div className="flex items-center gap-1.5 font-bold text-indigo-950 mb-1">
            <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
            Targeting Roles
          </div>
          <p className="text-slate-600 leading-relaxed mb-2">
            Senior Java & Full-Stack (React) in Bengaluru
          </p>
          <div className="flex flex-wrap gap-1">
            <span className="px-1.5 py-0.5 bg-white text-indigo-700 font-medium rounded border border-indigo-200 text-[10px]">
              Java
            </span>
            <span className="px-1.5 py-0.5 bg-white text-indigo-700 font-medium rounded border border-indigo-200 text-[10px]">
              Spring Boot
            </span>
            <span className="px-1.5 py-0.5 bg-white text-indigo-700 font-medium rounded border border-indigo-200 text-[10px]">
              ReactJS
            </span>
            <span className="px-1.5 py-0.5 bg-white text-indigo-700 font-medium rounded border border-indigo-200 text-[10px]">
              AWS
            </span>
          </div>
        </div>
      </div>

      {/* Footer Info */}
      <div className="pt-4 border-t border-slate-100 text-xs text-slate-400 flex items-center justify-between">
        <span>SmartJobMatch v1.0</span>
        <a
          href="/docs"
          target="_blank"
          rel="noreferrer"
          className="text-indigo-600 hover:underline flex items-center gap-1"
        >
          API Docs
          <ExternalLink className="w-3 h-3" />
        </a>
      </div>
    </aside>
  );
};

