from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class JobBase(BaseModel):
    source: str
    url: str
    title: str
    company: str
    location: Optional[str] = None
    remote_type: Optional[str] = None
    employment_type: Optional[str] = None
    seniority: Optional[str] = None
    description: Optional[str] = None
    salary_range: Optional[str] = None
    posted_date: Optional[str] = None


class JobResponse(JobBase):
    id: str
    external_id: Optional[str] = None
    scraped_at: datetime
    claude_score: Optional[int] = None
    claude_reasoning: Optional[str] = None
    claude_summary: Optional[str] = None
    claude_seniority: Optional[str] = None
    claude_red_flags: Optional[str] = None
    claude_role_type: Optional[str] = None
    status: str
    reviewed_at: Optional[datetime] = None
    applied_at: Optional[datetime] = None
    apply_error: Optional[str] = None

    model_config = {"from_attributes": True}


class JobStatusUpdate(BaseModel):
    status: str  # approved | rejected | skipped
