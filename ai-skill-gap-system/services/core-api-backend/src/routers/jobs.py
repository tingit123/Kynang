"""
Router: Tin Tuyển Dụng (Job Postings)
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from pydantic import BaseModel
from datetime import date

from src.database import get_db
from src.models.job import JobPosting
from src.models.skill import ExtractedSkill

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
    source_platform: Optional[str] = "Thủ công"
    skills: Optional[List[str]] = []


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
    skills: List[str] = []

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    total: int
    page: int
    limit: int
    items: List[JobOut]


# ── Endpoints ────────────────────────────────────────────────────
@router.get("/", response_model=List[JobOut])
def list_jobs(
    industry: Optional[str] = Query(None, description="Lọc theo ngành"),
    q: Optional[str] = Query(None, description="Tìm kiếm từ khóa"),
    limit: int = Query(50, le=2000),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """Lấy danh sách tin tuyển dụng có kèm kỹ năng trích xuất."""
    query = db.query(JobPosting)
    if industry and industry != "Tất cả":
        query = query.filter(JobPosting.industry == industry)
    if q:
        query = query.filter(
            or_(
                JobPosting.title.ilike(f"%{q}%"),
                JobPosting.company.ilike(f"%{q}%"),
                JobPosting.description.ilike(f"%{q}%")
            )
        )
    
    jobs = query.order_by(desc(JobPosting.id)).offset(offset).limit(limit).all()

    # Lấy kèm kỹ năng cho các jobs
    job_ids = [j.id for j in jobs]
    extracted = (
        db.query(ExtractedSkill)
        .filter(ExtractedSkill.job_id.in_(job_ids))
        .all()
    ) if job_ids else []

    skills_map = {}
    for es in extracted:
        skills_map.setdefault(es.job_id, []).append(es.skill_name)

    results = []
    for j in jobs:
        out = JobOut(
            id=j.id,
            title=j.title,
            company=j.company,
            location=j.location or "Cần Thơ",
            industry=j.industry,
            description=j.description,
            salary_min=j.salary_min,
            salary_max=j.salary_max,
            posted_date=j.posted_date,
            source_url=j.source_url,
            source_platform=j.source_platform,
            ai_classified=bool(j.ai_classified),
            skills=skills_map.get(j.id, [])
        )
        results.append(out)
    return results


@router.get("/paged", response_model=JobListResponse)
def list_jobs_paged(
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=100),
    industry: Optional[str] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Phân trang tin tuyển dụng cho giao diện người dùng."""
    query = db.query(JobPosting)
    if industry and industry != "Tất cả":
        query = query.filter(JobPosting.industry == industry)
    if q:
        query = query.filter(
            or_(
                JobPosting.title.ilike(f"%{q}%"),
                JobPosting.company.ilike(f"%{q}%"),
                JobPosting.description.ilike(f"%{q}%")
            )
        )

    total = query.count()
    offset = (page - 1) * limit
    jobs = query.order_by(desc(JobPosting.id)).offset(offset).limit(limit).all()

    job_ids = [j.id for j in jobs]
    extracted = (
        db.query(ExtractedSkill)
        .filter(ExtractedSkill.job_id.in_(job_ids))
        .all()
    ) if job_ids else []

    skills_map = {}
    for es in extracted:
        skills_map.setdefault(es.job_id, []).append(es.skill_name)

    results = []
    for j in jobs:
        out = JobOut(
            id=j.id,
            title=j.title,
            company=j.company,
            location=j.location or "Cần Thơ",
            industry=j.industry,
            description=j.description,
            salary_min=j.salary_min,
            salary_max=j.salary_max,
            posted_date=j.posted_date,
            source_url=j.source_url,
            source_platform=j.source_platform,
            ai_classified=bool(j.ai_classified),
            skills=skills_map.get(j.id, [])
        )
        results.append(out)

    return JobListResponse(total=total, page=page, limit=limit, items=results)


@router.post("/", response_model=JobOut, status_code=201)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    """Thêm tin tuyển dụng mới."""
    data = job.model_dump(exclude={"skills"})
    db_job = JobPosting(**data)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)

    # Thêm kỹ năng nếu có
    if job.skills:
        for sk in job.skills:
            db.add(ExtractedSkill(
                job_id=db_job.id,
                skill_name=sk,
                skill_category=db_job.industry,
                confidence=0.95
            ))
        db.commit()

    return JobOut(
        id=db_job.id,
        title=db_job.title,
        company=db_job.company,
        location=db_job.location or "Cần Thơ",
        industry=db_job.industry,
        description=db_job.description,
        salary_min=db_job.salary_min,
        salary_max=db_job.salary_max,
        posted_date=db_job.posted_date,
        source_url=db_job.source_url,
        source_platform=db_job.source_platform,
        ai_classified=bool(db_job.ai_classified),
        skills=job.skills or []
    )


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Không tìm thấy tin tuyển dụng")
    
    extracted = db.query(ExtractedSkill).filter(ExtractedSkill.job_id == job_id).all()
    skills = [es.skill_name for es in extracted]

    return JobOut(
        id=job.id,
        title=job.title,
        company=job.company,
        location=job.location or "Cần Thơ",
        industry=job.industry,
        description=job.description,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        posted_date=job.posted_date,
        source_url=job.source_url,
        source_platform=job.source_platform,
        ai_classified=bool(job.ai_classified),
        skills=skills
    )


@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    """Xóa tin tuyển dụng."""
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Không tìm thấy tin tuyển dụng")
    db.delete(job)
    db.commit()
    return {"message": "Đã xóa tin tuyển dụng thành công", "id": job_id}


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
