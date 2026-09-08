"""
Read endpoints (Step 6): GET /history, GET /reports/{id}, GET /reports/{id}/download.
"""
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Report, Scan, User
from app.pdf_generator import generate_report_pdf
from app.schemas import ReportOut, ScanHistoryItem

router = APIRouter(tags=["reports"])


def _get_owned_scan(scan_id: str, user: User, db: Session) -> Scan:
    scan = db.query(Scan).filter(Scan.id == scan_id, Scan.user_id == user.id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan


@router.get("/history", response_model=list[ScanHistoryItem])
def get_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    scans = (
        db.query(Scan)
        .filter(Scan.user_id == current_user.id)
        .order_by(Scan.created_at.desc())
        .all()
    )
    items = []
    for scan in scans:
        score = scan.report.score if scan.report else None
        items.append(ScanHistoryItem(
            scan_id=scan.id,
            url=scan.url,
            status=scan.status.value,
            score=score,
            created_at=scan.created_at,
        ))
    return items


@router.get("/reports/{scan_id}", response_model=ReportOut)
def get_report(scan_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    scan = _get_owned_scan(scan_id, current_user, db)
    report = scan.report

    return ReportOut(
        scan_id=scan.id,
        url=scan.url,
        status=scan.status.value,
        score=report.score if report else None,
        summary=report.summary if report else None,
        clauses=report.clauses if report else [],
        trackers=report.trackers if report else [],
        recommendations=report.recommendations if report else [],
        created_at=report.created_at if report else None,
    )


@router.get("/reports/{scan_id}/download")
def download_report_pdf(scan_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    scan = _get_owned_scan(scan_id, current_user, db)
    if not scan.report:
        raise HTTPException(status_code=409, detail="Report is not ready yet")

    pdf_bytes = generate_report_pdf(scan, scan.report)
    domain = urlparse(scan.url).netloc or "report"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{domain}_privacy_report.pdf"'},
    )
