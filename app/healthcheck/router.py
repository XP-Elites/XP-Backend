from fastapi import APIRouter, status, Response

from .health_check import database_latency

health_check_router = APIRouter(prefix="/health")


@health_check_router.get("/ready")
async def get_health_check(response: Response):
    db_latency = database_latency()
    db_ok = db_latency is not None
    response.status_code = (
        status.HTTP_200_OK if db_ok else status.HTTP_503_SERVICE_UNAVAILABLE
    )
    return {
        "api": "ok",
        "db": f"{db_latency}ms" if db_latency is not None else "unavailable",
    }


@health_check_router.get("/live")
async def get_live_check():
    return "ok"
