import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Lock } from "lucide-react";
import { login, signup } from "../lib/api";

export default function Auth({ onAuthed }) {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    if (!email.includes("@")) {
      setError("Enter a valid email address.");
      return;
    }
    if (password.length < 6) {
      setError("Password needs at least 6 characters.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const call = mode === "login" ? login : signup;
      const res = await call(email, password);
      const token = res?.data?.token;
      if (token) localStorage.setItem("token", token);
      onAuthed(email);
      navigate("/submit");
    } catch (err) {
      // Falls back to a local demo session if the backend isn't running yet,
      // so the frontend stays usable on its own.
      if (err?.code === "ERR_NETWORK") {
        onAuthed(email);
        navigate("/submit");
        return;
      }
      setError(err?.response?.data?.detail || "That didn't work. Check your details and try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-paper flex items-center justify-center px-6">
      <div className="w-[380px]">
        <div className="text-center mb-8">
          <Lock size={26} className="text-ink mx-auto mb-2.5" strokeWidth={1.5} />
          <div className="font-serif text-[26px] text-ink">Consent Analyzer</div>
          <div className="font-mono text-xs text-muted mt-1.5">know what a website does with your data</div>
        </div>

        <div className="bg-paper-raised border border-line p-7">
          <div className="flex mb-[22px] border-b border-line">
            {["login", "signup"].map((m) => (
              <button
                key={m}
                onClick={() => setMode(m)}
                className={`flex-1 pt-2 pb-3 bg-transparent border-0 border-b-2 font-mono text-xs tracking-wide -mb-px ${
                  mode === m ? "border-ink text-ink" : "border-transparent text-muted"
                }`}
              >
                {m === "login" ? "log in" : "sign up"}
              </button>
            ))}
          </div>

          <form onSubmit={submit}>
            <label className="block font-mono text-[11px] text-muted mb-1.5">email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@example.com"
              className="w-full box-border px-3 py-2.5 mb-4 border border-line bg-white font-serif text-sm text-ink"
            />
            <label className="block font-mono text-[11px] text-muted mb-1.5">password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className={`w-full box-border px-3 py-2.5 border border-line bg-white font-serif text-sm text-ink ${
                error ? "mb-2" : "mb-5"
              }`}
            />
            {error && <div className="font-mono text-[11px] text-risk-high mb-3.5">{error}</div>}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 bg-ink text-paper border-none font-mono text-xs tracking-wide cursor-pointer disabled:opacity-60"
            >
              {loading ? "please wait…" : mode === "login" ? "log in" : "create account"}
            </button>
          </form>
        </div>
        <div className="text-center font-mono text-[10px] text-faint mt-4">
          We never share your email or scan history.
        </div>
      </div>
    </div>
  );
}
