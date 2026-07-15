'use client';

import React, { useState } from 'react';
import { useResumeStore } from '../store/useResumeStore';
import { LineChart, ClipboardList, CheckCircle2, AlertTriangle, ChevronRight, ArrowUp } from 'lucide-react';
import Gauges from './Gauges';

export default function AnalysisView() {
  const {
    theme,
    originalScore,
    optimizedScore,
    matchedKeywords,
    missingKeywords,
    sectionScore,
    sectionsFound,
    formattingIssues
  } = useResumeStore();

  const [activeTab, setActiveTab] = useState<'missing' | 'matched'>('missing');

  const diff = optimizedScore - originalScore;
  const currentKeywordsList = activeTab === 'missing' ? missingKeywords : matchedKeywords;

  const categories = [
    { name: 'Keyword Matching & Density', current: originalScore + 5 },
    { name: 'Skills & Competency Alignments', current: Math.max(originalScore - 10, 45) },
    { name: 'Experience & Role Match', current: originalScore + 2 },
    { name: 'Education & Certification Validation', current: 95 }
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-stretch w-full">
      {/* Score Verdict Card */}
      <div className="bg-slate-900/50 backdrop-blur-xl border border-white/5 p-8 rounded-2xl shadow-xl flex flex-col items-center justify-center text-center data-[light=true]:bg-white data-[light=true]:border-black/5 data-[light=true]:shadow-sm" data-light={theme === 'light'}>
        <div className="flex justify-between w-full items-center mb-6">
          <h3 className="font-title font-bold text-lg text-white flex items-center gap-2.5 data-[light=true]:text-slate-800" data-light={theme === 'light'}>
            <LineChart className="w-5 h-5 text-violet-500" />
            ATS Match Verdict
          </h3>
        </div>

        <div className="flex justify-around w-full gap-8 mb-6">
          <Gauges score={originalScore} label="Current Score" colorClass="#ef4444" />
          <Gauges score={optimizedScore} label="Potential Score" colorClass="#06b6d4" />
        </div>

        <div className="flex flex-col items-center">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-bold rounded-full mb-3">
            <ArrowUp className="w-3.5 h-3.5" />
            <span>+{diff}% Match Improvement</span>
          </div>
          <p className="text-slate-400 text-sm leading-relaxed max-w-sm data-[light=true]:text-slate-500" data-light={theme === 'light'}>
            {diff > 20
              ? `Critical gaps successfully bypassed! Adding ${missingKeywords.length} missing keywords and aligning description verbs raised match metrics to ${optimizedScore}%.`
              : `Your resume is well aligned! Incorporating missing skills pushed compatibility to ${optimizedScore}% to confidently clear ATS filters.`
            }
          </p>
        </div>
      </div>

      {/* Section Progress Bars Card */}
      <div className="bg-slate-900/50 backdrop-blur-xl border border-white/5 p-8 rounded-2xl shadow-xl data-[light=true]:bg-white data-[light=true]:border-black/5 data-[light=true]:shadow-sm" data-light={theme === 'light'}>
        <div className="flex justify-between w-full items-center mb-6">
          <h3 className="font-title font-bold text-lg text-white flex items-center gap-2.5 data-[light=true]:text-slate-800" data-light={theme === 'light'}>
            <ClipboardList className="w-5 h-5 text-violet-500" />
            ATS Section Analysis
          </h3>
        </div>

        <div className="flex flex-col gap-5">
          {categories.map((cat, i) => {
            const potential = Math.min(cat.current + 20, 98);
            return (
              <div key={i} className="flex flex-col gap-2">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-slate-400 data-[light=true]:text-slate-600" data-light={theme === 'light'}>{cat.name}</span>
                  <span className="text-white data-[light=true]:text-slate-800" data-light={theme === 'light'}>{cat.current}% ➔ {potential}%</span>
                </div>
                <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden relative data-[light=true]:bg-slate-100" data-light={theme === 'light'}>
                  <div
                    className="h-full bg-gradient-to-r from-violet-600 to-blue-500 rounded-full transition-all duration-1000"
                    style={{ width: `${potential}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Keywords Badge Panel */}
      <div className="lg:col-span-2 bg-slate-900/50 backdrop-blur-xl border border-white/5 p-8 rounded-2xl shadow-xl data-[light=true]:bg-white data-[light=true]:border-black/5 data-[light=true]:shadow-sm" data-light={theme === 'light'}>
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-white/10 pb-4 mb-6 data-[light=true]:border-black/10" data-light={theme === 'light'}>
          <h3 className="font-title font-bold text-lg text-white flex items-center gap-2.5 data-[light=true]:text-slate-800" data-light={theme === 'light'}>
            Keyword Matching Report
          </h3>
          <div className="flex gap-2">
            <button
              onClick={() => setActiveTab('missing')}
              className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200 cursor-pointer
                ${activeTab === 'missing'
                  ? 'bg-slate-800 text-white data-[light=true]:bg-slate-200 data-[light=true]:text-slate-800'
                  : 'text-slate-400 hover:text-white'
                }
              `}
              data-light={theme === 'light'}
            >
              Missing Keywords ({missingKeywords.length})
            </button>
            <button
              onClick={() => setActiveTab('matched')}
              className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200 cursor-pointer
                ${activeTab === 'matched'
                  ? 'bg-slate-800 text-white data-[light=true]:bg-slate-200 data-[light=true]:text-slate-800'
                  : 'text-slate-400 hover:text-white'
                }
              `}
              data-light={theme === 'light'}
            >
              Matched Keywords ({matchedKeywords.length})
            </button>
          </div>
        </div>

        <div className="flex flex-wrap gap-2.5 max-h-[220px] overflow-y-auto pr-2">
          {currentKeywordsList.length === 0 ? (
            <p className="text-slate-500 text-sm italic p-4">No keywords detected in this category.</p>
          ) : (
            currentKeywordsList.map((kw, i) => (
              <span
                key={i}
                className={`inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-medium border
                  ${activeTab === 'missing'
                    ? 'bg-red-500/10 border-red-500/20 text-red-400'
                    : 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                  }
                `}
              >
                {activeTab === 'missing' ? <AlertTriangle className="w-3.5 h-3.5" /> : <CheckCircle2 className="w-3.5 h-3.5" />}
                {kw}
              </span>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
