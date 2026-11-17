from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from src.database import Base


class NotificationTemplate(Base):
    __tablename__ = "notification_templates"
    __table_args__ = (UniqueConstraint("owner_id", "action_type", "name", name="uq_notification_template_owner"),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action_type = Column(String(30), nullable=False)
    name = Column(String(100), nullable=False)
    title_template = Column(String(300), nullable=False)
    body_template = Column(Text, nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class NotificationBatch(Base):
    __tablename__ = "notification_batches"
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("job_postings.id"), nullable=False, index=True)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action_type = Column(String(30), nullable=False)
    channels = Column(JSON, nullable=False)
    content = Column(JSON, nullable=False)
    status = Column(String(30), nullable=False, default="processing")
    idempotency_key = Column(String(100), unique=True, nullable=False)
    request_hash = Column(String(64), nullable=False)
    simulated = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, server_default=func.now())


class NotificationRecipient(Base):
    __tablename__ = "notification_recipients"
    __table_args__ = (UniqueConstraint("batch_id", "application_id", "channel", name="uq_notification_target"),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(Integer, ForeignKey("notification_batches.id"), nullable=False, index=True)
    application_id = Column(Integer, ForeignKey("job_applications.id"), nullable=False)
    channel = Column(String(20), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    address = Column(String(150), nullable=True)
    candidate_name = Column(String(150), nullable=False)
    title = Column(String(300), nullable=False)
    body = Column(Text, nullable=False)
    status = Column(String(30), nullable=False, default="queued")
    attempt_count = Column(Integer, nullable=False, default=0)
    last_error = Column(Text, nullable=True)
    error_kind = Column(String(30), nullable=True)
    retryable = Column(Boolean, nullable=False, default=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class UserNotification(Base):
    __tablename__ = "user_notifications"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    recipient_id = Column(Integer, ForeignKey("notification_recipients.id"), nullable=False, unique=True)
    title = Column(String(300), nullable=False)
    body = Column(Text, nullable=False)
    simulated = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, server_default=func.now())
    read_at = Column(DateTime, nullable=True)
