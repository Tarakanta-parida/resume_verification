'use client';

import React, { useEffect, useState } from 'react';

interface GaugeProps {
  score: number;
  label: string;
  colorClass: string;
  size?: number;
}

export default function Gauges({ score, label, colorClass, size = 120 }: GaugeProps) {
  const [animatedScore, setAnimatedScore] = useState(0);
  const radius = 50;
  const strokeWidth = 10;
  const circumference = 2 * Math.PI * radius; // ~314

  useEffect(() => {
    // Animate score from 0 to target
    let start = 0;
    const duration = 1500;
    const stepTime = Math.abs(Math.floor(duration / score));

    if (score === 0) return;

    const timer = setInterval(() => {
      start += 1;
      setAnimatedScore(start);
      if (start >= score) {
        clearInterval(timer);
      }
    }, stepTime);

    return () => clearInterval(timer);
  }, [score]);

  const dashOffset = circumference - (animatedScore / 100) * circumference;

  return (
    <div className="flex flex-col items-center">
      <span className="text-sm font-semibold text-slate-400 mb-3">{label}</span>
      <div className="relative" style={{ width: size, height: size }}>
        <svg className="-rotate-90 w-full h-full">
          <circle
            className="fill-none stroke-slate-800"
            cx="60"
            cy="60"
            r={radius}
            strokeWidth={strokeWidth}
          />
          <circle
            className="fill-none transition-all duration-300 stroke-linecap-round"
            style={{
              strokeDasharray: circumference,
              strokeDashoffset: dashOffset,
              stroke: colorClass
            }}
            cx="60"
            cy="60"
            r={radius}
            strokeWidth={strokeWidth}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center font-title font-extrabold text-2xl" style={{ color: colorClass }}>
          {animatedScore}%
        </div>
      </div>
    </div>
  );
}
