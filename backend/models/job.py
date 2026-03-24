import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, UniqueConstraint
from backend.core.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    source = Column(String, nullable=False)           # 'linkedin' | 'indeed'
    external_id = Column(String, nullable=True)       # platform's own job ID
    url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, nullable=True)
    remote_type = Column(String, nullable=True)       # 'remote' | 'hybrid' | 'onsite'
    employment_type = Column(String, nullable=True)   # 'full-time' | 'part-time' | etc.
    seniority = Column(String, nullable=True)         # 'entry' | 'mid' | 'senior' | 'unknown'
    description = Column(Text, nullable=True)
    salary_range = Column(String, nullable=True)
    posted_date = Column(String, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    claude_score = Column(Integer, nullable=True)     # 0-100
    claude_reasoning = Column(Text, nullable=True)    # JSON array of bullets
    claude_summary = Column(Text, nullable=True)
    claude_seniority = Column(String, nullable=True)
    claude_red_flags = Column(Text, nullable=True)    # JSON array
    claude_role_type = Column(String, nullable=True)

    status = Column(String, default="pending_review", nullable=False)
    # pending_review | approved | rejected | applied | skipped

    reviewed_at = Column(DateTime, nullable=True)
    applied_at = Column(DateTime, nullable=True)
    apply_error = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_source_external_id"),
    )
