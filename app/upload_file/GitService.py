import logging
from uuid import UUID

import httpx
import requests
import tldextract
import re

from fastapi import Depends, BackgroundTasks

from core import get_logger, get_storage_service
from urllib.parse import urlparse, quote

from core.lifespan import get_job_status_service
from core.storage_service import StorageService

from status_tracker import JobStatusService

logger = get_logger(__name__, logging.DEBUG)

GITHUB_BASE = "https://api.github.com"
SIZE_PATH = "repos/{owner}/{repo_name}"

USERNAME_REGEX = r"(?!.*--)^[A-Za-z0-9][A-Za-z0-9-]{0,37}[A-Za-z0-9]$"
REPO_REGEX = "[A-Za-z0-9\.\-_]{1,100}"

session = requests.Session()


class RepoTooLargeException(Exception):
    pass


async def get_github_size(path: str) -> int:
    """
    :param path: GitHub repo path, in the format /{username}/{repo}/
    :return: int: The size of the repo, in kilobytes. See https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#get-a-repository
    """
    parts = path.removeprefix("/").removesuffix("/").split("/", 1)
    if len(parts) != 2:
        raise ValueError("Invalid path")

    username, repo = parts

    if re.fullmatch(USERNAME_REGEX, username, re.NOFLAG) is None:
        raise ValueError("Invalid username")
    if re.fullmatch(REPO_REGEX, repo, re.NOFLAG) is None:
        raise ValueError("Invalid repo name")
    url = f"{GITHUB_BASE}/{SIZE_PATH.format(owner=quote(username, ''),repo_name=quote(repo.removesuffix('.git'), ''))}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url, timeout=5
            )  # Quoted to prevent URL injection
            response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"GitHub request failed: {e}")
    data = response.json()
    if "size" not in data:
        raise RuntimeError(f"GitHub request returned invalid data")
    return int(data["size"])


class GitService:

    def __init__(
        self,
        background_tasks: BackgroundTasks,
        storage_service: StorageService,
        status_service: JobStatusService,
    ):
        self._background_tasks = background_tasks
        self._storage_service = storage_service
        self._status_service = status_service

    async def get_repo_size(self, link: str) -> int:
        extracted = tldextract.extract(link)
        match extracted.domain:
            case "github":
                repo_path = urlparse(link).path
                return await get_github_size(repo_path)
            case _:
                raise NotImplementedError(
                    "Support for this provider has not been implemented yet."
                )

    async def validate_repo(
        self,
        link: str,
    ):
        size = await self.get_repo_size(link)
        if size > 1024 * 1024 * 100:  # 100MB
            raise RepoTooLargeException(
                "Repository exceeds maximum supported size (100mb)"
            )

    async def download_repo(self, link: str, uuid: UUID):
        await self._storage_service.download_git_repo(link, uuid)
        await self._status_service.send_job(uuid)

    async def process_repo(self, link: str):
        uuid = await self._status_service.init_status()
        self._background_tasks.add_task(self.download_repo, link, uuid)


def get_git_service(
    background_tasks: BackgroundTasks,
    storage_service: StorageService = Depends(get_storage_service),
    status_service: JobStatusService = Depends(get_job_status_service),
) -> GitService:
    return GitService(
        background_tasks=background_tasks,
        storage_service=storage_service,
        status_service=status_service,
    )
