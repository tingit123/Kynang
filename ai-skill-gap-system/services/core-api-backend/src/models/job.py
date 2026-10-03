from sqlalchemy import Column, Integer, String, Text, Date, Boolean, Enum, TIMESTAMP
from sqlalchemy.sql import func
from src.database import Base


class JobPosting(Base):
    __tablename__ = "job_postings"

    id               = Column(Integer, primary_key=True, autoincrement=True)
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
    duplicate_hash   = Column(String(64))
    duplicate_group  = Column(Integer)
    created_at       = Column(TIMESTAMP, server_default=func.now())
