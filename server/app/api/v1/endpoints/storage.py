import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user_id
from app.api.dependencies.services import get_storage_service
from app.db.session import get_db
from app.models.resume_file import ResumeFile
from app.repositories.resume_repo import ResumeRepository
from app.schemas.resume import UploadUrlRequest, UploadUrlResponse
from app.services.storage_service import StorageService

router = APIRouter(prefix="/storage", tags=["storage"])


@router.post("/upload-url", response_model=UploadUrlResponse, status_code=status.HTTP_200_OK)
async def generate_upload_url(
    payload: UploadUrlRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    storage_service: StorageService = Depends(get_storage_service),
    session: AsyncSession = Depends(get_db),
) -> UploadUrlResponse:
    """
    Generates a secure storage path and signed upload target for direct client resume upload.
    """
    storage_path, upload_url, checksum = storage_service.generate_upload_metadata(
        user_id=user_id,
        filename=payload.filename,
        mime_type=payload.mime_type,
        file_size_bytes=payload.file_size_bytes,
    )

    resume_repo = ResumeRepository(session)
    file_record = ResumeFile(
        user_id=user_id,
        storage_provider="supabase_storage",
        storage_bucket=storage_service.settings.storage_bucket_resumes,
        storage_path=storage_path,
        original_filename=payload.filename,
        mime_type=payload.mime_type,
        file_size_bytes=payload.file_size_bytes,
        sha256_checksum=checksum,
    )
    await resume_repo.create_file(file_record)

    return UploadUrlResponse(
        upload_url=upload_url,
        storage_path=storage_path,
        resume_file_id=file_record.id,
    )
