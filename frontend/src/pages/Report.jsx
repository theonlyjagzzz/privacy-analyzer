import React, { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams, useLocation } from "react-router-dom";
import {
  ShieldCheck,
  ShieldAlert,
  ShieldX,
  FileText,
  Download,
  Cookie,
  ListChecks,
  ChevronDown,
  BarChart3,
  KeyRound,
} from "lucide-react";
import { getReport, getReportDownloadUrl } from "../lib/api";
import { MOCK_REPORT, riskColor, sortBySeverity } from "../lib/mockData";
import ScoreGauge from "../components/ScoreGauge";
import CompareBar from "../components/CompareBar";
import RiskLegend from "../components/RiskLegend";

const FILTERS = ["all", "high", "medium", "low"];

export default function Report() {
  const { id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const [report, setReport] = useState({
    ...MOCK_REPORT,
    site: location.state?.site || MOCK_REPORT.site,
  });
  const [usingDemoData, setUsingDemoData] = useState(true);
  const [filter, setFilter] = useState("all");
  const [expanded, setExpanded] = useState({});

  useEffect(() => {
    if (!id || id === "demo") return;
    getReport(id)
      .then((res) => {
        if (res.data) {
          setReport(res.data);
          setUsingDemoData(false);
        }
      })
      .catch(() => {
        // Backend not reachable yet — keep showing demo data for this URL.
      });
  }, [id]);

  const r = report;

  const sortedClauses = useMemo(() => sortBySeverity(r.clauses || []), [r.clauses]);
  const visibleClauses = filter === "all" ? sortedClauses : sortedClauses.filter((c) => c.level === filter);
  const counts = useMemo(() => {
    const c = { high: 0, medium: 0, low: 0 };
    (r.clauses || []).forEach((cl) => (c[cl.level] = (c[cl.level] || 0) + 1));
    return c;
  }, [r.clauses]);

  const toggleExpand = (i) => setExpanded((e) => ({ ...e, [i]: !e[i] }));

  return (
    <div className="max-w-[820px] mx-auto px-4 sm:px-6 pt-10 sm:pt-12 pb-20">
      <button onClick={() => navigate("/dashboard")} className="border-none bg-transparent cursor-pointer font-mono text-[11px] text-muted p-0 mb-6">
        ← back
      </button>

      {usingDemoData && (
        <div className="font-mono text-[10px] text-faint mb-4">showing demo data — connect the backend to see the real report</div>
      )}

      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4 mb-2">
        <div>
          <div className="font-mono text-[11px] text-muted tracking-wide">privacy report</div>
          <h1 className="font-serif text-[26px] sm:text-[30px] text-ink mt-1.5 mb-1 break-words">{r.site}</h1>
          <div className="font-mono text-[11px] text-faint">scanned {r.scannedAt}</div>
        </div>
        <a
          href={id && id !== "demo" ? getReportDownloadUrl(id) : undefined}
          className="inline-flex items-center gap-2 border border-line bg-paper-raised px-4 py-2.5 font-mono text-[11px] tracking-wide text-ink cursor-pointer h-fit no-underline w-fit"
        >
          <Download size={13} /> download report
        </a>
      </div>

      <div className="flex flex-col sm:flex-row gap-6 sm:gap-7 items-start sm:items-center py-7 border-t border-b border-line my-6">
        <ScoreGauge score={r.score} />
        <div>
          <div className="font-mono text-[11px] text-muted tracking-wide mb-1.5">summary</div>
          <p className="font-serif text-[15.5px] leading-relaxed text-[#2c2f2c] m-0 max-w-[500px]">{r.summary}</p>
        </div>
      </div>

      {typeof r.compareAverage === "number" && (
        <section className="mb-10">
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 size={15} className="text-ink" />
            <h2 className="font-serif text-[19px] text-ink m-0">How it compares</h2>
          </div>
          <div className="border border-line bg-paper-raised px-5 py-5">
            <CompareBar label={r.site} score={r.score} compareScore={r.compareAverage} />
          </div>
        </section>
      )}

      <section className="mb-10">
        <div className="flex items-center gap-2 mb-3">
          <ListChecks size={15} className="text-ink" />
          <h2 className="font-serif text-[19px] text-ink m-0">Flagged clauses</h2>
        </div>
        <RiskLegend />

        <div className="flex flex-wrap gap-2 mb-4">
          {FILTERS.map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className="font-mono text-[11px] px-3 py-1.5 border cursor-pointer"
              style={
                filter === f
                  ? { backgroundColor: "#1C2321", color: "#EDEBE2", borderColor: "#1C2321" }
                  : { backgroundColor: "transparent", color: "#6b6a63", borderColor: "#C9C5B6" }
              }
            >
              {f === "all" ? `all (${(r.clauses || []).length})` : `${f} (${counts[f] || 0})`}
            </button>
          ))}
        </div>

        {visibleClauses.map((c, i) => (
          <div key={i} className="mb-2 bg-paper-raised border-l-[3px]" style={{ borderLeftColor: riskColor(c.level) }}>
            <button
              onClick={() => toggleExpand(i)}
              className="w-full flex items-start gap-3.5 px-4 py-3.5 bg-transparent border-none text-left cursor-pointer"
            >
              {c.level === "high" ? (
                <ShieldX size={17} style={{ color: riskColor(c.level) }} className="flex-shrink-0 mt-0.5" />
              ) : c.level === "medium" ? (
                <ShieldAlert size={17} style={{ color: riskColor(c.level) }} className="flex-shrink-0 mt-0.5" />
              ) : (
                <ShieldCheck size={17} style={{ color: riskColor(c.level) }} className="flex-shrink-0 mt-0.5" />
              )}
              <div className="flex-1">
                <div className="flex items-center justify-between gap-2">
                  <div className="font-serif text-[15px] text-ink">{c.title}</div>
                  <ChevronDown
                    size={14}
                    className="text-faint flex-shrink-0 transition-transform"
                    style={{ transform: expanded[i] ? "rotate(180deg)" : "none" }}
                  />
                </div>
                <div className="font-serif text-[13.5px] text-[#5c5b55]">{c.detail}</div>
              </div>
            </button>
            {expanded[i] && c.source && (
              <div className="px-4 pb-4 pl-[46px]">
                <div className="font-mono text-[10px] text-faint tracking-wide mb-1.5">from the policy text</div>
                <div className="font-serif text-[13.5px] italic text-[#5c5b55] border-l-2 border-line pl-3 leading-relaxed">
                  {c.source}
                </div>
              </div>
            )}
          </div>
        ))}
        {visibleClauses.length === 0 && (
          <div className="font-serif text-sm text-muted py-6 text-center">No clauses in this category.</div>
        )}
      </section>

      {r.permissions?.length > 0 && (
        <section className="mb-10">
          <div className="flex items-center gap-2 mb-4">
            <KeyRound size={15} className="text-ink" />
            <h2 className="font-serif text-[19px] text-ink m-0">Requested permissions</h2>
          </div>
          <div className="flex flex-wrap gap-2">
            {r.permissions.map((p, i) => (
              <span
                key={i}
                className="font-mono text-[11px] px-3 py-1.5 border"
                style={{ color: riskColor(p.risk), borderColor: riskColor(p.risk), backgroundColor: `${riskColor(p.risk)}14` }}
              >
                {p.name}
              </span>
            ))}
          </div>
        </section>
      )}

      <section className="mb-10">
        <div className="flex items-center gap-2 mb-4">
          <Cookie size={15} className="text-ink" />
          <h2 className="font-serif text-[19px] text-ink m-0">Trackers and cookies</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse min-w-[400px]">
            <thead>
              <tr className="border-b border-line">
                <th className="text-left font-mono text-[11px] text-muted pb-2 font-normal">name</th>
                <th className="text-left font-mono text-[11px] text-muted pb-2 font-normal">type</th>
                <th className="text-right font-mono text-[11px] text-muted pb-2 font-normal">instances</th>
              </tr>
            </thead>
            <tbody>
              {r.trackers.map((t, i) => (
                <tr key={i} className="border-b border-line">
                  <td className="font-serif text-[14.5px] text-ink py-2.5">{t.name}</td>
                  <td className="font-mono text-xs text-muted py-2.5">{t.type}</td>
                  <td className="font-mono text-xs text-ink py-2.5 text-right">{t.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <div className="flex items-center gap-2 mb-4">
          <FileText size={15} className="text-ink" />
          <h2 className="font-serif text-[19px] text-ink m-0">Recommendations</h2>
        </div>
        <div className="border border-line bg-paper-raised">
          {r.recommendations.map((rec, i) => (
            <div key={i} className={`flex gap-3 px-[18px] py-3.5 ${i < r.recommendations.length - 1 ? "border-b border-line" : ""}`}>
              <span className="font-mono text-xs text-slate-accent flex-shrink-0">{String(i + 1).padStart(2, "0")}</span>
              <span className="font-serif text-[14.5px] text-[#2c2f2c] leading-relaxed">{rec}</span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
