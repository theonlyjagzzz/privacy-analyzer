"""
FastAPI app entrypoint. Run with:

    uvicorn app.main:app --reload

Wires together all routers and creates DB tables on startup (for local dev;
use Alembic migrations in production instead of create_all).
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import admin_router, auth_router, reports_router, scan_router

app = FastAPI(
    title="AI Privacy & Consent Analyzer — Backend",
    description="Middleman between Frontend, the scraper, the ML module, and the database.",
    version="1.0.0",
)

# Allow the frontend (running on a different origin during dev) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to the real frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


app.include_router(auth_router.router)
app.include_router(scan_router.router)
app.include_router(reports_router.router)
app.include_router(admin_router.router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
