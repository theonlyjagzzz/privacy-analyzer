"""
Pydantic request/response models — this is the API contract Frontend relies on.
Field names here must match what the Integration Lead's contract specifies.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


# ---------- Auth ----------

class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Scan ----------

class ScanCreateRequest(BaseModel):
    url: str


class ScanCreateResponse(BaseModel):
    scan_id: str
    status: str


class ScanHistoryItem(BaseModel):
    scan_id: str
    url: str
    status: str
    score: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Report ----------

class ClauseOut(BaseModel):
    category: str
    risk: str          # "high" | "medium" | "low"
    text: str


class TrackerOut(BaseModel):
    name: str
    domain: str
    category: Optional[str] = None


class ReportOut(BaseModel):
    scan_id: str
    url: str
    status: str
    score: Optional[int] = None
    summary: Optional[str] = None
    clauses: List[ClauseOut] = []
    trackers: List[TrackerOut] = []
    recommendations: List[str] = []
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ---------- Admin ----------

class AdminStatsResponse(BaseModel):
    total_scans: int
    total_users: int
    average_score: Optional[float] = None
    most_scanned_domains: List[dict]
