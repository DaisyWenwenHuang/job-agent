from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.application import Application
from backend.schemas.application import ApplicationResponse

router = APIRouter()


@router.get("", response_model=list[ApplicationResponse])
def list_applications(
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    query = db.query(Application)
    if status:
        query = query.filter(Application.status == status)
    query = query.order_by(Application.applied_at.desc())
    return query.offset((page - 1) * limit).limit(limit).all()


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(application_id: str, db: Session = Depends(get_db)):
    from fastapi import HTTPException
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app
