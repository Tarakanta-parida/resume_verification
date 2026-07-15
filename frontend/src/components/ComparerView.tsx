'use client';

import React, { useEffect, useRef, useState } from 'react';
import { useResumeStore, ResumeData, API_BASE_URL } from '../store/useResumeStore';
import { FileText, CircleCheck, FileDown } from 'lucide-react';

// Helper function to process bullet text based on active highlights
function processBulletText(html: string, showAdded: boolean, showOptimized: boolean, revertEntireString: boolean = false): string {
  if (!html) return html;
  let result = html;

  // 1. Process optimized bullets (class="mod")
  if (!showOptimized) {
    if (revertEntireString) {
      const match = result.match(/<mark\s+class="mod"\s+data-tooltip="Original:\s*([^"]+)"[^>]*>/i) 
                 || result.match(/<mark\s+class="mod"\s+data-tooltip='Original:\s*([^']+)'[^>]*>/i);
      if (match) {
        return match[1]; // Return the original bullet text in its entirety
      }
    }
    // Inline replacement
    result = result.replace(/<mark\s+class="mod"\s+data-tooltip="Original:\s*([^"]+)"[^>]*>.*?<\/mark>/gi, '$1');
    result = result.replace(/<mark\s+class="mod"\s+data-tooltip='Original:\s*([^']+)'[^>]*>.*?<\/mark>/gi, '$1');
  }

  // 2. Process added keywords (class="add")
  if (!showAdded) {
    result = result.replace(/<mark\s+class="add"[^>]*>.*?<\/mark>/gi, '');
    // Clean up punctuation spacing and double conjunctions
    result = result
      .replace(/\s+and\s*([.,;!])/gi, '$1')
      .replace(/\s+or\s*([.,;!])/gi, '$1')
      .replace(/,\s*and\s*([.,;!])/gi, '$1')
      .replace(/,\s*or\s*([.,;!])/gi, '$1')
      .replace(/\s+,\s*/g, ', ')
      .replace(/\s+/g, ' ')
      .replace(/\s+([.,;!])/g, '$1')
      .trim();
  }

  return result;
}

export default function ComparerView() {
  const {
    theme,
    originalResume,
    optimizedResume,
    resumeName,
    resultId
  } = useResumeStore();

  const [tooltip, setTooltip] = useState<{ text: string; top: number; left: number; visible: boolean }>({
    text: '', top: 0, left: 0, visible: false
  });

  const [showAdded, setShowAdded] = useState(true);
  const [showOptimized, setShowOptimized] = useState(true);

  const optContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = optContainerRef.current;
    if (!container) return;

    const handleMouseEnter = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (target.tagName === 'MARK' && target.hasAttribute('data-tooltip')) {
        const isAdd = target.classList.contains('add');
        const isMod = target.classList.contains('mod');
        if ((isAdd && !showAdded) || (isMod && !showOptimized)) {
          return; // Don't show tooltip if highlight is toggled off
        }
        const rect = target.getBoundingClientRect();
        const tooltipText = target.getAttribute('data-tooltip') || '';
        setTooltip({
          text: tooltipText,
          top: window.scrollY + rect.top - 40,
          left: window.scrollX + rect.left + (rect.width / 2),
          visible: true
        });
      }
    };

    const handleMouseLeave = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (target.tagName === 'MARK') {
        setTooltip(prev => ({ ...prev, visible: false }));
      }
    };

    container.addEventListener('mouseover', handleMouseEnter);
    container.addEventListener('mouseout', handleMouseLeave);

    return () => {
      container.removeEventListener('mouseover', handleMouseEnter);
      container.removeEventListener('mouseout', handleMouseLeave);
    };
  }, [optimizedResume, showAdded, showOptimized]);



  if (!originalResume || !optimizedResume) return null;

  // Export File Triggers
  const exportPDF = () => {
    if (!resultId) return;
    // Open the print-ready HTML page from FastAPI in a new tab
    window.open(`${API_BASE_URL}/optimize/${resultId}/download-pdf?show_added=${showAdded}&show_optimized=${showOptimized}`, '_blank');
  };

  const exportDocx = () => {
    if (!resultId) return;
    window.location.href = `${API_BASE_URL}/optimize/${resultId}/download-docx?show_added=${showAdded}&show_optimized=${showOptimized}`;
  };

  const exportPlainTxt = () => {
    // Generate simple text layout dynamically from JSON
    const data = optimizedResume;
    
    // Summary reversion
    const summaryText = (!showOptimized && originalResume) ? originalResume.summary : data.summary;
    const cleanSummary = processBulletText(summaryText, showAdded, showOptimized).replace(/<[^>]*>/g, '');

    const skills = data.skills
      .map(s => processBulletText(s, showAdded, showOptimized))
      .filter(s => s.trim().length > 0)
      .map(s => s.replace(/<[^>]*>/g, ''))
      .join(' • ');

    let expText = '';
    data.experience.forEach((exp, i) => {
      const bullets = exp.bullets
        .map((b, bIdx) => {
          const bulletText = (!showOptimized && originalResume && originalResume.experience[i]?.bullets[bIdx]) 
            ? originalResume.experience[i].bullets[bIdx] 
            : b;
          return `* ${processBulletText(bulletText, showAdded, showOptimized, true).replace(/<[^>]*>/g, '')}`;
        })
        .join('\n');
      expText += `\n${processBulletText(exp.role, showAdded, showOptimized).replace(/<[^>]*>/g, '')} | ${exp.company} (${exp.duration})\n${bullets}\n`;
    });

    let projText = '';
    data.projects.forEach((proj, i) => {
      const bullets = proj.bullets
        .map((b, bIdx) => {
          const bulletText = (!showOptimized && originalResume && originalResume.projects[i]?.bullets[bIdx]) 
            ? originalResume.projects[i].bullets[bIdx] 
            : b;
          return `* ${processBulletText(bulletText, showAdded, showOptimized, true).replace(/<[^>]*>/g, '')}`;
        })
        .join('\n');
      projText += `\n${proj.name} | ${processBulletText(proj.description, showAdded, showOptimized).replace(/<[^>]*>/g, '')}\n${bullets}\n`;
    });

    let eduText = '';
    data.education.forEach(edu => {
      eduText += `\n${edu.degree} | ${edu.school} (${edu.year})\n`;
    });

    let certText = '';
    if (data.certifications && data.certifications.length > 0) {
      data.certifications.forEach((cert, i) => {
        const certVal = (!showOptimized && originalResume && originalResume.certifications?.[i])
          ? originalResume.certifications[i]
          : cert;
        certText += `* ${processBulletText(certVal, showAdded, showOptimized).replace(/<[^>]*>/g, '')}\n`;
      });
    }

    const plainText = `
${data.personalInfo.name.toUpperCase()}
${data.personalInfo.email} | ${data.personalInfo.phone}

PROFESSIONAL SUMMARY
-------------------------------------
${cleanSummary}

TECHNICAL SKILLS
-------------------------------------
${skills}

WORK EXPERIENCE
-------------------------------------
${expText}
${projText ? `\nTECHNICAL PROJECTS\n-------------------------------------\n${projText}` : ''}
EDUCATION
-------------------------------------
${eduText}
${certText ? `\nCERTIFICATIONS\n-------------------------------------\n${certText}` : ''}
    `.trim();

    const blob = new Blob([plainText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${resumeName.replace(/\.[^/.]+$/, "")}_Optimized_Resume.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex flex-col gap-6 w-full">
      {/* Comparer Toolbar */}
      <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4 bg-slate-900/40 border border-white/5 px-6 py-4 rounded-xl data-[light=true]:bg-white data-[light=true]:border-black/5" data-light={theme === 'light'}>
        <div className="flex gap-5 text-xs font-semibold select-none">
          <button 
            id="toggle-added-keywords"
            onClick={() => setShowAdded(!showAdded)}
            className="flex items-center gap-2.5 cursor-pointer hover:opacity-80 transition-opacity focus:outline-none"
          >
            <div className={`w-4 h-4 rounded border flex items-center justify-center transition-colors
              ${showAdded 
                ? 'bg-emerald-500 border-emerald-500 text-white font-bold' 
                : 'bg-transparent border-slate-400 text-transparent'
              }
            `}>
              <span className="text-[9px] leading-none">✓</span>
            </div>
            <span className="text-slate-400 data-[light=true]:text-slate-700 font-bold" data-light={theme === 'light'}>
              Added Keyword
            </span>
          </button>

          <button 
            id="toggle-optimized-bullets"
            onClick={() => setShowOptimized(!showOptimized)}
            className="flex items-center gap-2.5 cursor-pointer hover:opacity-80 transition-opacity focus:outline-none"
          >
            <div className={`w-4 h-4 rounded border flex items-center justify-center transition-colors
              ${showOptimized 
                ? 'bg-amber-500 border-amber-500 text-white font-bold' 
                : 'bg-transparent border-slate-400 text-transparent'
              }
            `}>
              <span className="text-[9px] leading-none">✓</span>
            </div>
            <span className="text-slate-400 data-[light=true]:text-slate-700 font-bold" data-light={theme === 'light'}>
              Optimized Bullet
            </span>
          </button>
        </div>

        <div className="flex flex-wrap gap-3">
          <button onClick={exportPlainTxt} className="flex items-center gap-2 px-4 py-2 bg-slate-800 border border-white/10 hover:border-white/20 text-white rounded-lg text-xs font-bold transition-all cursor-pointer">
            <FileText className="w-3.5 h-3.5 text-slate-400" /> Export Plain Text
          </button>
          <button onClick={exportDocx} className="flex items-center gap-2 px-4 py-2 bg-slate-800 border border-white/10 hover:border-white/20 text-white rounded-lg text-xs font-bold transition-all cursor-pointer">
            <FileDown className="w-3.5 h-3.5 text-blue-400" /> Export DOCX
          </button>
          <button onClick={exportPDF} className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-violet-600 to-blue-500 hover:scale-[1.02] text-white rounded-lg text-xs font-bold shadow-md shadow-violet-500/10 transition-all cursor-pointer">
            <FileDown className="w-3.5 h-3.5" /> Download Optimized PDF
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8 items-start w-full">
        {/* Left pane: Original */}
        <div className="flex flex-col gap-3">
          <div className="flex justify-between items-center text-sm font-semibold text-slate-400">
            <span>Original Resume</span>
            <FileText className="w-4 h-4" />
          </div>
          <div className="bg-white text-slate-800 p-4 sm:p-10 rounded-2xl shadow-xl min-h-[400px] sm:min-h-[780px] text-xs leading-relaxed border border-black/5 selection:bg-slate-200">
            <ResumePaper data={originalResume} />
          </div>
        </div>

        {/* Right pane: Optimized */}
        <div className="flex flex-col gap-3">
          <div className="flex justify-between items-center text-sm font-semibold text-slate-400">
            <span>Optimized Resume</span>
            <CircleCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <div
            ref={optContainerRef}
            className="bg-white text-slate-800 p-4 sm:p-10 rounded-2xl shadow-xl min-h-[400px] sm:min-h-[780px] text-xs leading-relaxed border border-black/5 selection:bg-slate-200 relative optimized-paper"
          >
            <ResumePaper data={optimizedResume} originalData={originalResume} showAdded={showAdded} showOptimized={showOptimized} />
          </div>
        </div>
      </div>

      {/* Floating Tooltip Bubble */}
      {tooltip.visible && (
        <div
          className="absolute bg-slate-900 border border-white/10 text-white text-[11px] leading-relaxed p-2.5 rounded-lg max-w-[200px] shadow-2xl z-50 pointer-events-none -translate-x-1/2 -translate-y-full animate-fade-in"
          style={{ top: tooltip.top, left: tooltip.left }}
        >
          {tooltip.text}
        </div>
      )}
    </div>
  );
}

// Inner Component: Render formatted sections
function ResumePaper({ 
  data, 
  originalData, 
  showAdded = true, 
  showOptimized = true 
}: { 
  data: ResumeData; 
  originalData?: ResumeData; 
  showAdded?: boolean; 
  showOptimized?: boolean 
}) {
  const summaryText = (!showOptimized && originalData) ? originalData.summary : data.summary;

  return (
    <div>
      <h2 className="text-center font-bold text-[22px] text-black mb-1 font-serif">
        {data.personalInfo.name}
      </h2>
      <div className="text-center text-[11px] text-black font-semibold mb-4 flex justify-center gap-2">
        <span>Mobile: - {data.personalInfo.phone}</span> | <span>Email: - <a href={`mailto:${data.personalInfo.email}`} className="text-blue-600 underline">{data.personalInfo.email}</a></span>
        {data.personalInfo.linkedin && <> | <span><a href={data.personalInfo.linkedin} className="text-blue-600 underline">LinkedIn</a></span></>}
        {data.personalInfo.github && <> | <span><a href={data.personalInfo.github} className="text-blue-600 underline">GitHub</a></span></>}
      </div>

      <h3 className="font-bold text-[14px] text-black border-b border-black pb-0.5 mt-4 mb-2">
        Career Objective
      </h3>
      <p className="text-black text-justify mb-4 text-[11px] leading-relaxed" dangerouslySetInnerHTML={{ __html: processBulletText(summaryText, showAdded, showOptimized) }} />

      <h3 className="font-bold text-[14px] text-black border-b border-black pb-0.5 mt-4 mb-2">
        Technical Skills
      </h3>
      <div className="flex flex-col gap-0.5 mb-4 text-[11px] text-black">
        {data.skills
          .map(s => processBulletText(s, showAdded, showOptimized))
          .filter(s => s.trim().length > 0)
          .map((s, idx) => {
            // Bold the category name if it exists (before colon, or before " - ", " – ")
            const formattedSkill = s.replace(/^([^:]+:|.*?\s[-–—]\s)/, '<strong>$1</strong>');
            return (
              <div key={idx} dangerouslySetInnerHTML={{ __html: formattedSkill }} />
            );
          })}
      </div>

      {data.experience && data.experience.length > 0 && (
        <>
          <h3 className="font-bold text-[14px] text-black border-b border-black pb-0.5 mt-4 mb-2">
            Work Experience
          </h3>
      <div className="flex flex-col gap-4">
        {data.experience.map((exp, i) => (
          <div key={i} className="flex flex-col">
            <div className="flex justify-between items-baseline font-bold text-slate-900">
              <span dangerouslySetInnerHTML={{ __html: processBulletText(exp.role, showAdded, showOptimized) }} />
              <span>{exp.duration}</span>
            </div>
            <div className="flex justify-between items-baseline text-slate-500 text-[10px] italic mb-1.5">
              <span>{exp.company}</span>
            </div>
            <ul className="list-square list-inside pl-4 text-slate-700 flex flex-col gap-1">
              {exp.bullets.map((b, bIdx) => {
                const bulletText = (!showOptimized && originalData && originalData.experience[i]?.bullets[bIdx]) 
                  ? originalData.experience[i].bullets[bIdx] 
                  : b;
                return (
                  <li key={bIdx} className="text-justify indent-[-10px] pl-[10px]" dangerouslySetInnerHTML={{ __html: processBulletText(bulletText, showAdded, showOptimized, true) }} />
                );
              })}
            </ul>
          </div>
        ))}
      </div>
      </>
      )}
      {data.education && data.education.length > 0 && (
        <>
          <h3 className="font-bold text-[14px] text-black border-b border-black pb-0.5 mt-4 mb-2">
            Education
          </h3>
          <div className="flex flex-col gap-3 mb-4">
            {data.education.map((edu, i) => (
              <div key={i} className="flex flex-col text-[11px]">
                <div className="flex justify-between items-baseline font-bold text-black">
                  <span>{edu.degree}</span>
                  <span>{edu.year}</span>
                </div>
                <div className="text-black flex justify-between items-baseline">
                  {(() => {
                    const match = edu.school.match(/(.*?)\s+(CGPA:.*|Percentage:.*)$/i);
                    if (match) {
                      return (
                        <>
                          <span>{match[1]}</span>
                          <span>{match[2]}</span>
                        </>
                      );
                    }
                    return <span>{edu.school}</span>;
                  })()}
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {data.projects && data.projects.length > 0 && (
        <>
          <h3 className="font-bold text-[14px] text-black border-b border-black pb-0.5 mt-4 mb-2">
            Projects
          </h3>
          <div className="flex flex-col gap-4 mb-4">
            {data.projects.map((proj, i) => (
              <div key={i} className="flex flex-col text-[11px]">
                <div className="font-bold text-black mb-1">
                  <span>{proj.name}</span>
                  {proj.description && proj.description.trim() !== '' && (
                    <span dangerouslySetInnerHTML={{ __html: ` | ${processBulletText(proj.description, showAdded, showOptimized)}` }} />
                  )}
                </div>
                {proj.bullets && proj.bullets.length > 0 && (
                  <ul className="list-disc list-outside pl-4 ml-1 text-black flex flex-col gap-1">
                    {proj.bullets.map((b, bIdx) => {
                      const bulletText = (!showOptimized && originalData && originalData.projects[i]?.bullets[bIdx]) 
                        ? originalData.projects[i].bullets[bIdx] 
                        : b;
                      return (
                        <li key={bIdx} className="text-justify pl-1" dangerouslySetInnerHTML={{ __html: processBulletText(bulletText, showAdded, showOptimized, true) }} />
                      );
                    })}
                  </ul>
                )}
              </div>
            ))}
          </div>
        </>
      )}

      {data.certifications && data.certifications.length > 0 && (
        <>
          <h3 className="font-bold text-[14px] text-black border-b border-black pb-0.5 mt-4 mb-2">
            Certifications
          </h3>
          <ul className="list-disc list-outside pl-4 ml-1 text-black flex flex-col gap-1 text-[11px]">
            {data.certifications.map((cert, i) => {
              const certText = (!showOptimized && originalData?.certifications?.[i]) 
                ? originalData.certifications[i] 
                : cert;
              return (
                <li key={i} className="text-justify pl-1" dangerouslySetInnerHTML={{ __html: processBulletText(certText, showAdded, showOptimized) }} />
              );
            })}
          </ul>
        </>
      )}
    </div>
  );
}
