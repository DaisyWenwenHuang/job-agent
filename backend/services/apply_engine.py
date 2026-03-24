"""Orchestrates auto-applying to approved jobs."""
from datetime import datetime
from playwright.async_api import async_playwright

from backend.core.config import get_settings
from backend.core.database import SessionLocal
from backend.models.job import Job
from backend.models.application import Application
from backend.scrapers.stealth import create_stealth_context


async def apply_to_job(job_id: str) -> None:
    """Apply to a single approved job by ID."""
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            print(f"[apply_engine] Job {job_id} not found")
            return
        await _do_apply(db, job)
    finally:
        db.close()


async def run_pending_approvals(limit: int = 20) -> int:
    """Apply to all approved jobs up to the daily limit."""
    db = SessionLocal()
    applied = 0
    try:
        jobs = (
            db.query(Job)
            .filter(Job.status == "approved")
            .limit(limit)
            .all()
        )
        if not jobs:
            return 0

        settings = get_settings()
        async with async_playwright() as pw:
            context = await create_stealth_context(pw)
            page = await context.new_page()
            try:
                for job in jobs:
                    result = await _apply_with_page(page, job, settings.resume_file_path)
                    _save_application(db, job, result)
                    if result.success:
                        applied += 1
            finally:
                await context.close()
    finally:
        db.close()
    return applied


async def _do_apply(db, job: Job):
    settings = get_settings()
    async with async_playwright() as pw:
        context = await create_stealth_context(pw)
        page = await context.new_page()
        try:
            result = await _apply_with_page(page, job, settings.resume_file_path)
            _save_application(db, job, result)
        finally:
            await context.close()


async def _apply_with_page(page, job: Job, resume_path: str):
    if job.source == "linkedin":
        from backend.appliers.linkedin_apply import LinkedInApplier
        applier = LinkedInApplier()
    else:
        from backend.appliers.indeed_apply import IndeedApplier
        applier = IndeedApplier()
    return await applier.apply(page, job.url, resume_path)


def _save_application(db, job: Job, result) -> None:
    app = Application(
        job_id=job.id,
        platform=job.source,
        method=result.method,
        status=result.status,
        error_detail=result.error_detail,
        confirmation_text=result.confirmation_text,
        applied_at=datetime.utcnow(),
    )
    db.add(app)
    job.status = "applied" if result.success else ("requires_manual" if result.status == "requires_manual" else "applied")
    if result.success:
        job.applied_at = datetime.utcnow()
    else:
        job.apply_error = result.error_detail
    db.commit()
