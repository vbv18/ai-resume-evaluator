from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.factory import get_ai_provider
from app.ai.providers.base import AIProvider
from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.repositories.profile_repo import ProfileRepository
from app.services.evaluation_service import EvaluationService
from app.services.job_description_service import JobDescriptionService
from app.services.resume_service import ResumeService
from app.services.storage_service import StorageService


def get_ai(settings: Settings = Depends(get_settings)) -> AIProvider:
    return get_ai_provider(settings)


def get_profile_repo(session: AsyncSession = Depends(get_db)) -> ProfileRepository:
    return ProfileRepository(session)


def get_storage_service(settings: Settings = Depends(get_settings)) -> StorageService:
    return StorageService(settings)


def get_resume_service(
    session: AsyncSession = Depends(get_db),
    ai: AIProvider = Depends(get_ai),
) -> ResumeService:
    return ResumeService(session, ai)


def get_job_description_service(
    session: AsyncSession = Depends(get_db),
    ai: AIProvider = Depends(get_ai),
) -> JobDescriptionService:
    return JobDescriptionService(session, ai)


def get_evaluation_service(
    session: AsyncSession = Depends(get_db),
    ai: AIProvider = Depends(get_ai),
    settings: Settings = Depends(get_settings),
) -> EvaluationService:
    return EvaluationService(session, ai, settings)
