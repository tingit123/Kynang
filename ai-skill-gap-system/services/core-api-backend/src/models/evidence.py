from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from src.database import Base


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(Integer, ForeignKey("job_applications.id"), nullable=False, index=True)
    requirements_hash = Column(String(64), nullable=False)
    filter_profile_hash = Column(String(64), nullable=True)
    requirements_snapshot = Column(Text, nullable=False)
    cv_hash = Column(String(64), nullable=False)
    provider = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False)
    error_code = Column(String(80), nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class ApplicationEvidence(Base):
    __tablename__ = "application_evidence"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(Integer, ForeignKey("analysis_runs.id"), nullable=False, index=True)
    requirement_name = Column(String(100), nullable=False)
    result = Column(String(20), nullable=False)
    quote = Column(Text, nullable=False, default="")
    source_start = Column(Integer, nullable=True)
    source_end = Column(Integer, nullable=True)
    ai_result_original = Column(String(20), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    review_result = Column(String(20), nullable=True)
    review_reason = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
