from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from src.database import Base


class FilterProfile(Base):
    __tablename__ = "filter_profiles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("job_postings.id"), unique=True, nullable=False)
    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(150), nullable=False)
    items = Column(JSON, nullable=False)
    profile_hash = Column(String(64), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class QuickHireBatch(Base):
    __tablename__ = "quick_hire_batches"
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("job_postings.id"), nullable=False)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    profile_snapshot = Column(JSON, nullable=False)
    idempotency_key = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class ApplicationStatusEvent(Base):
    __tablename__ = "application_status_events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(Integer, ForeignKey("job_applications.id"), nullable=False, index=True)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    from_status = Column(String(50), nullable=False)
    to_status = Column(String(50), nullable=False)
    batch_id = Column(Integer, ForeignKey("quick_hire_batches.id"), nullable=True, index=True)
    notification_batch_id = Column(Integer, ForeignKey("notification_batches.id"), nullable=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
