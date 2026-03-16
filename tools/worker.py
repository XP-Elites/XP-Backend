import asyncio
import logging
import os
import subprocess
import sys
from pathlib import Path
from uuid import UUID

import dotenv
from aio_pika import ExchangeType
from sqlalchemy import update

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = PROJECT_ROOT / "app"

if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from core.database_service import create_db_from_env
from core.rabbit_service import create_rabbit_from_env
from status_tracker.model import JobStatus, StatusTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("xp-worker")

SCRIPT_PATH = Path(
    os.getenv(
        "XP_WORKER_SCRIPT_PATH",
        str(PROJECT_ROOT / "tools" / "XP-Scripts" / "run_all.py"),
    )
)
STORAGE_ROOT = Path(os.getenv("XP_WORKER_STORAGE", "/storage"))


async def set_status(database_service, uuid: UUID, status: StatusTypes):
    async with database_service.session_local()() as session:
        query = update(JobStatus).where(JobStatus.uuid == uuid).values(status=status)
        await session.execute(query)
        await session.commit()


async def process_job(database_service, uuid: UUID):
    job_dir = STORAGE_ROOT / str(uuid)
    if not job_dir.exists():
        raise FileNotFoundError(f"Job directory does not exist: {job_dir}")

    await set_status(database_service, uuid, StatusTypes.PROCESSING)
    logger.info("Processing job %s in %s", uuid, job_dir)

    result = await asyncio.to_thread(
        subprocess.run,
        [sys.executable, str(SCRIPT_PATH), str(job_dir)],
        capture_output=True,
        text=True,
        cwd=str(SCRIPT_PATH.parent),
        check=False,
    )

    if result.stdout:
        logger.info("xp-scripts stdout for %s:\n%s", uuid, result.stdout)
    if result.stderr:
        logger.warning("xp-scripts stderr for %s:\n%s", uuid, result.stderr)

    if result.returncode != 0:
        raise RuntimeError(f"xp-scripts failed for {uuid} with exit code {result.returncode}")

    await set_status(database_service, uuid, StatusTypes.COMPLETE)


async def main():
    dotenv.load_dotenv(APP_ROOT / ".env")
    dotenv.load_dotenv(PROJECT_ROOT / ".env")
    dotenv.load_dotenv(PROJECT_ROOT / "local" / ".env")

    rabbit_service = await create_rabbit_from_env()
    database_service = create_db_from_env()

    exchange = await rabbit_service.channel.declare_exchange(
        "processing", ExchangeType.DIRECT
    )
    queue = await rabbit_service.channel.declare_queue("jobs", durable=True)
    await queue.bind(exchange, "jobs")

    logger.info("Worker started, waiting for jobs...")

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process(requeue=False):
                uuid = UUID(bytes=message.body)
                try:
                    await process_job(database_service, uuid)
                except Exception:
                    logger.exception("Failed processing job %s", uuid)
                    await set_status(database_service, uuid, StatusTypes.ERROR)


if __name__ == "__main__":
    asyncio.run(main())