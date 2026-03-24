import asyncio
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.run_history import RunHistory
from backend.schemas.run_history import RunHistoryResponse
from backend.core.scheduler import is_running

router = APIRouter()

_active_run: bool = False


@router.get("", response_model=list[RunHistoryResponse])
def list_runs(page: int = 1, limit: int = 20, db: Session = Depends(get_db)):
    return (
        db.query(RunHistory)
        .order_by(RunHistory.started_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )


@router.get("/status")
def run_status():
    return {"active": _active_run, "scheduler": "running" if is_running() else "stopped"}


@router.get("/{run_id}", response_model=RunHistoryResponse)
def get_run(run_id: str, db: Session = Depends(get_db)):
    from fastapi import HTTPException
    run = db.query(RunHistory).filter(RunHistory.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.post("/trigger")
async def trigger_run(background_tasks: BackgroundTasks):
    global _active_run
    if _active_run:
        return {"message": "A run is already in progress"}
    background_tasks.add_task(_run_pipeline_background)
    return {"message": "Pipeline run triggered"}


async def _run_pipeline_background():
    global _active_run
    _active_run = True
    try:
        from backend.services.pipeline import run_daily_pipeline
        await run_daily_pipeline(trigger="manual")
    finally:
        _active_run = False
