import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text
from backend.core.database import Base


class RunHistory(Base):
    __tablename__ = "run_history"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    finished_at = Column(DateTime, nullable=True)
    trigger = Column(String, nullable=False)          # 'scheduled' | 'manual'
    status = Column(String, default="running", nullable=False)
    # running | completed | failed

    jobs_scraped = Column(Integer, default=0)
    jobs_new = Column(Integer, default=0)
    jobs_scored = Column(Integer, default=0)
    jobs_applied = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    log_output = Column(Text, nullable=True)
