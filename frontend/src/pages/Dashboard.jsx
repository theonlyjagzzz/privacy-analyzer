import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ChevronRight, Clock, Search } from "lucide-react";
import { getHistory } from "../lib/api";
import { MOCK_HISTORY, riskColor } from "../lib/mockData";

const RISK_FILTERS = ["all", "high", "medium", "low"];
const SORTS = [
  { id: "recent", label: "most recent" },
  { id: "riskiest", label: "riskiest first" },
  { id: "az", label: "site name a–z" },
];

export default function Dashboard() {
  const [history, setHistory] = useState(MOCK_HISTORY);
  const [usingDemoData, setUsingDemoData] = useState(true);
  const [query, setQuery] = useState("");
  const [riskFilter, setRiskFilter] = useState("all");
  const [sort, setSort] = useState("recent");
  const navigate = useNavigate();

  useEffect(() => {
    getHistory()
      .then((res) => {
        if (Array.isArray(res.data) && res.data.length) {
          setHistory(res.data);
          setUsingDemoData(false);
        }
      })
      .catch(() => {
        // Backend not reachable yet — keep showing demo data.
      });
  }, []);

  const visible = useMemo(() => {
    let list = history.filter((h) => h.site.toLowerCase().includes(query.toLowerCase()));
    if (riskFilter !== "all") list = list.filter((h) => h.risk === riskFilter);
    if (sort === "riskiest") list = [...list].sort((a, b) => a.score - b.score);
    else if (sort === "az") list = [...list].sort((a, b) => a.site.localeCompare(b.site));
    else list = [...list].sort((a, b) => new Date(b.date) - new Date(a.date));
    return list;
  }, [history, query, riskFilter, sort]);

  return (
    <div className="max-w-[800px] mx-auto px-4 sm:px-6 py-12 sm:py-14">
      <div className="font-mono text-[11px] text-muted tracking-wide mb-2.5">scan history</div>
      <h1 className="font-serif text-[26px] sm:text-[30px] text-ink mb-6">Your scans</h1>
      {usingDemoData && (
        <div className="font-mono text-[10px] text-faint mb-6">showing demo data — connect the backend to see real scans</div>
      )}

      {history.length > 0 && (
        <div className="mb-6 space-y-3">
          <div className="relative">
            <Search size={14} className="absolute left-3 top-2.5 text-faint" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search scanned sites"
              className="w-full box-border pl-8 pr-3 py-2 border border-line bg-white font-serif text-sm text-ink"
            />
          </div>
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex flex-wrap gap-2">
              {RISK_FILTERS.map((f) => (
                <button
                  key={f}
                  onClick={() => setRiskFilter(f)}
                  className="font-mono text-[11px] px-3 py-1.5 border cursor-pointer"
                  style={
                    riskFilter === f
                      ? { backgroundColor: "#1C2321", color: "#EDEBE2", borderColor: "#1C2321" }
                      : { backgroundColor: "transparent", color: "#6b6a63", borderColor: "#C9C5B6" }
                  }
                >
                  {f}
                </button>
              ))}
            </div>
            <select
              value={sort}
              onChange={(e) => setSort(e.target.value)}
              className="font-mono text-[11px] border border-line bg-white text-ink px-2.5 py-1.5 ml-auto"
            >
              {SORTS.map((s) => (
                <option key={s.id} value={s.id}>
                  sort: {s.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      )}

      {history.length === 0 ? (
        <div className="border border-dashed border-line p-10 text-center font-serif text-muted">
          No scans yet. Run your first one from "New scan".
        </div>
      ) : visible.length === 0 ? (
        <div className="border border-dashed border-line p-10 text-center font-serif text-muted">
          No scans match that search.
        </div>
      ) : (
        <div>
          {visible.map((h) => (
            <button
              key={h.id}
              onClick={() => navigate(`/report/${h.id}`, { state: { site: h.site } })}
              className="w-full flex items-center justify-between px-4 sm:px-5 py-4 sm:py-[18px] mb-2.5 bg-paper-raised border border-line cursor-pointer text-left"
            >
              <div className="flex items-center gap-4 min-w-0">
                <div
                  className="w-10 h-10 rounded-full border-2 flex items-center justify-center font-mono text-[13px] flex-shrink-0"
                  style={{ borderColor: riskColor(h.risk), color: riskColor(h.risk) }}
                >
                  {h.score}
                </div>
                <div className="min-w-0">
                  <div className="font-serif text-base text-ink truncate">{h.site}</div>
                  <div className="font-mono text-[11px] text-muted flex items-center gap-1.5 mt-0.5">
                    <Clock size={11} /> {h.date}
                  </div>
                </div>
              </div>
              <ChevronRight size={16} className="text-faint flex-shrink-0" />
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
