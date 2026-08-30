import uuid
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.providers.base import AIProvider
from app.ai.sanitizer import ensure_within_limit, wrap_with_delimiter
from app.core.exceptions import EmptyResumeTextError, ResourceNotFoundError
from app.core.logging import get_logger
from app.lib.constants import JOB_DESCRIPTION_EXTRACTION_PROMPT
from app.models.job_description import JobDescription
from app.models.job_description_version import JobDescriptionVersion
from app.repositories.job_description_repo import JobDescriptionRepository
from app.schemas.ai_contracts import JobDescriptionData
from app.schemas.job_description import JDCreate, JDUpdate
from app.services.parser_service import extract_text_from_url

logger = get_logger(__name__)


class JobDescriptionService:
    def __init__(
        self,
        session: AsyncSession,
        ai_provider: AIProvider,
    ):
        self.session = session
        self.ai = ai_provider
        self.jd_repo = JobDescriptionRepository(session)

    async def create_job_description(
        self, user_id: uuid.UUID, payload: JDCreate
    ) -> JobDescription:
        # Determine raw text
        if payload.input_source == "URL_IMPORT" and payload.source_url:
            raw_text = await extract_text_from_url(payload.source_url)
        else:
            raw_text = payload.raw_text.strip()

        if len(raw_text) < 20:
            raise EmptyResumeTextError("Job description text must be at least 20 characters long.")

        # Pre-flight token limit guard
        token_count = ensure_within_limit(raw_text, context="Job description")

        # Extract structured JobDescriptionData via AI Provider
        user_content = wrap_with_delimiter("job_description", raw_text)
        structured_data, usage = await self.ai.generate_structured(
            system_prompt=JOB_DESCRIPTION_EXTRACTION_PROMPT,
            user_content=user_content,
            response_schema=JobDescriptionData,
        )

        # Create logical container
        jd = JobDescription(
            user_id=user_id,
            title=payload.title,
            company_name=payload.company_name,
        )
        await self.jd_repo.create(jd)

        # Create version 1 snapshot
        version = JobDescriptionVersion(
            job_description_id=jd.id,
            version_number=1,
            input_source=payload.input_source,
            source_url=payload.source_url,
            raw_text=raw_text,
            structured_data=structured_data.model_dump(),
            parsing_metadata={"tokens": token_count, "usage": usage},
            change_summary="Initial JD extraction",
        )
        version.job_description = jd
        await self.jd_repo.create_version(version)

        # Point current version
        jd.current_version_id = version.id
        if version not in jd.versions:
            jd.versions.insert(0, version)
        await self.jd_repo.update(jd, current_version_id=version.id)

        return jd

    async def list_job_descriptions(
        self, user_id: uuid.UUID, *, skip: int = 0, limit: int = 20
    ) -> tuple[Sequence[JobDescription], int]:
        items = await self.jd_repo.list_active_by_user(user_id, skip=skip, limit=limit)
        total = await self.jd_repo.count_active_by_user(user_id)
        return items, total

    async def get_job_description_detail(
        self, jd_id: uuid.UUID, user_id: uuid.UUID
    ) -> JobDescription:
        jd = await self.jd_repo.get_with_versions(jd_id, user_id)
        if not jd:
            raise ResourceNotFoundError(f"Job Description with id {jd_id} was not found.")
        return jd

    async def update_job_description(
        self, jd_id: uuid.UUID, user_id: uuid.UUID, payload: JDUpdate
    ) -> JobDescription:
        jd = await self.jd_repo.get_by_id_and_user(jd_id, user_id)
        if not jd:
            raise ResourceNotFoundError(f"Job Description with id {jd_id} was not found.")
        return await self.jd_repo.update(
            jd,
            title=payload.title if payload.title is not None else jd.title,
            company_name=payload.company_name if payload.company_name is not None else jd.company_name,
        )

    async def archive_job_description(
        self, jd_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        jd = await self.jd_repo.get_by_id_and_user(jd_id, user_id)
        if not jd:
            raise ResourceNotFoundError(f"Job Description with id {jd_id} was not found.")
        await self.jd_repo.update(jd, is_archived=True)
