import React from "react";
import { verdictFor } from "../lib/mockData";

export default function ScoreGauge({ score, size = 128, showVerdict = true, showScale = true }) {
  const r = 52;
  const c = 2 * Math.PI * r;
  const pct = Math.max(0, Math.min(100, score)) / 100;
  const color = score >= 70 ? "#3F6B4A" : score >= 45 ? "#B8862E" : "#B23A2E";
  const verdict = verdictFor(score);

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size} viewBox="0 0 120 120">
        <circle cx="60" cy="60" r={r} fill="none" stroke="#C9C5B6" strokeWidth="10" />
        <circle
          cx="60"
          cy="60"
          r={r}
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeLinecap="butt"
          strokeDasharray={`${c * pct} ${c}`}
          transform="rotate(-90 60 60)"
        />
        <text x="60" y="56" textAnchor="middle" className="font-mono" fontSize="30" fontWeight="600" fill="#1C2321">
          {score}
        </text>
        <text x="60" y="74" textAnchor="middle" className="font-mono" fontSize="10" fill="#6b6a63" letterSpacing="1">
          / 100
        </text>
      </svg>
      {showVerdict && (
        <div
          className="font-mono text-xs tracking-wide px-2.5 py-1 mt-1 border"
          style={{ color, borderColor: color, backgroundColor: `${color}14` }}
        >
          {verdict}
        </div>
      )}
      {showScale && (
        <div className="flex items-center gap-1 mt-3 font-mono text-[9px] text-faint">
          <span style={{ color: "#B23A2E" }}>0 risky</span>
          <span>·</span>
          <span style={{ color: "#B8862E" }}>45 caution</span>
          <span>·</span>
          <span style={{ color: "#3F6B4A" }}>70 good</span>
          <span>·</span>
          <span>100</span>
        </div>
      )}
    </div>
  );
}
