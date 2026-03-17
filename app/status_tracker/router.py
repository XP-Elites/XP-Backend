import json
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from core.lifespan import get_job_status_service, get_storage_service
from core.storage_service import StorageService
from .JobStatusService import JobStatusService

status_router = APIRouter(prefix="/status")


@status_router.get("/{job_uuid}")
async def get_job_status(
	job_uuid: UUID,
	job_status_service: JobStatusService = Depends(get_job_status_service),
	storage_service: StorageService = Depends(get_storage_service),
):
	job_status = await job_status_service.get_status(job_uuid)
	if job_status is None:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f"Job not found: {job_uuid}",
		)

	results = None
	results_path = Path(storage_service._base_storage) / str(job_uuid) / "results.json"
	if results_path.exists():
		with open(results_path, "r") as results_file:
			results = json.load(results_file)

	return {
		"uuid": str(job_uuid),
		"status": job_status.status.name,
		"results": results,
	}