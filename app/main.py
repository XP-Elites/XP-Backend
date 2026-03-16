import logging
import time

from fastapi import FastAPI, Response, status
from core.lifespan import lifespan
from core.util import get_var
from fastapi.params import Depends
from healthcheck import (
    health_check_router,
    HealthCheckService,
    get_health_check_service,
)
from status_tracker.router import status_router
from upload_file import upload_router

app = FastAPI(lifespan=lifespan)
logging.basicConfig(level=logging.DEBUG)
version = get_var("APP_VERSION", "0.0.0")


@app.middleware("http")
async def timing_middleware(request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    response.headers["X-Process-Time"] = str(duration)
    logging.debug(f"{request.url.path} took {duration:.2f}s")
    return response


@app.get("/")
async def get_api_info(
    response: Response,
    health_check_service: HealthCheckService = Depends(get_health_check_service),
):
    api_is_ok, health_body = health_check_service.get_api_status()
    response.status_code = (
        status.HTTP_200_OK if api_is_ok else status.HTTP_503_SERVICE_UNAVAILABLE
    )
    return {
        "name": "XP-API",
        "version": version,
        "status": health_body,
    }


app.include_router(router=health_check_router)
app.include_router(router=status_router)
app.include_router(router=upload_router)
