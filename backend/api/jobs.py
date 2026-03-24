import json
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_

from backend.core.database import get_db
from backend.models.job import Job
from backend.schemas.job import JobResponse, JobStatusUpdate

router = APIRouter()


@router.get("", response_model=list[JobResponse])
def list_jobs(
    status: Optional[str] = None,
    source: Optional[str] = None,
    min_score: Optional[int] = None,
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    query = db.query(Job)
    if status:
        query = query.filter(Job.status == status)
    if source:
        query = query.filter(Job.source == source)
    if min_score is not None:
        query = query.filter(Job.claude_score >= min_score)
    query = query.order_by(Job.claude_score.desc().nullslast(), Job.scraped_at.desc())
    return query.offset((page - 1) * limit).limit(limit).all()


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.patch("/{job_id}/status", response_model=JobResponse)
def update_job_status(job_id: str, body: JobStatusUpdate, db: Session = Depends(get_db)):
    allowed = {"approved", "rejected", "skipped"}
    if body.status not in allowed:
        raise HTTPException(status_code=400, detail=f"status must be one of {allowed}")
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.status = body.status
    job.reviewed_at = datetime.utcnow()
    db.commit()
    db.refresh(job)
    return job


@router.post("/{job_id}/apply")
async def apply_to_job(job_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "approved":
        raise HTTPException(status_code=400, detail="Job must be approved before applying")
    background_tasks.add_task(_apply_background, job_id)
    return {"message": "Apply task queued", "job_id": job_id}


async def _apply_background(job_id: str):
    from backend.services.apply_engine import apply_to_job
    await apply_to_job(job_id)


@router.delete("/{job_id}", status_code=204)
def delete_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
