import asyncio
import json
import logging
import os
import shutil
from pathlib import Path, PurePosixPath
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

    async def get_results_file(self, uuid: UUID) -> dict | None:
        results_path = Path(self._base_storage) / str(uuid) / "results.json"
        if results_path.exists():
            with open(results_path, "r") as results_file:
                results = json.load(results_file)
                return results
        return None

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
            # Browser folder uploads use webkitRelativePath; keep nested structure safely.
            normalized_name = file.filename.replace("\\", "/")
            rel_path = PurePosixPath(normalized_name)

            # Prevent path traversal or absolute writes outside the job directory.
            if rel_path.is_absolute() or any(part == ".." for part in rel_path.parts):
                target_path = base_dir / rel_path.name
            else:
                target_path = base_dir.joinpath(*rel_path.parts)

            target_path.parent.mkdir(parents=True, exist_ok=True)
            async with self._semaphore:
                async with aiofiles.open(str(target_path), "wb") as out_file:
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
