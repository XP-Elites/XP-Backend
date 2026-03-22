from unittest.mock import patch, AsyncMock
from uuid import UUID

def test_upload_git_success(client):
    with patch("upload_file.git_service.get_github_size", new_callable=AsyncMock) as mock_size:
        mock_size.return_value = 10 * 1024  # Under 100MB limit

        response = client.post(
            "/upload/file_link/git",
            json={"git_link": "https://github.com/user/repo"}
        )

        assert response.status_code == 200
        uuid = UUID(response.json())


def test_upload_git_repo_too_large(client):
    with patch("upload_file.git_service.get_github_size", new_callable=AsyncMock) as mock_size:
        mock_size.return_value = 200 * 1024  # Over 100MB limit

        response = client.post(
            "/upload/file_link/git",
            json={"git_link": "https://github.com/user/huge-repo"}
        )

        assert response.status_code == 413
        assert "exceeds maximum" in response.json()["detail"]

def test_upload_git_invalid_link(client):
    response = client.post(
        "/upload/file_link/git",
        json={"git_link": "https://test.com/"}
    )

    assert response.status_code == 400
