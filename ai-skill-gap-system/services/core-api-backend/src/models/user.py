from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Enum, TIMESTAMP, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from src.database import Base


class UserRole(str, PyEnum):
    ADMIN = "admin"
    WORKER = "worker"
    EMPLOYER = "employer"
    COURSE_PROVIDER = "course_provider"
    # Tương thích ngược các role cũ nếu có
    CANDIDATE = "candidate"
    PROVIDER = "provider"


class User(Base):
    __tablename__ = "users"

    id                  = Column(Integer, primary_key=True, autoincrement=True)
    email               = Column(String(150), unique=True, index=True, nullable=False)
    password_hash       = Column(String(255), nullable=False)
    full_name           = Column(String(150), nullable=False)
    role                = Column(
        Enum("admin", "worker", "employer", "course_provider", "candidate", "provider", name="user_roles"),
        default="worker",
        nullable=False,
    )
    is_active           = Column(Boolean, default=True, nullable=False)
    is_deleted          = Column(Boolean, default=False, nullable=False)
    last_login_at       = Column(TIMESTAMP, nullable=True)
    company_name        = Column(String(200), nullable=True)
    company_logo_url    = Column(String(500), nullable=True)
    company_description = Column(Text, nullable=True)
    latest_cv_analysis  = Column(Text, nullable=True)
    created_at          = Column(TIMESTAMP, server_default=func.now())

    @property
    def user_id(self):
        return self.id


class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    token          = Column(String(500), unique=True, index=True, nullable=False)
    blacklisted_on = Column(TIMESTAMP, server_default=func.now())


class Company(Base):
    __tablename__ = "companies"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    employer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name        = Column(String(200), nullable=False)
    logo_url    = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    created_at  = Column(TIMESTAMP, server_default=func.now())

    @property
    def company_id(self):
        return self.id

    @property
    def company_name(self):
        return self.name


class Worker(Base):
    __tablename__ = "workers"

    worker_id  = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=True)
    full_name  = Column(String(150), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Employer(Base):
    __tablename__ = "employers"

    employer_id  = Column(Integer, primary_key=True, autoincrement=True)
    user_id      = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    company_id   = Column(Integer, ForeignKey("companies.id", ondelete="SET NULL"), nullable=True)
    contact_name = Column(String(150), nullable=True)
    phone        = Column(String(50), nullable=True)
    is_verified  = Column(Boolean, default=False, nullable=False)
    created_at   = Column(TIMESTAMP, server_default=func.now())


class CourseProvider(Base):
    __tablename__ = "course_providers"

    provider_id   = Column(Integer, primary_key=True, autoincrement=True)
    user_id       = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    provider_name = Column(String(200), unique=True, nullable=False)
    website       = Column(String(500), nullable=True)
    description   = Column(Text, nullable=True)
    is_verified   = Column(Boolean, default=False, nullable=False)
    created_at    = Column(TIMESTAMP, server_default=func.now())
