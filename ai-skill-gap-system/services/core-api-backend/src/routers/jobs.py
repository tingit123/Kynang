"""
Router: Tin Tuyển Dụng (Job Postings)
"""
from typing import Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from datetime import date, datetime
from src.database import get_db
from src.models.job import JobPosting, JobApplication
from src.models.skill import ExtractedSkill
from src.models.user import User
from src.core.security import get_current_user_optional, get_current_user, require_role, is_worker_token

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
    employer_id: Optional[int] = None
    skills: Optional[List[str]] = []


class JobOut(BaseModel):
    id: int
    employer_id: Optional[int] = None
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


class ApplicationCreate(BaseModel):
    cv_snapshot_text: Optional[str] = None


class ApplicationOut(BaseModel):
    id: int
    job_id: int
    candidate_id: int
    candidate_name: str
    candidate_email: str
    status: str
    cv_snapshot_text: Optional[str] = None
    applied_at: Optional[datetime] = None


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
    query = db.query(JobPosting).filter(JobPosting.is_deleted == False)
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
        loc = (j.location and j.location.strip()) or "Cần Thơ"
        out = JobOut(
            id=j.id,
            employer_id=j.employer_id,
            title=j.title,
            company=j.company,
            location=loc,
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
@router.get("/search", response_model=JobListResponse)
def list_jobs_paged(
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=100),
    offset: Optional[int] = Query(None, description="Bỏ qua số bản ghi (offset)"),
    industry: Optional[str] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Phân trang tin tuyển dụng cho giao diện người dùng."""
    query = db.query(JobPosting).filter(JobPosting.is_deleted == False)
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
    if offset is not None:
        actual_offset = max(0, offset)
        page = (actual_offset // limit) + 1
    else:
        actual_offset = (page - 1) * limit

    jobs = query.order_by(desc(JobPosting.id)).offset(actual_offset).limit(limit).all()

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
        loc = (j.location and j.location.strip()) or "Cần Thơ"
        out = JobOut(
            id=j.id,
            employer_id=j.employer_id,
            title=j.title,
            company=j.company,
            location=loc,
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


@router.get("/my-jobs", response_model=List[JobOut])
def get_my_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["employer", "admin"])),
):
    """Lấy danh sách tin tuyển dụng do chính nhà tuyển dụng tạo."""
    query = db.query(JobPosting).filter(JobPosting.is_deleted == False)
    if current_user.role == "employer":
        query = query.filter(JobPosting.employer_id == current_user.id)
    jobs = query.order_by(desc(JobPosting.id)).all()

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
        loc = (j.location and j.location.strip()) or "Cần Thơ"
        out = JobOut(
            id=j.id,
            employer_id=j.employer_id,
            title=j.title,
            company=j.company,
            location=loc,
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


@router.post("/", response_model=JobOut, status_code=201)
def create_job(
    job: JobCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
    worker_token: Optional[str] = Header(None, alias="X-Worker-Token"),
):
    """
    Thêm tin tuyển dụng mới.
    - Yêu cầu đăng nhập: Role 'employer' hoặc 'admin'.
    - Nếu là 'employer': gán employer_id = current_user.id.
    - Nếu là 'admin': cho phép tạo bình thường (có thể gán employer_id từ payload hoặc current_user.id).
    - Tự động cho phép bot crawler lưu tin tự động mà không bị chặn.
    """
    data = job.model_dump(exclude={"skills"})
    db_job = JobPosting(**data)

    if current_user:
        if current_user.role not in ["employer", "admin"]:
            raise HTTPException(
                status_code=403,
                detail="Chỉ Nhà tuyển dụng (employer) hoặc Admin mới có quyền tạo tin tuyển dụng",
            )
        if current_user.role == "employer":
            db_job.employer_id = current_user.id
        elif current_user.role == "admin":
            db_job.employer_id = job.employer_id or current_user.id
    else:
        # Nếu chưa đăng nhập, kiểm tra nếu là nguồn bot crawler tự động
        is_crawler = is_worker_token(worker_token)
        if is_crawler:
            db_job.employer_id = None
        else:
            raise HTTPException(
                status_code=401,
                detail="Yêu cầu đăng nhập tài khoản Nhà tuyển dụng hoặc Admin để đăng tin tuyển dụng",
            )

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

    loc = (db_job.location and db_job.location.strip()) or "Cần Thơ"
    return JobOut(
        id=db_job.id,
        employer_id=db_job.employer_id,
        title=db_job.title,
        company=db_job.company,
        location=loc,
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
    job = db.query(JobPosting).filter(JobPosting.id == job_id, JobPosting.is_deleted == False).first()
    if not job:
        raise HTTPException(status_code=404, detail="Không tìm thấy tin tuyển dụng hoặc tin đã bị xóa")
    
    extracted = db.query(ExtractedSkill).filter(ExtractedSkill.job_id == job_id).all()
    skills = [es.skill_name for es in extracted]
    loc = (job.location and job.location.strip()) or "Cần Thơ"

    return JobOut(
        id=job.id,
        employer_id=job.employer_id,
        title=job.title,
        company=job.company,
        location=loc,
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
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "employer"])),
):
    """Soft delete tin tuyển dụng. Admin có thể xóa mọi tin; Employer chỉ được xóa tin của chính họ."""
    job = db.query(JobPosting).filter(JobPosting.id == job_id, JobPosting.is_deleted == False).first()
    if not job:
        raise HTTPException(status_code=404, detail="Không tìm thấy tin tuyển dụng")

    if current_user:
        if current_user.role == "employer" and job.employer_id != current_user.id:
            raise HTTPException(status_code=403, detail="Bạn chỉ có thể xóa tin tuyển dụng do chính bạn tạo")
        elif current_user.role not in ["admin", "employer"]:
            raise HTTPException(status_code=403, detail="Bạn không có quyền xóa tin tuyển dụng này")

    # Soft delete: bảo toàn dữ liệu lịch sử
    job.is_deleted = True
    db.commit()
    return {"message": "Đã xóa tin tuyển dụng thành công", "id": job_id}


@router.post("/{job_id}/apply", status_code=201)
def apply_to_job(
    job_id: int,
    payload: Optional[ApplicationCreate] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["candidate", "admin"])),
):
    """Sinh viên / Ứng viên ứng tuyển vào tin tuyển dụng."""
    job = db.query(JobPosting).filter(JobPosting.id == job_id, JobPosting.is_deleted == False).first()
    if not job:
        raise HTTPException(status_code=404, detail="Không tìm thấy tin tuyển dụng hoặc tin đã hết hạn")

    existing = db.query(JobApplication).filter(
        JobApplication.job_id == job_id,
        JobApplication.candidate_id == current_user.id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bạn đã gửi đơn ứng tuyển vào vị trí này rồi")

    snapshot = payload.cv_snapshot_text if payload else (current_user.latest_cv_analysis or "Hồ sơ ứng viên")
    app = JobApplication(
        job_id=job_id,
        candidate_id=current_user.id,
        cv_snapshot_text=snapshot,
        status="applied",
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    return {
        "message": f"Ứng tuyển thành công vị trí '{job.title}' tại '{job.company}'",
        "application_id": app.id,
    }


@router.get("/{job_id}/applications", response_model=List[ApplicationOut])
def get_job_applications(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["employer", "admin"])),
):
    """Nhà tuyển dụng xem danh sách ứng viên đã nộp đơn vào tin tuyển dụng của mình."""
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Không tìm thấy tin tuyển dụng")
    if current_user.role == "employer" and job.employer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Bạn không có quyền xem ứng viên của tin tuyển dụng này")

    apps = (
        db.query(JobApplication, User)
        .join(User, JobApplication.candidate_id == User.id)
        .filter(JobApplication.job_id == job_id)
        .order_by(desc(JobApplication.id))
        .all()
    )
    return [
        ApplicationOut(
            id=a.id,
            job_id=a.job_id,
            candidate_id=u.id,
            candidate_name=u.full_name,
            candidate_email=u.email,
            status=a.status,
            cv_snapshot_text=a.cv_snapshot_text,
            applied_at=a.applied_at,
        )
        for a, u in apps
    ]


@router.get("/stats/by-industry")
def stats_by_industry(db: Session = Depends(get_db)):
    """Thống kê số tin tuyển dụng theo ngành."""
    from sqlalchemy import func
    results = (
        db.query(JobPosting.industry, func.count(JobPosting.id).label("count"))
        .filter(JobPosting.is_deleted == False)
        .group_by(JobPosting.industry)
        .all()
    )
    return [{"industry": r.industry, "count": r.count} for r in results]
