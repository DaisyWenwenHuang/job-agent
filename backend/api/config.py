from fastapi import APIRouter
from backend.core.config import get_job_config, save_job_config, JobConfig

router = APIRouter()


@router.get("", response_model=JobConfig)
def get_config():
    return get_job_config()


@router.put("", response_model=JobConfig)
def update_config(config: JobConfig):
    save_job_config(config)
    return config


@router.patch("", response_model=JobConfig)
def patch_config(partial: dict):
    current = get_job_config()
    merged = current.model_copy(update=partial)
    save_job_config(merged)
    return merged
