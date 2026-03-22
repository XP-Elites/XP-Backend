from uuid import UUID

def test_upload_file_success(client):
    response = client.post(
        "/upload/files",
        files=[("files", ("test.txt", b"test content", "text/plain"))]
    )

    assert response.status_code == 200


def test_upload_files_storage(storage_client):
    client, tmp_path = storage_client

    response = client.post(
        "/upload/files",
        files=[("files", ("hello.txt", b"hello world", "text/plain"))]
    )

    assert response.status_code == 200
    uuid = UUID(response.json())

    uploaded_file = tmp_path / str(uuid) / "hello.txt"
    assert uploaded_file.exists(), f"Expected file not found: {uploaded_file}"
    assert uploaded_file.read_bytes() == b"hello world"


def test_upload_multiple_files_storage(storage_client):
    client, tmp_path = storage_client

    response = client.post(
        "/upload/files",
        files=[
            ("files", ("a.txt", b"file a content", "text/plain")),
            ("files", ("b.txt", b"file b content", "text/plain")),
        ]
    )

    assert response.status_code == 200
    uuid = UUID(response.json())

    job_dir = tmp_path / str(uuid)
    assert (job_dir / "a.txt").read_bytes() == b"file a content"
    assert (job_dir / "b.txt").read_bytes() == b"file b content"