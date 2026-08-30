import math
import uuid
from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies.auth import get_current_user_id
from app.api.dependencies.services import get_evaluation_service
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.schemas.evaluation import (
    EvalRunListItem,
    EvaluationComparisonResponse,
    EvaluationCreate,
    EvaluationEnqueueResponse,
    EvaluationFullResponse,
    EvaluationStatusResponse,
)
from app.services.evaluation_service import EvaluationService

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


@router.post("", response_model=EvaluationEnqueueResponse, status_code=status.HTTP_202_ACCEPTED)
async def enqueue_evaluation(
    payload: EvaluationCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    eval_service: EvaluationService = Depends(get_evaluation_service),
) -> EvaluationEnqueueResponse:
    """
    Enqueues an asynchronous AI evaluation for a specific resume version and JD version.
    Job is picked up by the PostgreSQL SKIP LOCKED worker.
    """
    run = await eval_service.enqueue_evaluation(user_id, payload)
    return EvaluationEnqueueResponse(
        evaluation_id=run.id,
        status=run.status,
        message="Evaluation has been queued for background processing.",
    )


@router.get("", response_model=PaginatedResponse[EvalRunListItem], status_code=status.HTTP_200_OK)
async def list_evaluations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: uuid.UUID = Depends(get_current_user_id),
    eval_service: EvaluationService = Depends(get_evaluation_service),
) -> PaginatedResponse[EvalRunListItem]:
    """Lists historical evaluation runs for the authenticated user."""
    skip = (page - 1) * page_size
    runs = await eval_service.list_user_evaluations(user_id, skip=skip, limit=page_size)

    list_items = [
        EvalRunListItem(
            id=r.id,
            resume_version_id=r.resume_version_id,
            job_description_version_id=r.job_description_version_id,
            status=r.status,
            overall_score=r.overall_score,
            verdict=r.verdict,
            created_at=r.created_at,
            completed_at=r.completed_at,
        )
        for r in runs
    ]

    total = len(runs)  # or count query
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    return PaginatedResponse(
        data=list_items,
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=total_pages,
            has_next=False,
            has_prev=page > 1,
        ),
    )


@router.get("/compare", response_model=EvaluationComparisonResponse, status_code=status.HTTP_200_OK)
async def compare_evaluations(
    run_a: uuid.UUID = Query(..., description="First evaluation run UUID (e.g. v1)"),
    run_b: uuid.UUID = Query(..., description="Second evaluation run UUID (e.g. v2)"),
    user_id: uuid.UUID = Depends(get_current_user_id),
    eval_service: EvaluationService = Depends(get_evaluation_service),
) -> EvaluationComparisonResponse:
    """Compares score improvements and newly matched skills between two evaluation runs."""
    return await eval_service.compare_evaluations(run_a, run_b, user_id)


@router.get("/{id}", response_model=EvaluationFullResponse, status_code=status.HTTP_200_OK)
async def get_evaluation(
    id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    eval_service: EvaluationService = Depends(get_evaluation_service),
) -> EvaluationFullResponse:
    """Gets complete evaluation result breakdown and scores."""
    return await eval_service.get_full_evaluation(id, user_id)


@router.get("/{id}/status", response_model=EvaluationStatusResponse, status_code=status.HTTP_200_OK)
async def get_evaluation_status(
    id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    eval_service: EvaluationService = Depends(get_evaluation_service),
) -> EvaluationStatusResponse:
    """Fast status polling endpoint for evaluation progress tracker."""
    return await eval_service.get_status(id, user_id)
