"""
Router: Tin Tuyển Dụng (Job Postings)
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date

from src.database import get_db
from src.models.job import JobPosting

router = APIRouter()


# ── Pydantic Schemas ─────────────────────────────────────────────
class JobCreate(BaseModel):
    title: str
    company: str
    location: str = "Cần Thơ"
    industry: str
    description: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    posted_date: Optional[date] = None
    source_url: Optional[str] = None
    source_platform: Optional[str] = None


class JobOut(BaseModel):
    id: int
    title: str
    company: str
    location: str
    industry: str
    description: Optional[str]
    salary_min: Optional[int]
    salary_max: Optional[int]
    posted_date: Optional[date]
    source_url: Optional[str]
    source_platform: Optional[str]
    ai_classified: bool

    class Config:
        from_attributes = True


# ── Endpoints ────────────────────────────────────────────────────
@router.get("/", response_model=List[JobOut])
def list_jobs(
    industry: Optional[str] = Query(None, description="Lọc theo ngành"),
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """Lấy danh sách tin tuyển dụng, có thể lọc theo ngành."""
    q = db.query(JobPosting)
    if industry:
        q = q.filter(JobPosting.industry == industry)
    return q.offset(offset).limit(limit).all()


@router.post("/", response_model=JobOut, status_code=201)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    """Thêm tin tuyển dụng mới (dùng bởi Crawler)."""
    db_job = JobPosting(**job.model_dump())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Không tìm thấy tin tuyển dụng")
    return job


@router.get("/stats/by-industry")
def stats_by_industry(db: Session = Depends(get_db)):
    """Thống kê số tin tuyển dụng theo ngành."""
    from sqlalchemy import func
    results = (
        db.query(JobPosting.industry, func.count(JobPosting.id).label("count"))
        .group_by(JobPosting.industry)
        .all()
    )
    return [{"industry": r.industry, "count": r.count} for r in results]
