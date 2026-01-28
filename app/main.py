import logging
import os

from fastapi import FastAPI, Response

from healthcheck import health_check_router
from healthcheck.router import get_health_check

app = FastAPI()
logging.basicConfig(level=logging.INFO)
version = os.getenv("APP_VERSION", "0.0.0")


@app.get("/")
async def get_api_info(response: Response):
    return {
        "name": "FYP-API",
        "version": version,
        "status": await get_health_check(response),
    }


app.include_router(router=health_check_router)
