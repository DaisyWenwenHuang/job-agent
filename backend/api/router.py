from fastapi import APIRouter
from backend.api import jobs, applications, runs, config, health

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(applications.router, prefix="/applications", tags=["applications"])
api_router.include_router(runs.router, prefix="/runs", tags=["runs"])
api_router.include_router(config.router, prefix="/config", tags=["config"])
