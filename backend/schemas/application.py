from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ApplicationResponse(BaseModel):
    id: str
    job_id: str
    applied_at: datetime
    platform: str
    method: Optional[str] = None
    status: str
    error_detail: Optional[str] = None
    confirmation_text: Optional[str] = None

    model_config = {"from_attributes": True}
