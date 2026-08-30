from fastapi import APIRouter

from app.api.v1.endpoints import (
    evaluations,
    health,
    job_descriptions,
    profiles,
    resumes,
    storage,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(profiles.router)
api_router.include_router(storage.router)
api_router.include_router(resumes.router)
api_router.include_router(job_descriptions.router)
api_router.include_router(evaluations.router)