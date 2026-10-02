"""
Router: Kỹ Năng & Skill Gap
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.database import get_db
from src.models.skill import SkillCatalog

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
    db: Session = Depends(get_db),
):
    """Lấy danh sách kỹ năng, có thể lọc theo ngành."""
    q = db.query(SkillCatalog)
    if industry:
        q = q.filter(SkillCatalog.industry.in_([industry, "Tất cả"]))
    if sort_by_gap:
        q = q.order_by(SkillCatalog.gap_pct.desc())
    return q.all()


@router.get("/gap-matrix")
def skill_gap_matrix(db: Session = Depends(get_db)):
    """Ma trận skill gap – dùng cho biểu đồ Dashboard."""
    skills = db.query(SkillCatalog).order_by(SkillCatalog.gap_pct.desc()).limit(10).all()
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


@router.get("/trend-data")
def trend_data():
    """Dữ liệu xu hướng kỹ năng theo quý (mock – sẽ dùng ML model thực tế)."""
    return {
        "labels": ["Quý 3/2025", "Quý 4/2025", "Quý 1/2026", "Quý 2/2026", "Quý 3/2026"],
        "datasets": [
            {"label": "Python",           "data": [20, 35, 52, 70, 92],            "color": "#6366f1"},
            {"label": "AI Ethics",        "data": [5,  10, 18, 28, 38],            "color": "#f59e0b"},
            {"label": "Data Analysis",    "data": [30, 40, 50, 60, 68],            "color": "#10b981"},
            {"label": "Digital Marketing","data": [25, 28, 33, 38, 42.7],          "color": "#ef4444"},
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
