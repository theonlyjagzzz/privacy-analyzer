import React from "react";

const items = [
  { level: "High risk", color: "#B23A2E", desc: "Actively harmful — selling data, no deletion rights" },
  { level: "Caution", color: "#B8862E", desc: "Worth knowing about — broad collection, vague retention" },
  { level: "Low risk", color: "#3F6B4A", desc: "Standard practice or user-friendly" },
];

export default function RiskLegend() {
  return (
    <div className="flex flex-wrap gap-x-6 gap-y-2 font-mono text-[10px] text-muted mb-6">
      {items.map((it) => (
        <div key={it.level} className="flex items-center gap-1.5">
          <span className="w-2 h-2 flex-shrink-0" style={{ backgroundColor: it.color }} />
          <span style={{ color: it.color }}>{it.level}</span>
          <span className="text-faint">— {it.desc}</span>
        </div>
      ))}
    </div>
  );
}
