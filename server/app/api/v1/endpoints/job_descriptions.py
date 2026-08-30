import math
import uuid
from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies.auth import get_current_user_id
from app.api.dependencies.services import get_job_description_service
from app.schemas.common import PaginatedResponse, PaginationMeta, SuccessResponse
from app.schemas.job_description import (
    JDCreate,
    JDDetailResponse,
    JDListItem,
    JDUpdate,
    JDVersionResponse,
)
from app.services.job_description_service import JobDescriptionService

router = APIRouter(prefix="/job-descriptions", tags=["job-descriptions"])


@router.post("", response_model=JDDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_job_description(
    payload: JDCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    jd_service: JobDescriptionService = Depends(get_job_description_service),
) -> JDDetailResponse:
    """Creates a new job description and extracts structured requirements in version 1."""
    jd = await jd_service.create_job_description(user_id, payload)
    detailed = await jd_service.get_job_description_detail(jd.id, user_id)
    current_ver = detailed.versions[0] if detailed.versions else None

    return JDDetailResponse(
        id=detailed.id,
        user_id=detailed.user_id,
        title=detailed.title,
        company_name=detailed.company_name,
        current_version_id=detailed.current_version_id,
        current_version=JDVersionResponse.model_validate(current_ver) if current_ver else None,
        created_at=detailed.created_at,
        updated_at=detailed.updated_at,
    )


@router.get("", response_model=PaginatedResponse[JDListItem], status_code=status.HTTP_200_OK)
async def list_job_descriptions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: uuid.UUID = Depends(get_current_user_id),
    jd_service: JobDescriptionService = Depends(get_job_description_service),
) -> PaginatedResponse[JDListItem]:
    """Lists saved job descriptions for the authenticated user."""
    skip = (page - 1) * page_size
    items, total = await jd_service.list_job_descriptions(user_id, skip=skip, limit=page_size)

    list_items = [
        JDListItem(
            id=jd.id,
            title=jd.title,
            company_name=jd.company_name,
            current_version_id=jd.current_version_id,
            created_at=jd.created_at,
            updated_at=jd.updated_at,
        )
        for jd in items
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


@router.get("/{id}", response_model=JDDetailResponse, status_code=status.HTTP_200_OK)
async def get_job_description(
    id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    jd_service: JobDescriptionService = Depends(get_job_description_service),
) -> JDDetailResponse:
    """Gets details and latest structured requirements for a job description."""
    detailed = await jd_service.get_job_description_detail(id, user_id)
    current_ver = detailed.versions[0] if detailed.versions else None

    return JDDetailResponse(
        id=detailed.id,
        user_id=detailed.user_id,
        title=detailed.title,
        company_name=detailed.company_name,
        current_version_id=detailed.current_version_id,
        current_version=JDVersionResponse.model_validate(current_ver) if current_ver else None,
        created_at=detailed.created_at,
        updated_at=detailed.updated_at,
    )


@router.patch("/{id}", response_model=JDDetailResponse, status_code=status.HTTP_200_OK)
async def update_job_description(
    id: uuid.UUID,
    payload: JDUpdate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    jd_service: JobDescriptionService = Depends(get_job_description_service),
) -> JDDetailResponse:
    """Updates title or company name for a job description."""
    await jd_service.update_job_description(id, user_id, payload)
    detailed = await jd_service.get_job_description_detail(id, user_id)
    current_ver = detailed.versions[0] if detailed.versions else None

    return JDDetailResponse(
        id=detailed.id,
        user_id=detailed.user_id,
        title=detailed.title,
        company_name=detailed.company_name,
        current_version_id=detailed.current_version_id,
        current_version=JDVersionResponse.model_validate(current_ver) if current_ver else None,
        created_at=detailed.created_at,
        updated_at=detailed.updated_at,
    )


@router.delete("/{id}", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
async def archive_job_description(
    id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    jd_service: JobDescriptionService = Depends(get_job_description_service),
) -> SuccessResponse:
    """Archives a job description."""
    await jd_service.archive_job_description(id, user_id)
    return SuccessResponse(message="Job description archived successfully.")
