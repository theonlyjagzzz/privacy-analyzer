import React, { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Search, Clock, Check } from "lucide-react";
import { submitScan } from "../lib/api";
import { MOCK_HISTORY, EXAMPLE_SITES, riskColor } from "../lib/mockData";

const STEPS = ["Fetching policy text", "Classifying clauses", "Scoring privacy practices", "Writing summary"];

export default function Submit() {
  const [url, setUrl] = useState("");
  const [scanning, setScanning] = useState(false);
  const [stepIndex, setStepIndex] = useState(0);
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const timerRef = useRef(null);

  useEffect(() => () => clearInterval(timerRef.current), []);

  const runScan = async (targetUrl) => {
    const trimmed = targetUrl.trim();
    if (!/^https?:\/\/.+\..+/.test(trimmed)) {
      setError("Enter a full URL, like https://example.com.");
      return;
    }
    setError("");
    setScanning(true);
    setStepIndex(0);
    timerRef.current = setInterval(() => {
      setStepIndex((i) => Math.min(i + 1, STEPS.length - 1));
    }, 650);

    try {
      const res = await submitScan(trimmed);
      const id = res?.data?.id;
      clearInterval(timerRef.current);
      navigate(id ? `/report/${id}` : "/report/demo", { state: { site: trimmed } });
    } catch (err) {
      clearInterval(timerRef.current);
      if (err?.code === "ERR_NETWORK") {
        // Backend isn't running yet — fall through to the demo report so the
        // frontend can still be reviewed end to end.
        setStepIndex(STEPS.length - 1);
        setTimeout(() => navigate("/report/demo", { state: { site: trimmed } }), 400);
        return;
      }
      setScanning(false);
      setError("Couldn't scan that site. Check the URL and try again.");
    }
  };

  const scan = (e) => {
    e.preventDefault();
    runScan(url);
  };

  return (
    <div className="max-w-[640px] mx-auto px-4 sm:px-6 py-14 sm:py-[72px]">
      <div className="font-mono text-[11px] text-muted tracking-wide mb-3">new scan</div>
      <h1 className="font-serif text-[28px] sm:text-[34px] text-ink mb-3.5 leading-tight">
        Enter a website to read its privacy policy for you.
      </h1>
      <p className="font-serif text-base text-[#4a4944] leading-relaxed mb-8 max-w-[480px]">
        We scan the privacy policy, terms, and cookie notice, then score how the site actually treats your data.
      </p>

      <form onSubmit={scan} className="flex flex-col sm:flex-row gap-2.5">
        <div className="flex-1 relative">
          <Search size={16} className="absolute left-3.5 top-3.5 text-faint" />
          <input
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com"
            disabled={scanning}
            className="w-full box-border pl-[38px] pr-3.5 py-3 border border-line bg-white font-serif text-[15px] text-ink"
          />
        </div>
        <button
          type="submit"
          disabled={scanning}
          className={`px-[22px] py-3 sm:py-0 border-none font-mono text-xs tracking-wide sm:min-w-[110px] text-paper ${
            scanning ? "bg-faint cursor-default" : "bg-ink cursor-pointer"
          }`}
        >
          {scanning ? "scanning…" : "scan site"}
        </button>
      </form>
      {error && <div className="font-mono text-[11px] text-risk-high mt-2.5">{error}</div>}

      {!scanning && (
        <div className="flex flex-wrap gap-2 mt-4">
          <span className="font-mono text-[10px] text-faint self-center">try one:</span>
          {EXAMPLE_SITES.map((site) => (
            <button
              key={site}
              onClick={() => {
                setUrl(site);
                runScan(site);
              }}
              className="font-mono text-[11px] px-2.5 py-1 border border-line bg-transparent text-muted cursor-pointer hover:border-ink hover:text-ink"
            >
              {site.replace("https://", "")}
            </button>
          ))}
        </div>
      )}

      {scanning && (
        <div className="mt-7 border border-line bg-paper-raised px-5 py-5">
          {STEPS.map((step, i) => {
            const done = i < stepIndex;
            const active = i === stepIndex;
            return (
              <div key={step} className="flex items-center gap-3 py-1.5">
                <div
                  className="w-4 h-4 flex-shrink-0 flex items-center justify-center border font-mono text-[9px]"
                  style={{
                    borderColor: done || active ? "#1C2321" : "#C9C5B6",
                    backgroundColor: done ? "#1C2321" : "transparent",
                    color: done ? "#EDEBE2" : "#1C2321",
                  }}
                >
                  {done ? <Check size={11} /> : i + 1}
                </div>
                <span
                  className="font-mono text-[12px]"
                  style={{ color: active ? "#1C2321" : done ? "#6b6a63" : "#8a887e" }}
                >
                  {step}
                  {active ? "…" : ""}
                </span>
              </div>
            );
          })}
        </div>
      )}

      <div className="mt-14 pt-7 border-t border-line">
        <div className="font-mono text-[11px] text-muted mb-3.5 tracking-wide">recent</div>
        {MOCK_HISTORY.slice(0, 3).map((h) => (
          <div key={h.id} className="flex justify-between py-2.5 border-b border-line">
            <span className="font-serif text-sm text-ink">{h.site}</span>
            <span className="font-mono text-xs" style={{ color: riskColor(h.risk) }}>
              {h.score}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
