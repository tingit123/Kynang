from sqlalchemy import Column, Integer, String, Date, ForeignKey, TIMESTAMP, CheckConstraint
from sqlalchemy.sql import func
from src.database import Base


class SurveyResponse(Base):
    __tablename__ = "survey_responses"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    student_code = Column(String(20), unique=True, nullable=False)
    full_name    = Column(String(100), nullable=False)
    major        = Column(String(100))
    year_of_study= Column(Integer)
    institution  = Column(String(200))
    completed_at = Column(Date)
    created_at   = Column(TIMESTAMP, server_default=func.now())


class SurveySkillRating(Base):
    __tablename__ = "survey_skill_ratings"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    survey_id   = Column(Integer, ForeignKey("survey_responses.id"), nullable=False)
    skill_id    = Column(Integer, ForeignKey("skill_catalog.id"), nullable=False)
    self_rating = Column(Integer, CheckConstraint("self_rating BETWEEN 0 AND 100"))
