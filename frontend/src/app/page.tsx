'use client';

import React from 'react';
import { useResumeStore } from '../store/useResumeStore';
import Sidebar from '../components/Sidebar';
import Loader from '../components/Loader';
import DashboardView from '../components/DashboardView';
import AnalysisView from '../components/AnalysisView';
import ComparerView from '../components/ComparerView';
import ReportView from '../components/ReportView';

export default function Home() {
  const { 
    theme, 
    currentTab, 
    loadSampleProfile 
  } = useResumeStore();

  const getPageTitle = () => {
    switch (currentTab) {
      case 'dashboard':
        return {
          title: 'Resume Optimizer',
          sub: 'Upload your resume and the target job description to match keywords and boost your score.'
        };
      case 'analysis':
        return {
          title: 'ATS Match & Analysis',
          sub: 'Review missing keywords, category scores, and customized recommendations.'
        };
      case 'comparer':
        return {
          title: 'Before & After Comparison',
          sub: 'Review optimized enhancements made directly to your resume without altering layout.'
        };
      case 'report':
        return {
          title: 'ATS Audit Report',
          sub: 'Detailed compatibility audit report, keyword frequency check, and action items.'
        };
      default:
        return {
          title: 'Resume Optimizer',
          sub: 'Upload your resume and the target job description to match keywords and boost your score.'
        };
    }
  };

  const pageMeta = getPageTitle();

  return (
    <div className="flex min-h-screen w-full bg-slate-950 text-slate-100 transition-colors duration-300 data-[light=true]:bg-slate-50 data-[light=true]:text-slate-900" data-light={theme === 'light'}>
      {/* Sidebar Navigation */}
      <Sidebar />

      {/* Main Content Area */}
      <main className="ml-[260px] flex-grow p-10 min-h-screen flex flex-col">
        {/* Top Header Bar */}
        <header className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-6 mb-10 w-full">
          <div>
            <h1 className="font-title font-bold text-3xl text-white tracking-tight mb-1 data-[light=true]:text-slate-900" data-light={theme === 'light'}>
              {pageMeta.title}
            </h1>
            <p className="text-slate-400 text-sm max-w-xl data-[light=true]:text-slate-500" data-light={theme === 'light'}>
              {pageMeta.sub}
            </p>
          </div>

          <div className="flex items-center gap-3 bg-slate-900/40 border border-white/5 px-4 py-2.5 rounded-xl shrink-0 data-[light=true]:bg-white data-[light=true]:border-black/5" data-light={theme === 'light'}>
            <span className="text-xs font-bold text-slate-400 data-[light=true]:text-slate-500" data-light={theme === 'light'}>
              Load Template Profile:
            </span>
            <select
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) => loadSampleProfile(e.target.value)}
              className="bg-slate-950 border border-white/10 text-white rounded-lg px-3 py-1.5 text-xs font-semibold focus:outline-none focus:border-violet-500 cursor-pointer data-[light=true]:bg-slate-100 data-[light=true]:border-black/10 data-[light=true]:text-slate-800"
              data-light={theme === 'light'}
            >
              <option value="">-- Custom Upload --</option>
              <option value="software_engineer">Software Engineer</option>
              <option value="data_analyst">Data Analyst</option>
              <option value="product_manager">Product Manager</option>
              <option value="marketing_specialist">Marketing Specialist</option>
            </select>
          </div>
        </header>

        {/* Render Active Tab Views */}
        <div className="flex-grow flex flex-col">
          {currentTab === 'dashboard' && <DashboardView />}
          {currentTab === 'analysis' && <AnalysisView />}
          {currentTab === 'comparer' && <ComparerView />}
          {currentTab === 'report' && <ReportView />}
        </div>
      </main>

      {/* Global Fullscreen Processing Loader */}
      <Loader />
    </div>
  );
}
