"""
Database schema (Step 3 of the build order).

Tables: users, scans (url, status, timestamp), reports
(score, summary, clauses, trackers), activity_logs.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, DateTime, ForeignKey, Integer, Text, Enum, JSON
)
from sqlalchemy.orm import relationship

from app.database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class ScanStatus(str, enum.Enum):
    pending = "pending"
    scraping = "scraping"
    analyzing = "analyzing"
    complete = "complete"
    failed = "failed"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Integer, default=0)  # 0/1 flag, simple for this project
    created_at = Column(DateTime, default=datetime.utcnow)

    scans = relationship("Scan", back_populates="owner", cascade="all, delete-orphan")


class Scan(Base):
    __tablename__ = "scans"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    url = Column(String, nullable=False)
    status = Column(Enum(ScanStatus), default=ScanStatus.pending, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    owner = relationship("User", back_populates="scans")
    report = relationship(
        "Report", back_populates="scan", uselist=False, cascade="all, delete-orphan"
    )


class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=gen_uuid)
    scan_id = Column(String, ForeignKey("scans.id"), nullable=False, unique=True)

    score = Column(Integer, nullable=True)
    summary = Column(Text, nullable=True)
    clauses = Column(JSON, nullable=True)         # list of {category, risk, text}
    trackers = Column(JSON, nullable=True)        # list of {name, domain, category}
    recommendations = Column(JSON, nullable=True)  # list of strings

    created_at = Column(DateTime, default=datetime.utcnow)

    scan = relationship("Scan", back_populates="report")


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)   # e.g. "login", "scan_created"
    detail = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
