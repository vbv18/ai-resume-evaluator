import math
import uuid
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status

from app.api.dependencies.auth import get_current_user_id
from app.api.dependencies.services import get_resume_service
from app.schemas.common import PaginatedResponse, PaginationMeta, SuccessResponse
from app.schemas.resume import (
    ResumeCreate,
    ResumeDetailResponse,
    ResumeListItem,
    ResumeUpdate,
)
from app.schemas.resume_version import (
    ResumeVersionCreate,
    ResumeVersionResponse,
    ResumeVersionSummary,
)
from app.services.resume_service import ResumeService

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("", response_model=ResumeDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_resume(
    payload: ResumeCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    resume_service: ResumeService = Depends(get_resume_service),
) -> ResumeDetailResponse:
    """Creates a new logical resume with optional initial version."""
    resume = await resume_service.create_resume(user_id, payload)
    detailed = await resume_service.get_resume_detail(resume.id, user_id)
    current_ver = detailed.versions[0] if detailed.versions else None
    if not current_ver and detailed.current_version_id:
        current_ver = await resume_service.get_version(detailed.current_version_id, user_id)

    return ResumeDetailResponse(
        id=detailed.id,
        user_id=detailed.user_id,
        title=detailed.title,
        target_role=detailed.target_role,
        current_version_id=detailed.current_version_id,
        current_version=ResumeVersionResponse.model_validate(current_ver) if current_ver else None,
        created_at=detailed.created_at,
        updated_at=detailed.updated_at,
    )


@router.post("/upload", response_model=ResumeDetailResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume_file(
    file: UploadFile = File(...),
    title: str = Form("My Resume"),
    target_role: str | None = Form(None),
    user_id: uuid.UUID = Depends(get_current_user_id),
    resume_service: ResumeService = Depends(get_resume_service),
) -> ResumeDetailResponse:
    """Multipart upload creating a resume and parsing version 1 in one step."""
    file_bytes = await file.read()
    payload = ResumeCreate(
        title=title,
        target_role=target_role,
        input_source="FILE_UPLOAD",
    )
    resume = await resume_service.create_resume(
        user_id=user_id,
        payload=payload,
        file_bytes=file_bytes,
        filename=file.filename or "resume.pdf",
        content_type=file.content_type,
    )
    detailed = await resume_service.get_resume_detail(resume.id, user_id)
    current_ver = detailed.versions[0] if detailed.versions else None
    if not current_ver and detailed.current_version_id:
        current_ver = await resume_service.get_version(detailed.current_version_id, user_id)

    return ResumeDetailResponse(
        id=detailed.id,
        user_id=detailed.user_id,
        title=detailed.title,
        target_role=detailed.target_role,
        current_version_id=detailed.current_version_id,
        current_version=ResumeVersionResponse.model_validate(current_ver) if current_ver else None,
        created_at=detailed.created_at,
        updated_at=detailed.updated_at,
    )


@router.get("", response_model=PaginatedResponse[ResumeListItem], status_code=status.HTTP_200_OK)
async def list_resumes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: uuid.UUID = Depends(get_current_user_id),
    resume_service: ResumeService = Depends(get_resume_service),
) -> PaginatedResponse[ResumeListItem]:
    """Lists active resumes for the authenticated user."""
    skip = (page - 1) * page_size
    items, total = await resume_service.list_resumes(user_id, skip=skip, limit=page_size)

    list_items = [
        ResumeListItem(
            id=r.id,
            title=r.title,
            target_role=r.target_role,
            current_version_id=r.current_version_id,
            version_count=len(r.versions),
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in items
    ]

    total_pages = math.ceil(total / page_size) if total > 0 else 0
    return PaginatedResponse(
        data=list_items,
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        ),
    )


@router.get("/{id}", response_model=ResumeDetailResponse, status_code=status.HTTP_200_OK)
async def get_resume(
    id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    resume_service: ResumeService = Depends(get_resume_service),
) -> ResumeDetailResponse:
    """Gets details and latest version for a specific resume."""
    resume = await resume_service.get_resume_detail(id, user_id)
    current_ver = resume.versions[0] if resume.versions else None
    if not current_ver and resume.current_version_id:
        current_ver = await resume_service.get_version(resume.current_version_id, user_id)

    return ResumeDetailResponse(
        id=resume.id,
        user_id=resume.user_id,
        title=resume.title,
        target_role=resume.target_role,
        current_version_id=resume.current_version_id,
        current_version=ResumeVersionResponse.model_validate(current_ver) if current_ver else None,
        created_at=resume.created_at,
        updated_at=resume.updated_at,
    )


@router.patch("/{id}", response_model=ResumeDetailResponse, status_code=status.HTTP_200_OK)
async def update_resume(
    id: uuid.UUID,
    payload: ResumeUpdate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    resume_service: ResumeService = Depends(get_resume_service),
) -> ResumeDetailResponse:
    """Updates title or target role for a resume."""
    await resume_service.update_resume(id, user_id, payload)
    detailed = await resume_service.get_resume_detail(id, user_id)
    return ResumeDetailResponse.model_validate(detailed)


@router.delete("/{id}", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
async def delete_resume(
    id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    resume_service: ResumeService = Depends(get_resume_service),
) -> SuccessResponse:
    """Soft deletes a resume."""
    await resume_service.delete_resume(id, user_id)
    return SuccessResponse(message="Resume deleted successfully.")


# Versioning Endpoints
@router.post("/{id}/versions", response_model=ResumeVersionResponse, status_code=status.HTTP_201_CREATED)
async def create_resume_version(
    id: uuid.UUID,
    payload: ResumeVersionCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    resume_service: ResumeService = Depends(get_resume_service),
) -> ResumeVersionResponse:
    """Creates a new immutable version snapshot for a resume."""
    version = await resume_service.create_version(user_id, id, payload)
    return ResumeVersionResponse.model_validate(version)


@router.get("/{id}/versions", response_model=list[ResumeVersionSummary], status_code=status.HTTP_200_OK)
async def list_resume_versions(
    id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    resume_service: ResumeService = Depends(get_resume_service),
) -> list[ResumeVersionSummary]:
    """Lists all version history summaries for a resume."""
    versions = await resume_service.list_versions(id, user_id)
    return [ResumeVersionSummary.model_validate(v) for v in versions]


@router.get("/{id}/versions/{version_id}", response_model=ResumeVersionResponse, status_code=status.HTTP_200_OK)
async def get_resume_version(
    id: uuid.UUID,
    version_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    resume_service: ResumeService = Depends(get_resume_service),
) -> ResumeVersionResponse:
    """Gets complete structured snapshot for a specific resume version."""
    version = await resume_service.get_version(version_id, user_id)
    return ResumeVersionResponse.model_validate(version)
