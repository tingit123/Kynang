"""
Router: Khảo Sát Sinh Viên & Hồ Sơ CV
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from pydantic import BaseModel
from datetime import date

from src.database import get_db
from src.models.survey import SurveyResponse, SurveySkillRating
from src.models.skill import SkillCatalog
from src.models.course import CourseRecommendation

router = APIRouter()


class SkillRatingOut(BaseModel):
    skill_name: str
    self_rating: int
    industry: Optional[str] = None


class SurveyOut(BaseModel):
    id: int
    student_code: str
    full_name: str
    major: Optional[str]
    year_of_study: Optional[int]
    institution: Optional[str]
    completed_at: Optional[date]
    skills: List[str] = []
    top_ratings: List[SkillRatingOut] = []
    recommended_role: Optional[str] = None
    status: str = "active"

    class Config:
        from_attributes = True


class SurveyListResponse(BaseModel):
    total: int
    page: int
    limit: int
    items: List[SurveyOut]


class DiagnosisRequest(BaseModel):
    student_code: str
    target_job_title: Optional[str] = None
    target_industry: Optional[str] = "IT"


def _infer_role(major: str, top_skills: List[str]) -> str:
    m = (major or "").lower()
    if "thông tin" in m or "phần mềm" in m or "máy tính" in m:
        if "Python" in top_skills or "Machine Learning" in top_skills:
            return "AI / Data Engineer"
        elif "ReactJS" in top_skills or "JavaScript" in top_skills:
            return "Frontend Web Developer"
        return "Backend Developer"
    elif "du lịch" in m or "khách sạn" in m:
        if "Customer Service" in top_skills:
            return "Quản Lý Tiền Sảnh / Khách Sạn"
        return "Chuyên Viên Điều Hành Tour"
    elif "logistics" in m or "vận tải" in m or "ngoại thương" in m:
        if "Customs Compliance" in top_skills or "International Trade Regulations" in top_skills:
            return "Chuyên Viên Xuất Nhập Khẩu"
        return "Quản Lý Chuỗi Cung Ứng / Kho Bãi"
    elif "kế toán" in m or "kiểm toán" in m or "tài chính" in m:
        if "Tax Compliance" in top_skills:
            return "Kế Toán Thuế & Báo Cáo"
        return "Chuyên Viên Phân Tích Tài Chính"
    return "Chuyên Viên Nghiệp Vụ"


@router.get("/", response_model=List[SurveyOut])
def list_surveys(
    q: Optional[str] = Query(None, description="Tìm theo tên hoặc mã"),
    institution: Optional[str] = Query(None),
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(SurveyResponse)
    if institution and institution != "Tất cả":
        query = query.filter(SurveyResponse.institution == institution)
    if q:
        query = query.filter(
            or_(
                SurveyResponse.full_name.ilike(f"%{q}%"),
                SurveyResponse.student_code.ilike(f"%{q}%"),
                SurveyResponse.major.ilike(f"%{q}%")
            )
        )
    surveys = query.order_by(desc(SurveyResponse.id)).offset(offset).limit(limit).all()

    # Lấy kèm ratings
    s_ids = [s.id for s in surveys]
    ratings = (
        db.query(SurveySkillRating, SkillCatalog)
        .join(SkillCatalog, SurveySkillRating.skill_id == SkillCatalog.id)
        .filter(SurveySkillRating.survey_id.in_(s_ids))
        .all()
    ) if s_ids else []

    ratings_map = {}
    for r, sk in ratings:
        ratings_map.setdefault(r.survey_id, []).append((sk.skill_name, r.self_rating, sk.industry))

    results = []
    for s in surveys:
        s_ratings = ratings_map.get(s.id, [])
        s_ratings.sort(key=lambda x: x[1], reverse=True)
        top_skills = [item[0] for item in s_ratings[:6]]
        top_ratings_obj = [
            SkillRatingOut(skill_name=item[0], self_rating=item[1], industry=item[2])
            for item in s_ratings[:6]
        ]
        role = _infer_role(s.major, top_skills)
        results.append(
            SurveyOut(
                id=s.id,
                student_code=s.student_code,
                full_name=s.full_name,
                major=s.major,
                year_of_study=s.year_of_study,
                institution=s.institution,
                completed_at=s.completed_at,
                skills=top_skills,
                top_ratings=top_ratings_obj,
                recommended_role=role,
                status="active"
            )
        )
    return results


@router.get("/paged", response_model=SurveyListResponse)
def list_surveys_paged(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    q: Optional[str] = None,
    institution: Optional[str] = None,
    major: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Phân trang danh sách 500 sinh viên CVs."""
    query = db.query(SurveyResponse)
    if institution and institution != "Tất cả":
        query = query.filter(SurveyResponse.institution == institution)
    if major and major != "Tất cả":
        query = query.filter(SurveyResponse.major.ilike(f"%{major}%"))
    if q:
        query = query.filter(
            or_(
                SurveyResponse.full_name.ilike(f"%{q}%"),
                SurveyResponse.student_code.ilike(f"%{q}%"),
                SurveyResponse.major.ilike(f"%{q}%")
            )
        )

    total = query.count()
    offset = (page - 1) * limit
    surveys = query.order_by(desc(SurveyResponse.id)).offset(offset).limit(limit).all()

    s_ids = [s.id for s in surveys]
    ratings = (
        db.query(SurveySkillRating, SkillCatalog)
        .join(SkillCatalog, SurveySkillRating.skill_id == SkillCatalog.id)
        .filter(SurveySkillRating.survey_id.in_(s_ids))
        .all()
    ) if s_ids else []

    ratings_map = {}
    for r, sk in ratings:
        ratings_map.setdefault(r.survey_id, []).append((sk.skill_name, r.self_rating, sk.industry))

    results = []
    for s in surveys:
        s_ratings = ratings_map.get(s.id, [])
        s_ratings.sort(key=lambda x: x[1], reverse=True)
        top_skills = [item[0] for item in s_ratings[:6]]
        top_ratings_obj = [
            SkillRatingOut(skill_name=item[0], self_rating=item[1], industry=item[2])
            for item in s_ratings[:6]
        ]
        role = _infer_role(s.major, top_skills)
        results.append(
            SurveyOut(
                id=s.id,
                student_code=s.student_code,
                full_name=s.full_name,
                major=s.major,
                year_of_study=s.year_of_study,
                institution=s.institution,
                completed_at=s.completed_at,
                skills=top_skills,
                top_ratings=top_ratings_obj,
                recommended_role=role,
                status="active"
            )
        )

    return SurveyListResponse(total=total, page=page, limit=limit, items=results)


@router.get("/{student_code}")
def get_student_detail(student_code: str, db: Session = Depends(get_db)):
    """Lấy chi tiết hồ sơ CV sinh viên và tất cả điểm kỹ năng."""
    student = db.query(SurveyResponse).filter(SurveyResponse.student_code == student_code).first()
    if not student:
        raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên")

    ratings = (
        db.query(SurveySkillRating, SkillCatalog)
        .join(SkillCatalog, SurveySkillRating.skill_id == SkillCatalog.id)
        .filter(SurveySkillRating.survey_id == student.id)
        .order_by(desc(SurveySkillRating.self_rating))
        .all()
    )

    ratings_list = [
        {
            "skill_name": sk.skill_name,
            "rating": r.self_rating,
            "industry": sk.industry,
            "is_proficient": r.self_rating >= 65
        }
        for r, sk in ratings
    ]

    return {
        "student_code": student.student_code,
        "full_name": student.full_name,
        "major": student.major,
        "institution": student.institution,
        "year_of_study": student.year_of_study,
        "completed_at": student.completed_at,
        "skills": ratings_list
    }


@router.post("/diagnosis")
def diagnose_student_gap(req: DiagnosisRequest, db: Session = Depends(get_db)):
    """Chẩn đoán khoảng cách kỹ năng (Gap) giữa sinh viên và vị trí mong muốn."""
    student = db.query(SurveyResponse).filter(SurveyResponse.student_code == req.student_code).first()
    if not student:
        raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên")

    ratings = (
        db.query(SurveySkillRating, SkillCatalog)
        .join(SkillCatalog, SurveySkillRating.skill_id == SkillCatalog.id)
        .filter(SurveySkillRating.survey_id == student.id)
        .all()
    )
    user_skills = {sk.skill_name: r.self_rating for r, sk in ratings}

    # Lấy các kỹ năng mục tiêu theo ngành yêu cầu
    target_ind = req.target_industry or "IT"
    industry_skills = (
        db.query(SkillCatalog)
        .filter(SkillCatalog.industry.in_([target_ind, "Tất cả"]))
        .order_by(desc(SkillCatalog.demand_pct))
        .limit(10)
        .all()
    )

    possessed = []
    missing = []
    prescriptions = []

    for sk in industry_skills:
        rating = user_skills.get(sk.skill_name, 0)
        if rating >= 65:
            possessed.append({
                "skill": sk.skill_name,
                "rating": rating,
                "status": "Đạt yêu cầu"
            })
        else:
            gap_amount = round(sk.demand_pct - (rating / 100 * sk.supply_pct), 1)
            missing.append({
                "skill": sk.skill_name,
                "current_rating": rating,
                "target_demand": sk.demand_pct,
                "gap": gap_amount,
                "urgency": "Cao" if gap_amount > 20 else "Trung bình"
            })

            # Tìm khóa học gợi ý
            courses = (
                db.query(CourseRecommendation)
                .filter(CourseRecommendation.skill_id == sk.id)
                .order_by(CourseRecommendation.priority)
                .all()
            )
            for c in courses:
                prescriptions.append({
                    "skill": sk.skill_name,
                    "course_name": c.course_name,
                    "platform": c.platform,
                    "url": c.url
                })

    return {
        "student_code": student.student_code,
        "full_name": student.full_name,
        "major": student.major,
        "target_industry": target_ind,
        "possessed_skills": possessed,
        "missing_skills": missing,
        "prescriptions": prescriptions[:6]
    }


@router.get("/stats")
def survey_stats(db: Session = Depends(get_db)):
    """Thống kê khảo sát theo trường, ngành."""
    from sqlalchemy import func
    by_major = (
        db.query(SurveyResponse.major, func.count(SurveyResponse.id).label("count"))
        .group_by(SurveyResponse.major)
        .all()
    )
    by_institution = (
        db.query(SurveyResponse.institution, func.count(SurveyResponse.id).label("count"))
        .group_by(SurveyResponse.institution)
        .all()
    )
    return {
        "total": db.query(SurveyResponse).count(),
        "by_major": [{"major": r.major, "count": r.count} for r in by_major],
        "by_institution": [{"institution": r.institution, "count": r.count} for r in by_institution],
    }
