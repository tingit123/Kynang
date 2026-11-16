from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from src.database import Base


class RecruiterContact(Base):
    __tablename__ = "recruiter_contacts"
    __table_args__ = (UniqueConstraint("owner_id", "name", "email", name="uq_recruiter_contact"),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, default="")
    title = Column(String(100), nullable=False, default="")
    created_at = Column(DateTime, server_default=func.now())


class ApplicationProcess(Base):
    __tablename__ = "application_processes"
    application_id = Column(Integer, ForeignKey("job_applications.id"), primary_key=True)
    stage = Column(String(40), nullable=False, default="new", index=True)
    assignee_id = Column(Integer, ForeignKey("recruiter_contacts.id"), nullable=True, index=True)
    version = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class ApplicationProcessEvent(Base):
    __tablename__ = "application_process_events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(Integer, ForeignKey("job_applications.id"), nullable=False, index=True)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    actor_name = Column(String(150), nullable=False)
    event_type = Column(String(40), nullable=False)
    details = Column(JSON, nullable=False)
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
