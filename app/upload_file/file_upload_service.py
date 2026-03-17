import logging

from fastapi import BackgroundTasks, Depends, UploadFile

from core import get_logger, StorageService, get_storage_service
from core.lifespan import get_job_status_service
from core.job_status import JobStatusService

logger = get_logger(__name__, logging.DEBUG)


class FileUploadService:

    def __init__(
        self,
        background_tasks: BackgroundTasks,
        job_status_service: JobStatusService,
        storage_service: StorageService,
    ):
        self._background_tasks = background_tasks
        self._job_status_service = job_status_service
        self._storage_service = storage_service

    async def store_files(self, uuid, files):
        await self._storage_service.store_files(uuid, files)
        await self._job_status_service.send_job(uuid)

    async def process_files(self, files: list[UploadFile]):
        uuid = await self._job_status_service.init_status()
        self._background_tasks.add_task(self.store_files, uuid, files)
        return uuid


def get_file_upload_service(
    background_tasks: BackgroundTasks,
    job_status_service: JobStatusService = Depends(get_job_status_service),
    storage_service: StorageService = Depends(get_storage_service),
):
    return FileUploadService(
        background_tasks=background_tasks,
        job_status_service=job_status_service,
        storage_service=storage_service,
    )
