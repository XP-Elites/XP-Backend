from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from status_tracker.status_tracking_service import (
    get_status_tracking_service,
    StatusTrackingService,
    JobNotFoundException,
    JobCorruptedException,
)

status_router = APIRouter(prefix="/status")


@status_router.get("/{uuid}")
async def get_job_status(
    uuid: UUID,
    status_tracking_service: StatusTrackingService = Depends(
        get_status_tracking_service
    ),
):
    try:
        job_status = await status_tracking_service.get_job_status(uuid)
    except JobNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job not found: {uuid}",
        )
    except JobCorruptedException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e
        )
    return job_status
