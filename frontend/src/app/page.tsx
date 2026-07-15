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
    currentTab, 
    loadSampleProfile,
    setCurrentTab
  } = useResumeStore();

  const getPageTitle = () => {
    switch (currentTab) {
      case 'dashboard':
        return {
          title: 'Optimize your resume',
          sub: 'Upload your resume and target job description to get keyword-matched recommendations'
        };
      case 'analysis':
        return {
          title: 'Your analysis',
          sub: 'Detailed keyword matching & ATS compatibility check'
        };
      case 'comparer':
        return {
          title: 'Before & after comparison',
          sub: 'See exactly how your resume was optimized to match job requirements'
        };
      case 'report':
        return {
          title: 'ATS audit report',
          sub: 'Detailed compatibility analysis and actionable recommendations'
        };
      default:
        return {
          title: 'Optimize your resume',
          sub: 'Upload your resume and target job description to get keyword-matched recommendations'
        };
    }
  };

  const pageMeta = getPageTitle();

  return (
    <div className="flex flex-col lg:flex-row min-h-screen w-full bg-white text-slate-900 font-sans">
      {/* Sidebar Navigation */}
      <Sidebar />

      {/* Main Content Area */}
      <main className="lg:ml-[260px] flex-grow w-full p-4 md:p-8 flex flex-col overflow-x-hidden">
        {/* Page Title & Profile Header */}
        <div className="mb-8 w-full flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <h1 className="font-bold text-[32px] text-slate-900 mb-1">
              {pageMeta.title}
            </h1>
            <p className="text-slate-500 text-[15px]">
              {pageMeta.sub}
            </p>
          </div>
          
          <div className="flex items-center gap-3 bg-[#f0f9fa] border border-[#d6eef1] px-4 py-2 rounded-lg shrink-0">
            <span className="text-sm font-semibold text-[#00829a] flex items-center gap-2">
              📄 Template Profile:
            </span>
            <select
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) => loadSampleProfile(e.target.value)}
              className="bg-slate-800 border-none text-white rounded px-3 py-1.5 text-sm font-semibold focus:outline-none cursor-pointer"
            >
              <option value="">-- Custom Upload --</option>
              <option value="software_engineer">Software Engineer</option>
              <option value="data_analyst">Data Analyst</option>
              <option value="product_manager">Product Manager</option>
              <option value="marketing_specialist">Marketing Specialist</option>
            </select>
          </div>
        </div>

        {/* Render Active Tab Views */}
        <div className="flex-grow flex flex-col">
          {currentTab === 'dashboard' && <DashboardView />}
          {currentTab === 'analysis' && <AnalysisView />}
          {currentTab === 'comparer' && <ComparerView />}
          {currentTab === 'report' && <ReportView />}
        </div>
        
        {/* Navigation Arrows for single-page feel */}
        {currentTab !== 'report' && (
          <div className="flex justify-center mt-12 mb-8">
            <button 
              onClick={() => {
                const tabs: any[] = ['dashboard', 'analysis', 'comparer', 'report'];
                const nextIdx = tabs.indexOf(currentTab) + 1;
                if (nextIdx < tabs.length) setCurrentTab(tabs[nextIdx]);
              }}
              className="w-10 h-10 rounded-full bg-slate-600 text-white flex items-center justify-center hover:bg-slate-700 transition-colors"
            >
              ↓
            </button>
          </div>
        )}
      </main>

      {/* Global Fullscreen Processing Loader */}
      <Loader />
    </div>
  );
}
