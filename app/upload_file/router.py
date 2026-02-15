from fastapi import (
    APIRouter,
    UploadFile,
    Depends,
    status,
    HTTPException,
)
from pydantic import BaseModel
from .FileUploadService import FileUploadService, get_file_upload_service
from .GitService import RepoTooLargeException, get_git_service, GitService

upload_router = APIRouter(prefix="/upload")


class GitRequest(BaseModel):
    git_link: str


@upload_router.post("/files")
async def create_upload_files(
    files: list[UploadFile],
    file_upload_service: FileUploadService = Depends(get_file_upload_service),
):
    uuid = await file_upload_service.process_files(files)
    return uuid


@upload_router.post("/file_link/git")
async def github_upload_files(
    body: GitRequest,
    git_service: GitService = Depends(get_git_service),
):
    link = body.git_link
    try:
        await git_service.validate_repo(link)
    except RepoTooLargeException as e:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE, detail=str(e)
        )
    uuid = await git_service.process_repo(link)
    return uuid
