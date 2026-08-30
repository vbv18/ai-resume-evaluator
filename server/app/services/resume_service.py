import uuid
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.providers.base import AIProvider
from app.ai.sanitizer import ensure_within_limit, wrap_with_delimiter
from app.core.exceptions import EmptyResumeTextError, ResourceNotFoundError
from app.core.logging import get_logger
from app.lib.constants import RESUME_EXTRACTION_PROMPT
from app.models.resume import Resume
from app.models.resume_file import ResumeFile
from app.models.resume_version import ResumeVersion
from app.repositories.resume_repo import ResumeRepository
from app.repositories.resume_version_repo import ResumeVersionRepository
from app.schemas.ai_contracts import ResumeData
from app.schemas.resume import ResumeCreate, ResumeUpdate
from app.schemas.resume_version import ResumeVersionCreate
from app.services.parser_service import extract_text_from_file, extract_text_from_url

logger = get_logger(__name__)


class ResumeService:
    def __init__(
        self,
        session: AsyncSession,
        ai_provider: AIProvider,
    ):
        self.session = session
        self.ai = ai_provider
        self.resume_repo = ResumeRepository(session)
        self.version_repo = ResumeVersionRepository(session)

    async def create_resume(
        self,
        user_id: uuid.UUID,
        payload: ResumeCreate,
        file_bytes: bytes | None = None,
        filename: str | None = None,
        content_type: str | None = None,
    ) -> Resume:
        resume = Resume(
            user_id=user_id,
            title=payload.title,
            target_role=payload.target_role,
        )
        await self.resume_repo.create(resume)

        # If initial version content provided, create version 1
        if payload.input_source:
            version_payload = ResumeVersionCreate(
                input_source=payload.input_source,
                resume_file_id=payload.resume_file_id,
                source_url=payload.source_url,
                raw_text=payload.raw_text,
                change_summary="Initial version",
            )
            version = await self.create_version(
                user_id=user_id,
                resume_id=resume.id,
                payload=version_payload,
                file_bytes=file_bytes,
                filename=filename,
                content_type=content_type,
            )
            resume.current_version_id = version.id
            await self.resume_repo.update(resume, current_version_id=version.id)

        return resume

    async def create_version(
        self,
        user_id: uuid.UUID,
        resume_id: uuid.UUID,
        payload: ResumeVersionCreate,
        file_bytes: bytes | None = None,
        filename: str | None = None,
        content_type: str | None = None,
    ) -> ResumeVersion:
        resume = await self.resume_repo.get_by_id_and_user(resume_id, user_id)
        if not resume:
            raise ResourceNotFoundError(f"Resume with id {resume_id} was not found.")

        # Determine raw text based on source
        if payload.input_source == "DIRECT_TEXT":
            if not payload.raw_text or len(payload.raw_text.strip()) < 20:
                raise EmptyResumeTextError("Resume text must be at least 20 characters long.")
            raw_text = payload.raw_text.strip()
        elif payload.input_source == "URL_IMPORT":
            if not payload.source_url:
                raise EmptyResumeTextError("Source URL is required for URL import.")
            raw_text = await extract_text_from_url(payload.source_url)
        elif payload.input_source == "FILE_UPLOAD":
            if file_bytes and filename:
                raw_text = extract_text_from_file(filename, content_type, file_bytes)
            elif payload.resume_file_id:
                file_record = await self.resume_repo.get_file_by_id_and_user(
                    payload.resume_file_id, user_id
                )
                if not file_record:
                    raise ResourceNotFoundError("Uploaded resume file was not found.")
                raw_text = payload.raw_text or "Extracted resume content"
            else:
                raise EmptyResumeTextError("File bytes or resume_file_id required for file upload.")
        else:
            raise EmptyResumeTextError(f"Unsupported input source: {payload.input_source}")

        # Pre-flight token limit guard
        token_count = ensure_within_limit(raw_text, context="Resume")

        # Extract structured ResumeData via AI Provider
        user_content = wrap_with_delimiter("candidate_resume", raw_text)
        structured_data, usage = await self.ai.generate_structured(
            system_prompt=RESUME_EXTRACTION_PROMPT,
            user_content=user_content,
            response_schema=ResumeData,
        )

        version_number = await self.version_repo.get_next_version_number(resume_id)

        version = ResumeVersion(
            resume_id=resume_id,
            version_number=version_number,
            input_source=payload.input_source,
            resume_file_id=payload.resume_file_id,
            source_url=payload.source_url,
            raw_text=raw_text,
            structured_data=structured_data.model_dump(),
            parsing_metadata={"tokens": token_count, "usage": usage},
            change_summary=payload.change_summary,
        )
        version.resume = resume
        await self.version_repo.create(version)

        # Update current version pointer
        resume.current_version_id = version.id
        if version not in resume.versions:
            resume.versions.insert(0, version)
        await self.resume_repo.update(resume, current_version_id=version.id)

        return version

    async def list_resumes(
        self, user_id: uuid.UUID, *, skip: int = 0, limit: int = 20
    ) -> tuple[Sequence[Resume], int]:
        items = await self.resume_repo.list_active_by_user(user_id, skip=skip, limit=limit)
        total = await self.resume_repo.count_active_by_user(user_id)
        return items, total

    async def get_resume_detail(self, resume_id: uuid.UUID, user_id: uuid.UUID) -> Resume:
        resume = await self.resume_repo.get_with_versions(resume_id, user_id)
        if not resume:
            raise ResourceNotFoundError(f"Resume with id {resume_id} was not found.")
        return resume

    async def update_resume(
        self, resume_id: uuid.UUID, user_id: uuid.UUID, payload: ResumeUpdate
    ) -> Resume:
        resume = await self.resume_repo.get_by_id_and_user(resume_id, user_id)
        if not resume:
            raise ResourceNotFoundError(f"Resume with id {resume_id} was not found.")
        return await self.resume_repo.update(
            resume,
            title=payload.title if payload.title is not None else resume.title,
            target_role=payload.target_role if payload.target_role is not None else resume.target_role,
        )

    async def delete_resume(self, resume_id: uuid.UUID, user_id: uuid.UUID) -> None:
        resume = await self.resume_repo.get_by_id_and_user(resume_id, user_id)
        if not resume:
            raise ResourceNotFoundError(f"Resume with id {resume_id} was not found.")
        await self.resume_repo.soft_delete(resume)

    async def list_versions(
        self, resume_id: uuid.UUID, user_id: uuid.UUID
    ) -> Sequence[ResumeVersion]:
        resume = await self.resume_repo.get_by_id_and_user(resume_id, user_id)
        if not resume:
            raise ResourceNotFoundError(f"Resume with id {resume_id} was not found.")
        return await self.version_repo.list_by_resume(resume_id)

    async def get_version(
        self, version_id: uuid.UUID, user_id: uuid.UUID
    ) -> ResumeVersion:
        version = await self.version_repo.get_by_id_and_user(version_id, user_id)
        if not version:
            raise ResourceNotFoundError(f"Resume version {version_id} was not found.")
        return version
