from fastapi import Depends

from core import (
    DatabaseService,
    RabbitService,
    StorageService,
    get_rabbit_service,
    get_storage_service,
    get_database_service,
)


def bool_to_status(status: bool):
    if status:
        return "ok"
    return "unavailable"


class HealthCheckService:

    def __init__(self, database_service, rabbit_service, storage_service):
        self.database_service: DatabaseService = database_service
        self.rabbit_service: RabbitService = rabbit_service
        self.storage_service: StorageService = storage_service

    async def get_api_status(self) -> tuple[bool, dict[str, str]]:
        db_ok = await self.database_service.is_ok()
        rabbit_ok = self.rabbit_service.is_ok()
        storage_ok = self.storage_service.is_ok()
        body = {
            "api": "ok",
            "db": bool_to_status(db_ok),
            "rabbit": bool_to_status(rabbit_ok),
            "storage": bool_to_status(storage_ok),
        }
        api_is_ok = db_ok & rabbit_ok & storage_ok
        return api_is_ok, body


def get_health_check_service(
    database_service: DatabaseService = Depends(get_database_service),
    rabbit_service: RabbitService = Depends(get_rabbit_service),
    storage_service: StorageService = Depends(get_storage_service),
) -> HealthCheckService:
    return HealthCheckService(database_service, rabbit_service, storage_service)
