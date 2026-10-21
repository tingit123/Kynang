"""
Router: Gợi Ý & Quản Lý Khóa Học
"""
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel

from src.database import get_db
from src.models.course import CourseRecommendation
from src.models.skill import SkillCatalog
from src.models.user import User
from src.core.security import get_current_user_optional

router = APIRouter()


class CourseCreate(BaseModel):
    skill_id: Optional[int] = None
    skill_name: Optional[str] = None
    industry: Optional[str] = "IT"
    course_name: str
    platform: Optional[str] = "Mekong Skills"
    url: Optional[str] = None
    priority: int = 1
    status: Optional[str] = "pending"
    outcomes: Optional[str] = None
    skills_acquired: Optional[str] = None
    tools_acquired: Optional[str] = None


class CourseUpdate(BaseModel):
    skill_id: Optional[int] = None
    skill_name: Optional[str] = None
    industry: Optional[str] = None
    course_name: Optional[str] = None
    platform: Optional[str] = None
    url: Optional[str] = None
    priority: Optional[int] = None
    status: Optional[str] = None
    outcomes: Optional[str] = None
    skills_acquired: Optional[str] = None
    tools_acquired: Optional[str] = None


class CourseOut(BaseModel):
    id: int
    provider_id: Optional[int] = None
    skill_id: int
    skill_name: str
    industry: Optional[str] = None
    course_name: str
    platform: Optional[str] = None
    url: Optional[str] = None
    priority: int = 1
    status: str = "pending"
    click_count: int = 0
    outcomes: Optional[str] = None
    skills_acquired: Optional[str] = None
    tools_acquired: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/", response_model=List[CourseOut])
def list_courses(
    q: Optional[str] = Query(None, description="Tìm kiếm theo tên khóa học, nền tảng, kỹ năng"),
    skill_id: Optional[int] = Query(None),
    skill: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = (
        db.query(CourseRecommendation, SkillCatalog)
        .join(SkillCatalog, CourseRecommendation.skill_id == SkillCatalog.id)
        .filter(CourseRecommendation.is_deleted == False)
    )

    if status and status.lower() != "all":
        query = query.filter(CourseRecommendation.status == status.lower())

    if skill and skill.lower() != "all":
        clean_skill = skill.split("·")[0].split("-")[0].strip()
        query = query.filter(SkillCatalog.skill_name.ilike(f"%{clean_skill}%"))

    if skill_id:
        query = query.filter(CourseRecommendation.skill_id == skill_id)

    if industry and industry != "Tất cả" and industry.lower() != "all":
        query = query.filter(
            or_(
                CourseRecommendation.industry == industry,
                CourseRecommendation.industry == "all",
                SkillCatalog.industry == industry,
                SkillCatalog.industry == "Tất cả",
            )
        )

    if q and q.strip():
        term = f"%{q.strip()}%"
        query = query.filter(
            or_(
                CourseRecommendation.course_name.ilike(term),
                CourseRecommendation.platform.ilike(term),
                SkillCatalog.skill_name.ilike(term),
            )
        )

    results = query.order_by(CourseRecommendation.id.desc()).all()
    return [
        CourseOut(
            id=c.id,
            provider_id=c.provider_id,
            skill_id=c.skill_id,
            skill_name=sk.skill_name,
            industry=c.industry or sk.industry or "IT",
            course_name=c.course_name,
            platform=c.platform,
            url=c.url,
            priority=c.priority or 1,
            status=c.status or "pending",
            click_count=c.click_count or 0,
            outcomes=c.outcomes,
            skills_acquired=c.skills_acquired,
            tools_acquired=c.tools_acquired,
            created_at=c.created_at or "12/10/2026",
        )
        for c, sk in results
    ]


@router.post("/", response_model=CourseOut, status_code=201)
def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Thêm khóa học mới vào MySQL."""
    target_skill = None
    if course.skill_id:
        target_skill = db.query(SkillCatalog).filter(SkillCatalog.id == course.skill_id).first()

    if not target_skill and course.skill_name:
        clean_name = course.skill_name.split("·")[0].split("-")[0].strip()
        target_skill = (
            db.query(SkillCatalog)
            .filter(SkillCatalog.skill_name.ilike(f"%{clean_name}%"))
            .first()
        )
        if not target_skill:
            target_skill = SkillCatalog(skill_name=clean_name, industry=course.industry or "IT")
            db.add(target_skill)
            db.commit()
            db.refresh(target_skill)

    if not target_skill:
        target_skill = db.query(SkillCatalog).first()

    skill_id = target_skill.id if target_skill else 1
    today_str = datetime.now().strftime("%d/%m/%Y")
    course_status = course.status if course.status else ("approved" if (current_user and current_user.role == "admin") else "pending")

    db_course = CourseRecommendation(
        skill_id=skill_id,
        course_name=course.course_name,
        platform=course.platform or "Mekong Skills",
        url=course.url or "https://mekongskills.vn",
        priority=course.priority or 1,
        status=course_status,
        click_count=0,
        is_deleted=False,
        provider_id=current_user.id if current_user else 12,
        industry=course.industry or (target_skill.industry if target_skill else "IT"),
        outcomes=course.outcomes,
        skills_acquired=course.skills_acquired,
        tools_acquired=course.tools_acquired,
        created_at=today_str,
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)

    return CourseOut(
        id=db_course.id,
        provider_id=db_course.provider_id,
        skill_id=db_course.skill_id,
        skill_name=target_skill.skill_name if target_skill else "Chung",
        industry=db_course.industry or (target_skill.industry if target_skill else "IT"),
        course_name=db_course.course_name,
        platform=db_course.platform,
        url=db_course.url,
        priority=db_course.priority or 1,
        status=db_course.status,
        click_count=db_course.click_count or 0,
        outcomes=db_course.outcomes,
        skills_acquired=db_course.skills_acquired,
        tools_acquired=db_course.tools_acquired,
        created_at=db_course.created_at,
    )


@router.put("/{course_id}", response_model=CourseOut)
def update_course(
    course_id: int,
    course_data: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Sửa thông tin khóa học (Lưu đè dữ liệu cũ vào MySQL)."""
    db_course = (
        db.query(CourseRecommendation)
        .filter(CourseRecommendation.id == course_id, CourseRecommendation.is_deleted == False)
        .first()
    )
    if not db_course:
        raise HTTPException(status_code=404, detail="Không tìm thấy khóa học cần cập nhật")

    if course_data.course_name is not None:
        db_course.course_name = course_data.course_name
    if course_data.platform is not None:
        db_course.platform = course_data.platform
    if course_data.url is not None:
        db_course.url = course_data.url
    if course_data.priority is not None:
        db_course.priority = course_data.priority
    if course_data.status is not None:
        db_course.status = course_data.status
    if course_data.industry is not None:
        db_course.industry = course_data.industry
    if course_data.outcomes is not None:
        db_course.outcomes = course_data.outcomes
    if course_data.skills_acquired is not None:
        db_course.skills_acquired = course_data.skills_acquired
    if course_data.tools_acquired is not None:
        db_course.tools_acquired = course_data.tools_acquired

    if course_data.skill_id:
        db_course.skill_id = course_data.skill_id
    elif course_data.skill_name:
        clean_name = course_data.skill_name.split("·")[0].split("-")[0].strip()
        sk = db.query(SkillCatalog).filter(SkillCatalog.skill_name.ilike(f"%{clean_name}%")).first()
        if sk:
            db_course.skill_id = sk.id

    db.commit()
    db.refresh(db_course)

    skill = db.query(SkillCatalog).filter(SkillCatalog.id == db_course.skill_id).first()

    return CourseOut(
        id=db_course.id,
        provider_id=db_course.provider_id,
        skill_id=db_course.skill_id,
        skill_name=skill.skill_name if skill else "Chung",
        industry=db_course.industry or (skill.industry if skill else "IT"),
        course_name=db_course.course_name,
        platform=db_course.platform,
        url=db_course.url,
        priority=db_course.priority or 1,
        status=db_course.status,
        click_count=db_course.click_count or 0,
        outcomes=db_course.outcomes,
        skills_acquired=db_course.skills_acquired,
        tools_acquired=db_course.tools_acquired,
        created_at=db_course.created_at,
    )


@router.delete("/{course_id}")
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Xóa khóa học (Soft delete trong MySQL)."""
    course = (
        db.query(CourseRecommendation)
        .filter(CourseRecommendation.id == course_id, CourseRecommendation.is_deleted == False)
        .first()
    )
    if not course:
        raise HTTPException(status_code=404, detail="Không tìm thấy khóa học")

    course.is_deleted = True
    db.commit()
    return {"message": "Đã xóa khóa học thành công", "id": course_id}


@router.get("/redirect/{course_id}")
def redirect_course(course_id: int, db: Session = Depends(get_db)):
    """Đếm lượt click khóa học và chuyển hướng 302 tới URL gốc."""
    course = (
        db.query(CourseRecommendation)
        .filter(CourseRecommendation.id == course_id, CourseRecommendation.is_deleted == False)
        .first()
    )
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
