'use client';

import React from 'react';
import { useResumeStore } from '../store/useResumeStore';
import {
  LayoutDashboard,
  Gauge,
  SplitSquareHorizontal,
  FileCheck2
} from 'lucide-react';

export default function Sidebar() {
  const {
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
    <aside className="w-full lg:w-[260px] bg-slate-50 border-b lg:border-b-0 lg:border-r border-slate-200 flex flex-col p-4 lg:p-6 lg:fixed lg:h-screen z-10 transition-colors duration-300 select-none shrink-0">
      {/* Logo Area */}
      <div className="flex items-center gap-2 lg:gap-3 mb-4 lg:mb-10">
        <div className="w-8 h-8 lg:w-10 lg:h-10 bg-[#0097b2] rounded-xl flex items-center justify-center shrink-0 shadow-sm">
          <SparklesIcon className="w-4 h-4 lg:w-5 lg:h-5 text-white" />
        </div>
        <span className="font-bold text-lg lg:text-xl text-[#0097b2] tracking-tight truncate">
          ResuMatch
        </span>
      </div>

      {/* Navigation */}
      <nav className="flex flex-row lg:flex-col gap-2 overflow-x-auto lg:overflow-visible pb-1 lg:pb-0 scrollbar-hide flex-none lg:flex-grow">
        {menuItems.map(item => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;

          return (
            <button
              key={item.id}
              onClick={() => !item.disabled && setCurrentTab(item.id)}
              disabled={item.disabled}
              className={`flex items-center justify-center lg:justify-start gap-2 lg:gap-3.5 px-3 py-2 lg:px-4 lg:py-3 rounded-xl font-medium transition-all duration-200 text-left cursor-pointer whitespace-nowrap shrink-0 lg:w-full
                ${isActive
                  ? 'bg-cyan-600 text-white shadow-md shadow-cyan-600/20'
                  : 'text-slate-600 hover:bg-slate-200 hover:text-cyan-700 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-transparent disabled:hover:text-slate-600'
                }
              `}
            >
              <Icon className="w-4 h-4 lg:w-5 lg:h-5 shrink-0" />
              <span className="text-[13px] lg:text-sm font-bold tracking-wide">{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Status Footer (Hidden on mobile for space) */}
      <div className="hidden lg:flex mt-auto flex-col gap-4 pt-4 border-t border-slate-200">
        <div className="flex items-center gap-2.5 bg-white border border-slate-200 px-3.5 py-2.5 rounded-xl text-xs shadow-sm">
          <div className={`w-2 h-2 rounded-full shadow-sm animate-pulse shrink-0
            ${isOptimized ? 'bg-emerald-500 shadow-emerald-500' : 'bg-red-500 shadow-red-500'}
          `} />
          <span className="text-slate-600 font-medium truncate">
            {isOptimized ? 'Resume Optimized' : resumeName ? 'Ready to Optimize' : 'Upload files to begin'}
          </span>
        </div>
      </div>
    </aside>
  );
}

// Simple local component for the sparkle icon since we didn't import it from lucide-react at the top to save space
function SparklesIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z" />
      <path d="M20 3v4" />
      <path d="M22 5h-4" />
      <path d="M4 17v2" />
      <path d="M5 18H3" />
    </svg>
  );
}
