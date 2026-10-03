"""
Router: Gợi Ý Khóa Học
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.database import get_db
from src.models.course import CourseRecommendation
from src.models.skill import SkillCatalog

router = APIRouter()


class CourseOut(BaseModel):
    id: int
    skill_id: int
    skill_name: str
    industry: Optional[str] = None
    course_name: str
    platform: Optional[str]
    url: Optional[str]
    priority: int

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
    )
    if skill_id:
        q = q.filter(CourseRecommendation.skill_id == skill_id)
    if industry and industry != "Tất cả":
        q = q.filter(SkillCatalog.industry.in_([industry, "Tất cả"]))

    results = q.order_by(CourseRecommendation.priority, CourseRecommendation.id).all()
    return [
        CourseOut(
            id=c.id,
            skill_id=c.skill_id,
            skill_name=sk.skill_name,
            industry=sk.industry,
            course_name=c.course_name,
            platform=c.platform,
            url=c.url,
            priority=c.priority
        )
        for c, sk in results
    ]


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
        .filter(CourseRecommendation.skill_id == skill.id)
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
