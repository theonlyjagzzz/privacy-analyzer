import React from "react";

export default function CompareBar({ label, score, compareLabel = "similar sites avg.", compareScore }) {
  const color = (s) => (s >= 70 ? "#3F6B4A" : s >= 45 ? "#B8862E" : "#B23A2E");

  const Row = ({ name, value }) => (
    <div className="mb-3 last:mb-0">
      <div className="flex justify-between font-mono text-[11px] text-muted mb-1">
        <span>{name}</span>
        <span style={{ color: color(value) }}>{value}</span>
      </div>
      <div className="h-2 bg-line/60 w-full">
        <div className="h-full" style={{ width: `${value}%`, backgroundColor: color(value) }} />
      </div>
    </div>
  );

  return (
    <div>
      <Row name={label} value={score} />
      <Row name={compareLabel} value={compareScore} />
    </div>
  );
}
