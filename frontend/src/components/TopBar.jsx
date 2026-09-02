import React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Lock, LogOut } from "lucide-react";

export default function TopBar({ user, onLogout }) {
  const navigate = useNavigate();
  const location = useLocation();

  const tabs = [
    { id: "/submit", label: "New scan" },
    { id: "/dashboard", label: "History" },
  ];

  const isActive = (path) =>
    location.pathname === path || (path === "/dashboard" && location.pathname.startsWith("/report"));

  return (
    <div className="border-b border-line bg-paper-raised">
      <div className="max-w-[880px] mx-auto px-4 sm:px-6 py-[14px] sm:py-[18px] flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <Lock size={18} className="text-ink" strokeWidth={1.75} />
          <span className="font-serif text-[17px] sm:text-[19px] text-ink">Consent Analyzer</span>
        </div>
        <div className="flex items-center gap-1">
          {tabs.map((t) => (
            <button
              key={t.id}
              onClick={() => navigate(t.id)}
              className={`border-none font-mono text-xs tracking-wide px-2.5 sm:px-3.5 py-2 rounded-sm cursor-pointer ${
                isActive(t.id) ? "bg-ink/[0.08] text-ink" : "bg-transparent text-ink"
              }`}
            >
              {t.label}
            </button>
          ))}
          <div className="w-px h-5 bg-line mx-2 hidden sm:block" />
          <span className="font-mono text-xs text-muted hidden sm:inline">{user}</span>
          <button
            onClick={onLogout}
            title="Log out"
            className="border-none bg-transparent cursor-pointer p-1.5 text-muted"
          >
            <LogOut size={15} />
          </button>
        </div>
      </div>
    </div>
  );
}
