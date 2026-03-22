from unittest.mock import MagicMock
from uuid import UUID, uuid4
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

    async def connect(self, retries: int = 10, delay: float = 3.0):
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
        self._database_service = database_service
        self._rabbit_service = rabbit_service

    async def init(self):
        pass

    async def init_status(self) -> UUID:
        return uuid4()

    async def send_job(self, uuid: UUID):
        pass


def create_mock_rabbit_from_env() -> MockRabbitService:
    return MockRabbitService(host="localhost")


def create_mock_db_from_env() -> MockDatabaseService:
    db = MockDatabaseService(db_url="mock://localhost/test")
    db.init()
    return db


def create_mock_storage_from_env() -> MockStorageService:
    return MockStorageService()


async def create_mock_job_status_service(
    database_service=None, rabbit_service=None
) -> MockJobStatusService:
    service = MockJobStatusService(
        database_service=database_service,
        rabbit_service=rabbit_service,
    )
    await service.init()
    return service