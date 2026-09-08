"""
Admin Analytics endpoints (Step 7): total scans, most-scanned domains,
average privacy score.
"""
from collections import Counter
from urllib.parse import urlparse

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import require_admin
from app.database import get_db
from app.models import Report, Scan, User
from app.schemas import AdminStatsResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=AdminStatsResponse)
def get_stats(db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    total_scans = db.query(func.count(Scan.id)).scalar() or 0
    total_users = db.query(func.count(User.id)).scalar() or 0
    average_score = db.query(func.avg(Report.score)).scalar()

    urls = [row[0] for row in db.query(Scan.url).all()]
    domain_counts = Counter(urlparse(u).netloc or u for u in urls)
    most_scanned = [
        {"domain": domain, "count": count}
        for domain, count in domain_counts.most_common(10)
    ]

    return AdminStatsResponse(
        total_scans=total_scans,
        total_users=total_users,
        average_score=round(average_score, 1) if average_score is not None else None,
        most_scanned_domains=most_scanned,
    )
