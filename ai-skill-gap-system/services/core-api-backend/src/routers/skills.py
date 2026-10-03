"""
Router: Kỹ Năng & Skill Gap
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel

from src.database import get_db
from src.models.skill import SkillCatalog
from src.models.course import CourseRecommendation

router = APIRouter()


# ── Pydantic Schemas ─────────────────────────────────────────────
class SkillOut(BaseModel):
    id: int
    skill_name: str
    industry: Optional[str]
    demand_pct: float
    supply_pct: float
    gap_pct: float
    trend_pct: Optional[str]

    class Config:
        from_attributes = True


class SkillDetailOut(BaseModel):
    id: int
    skill_name: str
    industry: Optional[str]
    demand_pct: float
    supply_pct: float
    gap_pct: float
    trend_pct: Optional[str]
    courses: List[Dict[str, str]] = []


class SkillUpdate(BaseModel):
    demand_pct: Optional[float] = None
    supply_pct: Optional[float] = None
    gap_pct: Optional[float] = None
    trend_pct: Optional[str] = None


# ── Endpoints ────────────────────────────────────────────────────
@router.get("/", response_model=List[SkillOut])
def list_skills(
    industry: Optional[str] = Query(None),
    sort_by_gap: bool = Query(True, description="Sắp xếp theo gap giảm dần"),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
):
    """Lấy danh sách kỹ năng, có thể lọc theo ngành."""
    q = db.query(SkillCatalog)
    if industry and industry != "Tất cả":
        q = q.filter(SkillCatalog.industry.in_([industry, "Tất cả"]))
    elif industry == "Tất cả":
        q = q.filter(SkillCatalog.industry == "Tất cả")

    if sort_by_gap:
        q = q.order_by(SkillCatalog.gap_pct.desc())
    return q.limit(limit).all()


@router.get("/detailed", response_model=List[SkillDetailOut])
def list_skills_detailed(
    industry: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Lấy danh sách kỹ năng kèm danh sách khóa học gợi ý."""
    q = db.query(SkillCatalog)
    if industry and industry != "Tất cả":
        q = q.filter(SkillCatalog.industry.in_([industry, "Tất cả"]))
    skills = q.order_by(SkillCatalog.gap_pct.desc()).all()

    skill_ids = [s.id for s in skills]
    courses = (
        db.query(CourseRecommendation)
        .filter(CourseRecommendation.skill_id.in_(skill_ids))
        .all()
    ) if skill_ids else []

    courses_map = {}
    for c in courses:
        courses_map.setdefault(c.skill_id, []).append({
            "course_name": c.course_name,
            "platform": c.platform or "",
            "url": c.url or ""
        })

    results = []
    for s in skills:
        results.append(SkillDetailOut(
            id=s.id,
            skill_name=s.skill_name,
            industry=s.industry,
            demand_pct=s.demand_pct or 0.0,
            supply_pct=s.supply_pct or 0.0,
            gap_pct=s.gap_pct or 0.0,
            trend_pct=s.trend_pct or "+0%",
            courses=courses_map.get(s.id, [])
        ))
    return results


@router.get("/gap-matrix")
def skill_gap_matrix(
    limit: int = Query(10, le=50),
    industry: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Ma trận skill gap – dùng cho biểu đồ Dashboard."""
    q = db.query(SkillCatalog)
    if industry and industry != "Tất cả":
        q = q.filter(SkillCatalog.industry == industry)
    skills = q.order_by(SkillCatalog.gap_pct.desc()).limit(limit).all()
    return [
        {
            "skill": s.skill_name,
            "demand": s.demand_pct,
            "supply": s.supply_pct,
            "gap": s.gap_pct,
            "trend": s.trend_pct,
            "industry": s.industry,
        }
        for s in skills
    ]


@router.get("/soft-skills")
def get_soft_skills(db: Session = Depends(get_db)):
    """Lấy danh sách các kỹ năng mềm/chuyển giao (Transversal Skills)."""
    skills = (
        db.query(SkillCatalog)
        .filter(SkillCatalog.industry == "Tất cả")
        .order_by(desc(SkillCatalog.gap_pct))
        .all()
    )
    return [
        {
            "skill": s.skill_name,
            "demand": s.demand_pct,
            "supply": s.supply_pct,
            "gap": s.gap_pct,
            "trend": s.trend_pct,
            "industry": "Kỹ năng mềm"
        }
        for s in skills
    ]


@router.get("/trend-data")
def trend_data():
    """Dữ liệu xu hướng kỹ năng thực tế."""
    return {
        "labels": ["Quý 4/2025", "Quý 1/2026", "Quý 2/2026", "Quý 3/2026", "Hiện tại (10/2026)"],
        "datasets": [
            {"label": "Python & AI",          "data": [35, 48, 62, 78, 89.2], "color": "#6366f1"},
            {"label": "Data Analysis",       "data": [28, 36, 45, 50, 52.3], "color": "#10b981"},
            {"label": "Customer Service",     "data": [40, 55, 75, 95, 115.2],"color": "#f59e0b"},
            {"label": "Customs & Logistics",  "data": [22, 28, 36, 42, 48.0], "color": "#06b6d4"},
            {"label": "Financial Statements", "data": [30, 38, 45, 52, 58.5], "color": "#ef4444"},
        ],
    }


@router.get("/{skill_id}", response_model=SkillOut)
def get_skill(skill_id: int, db: Session = Depends(get_db)):
    skill = db.query(SkillCatalog).filter(SkillCatalog.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Kỹ năng không tồn tại")
    return skill


@router.put("/{skill_id}", response_model=SkillOut)
def update_skill(skill_id: int, data: SkillUpdate, db: Session = Depends(get_db)):
    """Cập nhật % demand/supply/gap (dùng bởi AI Worker)."""
    skill = db.query(SkillCatalog).filter(SkillCatalog.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Kỹ năng không tồn tại")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(skill, field, value)
    db.commit()
    db.refresh(skill)
    return skill
