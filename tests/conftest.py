import sys
import pytest
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from fastapi.testclient import TestClient

env_file = Path(__file__).parent / ".env.test"
load_dotenv(env_file)

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from mocks import (
    create_mock_db_from_env,
    create_mock_rabbit_from_env,
    create_mock_storage_from_env,
    create_mock_job_status_service,
)

from app.main import app


def _setup_mock_services():
    app.state.database_service = create_mock_db_from_env()
    app.state.storage_service = create_mock_storage_from_env()
    app.state.rabbit_service = asyncio.run(create_mock_rabbit_from_env())
    app.state.job_status_service = asyncio.run(
        create_mock_job_status_service(
            app.state.database_service, 
            app.state.rabbit_service
        )
    )


@pytest.fixture
def client():
    _setup_mock_services()
    return TestClient(app)
