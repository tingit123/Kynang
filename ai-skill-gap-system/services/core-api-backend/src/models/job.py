from sqlalchemy import Column, Integer, String, Text, Date, Boolean, Enum, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from src.database import Base


class JobPosting(Base):
    __tablename__ = "job_postings"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    employer_id      = Column(Integer, ForeignKey("users.id"), nullable=True)
    title            = Column(String(300), nullable=False)
    company          = Column(String(200), nullable=False)
    location         = Column(String(100), default="Cần Thơ")
    industry         = Column(String(50), nullable=False)
    description      = Column(Text)
    salary_min       = Column(Integer)
    salary_max       = Column(Integer)
    posted_date      = Column(Date)
    source_url       = Column(String(500))
    source_platform  = Column(String(50))
    ai_classified    = Column(Boolean, default=False)
    is_deleted       = Column(Boolean, default=False, nullable=False)
    duplicate_hash   = Column(String(64))
    duplicate_group  = Column(Integer)
    created_at       = Column(TIMESTAMP, server_default=func.now())


class JobApplication(Base):
    __tablename__ = "job_applications"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    job_id           = Column(Integer, ForeignKey("job_postings.id"), nullable=False)
    candidate_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    cv_snapshot_text = Column(Text, nullable=True)
    status           = Column(String(50), default="applied", nullable=False)
    applied_at       = Column(TIMESTAMP, server_default=func.now())
