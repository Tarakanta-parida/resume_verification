'use client';

import React from 'react';
import { useResumeStore } from '../store/useResumeStore';
import { ChevronRight, FileCheck, CheckCircle2, Star, AlertTriangle, ShieldCheck } from 'lucide-react';

export default function ReportView() {
  const {
    theme,
    originalScore,
    optimizedScore,
    matchedKeywords,
    missingKeywords,
    formattingIssues
  } = useResumeStore();

  const mockDensities = [
    { word: matchedKeywords[0] || 'TECHNICAL SKILLS', orig: 1, opt: 3 },
    { word: matchedKeywords[1] || 'METRICS & RESULTS', orig: 0, opt: 2 },
    { word: missingKeywords[0] || 'INDUSTRY KNOWLEDGE', orig: 0, opt: 2 },
    { word: matchedKeywords[2] || 'COLLABORATION', orig: 1, opt: 3 }
  ];

  const improvements = [
    {
      title: 'Missing Keyword Injection',
      desc: `Injected missing target skills: ${missingKeywords.slice(0, 4).join(', ')} into Core Competencies.`,
      type: 'success'
    },
    {
      title: 'Action-Verb Rewriting',
      desc: 'Updated role bullets to use strong action verbs like Led, Spearheaded, and Optimized.',
      type: 'success'
    },
    {
      title: 'Impact Metric Quantifying',
      desc: 'Added performance percentages and measurable metrics to key experience items.',
      type: 'success'
    },
    {
      title: 'Resume Design Locked',
      desc: 'Successfully locked layout spacing, margins, styles, and typography.',
      type: 'success'
    }
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start w-full">
      {/* Top Stats Banner */}
      <div className="lg:col-span-2 bg-gradient-to-r from-violet-600 to-blue-500 p-8 rounded-2xl shadow-xl flex flex-col md:flex-row items-center justify-between gap-6 text-white">
        <div>
          <h2 className="font-title font-bold text-2xl mb-2 tracking-tight">
            ATS Compatibility Audit Report
          </h2>
          <p className="text-white/80 text-sm max-w-md">
            This detailed audit checks keyword density, formatting structures, and skill completeness against target candidate profiles.
          </p>
        </div>

        <div className="flex items-center gap-6">
          <div className="w-20 h-20 bg-white/10 rounded-full flex flex-col items-center justify-center border border-white/20">
            <span className="font-title font-extrabold text-xl leading-none">{originalScore}%</span>
            <span className="text-[9px] uppercase tracking-wider font-semibold opacity-75 mt-0.5">Original</span>
          </div>
          <ChevronRight className="w-5 h-5 opacity-70" />
          <div className="w-20 h-20 bg-emerald-500 rounded-full flex flex-col items-center justify-center shadow-lg shadow-emerald-500/20 border border-white/20">
            <span className="font-title font-extrabold text-xl leading-none">{optimizedScore}%</span>
            <span className="text-[9px] uppercase tracking-wider font-semibold opacity-90 mt-0.5">Optimized</span>
          </div>
        </div>
      </div>

      {/* Keyword Frequencies Check */}
      <div className="bg-slate-900/50 backdrop-blur-xl border border-white/5 p-8 rounded-2xl shadow-xl data-[light=true]:bg-white data-[light=true]:border-black/5 data-[light=true]:shadow-sm" data-light={theme === 'light'}>
        <h3 className="font-title font-bold text-lg text-white flex items-center gap-2.5 mb-6 data-[light=true]:text-slate-800" data-light={theme === 'light'}>
          <Star className="w-5 h-5 text-violet-500" />
          Keyword Density Analysis
        </h3>

        <div className="flex flex-col gap-5">
          {mockDensities.map((item, idx) => (
            <div key={idx} className="flex flex-col gap-2">
              <div className="flex justify-between text-xs font-semibold">
                <span className="text-slate-400 data-[light=true]:text-slate-600" data-light={theme === 'light'}>{item.word}</span>
                <span className="text-slate-500">Original: {item.orig} | Optimized: {item.opt}</span>
              </div>
              <div className="w-full h-2.5 bg-slate-950 rounded-full overflow-hidden relative data-[light=true]:bg-slate-100" data-light={theme === 'light'}>
                <div
                  className="h-full bg-gradient-to-r from-violet-600 to-blue-500 rounded-full transition-all duration-1000"
                  style={{ width: `${(item.opt / 4) * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Checklist items */}
      <div className="bg-slate-900/50 backdrop-blur-xl border border-white/5 p-8 rounded-2xl shadow-xl data-[light=true]:bg-white data-[light=true]:border-black/5 data-[light=true]:shadow-sm" data-light={theme === 'light'}>
        <h3 className="font-title font-bold text-lg text-white flex items-center gap-2.5 mb-6 data-[light=true]:text-slate-800" data-light={theme === 'light'}>
          <ShieldCheck className="w-5 h-5 text-violet-500" />
          Optimizations Applied
        </h3>

        <div className="flex flex-col gap-4">
          {improvements.map((item, idx) => (
            <div key={idx} className="flex items-start gap-4 p-4 bg-slate-950/40 border border-white/5 rounded-xl data-[light=true]:bg-slate-50 data-[light=true]:border-black/5" data-light={theme === 'light'}>
              <div className="w-9 h-9 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-lg flex items-center justify-center shrink-0">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-title font-bold text-sm text-white mb-1 data-[light=true]:text-slate-800" data-light={theme === 'light'}>
                  {item.title}
                </h4>
                <p className="text-slate-400 text-xs leading-relaxed data-[light=true]:text-slate-500" data-light={theme === 'light'}>
                  {item.desc}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
