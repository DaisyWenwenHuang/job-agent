"""Daily pipeline: scrape → score → save."""
import json
from datetime import datetime

from sqlalchemy.exc import IntegrityError

from backend.core.config import get_job_config, get_settings
from backend.core.database import SessionLocal
from backend.models.job import Job
from backend.models.run_history import RunHistory
from backend.services.resume_parser import parse_resume
from backend.services.claude_matcher import score_jobs_batch


async def run_daily_pipeline(trigger: str = "scheduled"):
    db = SessionLocal()
    run = RunHistory(trigger=trigger, status="running", started_at=datetime.utcnow())
    db.add(run)
    db.commit()
    db.refresh(run)

    log_lines = []

    def log(msg: str):
        print(msg)
        log_lines.append(msg)

    try:
        config = get_job_config()
        settings = get_settings()

        log(f"[pipeline] Starting {trigger} run at {run.started_at}")

        # Parse resume
        resume_text = ""
        if settings.resume_file_path:
            try:
                resume_text = parse_resume(settings.resume_file_path)
                log(f"[pipeline] Resume parsed: {len(resume_text)} chars")
            except Exception as e:
                log(f"[pipeline] Resume parse error: {e}")

        location = f"{config.location.city}, {config.location.state}"
        new_jobs: list[Job] = []
        total_scraped = 0

        # Scrape LinkedIn
        linkedin_cfg = config.platforms.get("linkedin")
        if linkedin_cfg and linkedin_cfg.enabled:
            try:
                from backend.scrapers.linkedin import LinkedInScraper
                max_r = linkedin_cfg.max_results_per_run
                scraper = LinkedInScraper()
                raw_jobs = await scraper.search_jobs(config.target_roles, location, max_r)
                total_scraped += len(raw_jobs)
                saved = _save_jobs(db, raw_jobs)
                new_jobs.extend(saved)
                log(f"[pipeline] LinkedIn: scraped={len(raw_jobs)}, new={len(saved)}")
            except Exception as e:
                log(f"[pipeline] LinkedIn scraper failed: {e}")

        # Scrape Indeed
        indeed_cfg = config.platforms.get("indeed")
        if indeed_cfg and indeed_cfg.enabled:
            try:
                from backend.scrapers.indeed import IndeedScraper
                max_r = indeed_cfg.max_results_per_run
                scraper = IndeedScraper()
                raw_jobs = await scraper.search_jobs(config.target_roles, location, max_r)
                total_scraped += len(raw_jobs)
                saved = _save_jobs(db, raw_jobs)
                new_jobs.extend(saved)
                log(f"[pipeline] Indeed: scraped={len(raw_jobs)}, new={len(saved)}")
            except Exception as e:
                log(f"[pipeline] Indeed scraper failed: {e}")

        # Score new jobs with Claude
        scored_count = 0
        if new_jobs and resume_text:
            job_dicts = [
                {
                    "title": j.title, "company": j.company,
                    "location": j.location, "employment_type": j.employment_type,
                    "description": j.description,
                }
                for j in new_jobs
            ]
            scores = await score_jobs_batch(job_dicts, resume_text)
            for job, score in zip(new_jobs, scores):
                if score:
                    job.claude_score = score.score
                    job.claude_reasoning = json.dumps(score.reasoning)
                    job.claude_summary = score.summary
                    job.claude_seniority = score.seniority_assessment
                    job.claude_red_flags = json.dumps(score.red_flags)
                    job.claude_role_type = score.role_type
                    if score.score < config.min_claude_score:
                        job.status = "skipped"
                    scored_count += 1
            db.commit()
            log(f"[pipeline] Scored {scored_count} jobs")

        # Auto-apply if enabled
        applied_count = 0
        if config.apply_automatically:
            try:
                from backend.services.apply_engine import run_pending_approvals
                applied_count = await run_pending_approvals(limit=config.daily_apply_limit)
                log(f"[pipeline] Auto-applied to {applied_count} jobs")
            except Exception as e:
                log(f"[pipeline] Auto-apply error: {e}")

        # Finalize run
        run.status = "completed"
        run.finished_at = datetime.utcnow()
        run.jobs_scraped = total_scraped
        run.jobs_new = len(new_jobs)
        run.jobs_scored = scored_count
        run.jobs_applied = applied_count
        run.log_output = "\n".join(log_lines)
        db.commit()
        log(f"[pipeline] Run completed.")

    except Exception as e:
        log(f"[pipeline] Fatal error: {e}")
        run.status = "failed"
        run.finished_at = datetime.utcnow()
        run.error_message = str(e)
        run.log_output = "\n".join(log_lines)
        db.commit()
    finally:
        db.close()


def _save_jobs(db, raw_jobs) -> list[Job]:
    """Save raw scraped jobs to DB, skip duplicates. Returns newly inserted jobs."""
    new = []
    for r in raw_jobs:
        job = Job(
            source=r.source,
            external_id=r.external_id,
            url=r.url,
            title=r.title,
            company=r.company,
            location=r.location,
            remote_type=r.remote_type,
            employment_type=r.employment_type,
            seniority=r.seniority,
            description=r.description,
            salary_range=r.salary_range,
            posted_date=r.posted_date,
            scraped_at=datetime.utcnow(),
            status="pending_review",
        )
        try:
            db.add(job)
            db.flush()
            new.append(job)
        except IntegrityError:
            db.rollback()  # duplicate — skip
    db.commit()
    return new
