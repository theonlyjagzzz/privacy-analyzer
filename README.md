# 🔐 AI Privacy & Consent Analyzer

> Know what a website actually does with your data — before you accept.

[![React](https://img.shields.io/badge/Frontend-React.js-61DAFB?logo=react&logoColor=white)](#)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)](#)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql&logoColor=white)](#)
[![HuggingFace](https://img.shields.io/badge/AI%2FNLP-Transformers-FFD21E?logo=huggingface&logoColor=black)](#)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](#)

---

## 📌 Problem Statement

Users routinely accept Privacy Policies, Terms & Conditions, and Cookie Notices without understanding how their personal data is collected, stored, or shared. These lengthy legal documents make it difficult for the average person to identify privacy risks or make informed decisions about the services they use.

## 💡 Proposed Solution

**AI Privacy & Consent Analyzer** is an AI-powered web platform that analyzes a website's privacy practices from just a URL. It uses AI and NLP to evaluate Privacy Policies, Terms & Conditions, cookie usage, third-party trackers, and data collection practices — then returns an easy-to-understand **Privacy Score**, highlights risky clauses in plain English, and gives concrete recommendations to protect the user.

### Key features

- 🔎 **One-click website scanning** — just paste a URL
- 📊 **Privacy Score (0–100)** with a plain-English verdict (low / caution / high risk)
- 📝 **Plain-English policy summaries** — no legal jargon
- 🚩 **Risky clause detection**, sorted by severity, with the original policy excerpt shown for transparency
- 🍪 **Third-party tracker & cookie detection**
- 🔑 **Requested permission analysis** (location, camera, contacts, etc.)
- 📈 **Comparison with similar websites**
- ✅ **AI-generated privacy recommendations**
- 📄 **Downloadable privacy assessment report** (PDF)
- 🕓 **Scan history dashboard** with search, filter, and sort

---

## 🏗️ Architecture

```
┌──────────┐      ┌──────────────┐      ┌─────────────────────┐      ┌──────────────┐
│  USER    │─────▶│  FRONTEND    │─────▶│  BACKEND (FastAPI)  │─────▶│  DATABASE    │
│          │      │  React.js    │◀─────│                      │◀─────│  PostgreSQL  │
└──────────┘      └──────────────┘      └──────────┬───────────┘      └──────────────┘
                                                     │
                                                     ▼
                                         ┌───────────────────────┐
                                         │   AI / NLP LAYER       │
                                         │  Legal-BERT + BART     │
                                         │  Scoring · Trackers    │
                                         │  Recommendations       │
                                         └───────────────────────┘
```

**Flow:** User submits a URL → Backend scrapes the Privacy Policy / T&C / Cookie Notice → text is sent to the ML module → Legal-BERT classifies risky clauses, BART summarizes, a rule-based engine scores the site → results are stored and returned to the frontend as a report.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React.js, Tailwind CSS, React Router, Chart.js / Plotly |
| **Backend** | Python, FastAPI, PostgreSQL, SQLAlchemy |
| **Web Scraping** | BeautifulSoup, Requests, Selenium |
| **AI / NLP** | Legal-BERT (`nlpaueb/legal-bert-base-uncased`), BART (`facebook/bart-large-cnn`), spaCy, NLTK, Hugging Face Transformers |
| **Report Generation** | reportlab / weasyprint |
| **Auth** | JWT, bcrypt |
| **Deployment** | Docker, Docker Compose, Nginx |
| **Dataset** | OPP-115 (Privacy Policy corpus) |

---

## 📂 Repository Structure

```
.
├── frontend/            # React.js client (this repo's UI)
│   ├── src/
│   │   ├── components/  # TopBar, ScoreGauge, CompareBar, RiskLegend, ProtectedRoute
│   │   ├── pages/        # Auth, Submit, Dashboard, Report
│   │   └── lib/          # api.js (backend client), mockData.js (demo fallback)
│   └── README.md
├── backend/              # FastAPI service — auth, scraping, orchestration, PDF reports
├── ml-service/           # Legal-BERT + BART pipeline, scoring, tracker/cookie detection
├── docs/                 # API contract, architecture diagrams, research write-up
└── docker-compose.yml    # Runs frontend + backend + database + ML service together
```

---

## 🚀 Getting Started

### Prerequisites
- Node.js ≥ 18
- Python ≥ 3.10
- PostgreSQL ≥ 14
- Docker & Docker Compose (recommended for full-stack setup)

### Run with Docker Compose (recommended)

```bash
git clone https://github.com/<your-org>/ai-privacy-consent-analyzer.git
cd ai-privacy-consent-analyzer
docker compose up --build
```

### Run frontend only (development)

```bash
cd frontend
npm install
cp .env.example .env      # set VITE_API_BASE_URL
npm run dev
```

Runs at `http://localhost:5173`. The frontend falls back to built-in demo data whenever the backend isn't reachable, so it's fully browsable on its own.

### Run backend only (development)

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Runs at `http://localhost:8000`. Interactive API docs at `http://localhost:8000/docs`.

---

## 🔌 API Contract (summary)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/signup` | Create an account |
| `POST` | `/auth/login` | Log in, returns a JWT |
| `POST` | `/scan` | Submit a URL to scan (background task) |
| `GET` | `/history` | List past scans for the logged-in user |
| `GET` | `/reports/{id}` | Full report detail |
| `GET` | `/reports/{id}/download` | Download the report as PDF |

Full request/response shapes are defined in [`docs/api-contract.md`](docs/api-contract.md).

---

## 📊 Expected Output

- Privacy Score (0–100)
- Plain-English privacy summary
- Risky clause detection with source excerpts
- Third-party tracker & cookie detection
- Requested permission analysis
- Privacy comparison with similar websites
- AI-generated privacy recommendations
- Downloadable privacy assessment report

---

## 👥 Team

| Name | Role |
|---|---|
| Aorhi Tyagi | Backend Developer |
| Harmeet Sandhu | ML / NLP Engineer  |
| Jagriti Prasad |  Frontend Developer |
| Janhavi Kadam | Integration & Research Lead |

**Under the guidance of:** Prof. Rubina Shaikh

---

## 📄 License

This project is submitted as part of Smart India Hackathon 2026 and is licensed under the [MIT License](LICENSE).
