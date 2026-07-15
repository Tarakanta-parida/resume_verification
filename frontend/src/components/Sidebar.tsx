'use client';

import React from 'react';
import { useResumeStore } from '../store/useResumeStore';
import {
  LayoutDashboard,
  Gauge,
  SplitSquareHorizontal,
  FileCheck2,
  Sun,
  Moon,
  Sparkles
} from 'lucide-react';

export default function Sidebar() {
  const {
    theme,
    toggleTheme,
    currentTab,
    setCurrentTab,
    isOptimized,
    resumeName
  } = useResumeStore();

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, disabled: false },
    { id: 'analysis', label: 'ATS Analysis', icon: Gauge, disabled: !isOptimized },
    { id: 'comparer', label: 'Side-by-Side', icon: SplitSquareHorizontal, disabled: !isOptimized },
    { id: 'report', label: 'ATS Report', icon: FileCheck2, disabled: !isOptimized }
  ] as const;

  return (
    <aside className="w-[260px] bg-slate-900 border-r border-white/10 flex flex-col p-6 fixed h-screen z-10 transition-colors duration-300 select-none data-[light=true]:bg-white data-[light=true]:border-black/10" data-light={theme === 'light'}>
      <div className="flex items-center gap-3 mb-10">
        <div className="w-10 h-10 bg-gradient-to-br from-violet-600 to-blue-500 rounded-xl flex items-center justify-center text-white shadow-lg shadow-violet-500/25">
          <Sparkles className="w-5 h-5" />
        </div>
        <span className="font-title font-extrabold text-xl bg-gradient-to-r from-violet-400 to-blue-400 bg-clip-text text-transparent tracking-tight">
          ResuMatch AI
        </span>
      </div>

      <nav className="flex flex-col gap-2 flex-grow">
        {menuItems.map(item => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;

          return (
            <button
              key={item.id}
              onClick={() => !item.disabled && setCurrentTab(item.id)}
              disabled={item.disabled}
              className={`flex items-center gap-3.5 px-4 py-3 rounded-xl font-medium transition-all duration-300 w-full text-left cursor-pointer
                ${isActive
                  ? 'bg-gradient-to-r from-violet-600 to-blue-500 text-white shadow-lg shadow-violet-500/20'
                  : theme === 'light'
                    ? 'text-slate-700 hover:bg-slate-100 hover:text-violet-600 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-transparent'
                    : 'text-slate-400 hover:bg-slate-800 hover:text-white disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-transparent'
                }
              `}
            >
              <Icon className="w-5 h-5" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="mt-auto flex flex-col gap-4 pt-4 border-t border-white/10 data-[light=true]:border-black/10" data-light={theme === 'light'}>
        <div className="flex items-center justify-between p-2.5 bg-slate-800 rounded-xl text-sm font-semibold text-slate-400 data-[light=true]:bg-slate-100 data-[light=true]:text-slate-600" data-light={theme === 'light'}>
          <span className="capitalize">{theme} Theme</span>
          <button
            onClick={toggleTheme}
            className="w-11 h-6 bg-slate-600 rounded-full p-0.5 transition-colors relative cursor-pointer data-[active=true]:bg-violet-600"
            data-active={theme === 'light'}
          >
            <div className={`w-5 h-5 bg-white rounded-full shadow transition-transform duration-300 flex items-center justify-center
              ${theme === 'light' ? 'translate-x-5' : 'translate-x-0'}
            `}>
              {theme === 'light' ? <Sun className="w-3.5 h-3.5 text-amber-500" /> : <Moon className="w-3.5 h-3.5 text-violet-600" />}
            </div>
          </button>
        </div>

        <div className="flex items-center gap-2.5 bg-white/5 border border-white/10 px-3.5 py-2.5 rounded-xl text-xs data-[light=true]:bg-black/5 data-[light=true]:border-black/10" data-light={theme === 'light'}>
          <div className={`w-2 h-2 rounded-full shadow-sm animate-pulse
            ${isOptimized ? 'bg-emerald-500 shadow-emerald-500' : 'bg-red-500 shadow-red-500'}
          `} />
          <span className="text-slate-400 data-[light=true]:text-slate-600" data-light={theme === 'light'}>
            {isOptimized ? 'Resume Optimized' : resumeName ? 'Ready to Optimize' : 'Upload files to begin'}
          </span>
        </div>
      </div>
    </aside>
  );
}
