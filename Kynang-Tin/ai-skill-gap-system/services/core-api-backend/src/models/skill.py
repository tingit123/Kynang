from sqlalchemy import Column, Integer, String, Float, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from src.database import Base


class SkillCatalog(Base):
    __tablename__ = "skill_catalog"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    skill_name  = Column(String(100), unique=True, nullable=False)
    industry    = Column(String(50))
    demand_pct  = Column(Float, default=0.0)
    supply_pct  = Column(Float, default=0.0)
    gap_pct     = Column(Float, default=0.0)
    trend_pct   = Column(String(20))
    updated_at  = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class ExtractedSkill(Base):
    __tablename__ = "extracted_skills"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    job_id         = Column(Integer, ForeignKey("job_postings.id", ondelete="CASCADE"), nullable=False)
    skill_name     = Column(String(100), nullable=False)
    skill_category = Column(String(50))
    confidence     = Column(Float, default=0.0)
