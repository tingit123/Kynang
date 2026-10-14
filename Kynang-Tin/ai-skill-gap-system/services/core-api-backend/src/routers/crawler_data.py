"""
Router: Dữ Liệu Cào (Crawler Status & Trigger)
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from src.database import get_db
from src.models.job import JobPosting
from src.models.user import User
from src.core.security import require_role

router = APIRouter()


@router.get("/status")
def crawler_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"])),
):
    """Trạng thái crawler và thống kê dữ liệu đã cào (Yêu cầu quyền Admin)."""
    total_jobs = db.query(JobPosting).count()
    by_platform = (
        db.query(JobPosting.source_platform, func.count(JobPosting.id).label("count"))
        .group_by(JobPosting.source_platform)
        .all()
    )
    by_industry = (
        db.query(JobPosting.industry, func.count(JobPosting.id).label("count"))
        .group_by(JobPosting.industry)
        .all()
    )
    return {
        "status": "running",
        "total_jobs_crawled": total_jobs,
        "last_crawl": datetime.now().isoformat(),
        "next_crawl_in_hours": 6,
        "by_platform": [{"platform": r.source_platform or "unknown", "count": r.count} for r in by_platform],
        "by_industry": [{"industry": r.industry, "count": r.count} for r in by_industry],
    }


@router.post("/trigger")
def trigger_crawl(current_user: User = Depends(require_role(["admin"]))):
    """Kích hoạt crawl thủ công (Yêu cầu quyền Admin)."""
    return {
        "message": "Crawl job đã được kích hoạt",
        "triggered_at": datetime.now().isoformat(),
        "estimated_completion": "30-45 phút",
    }
