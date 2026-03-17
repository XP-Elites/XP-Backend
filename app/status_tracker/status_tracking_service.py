from uuid import UUID

from fastapi import Depends

from core import StorageService
from core.job_status import JobStatusService
from core.job_status.model import StatusTypes
from core.lifespan import get_job_status_service, get_storage_service


class JobNotFoundException(Exception):
    pass


class JobCorruptedException(Exception):
    pass


class StatusTrackingService:

    def __init__(
        self,
        job_status_service: JobStatusService,
        storage_service: StorageService,
    ):
        self._job_status_service = job_status_service
        self._storage_service = storage_service

    async def get_job_status(self, uuid: UUID):
        job_status = await self._job_status_service.get_status(uuid)
        if job_status is None:
            raise JobNotFoundException()
        result = None
        if job_status == StatusTypes.COMPLETE:
            result = self._storage_service.get_results_file(uuid)
            if result is None:
                raise JobCorruptedException()
        return {"uuid": uuid, "status": job_status, "result": result}


def get_status_tracking_service(
    job_status_service: JobStatusService = Depends(get_job_status_service),
    storage_service: StorageService = Depends(get_storage_service),
):
    return StatusTrackingService(
        job_status_service=job_status_service, storage_service=storage_service
    )
