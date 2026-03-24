import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from backend.core.database import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    applied_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    platform = Column(String, nullable=False)         # 'linkedin' | 'indeed'
    method = Column(String, nullable=True)            # 'easy_apply' | 'quick_apply'
    status = Column(String, nullable=False)           # 'submitted' | 'failed' | 'requires_manual'
    error_detail = Column(Text, nullable=True)
    confirmation_text = Column(Text, nullable=True)
