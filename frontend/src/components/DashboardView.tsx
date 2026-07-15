'use client';

import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useResumeStore } from '../store/useResumeStore';
import { Upload, FileText, Briefcase, FileUp, Sparkles, X } from 'lucide-react';

export default function DashboardView() {
  const {
    theme,
    resumeName,
    jdText,
    setJdText,
    uploadResumeFile,
    removeResumeFile,
    runOptimization,
    originalResume
  } = useResumeStore();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      uploadResumeFile(acceptedFiles[0]);
    }
  }, [uploadResumeFile]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/json': ['.json']
    },
    multiple: false
  });

  const isReady = (resumeName !== '' || originalResume !== null) && jdText.trim().length > 15;

  return (
    <div className="grid grid-cols-1 xl:grid-cols-2 gap-8 items-stretch w-full">
      {/* Upload Resume Panel */}
      <div className="flex flex-col bg-slate-900/50 backdrop-blur-xl border border-white/5 p-8 rounded-2xl shadow-xl transition-all duration-300 hover:border-white/10 data-[light=true]:bg-white data-[light=true]:border-black/5 data-[light=true]:shadow-sm" data-light={theme === 'light'}>
        <div className="flex justify-between items-center mb-6">
          <h3 className="font-title font-bold text-lg text-white flex items-center gap-2.5 data-[light=true]:text-slate-800" data-light={theme === 'light'}>
            <FileUp className="w-5 h-5 text-violet-500" />
            1. Upload Resume
          </h3>
        </div>

        <div className="flex-grow flex flex-col justify-center">
          {!(resumeName || originalResume) ? (
            <div
              {...getRootProps()}
              className={`border-2 border-dashed border-white/10 rounded-xl p-12 text-center cursor-pointer transition-all duration-300 flex flex-col items-center justify-center bg-white/[0.01] hover:border-violet-500 hover:bg-violet-500/[0.02]
                ${isDragActive ? 'border-violet-500 bg-violet-500/[0.05]' : ''}
                ${theme === 'light' ? 'border-black/10 hover:border-violet-500 bg-black/[0.01]' : ''}
              `}
            >
              <input {...getInputProps()} />
              <div className="w-14 h-14 bg-gradient-to-br from-violet-600 to-blue-500 rounded-2xl flex items-center justify-center text-white shadow-md shadow-violet-500/10 mb-5 transition-transform duration-300 group-hover:scale-105">
                <Upload className="w-6 h-6" />
              </div>
              <p className="font-semibold text-white text-base mb-1.5 data-[light=true]:text-slate-800" data-light={theme === 'light'}>
                Drag and drop your resume here
              </p>
              <p className="text-slate-400 text-xs data-[light=true]:text-slate-500" data-light={theme === 'light'}>
                Supports PDF, DOCX, and JSON formats
              </p>
              <button className="mt-6 px-5 py-2.5 bg-gradient-to-r from-violet-600 to-blue-500 text-white rounded-lg text-xs font-semibold shadow shadow-violet-500/20 hover:scale-[1.02] transition-transform duration-300">
                Browse Files
              </button>
            </div>
          ) : (
            <div className="flex items-center justify-between bg-slate-800/60 border border-white/5 p-4 rounded-xl data-[light=true]:bg-slate-100 data-[light=true]:border-black/5" data-light={theme === 'light'}>
              <div className="flex items-center gap-3.5">
                <div className="w-11 h-11 bg-violet-600/10 border border-violet-500/20 rounded-lg flex items-center justify-center text-violet-400">
                  <FileText className="w-5 h-5" />
                </div>
                <div>
                  <p className="font-semibold text-sm text-white truncate max-w-[200px] data-[light=true]:text-slate-800" data-light={theme === 'light'}>
                    {resumeName || 'Sample_Resume.docx'}
                  </p>
                  <p className="text-slate-400 text-xs data-[light=true]:text-slate-500" data-light={theme === 'light'}>
                    Structure loaded
                  </p>
                </div>
              </div>
              <button
                onClick={removeResumeFile}
                className="p-1.5 hover:bg-red-500/10 hover:text-red-400 text-slate-400 rounded-lg transition-colors cursor-pointer"
                title="Remove File"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Target Job Description Panel */}
      <div className="flex flex-col bg-slate-900/50 backdrop-blur-xl border border-white/5 p-8 rounded-2xl shadow-xl transition-all duration-300 hover:border-white/10 data-[light=true]:bg-white data-[light=true]:border-black/5 data-[light=true]:shadow-sm" data-light={theme === 'light'}>
        <div className="flex justify-between items-center mb-6">
          <h3 className="font-title font-bold text-lg text-white flex items-center gap-2.5 data-[light=true]:text-slate-800" data-light={theme === 'light'}>
            <Briefcase className="w-5 h-5 text-violet-500" />
            2. Target Job Description
          </h3>
        </div>

        <div className="flex flex-col gap-4 flex-grow min-h-[260px]">
          <div
            className="flex-grow bg-slate-950/40 border border-white/5 p-5 rounded-xl transition-colors min-h-[210px] flex flex-col focus-within:border-violet-500 data-[light=true]:bg-slate-50 data-[light=true]:border-black/5"
            data-light={theme === 'light'}
          >
            <textarea
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
              placeholder="Paste target job description details here... Include required technical skills, experience requirements, and key terms to match."
              className="w-full flex-grow bg-transparent text-white text-sm leading-relaxed resize-none focus:outline-none scrollbar-none data-[light=true]:text-slate-800"
              data-light={theme === 'light'}
            />
          </div>
        </div>
      </div>

      {/* Action Trigger Button */}
      <div className="col-span-1 xl:col-span-2 flex justify-center mt-6">
        <button
          onClick={runOptimization}
          disabled={!isReady}
          className={`flex items-center gap-2 px-12 py-4 bg-gradient-to-r from-violet-600 to-blue-500 text-white rounded-xl font-title font-bold text-lg shadow-lg shadow-violet-500/20 transition-all duration-300 hover:scale-[1.02] disabled:opacity-40 disabled:scale-100 disabled:shadow-none disabled:cursor-not-allowed cursor-pointer`}
        >
          <Sparkles className="w-5 h-5" />
          Optimize Resume
        </button>
      </div>
    </div>
  );
}
