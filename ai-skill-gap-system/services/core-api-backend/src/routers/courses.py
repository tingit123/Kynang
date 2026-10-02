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
    course_name: str
    platform: Optional[str]
    url: Optional[str]
    priority: int

    class Config:
        from_attributes = True


@router.get("/", response_model=List[CourseOut])
def list_courses(
    skill_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(CourseRecommendation)
    if skill_id:
        q = q.filter(CourseRecommendation.skill_id == skill_id)
    return q.order_by(CourseRecommendation.priority).all()


@router.get("/by-skill-name")
def courses_by_skill_name(
    skill_name: str = Query(..., description="Tên kỹ năng"),
    db: Session = Depends(get_db),
):
    """Lấy gợi ý khóa học theo tên kỹ năng."""
    skill = db.query(SkillCatalog).filter(SkillCatalog.skill_name == skill_name).first()
    if not skill:
        # Fallback data nếu chưa có trong DB
        return _fallback_courses(skill_name)

    courses = (
        db.query(CourseRecommendation)
        .filter(CourseRecommendation.skill_id == skill.id)
        .order_by(CourseRecommendation.priority)
        .all()
    )
    return [
        {"course_name": c.course_name, "platform": c.platform, "url": c.url}
        for c in courses
    ]


def _fallback_courses(skill_name: str):
    """Dữ liệu khóa học fallback khi DB chưa có."""
    fallback = {
        "Python": [
            {"course_name": "Python for Everyone", "platform": "Coursera", "url": "https://coursera.org"},
            {"course_name": "FastAPI Masterclass", "platform": "Udemy",    "url": "https://udemy.com"},
        ],
        "Machine Learning": [
            {"course_name": "ML Crash Course", "platform": "Google",   "url": "https://developers.google.com/machine-learning/crash-course"},
            {"course_name": "Deep Learning Spec","platform": "Coursera","url": "https://coursera.org"},
        ],
        "English": [
            {"course_name": "IELTS Academic",     "platform": "British Council", "url": "https://britishcouncil.vn"},
            {"course_name": "Business English",   "platform": "EF",              "url": "https://ef.com"},
        ],
    }
    return fallback.get(skill_name, [{"course_name": f"Học {skill_name} cơ bản", "platform": "Online", "url": "#"}])
