from contextlib import asynccontextmanager

import dotenv

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.database_service import DatabaseService, create_db_from_env
from core.rabbit_service import RabbitService, create_rabbit_from_env
from core.storage_service import create_storage_from_env, StorageService
from core.job_status import JobStatusService, create_job_status_service


@asynccontextmanager
async def lifespan(app):
    dotenv.load_dotenv()

    rabbit_service: RabbitService = await create_rabbit_from_env()
    database_service: DatabaseService = create_db_from_env()
    storage_service: StorageService = create_storage_from_env()
    job_status_service = await create_job_status_service(
        database_service, rabbit_service
    )

    app.state.rabbit_service = rabbit_service
    app.state.database_service = database_service
    app.state.storage_service = storage_service
    app.state.job_status_service = job_status_service
    yield
    await rabbit_service.close()


def get_database_session(request: Request):
    db_provider: DatabaseService = request.app.state.database_service
    session: AsyncSession = (
        db_provider.session_local()()
    )  # First get, then init the session.
    try:
        yield session
    finally:
        session.close()


def get_database_service(request: Request):
    service: DatabaseService = request.app.state.database_service
    return service


def get_storage_service(request: Request):
    service: StorageService = request.app.state.storage_service
    return service


def get_rabbit_service(request: Request):
    service: RabbitService = request.app.state.rabbit_service
    return service


def get_job_status_service(request: Request):
    service: JobStatusService = request.app.state.job_status_service
    return service
