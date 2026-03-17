from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from status_tracker.status_tracking_service import (
    get_status_tracking_service,
    StatusTrackingService,
    JobNotFoundException,
    JobCorruptedException,
)

status_router = APIRouter(prefix="/status")


@status_router.get("/{job_uuid}")
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
    except JobCorruptedException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Job status file not found, please rerun job.",
        )
    return job_status
