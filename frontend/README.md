# AI Privacy & Consent Analyzer — Frontend

React + Vite + Tailwind. Built to the API contract described in the Team Role
Guide: it calls `/auth/login`, `/auth/signup`, `/scan`, `/history`,
`/reports/{id}`, and `/reports/{id}/download` on the FastAPI backend.

If the backend isn't running yet, every page falls back to built-in demo
data so the UI stays fully browsable on its own.

## UI/UX features

- **Report hierarchy** — score + a plain-language verdict ("High risk" /
  "Caution" / "Low risk") lead the page, ahead of the detail sections.
- **Severity-sorted, filterable clauses** — high-risk clauses surface first;
  filter chips narrow to just high / medium / low.
- **Source excerpts** — each clause expands to show the policy text it was
  flagged from, so the score isn't a black box.
- **Comparison chart** — score vs. a similar-sites average.
- **Requested permissions** — camera/location/contacts-style chips, color
  coded by risk.
- **Risk legend** — one explanation of what red/amber/green mean, shown once
  per report.
- **Step-by-step scan progress** — real named steps (fetch → classify →
  score → summarize) instead of a generic spinner.
- **One-click example sites** on the scan page for first-time users.
- **Dashboard search, risk filter, and sort** (recent / riskiest / a–z)
  across scan history.
- Responsive down to mobile: nav, report layout, and tables all reflow.

## Setup

```bash
npm install
cp .env.example .env   # point VITE_API_BASE_URL at your backend
npm run dev
```

Runs at `http://localhost:5173`.

## Project structure

```
src/
  components/
    TopBar.jsx          nav bar shown once logged in
    ScoreGauge.jsx       circular privacy-score chart
    ProtectedRoute.jsx  redirects to /login if not authed
  pages/
    Auth.jsx             /login  — login + signup forms
    Submit.jsx           /submit — URL input, calls POST /scan
    Dashboard.jsx         /dashboard — scan history, calls GET /history
    Report.jsx            /report/:id — full report, calls GET /reports/:id
  lib/
    api.js                axios client + all backend calls
    mockData.js           demo data used until the backend responds
  App.jsx                 routes + auth state
  main.jsx                entry point
```

## Wiring up the real backend

1. Set `VITE_API_BASE_URL` in `.env` to the backend's address.
2. Confirm the `/scan` response shape matches `mockData.js`'s `MOCK_REPORT`
   (`score`, `summary`, `clauses[]`, `trackers[]`, `recommendations[]`). If
   Backend's shape differs, update `mockData.js` and the `Report.jsx` render
   logic to match — that's the only place the shape is assumed.
3. Auth expects a `token` field back from `/auth/login` and `/auth/signup`;
   it's stored in `localStorage` and sent as `Authorization: Bearer <token>`
   on every request after that.

## Build

```bash
npm run build
```

Outputs static files to `dist/`.
