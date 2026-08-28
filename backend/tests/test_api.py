from fastapi.testclient import TestClient
from app.main import app, store

client = TestClient(app)


def setup_function():
    store.documents.clear()
    store.retriever.replace([])


def test_upload_and_query():
    response = client.post("/api/documents/upload", files={"file": ("handbook.txt", b"Remote work is available three days per week. Team leads approve exceptions.", "text/plain")})
    assert response.status_code == 200
    response = client.post("/api/query", json={"question": "How often is remote work available?"})
    assert response.status_code == 200
    body = response.json()
    assert "three days" in body["answer"]
    assert body["citations"][0]["document"] == "handbook.txt"
