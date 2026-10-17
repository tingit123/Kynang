from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Enum, TIMESTAMP, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from src.database import Base


class UserRole(str, PyEnum):
    ADMIN = "admin"
    CANDIDATE = "candidate"
    EMPLOYER = "employer"
    PROVIDER = "provider"


class User(Base):
    __tablename__ = "users"

    id                  = Column(Integer, primary_key=True, autoincrement=True)
    email               = Column(String(150), unique=True, index=True, nullable=False)
    password_hash       = Column(String(255), nullable=False)
    full_name           = Column(String(150), nullable=False)
    role                = Column(
        Enum("admin", "candidate", "employer", "provider", name="user_roles"),
        default="candidate",
        nullable=False,
    )
    is_deleted          = Column(Boolean, default=False, nullable=False)
    is_active           = Column(Boolean, default=True, nullable=False)
    phone               = Column(String(30), nullable=True)
    company_name        = Column(String(200), nullable=True)
    company_logo_url    = Column(String(500), nullable=True)
    company_description = Column(Text, nullable=True)
    latest_cv_analysis  = Column(Text, nullable=True)
    created_at          = Column(TIMESTAMP, server_default=func.now())


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
