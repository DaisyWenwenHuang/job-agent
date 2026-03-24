from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from backend.core.config import get_job_config

_scheduler: AsyncIOScheduler | None = None


def start_scheduler():
    global _scheduler
    try:
        config = get_job_config()
        hour, minute = config.scheduler.run_time.split(":")

        _scheduler = AsyncIOScheduler(timezone=config.scheduler.timezone)
        _scheduler.add_job(
            _run_pipeline,
            CronTrigger(hour=int(hour), minute=int(minute), timezone=config.scheduler.timezone),
            id="daily_pipeline",
            replace_existing=True,
        )
        _scheduler.start()
        print(f"[scheduler] Started — daily run at {config.scheduler.run_time} {config.scheduler.timezone}")
    except Exception as e:
        print(f"[scheduler] Failed to start: {e}")


def stop_scheduler():
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)


def is_running() -> bool:
    return _scheduler is not None and _scheduler.running


async def _run_pipeline():
    from backend.services.pipeline import run_daily_pipeline
    await run_daily_pipeline(trigger="scheduled")
