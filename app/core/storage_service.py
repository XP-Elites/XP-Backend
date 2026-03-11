import asyncio
import logging
import os
import shutil
from pathlib import Path
from uuid import UUID

import aiofiles
from fastapi import UploadFile
from git import Repo

from core.util import get_logger, get_var

logger = get_logger(__name__, logging.DEBUG)


class ServiceNoStorageError(Exception):
    pass


class StorageService:

    MIN_FREE_SPACE_BYTES = 500 * 1024 * 1024
    CHUNK_SIZE = 1024 * 1024
    CLONE_DEPTH = 1

    def __init__(self, base_storage: str, max_concurrency: int):
        self._base_storage = base_storage
        self._semaphore = asyncio.Semaphore(max_concurrency)

    async def download_git_repo(self, link: str, uuid: UUID):
        if not self.is_ok():
            raise ServiceNoStorageError
        destination = f"{self._base_storage}/{uuid}"
        logger.info(f"Cloning to {destination}...")
        async with self._semaphore:
            # noinspection PyTypeChecker
            await asyncio.to_thread(
                Repo.clone_from, url=link, to_path=destination, depth=self.CLONE_DEPTH
            )

    async def store_files(
        self,
        uuid: UUID,
        files: list[UploadFile],
    ):
        if not self.is_ok():
            raise ServiceNoStorageError
        base_dir = Path(f"{self._base_storage}/{uuid}")
        base_dir.mkdir(parents=True, exist_ok=True)
        for file in files:
            async with self._semaphore:
                async with aiofiles.open(
                    f"{base_dir}/{file.filename}", "wb"
                ) as out_file:
                    while content := await file.read(self.CHUNK_SIZE):  # Read chunks
                        await out_file.write(content)  # Write chunks

    def is_ok(self) -> bool:
        """
        Checks if the base storage exists and has >500MB free space.
        """
        if not os.path.exists(self._base_storage):
            return False

        usage = shutil.disk_usage(self._base_storage)
        if usage.free < self.MIN_FREE_SPACE_BYTES:
            return False

        return True


def create_storage_from_env():
    base_storage = get_var("XP_WEBSERVER_STORAGE")
    max_concurrency = int(get_var("XP_WEBSERVER_MAX_STORAGE_CONCURRENCY"))
    return StorageService(base_storage, max_concurrency)
