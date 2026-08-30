import asyncio
import uuid
from app.ai.factory import get_ai_provider
from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.db.session import get_session_factory
from app.repositories.evaluation_repo import EvaluationRepository
from app.services.evaluation_service import EvaluationService

logger = get_logger(__name__)

_worker_task: asyncio.Task | None = None
_stop_event = asyncio.Event()


async def run_evaluation_worker_loop(settings: Settings) -> None:
    """
    Continuous background loop that polls for QUEUED evaluation runs
    using atomic SELECT FOR UPDATE SKIP LOCKED on PostgreSQL.
    """
    logger.info("evaluation_worker_started", interval=settings.worker_poll_interval_seconds)
    session_factory = get_session_factory()
    ai_provider = get_ai_provider(settings)

    while not _stop_event.is_set():
        claimed_run_id: uuid.UUID | None = None

        try:
            # 1. Claim next queued job atomically
            async with session_factory() as session:
                eval_repo = EvaluationRepository(session)
                claimed_run = await eval_repo.claim_next_queued_run()
                if claimed_run:
                    claimed_run_id = claimed_run.id
                    await session.commit()

            # 2. Process job if claimed
            if claimed_run_id:
                logger.info("worker_processing_job", run_id=str(claimed_run_id))
                async with session_factory() as session:
                    service = EvaluationService(session, ai_provider, settings)
                    await service.process_evaluation_run(claimed_run_id)
            else:
                # No job queued, sleep before next poll
                await asyncio.sleep(settings.worker_poll_interval_seconds)

        except asyncio.CancelledError:
            logger.info("evaluation_worker_cancelled")
            break
        except Exception as exc:
            logger.error("evaluation_worker_error", error=str(exc), run_id=str(claimed_run_id) if claimed_run_id else None)
            await asyncio.sleep(settings.worker_poll_interval_seconds)


def start_evaluation_worker(settings: Settings) -> None:
    global _worker_task, _stop_event
    _stop_event.clear()
    if _worker_task is None or _worker_task.done():
        _worker_task = asyncio.create_task(run_evaluation_worker_loop(settings))


async def stop_evaluation_worker() -> None:
    global _worker_task, _stop_event
    _stop_event.set()
    if _worker_task and not _worker_task.done():
        _worker_task.cancel()
        try:
            await _worker_task
        except asyncio.CancelledError:
            pass
    logger.info("evaluation_worker_stopped")
