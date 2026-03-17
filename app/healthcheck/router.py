from fastapi import APIRouter, Response, Depends, status

from .health_check import HealthCheckService, get_health_check_service

health_check_router = APIRouter(prefix="/health")


@health_check_router.get("/ready")
async def get_health_check(
    response: Response,
    health_check_service: HealthCheckService = Depends(get_health_check_service),
):
    api_is_ok, body = await health_check_service.get_api_status()
    response.status_code = (
        status.HTTP_200_OK if api_is_ok else status.HTTP_503_SERVICE_UNAVAILABLE
    )
    return body


@health_check_router.get("/live")
async def get_live_check():
    return "ok"
