"""
Router: Khảo Sát Sinh Viên
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date

from src.database import get_db
from src.models.survey import SurveyResponse

router = APIRouter()


class SurveyCreate(BaseModel):
    student_code: str
    full_name: str
    major: Optional[str] = None
    year_of_study: Optional[int] = None
    institution: Optional[str] = None
    completed_at: Optional[date] = None


class SurveyOut(BaseModel):
    id: int
    student_code: str
    full_name: str
    major: Optional[str]
    year_of_study: Optional[int]
    institution: Optional[str]
    completed_at: Optional[date]

    class Config:
        from_attributes = True


@router.get("/", response_model=List[SurveyOut])
def list_surveys(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    return db.query(SurveyResponse).offset(offset).limit(limit).all()


@router.post("/", response_model=SurveyOut, status_code=201)
def create_survey(survey: SurveyCreate, db: Session = Depends(get_db)):
    """Ghi nhận phản hồi khảo sát mới từ Mobile App."""
    existing = db.query(SurveyResponse).filter(
        SurveyResponse.student_code == survey.student_code
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Sinh viên đã khảo sát rồi")
    db_survey = SurveyResponse(**survey.model_dump())
    db.add(db_survey)
    db.commit()
    db.refresh(db_survey)
    return db_survey


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
