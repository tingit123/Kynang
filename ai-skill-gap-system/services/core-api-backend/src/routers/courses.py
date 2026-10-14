"""
Router: Gợi Ý Khóa Học
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.database import get_db
from src.models.course import CourseRecommendation
from src.models.skill import SkillCatalog
from src.models.user import User
from src.core.security import require_role, get_current_user_optional

router = APIRouter()


class CourseCreate(BaseModel):
    skill_id: int
    course_name: str
    platform: Optional[str] = "Coursera"
    url: Optional[str] = None
    priority: int = 1


class CourseOut(BaseModel):
    id: int
    provider_id: Optional[int] = None
    skill_id: int
    skill_name: str
    industry: Optional[str] = None
    course_name: str
    platform: Optional[str]
    url: Optional[str]
    priority: int
    status: str = "pending"
    click_count: int = 0

    class Config:
        from_attributes = True


@router.get("/", response_model=List[CourseOut])
def list_courses(
    skill_id: Optional[int] = Query(None),
    industry: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    q = (
        db.query(CourseRecommendation, SkillCatalog)
        .join(SkillCatalog, CourseRecommendation.skill_id == SkillCatalog.id)
        .filter(CourseRecommendation.is_deleted == False)
    )
    if skill_id:
        q = q.filter(CourseRecommendation.skill_id == skill_id)
    if industry and industry != "Tất cả":
        q = q.filter(SkillCatalog.industry.in_([industry, "Tất cả"]))

    results = q.order_by(CourseRecommendation.priority, CourseRecommendation.id).all()
    return [
        CourseOut(
            id=c.id,
            provider_id=c.provider_id,
            skill_id=c.skill_id,
            skill_name=sk.skill_name,
            industry=sk.industry,
            course_name=c.course_name,
            platform=c.platform,
            url=c.url,
            priority=c.priority,
            status=c.status or "pending",
            click_count=c.click_count or 0,
        )
        for c, sk in results
    ]


@router.post("/", response_model=CourseOut, status_code=201)
def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["provider", "admin"])),
):
    """Thêm khóa học mới (Yêu cầu vai trò Provider hoặc Admin)."""
    skill = db.query(SkillCatalog).filter(SkillCatalog.id == course.skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Không tìm thấy kỹ năng tương ứng")

    db_course = CourseRecommendation(
        skill_id=course.skill_id,
        course_name=course.course_name,
        platform=course.platform,
        url=course.url,
        priority=course.priority,
        status="approved" if current_user.role == "admin" else "pending",
        click_count=0,
        is_deleted=False,
        provider_id=current_user.id if current_user.role == "provider" else current_user.id,
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)

    return CourseOut(
        id=db_course.id,
        provider_id=db_course.provider_id,
        skill_id=db_course.skill_id,
        skill_name=skill.skill_name,
        industry=skill.industry,
        course_name=db_course.course_name,
        platform=db_course.platform,
        url=db_course.url,
        priority=db_course.priority,
        status=db_course.status,
        click_count=db_course.click_count,
    )


@router.get("/redirect/{course_id}")
def redirect_course(course_id: int, db: Session = Depends(get_db)):
    """Đếm lượt click khóa học và chuyển hướng 302 tới URL gốc của khóa học."""
    course = db.query(CourseRecommendation).filter(
        CourseRecommendation.id == course_id,
        CourseRecommendation.is_deleted == False,
    ).first()
    if not course:
        raise HTTPException(status_code=404, detail="Không tìm thấy khóa học")

    course.click_count = (course.click_count or 0) + 1
    db.commit()

    target_url = course.url or "https://coursera.org"
    return RedirectResponse(url=target_url, status_code=status.HTTP_302_FOUND)


@router.get("/by-skill-name")
def courses_by_skill_name(
    skill_name: str = Query(..., description="Tên kỹ năng"),
    db: Session = Depends(get_db),
):
    """Lấy gợi ý khóa học theo tên kỹ năng."""
    skill = db.query(SkillCatalog).filter(SkillCatalog.skill_name == skill_name).first()
    if not skill:
        return _fallback_courses(skill_name)

    courses = (
        db.query(CourseRecommendation)
        .filter(CourseRecommendation.skill_id == skill.id, CourseRecommendation.is_deleted == False)
        .order_by(CourseRecommendation.priority)
        .all()
    )
    if not courses:
        return _fallback_courses(skill_name)

    return [
        {"course_name": c.course_name, "platform": c.platform, "url": c.url}
        for c in courses
    ]


def _fallback_courses(skill_name: str):
    return [
        {"course_name": f"Khóa học chuyên sâu: {skill_name} 2026", "platform": "Coursera / Udemy", "url": "https://coursera.org"}
    ]


@router.delete("/{course_id}")
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["provider", "admin"])),
):
    """Xóa khóa học (Soft delete). Admin có thể xóa mọi khóa học; Provider chỉ được xóa khóa học của chính họ."""
    course = db.query(CourseRecommendation).filter(
        CourseRecommendation.id == course_id,
        CourseRecommendation.is_deleted == False,
    ).first()
    if not course:
        raise HTTPException(status_code=404, detail="Không tìm thấy khóa học")

    if current_user.role == "provider" and course.provider_id != current_user.id:
        raise HTTPException(status_code=403, detail="Bạn chỉ có thể xóa khóa học do chính bạn tạo")

    course.is_deleted = True
    db.commit()
    return {"message": "Đã xóa khóa học thành công", "id": course_id}

