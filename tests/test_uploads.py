from unittest.mock import patch, AsyncMock
from uuid import UUID


def test_upload_link_success(client):
    with patch("upload_file.GitService.get_github_size", new_callable=AsyncMock) as mock_size:
        mock_size.return_value = 10 * 1024 * 1024  # 10MB (under 100MB limit)
        
        response = client.post(
            "/upload/file_link/git",
            json={"git_link": "https://github.com/user/repo"}
        )
        
        assert response.status_code == 200
        uuid = UUID(response.json())
        assert uuid is not None


def test_upload_link_repo_too_large(client):
    with patch("upload_file.GitService.get_github_size", new_callable=AsyncMock) as mock_size:
        mock_size.return_value = 200 * 1024 * 1024  # 200MB (over 100MB limit)

        response = client.post(
            "/upload/file_link/git",
            json={"git_link": "https://github.com/user/huge-repo"}
        )

        assert response.status_code == 413
        assert "exceeds maximum" in response.json()["detail"]

def test_upload_file_success(client):
    response = client.post(
        "/upload/files",
        files=[("files", ("test.txt", b"test content", "text/plain"))]
    )
    
    assert response.status_code == 200
    uuid = UUID(response.json())
    assert uuid is not None
