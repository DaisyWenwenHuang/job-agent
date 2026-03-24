from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class RunHistoryResponse(BaseModel):
    id: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    trigger: str
    status: str
    jobs_scraped: int
    jobs_new: int
    jobs_scored: int
    jobs_applied: int
    error_message: Optional[str] = None
    log_output: Optional[str] = None

    model_config = {"from_attributes": True}
