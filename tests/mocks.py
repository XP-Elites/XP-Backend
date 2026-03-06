from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
import tempfile


class MockDatabaseService:
    def __init__(self, db_url: str = ""):
        self.db_url = db_url
        self._SessionLocal = None

    def init(self):
        self._SessionLocal = MagicMock()

    def session_local(self):
        return self._SessionLocal

    def is_ok(self):
        return True


class MockRabbitService:
    def __init__(self, host: str = "localhost"):
        self._host = host
        self._connection = MagicMock()
        self._channel = MagicMock()

    async def connect(self):
        pass

    def is_ok(self) -> bool:
        return True

    async def close(self):
        pass

    @property
    def channel(self):
        return self._channel


class MockStorageService:
    def __init__(self, base_storage: str = "", max_concurrency: int = 8):
        self._base_storage = base_storage or tempfile.gettempdir()
        self._max_concurrency = max_concurrency

    async def download_git_repo(self, link: str, uuid):
        pass

    async def store_files(self, uuid, files):
        pass

    def is_ok(self) -> bool:
        return True


class MockJobStatusService:
    def __init__(self, database_service=None, rabbit_service=None):
        self.database_service = database_service
        self.rabbit_service = rabbit_service

    async def init(self):
        pass

    async def init_status(self):
        return uuid4()

    async def send_job(self, uuid):
        pass


async def create_mock_rabbit_from_env():
    service = MockRabbitService(host="localhost")
    await service.connect()
    return service


def create_mock_db_from_env():
    db = MockDatabaseService(db_url="mock://localhost/test")
    db.init()
    return db


def create_mock_storage_from_env():
    return MockStorageService(base_storage=tempfile.gettempdir(), max_concurrency=8)


async def create_mock_job_status_service(database_service, rabbit_service):
    service = MockJobStatusService(database_service, rabbit_service)
    await service.init()
    return service
