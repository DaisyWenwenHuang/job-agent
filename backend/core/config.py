import json
from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

CONFIG_PATH = Path(__file__).parent.parent / "data" / "job_config.json"


class LocationConfig(BaseModel):
    city: str = "Redmond"
    state: str = "WA"
    max_miles_onsite: int = 20
    allowed_remote_types: list[str] = ["remote", "hybrid", "onsite"]


class PlatformConfig(BaseModel):
    enabled: bool = True
    max_results_per_run: int = 50


class SchedulerConfig(BaseModel):
    run_time: str = "08:00"
    timezone: str = "America/Los_Angeles"


class JobConfig(BaseModel):
    target_roles: list[str] = ["Data Scientist", "Data Engineer", "ML Engineer"]
    location: LocationConfig = LocationConfig()
    employment_types: list[str] = ["full-time", "part-time", "contract", "internship"]
    seniority_levels: list[str] = ["entry", "mid", "senior"]
    min_claude_score: int = 60
    apply_automatically: bool = False
    daily_apply_limit: int = 20
    platforms: dict[str, PlatformConfig] = {
        "linkedin": PlatformConfig(),
        "indeed": PlatformConfig(),
    }
    scheduler: SchedulerConfig = SchedulerConfig()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    anthropic_api_key: str = ""
    resume_file_path: str = ""
    linkedin_email: str = ""
    linkedin_password: str = ""
    indeed_email: str = ""
    indeed_password: str = ""
    database_url: str = "sqlite:///./backend/data/job_agent.db"
    frontend_origin: str = "http://localhost:5173"
    demo_mode: bool = False


def get_settings() -> Settings:
    return Settings()


def get_job_config() -> JobConfig:
    if CONFIG_PATH.exists():
        data = json.loads(CONFIG_PATH.read_text())
        return JobConfig(**data)
    return JobConfig()


def save_job_config(config: JobConfig) -> None:
    CONFIG_PATH.write_text(config.model_dump_json(indent=2))
