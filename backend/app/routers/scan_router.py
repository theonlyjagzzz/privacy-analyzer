"""
POST /scan (Step 5): accepts a URL from frontend, runs the scraper, sends the
extracted text to the ML module, stores everything in the database.

Runs as a background task since scraping + ML inference is slow
(frontend shows a 10-30s loading state while this runs).
"""
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import SessionLocal, get_db
from app.ml_client import MLServiceError, analyze_policy_text
from app.models import ActivityLog, Report, Scan, ScanStatus, User
from app.scraper import ScrapeError, scrape_policy_text
from app.schemas import ScanCreateRequest, ScanCreateResponse

router = APIRouter(tags=["scan"])


def process_scan(scan_id: str) -> None:
    """
    Background worker: scrape -> ML analyze -> persist Report.
    Uses its own DB session since it runs outside the request lifecycle.
    """
    db: Session = SessionLocal()
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            return

        scan.status = ScanStatus.scraping
        db.commit()

        try:
            policy_text = scrape_policy_text(scan.url)
        except ScrapeError as exc:
            scan.status = ScanStatus.failed
            scan.error_message = str(exc)
            db.commit()
            return

        scan.status = ScanStatus.analyzing
        db.commit()

        try:
            result = analyze_policy_text(policy_text)
        except MLServiceError as exc:
            scan.status = ScanStatus.failed
            scan.error_message = str(exc)
            db.commit()
            return

        report = Report(
            scan_id=scan.id,
            score=result.get("score"),
            summary=result.get("summary"),
            clauses=result.get("flagged_clauses", []),
            trackers=result.get("trackers", []),
            recommendations=result.get("recommendations", []),
        )
        db.add(report)

        scan.status = ScanStatus.complete
        scan.completed_at = datetime.utcnow()
        db.commit()

    except Exception as exc:  # noqa: BLE001 - guard the whole background job
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if scan:
            scan.status = ScanStatus.failed
            scan.error_message = f"Unexpected error: {exc}"
            db.commit()
    finally:
        db.close()


@router.post("/scan", response_model=ScanCreateResponse)
def create_scan(
    payload: ScanCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not payload.url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="URL must start with http:// or https://")

    scan = Scan(user_id=current_user.id, url=payload.url, status=ScanStatus.pending)
    db.add(scan)
    db.commit()
    db.refresh(scan)

    db.add(ActivityLog(user_id=current_user.id, action="scan_created", detail=payload.url))
    db.commit()

    background_tasks.add_task(process_scan, scan.id)

    return ScanCreateResponse(scan_id=scan.id, status=scan.status.value)
