from fastapi.testclient import TestClient
from app.main import app, store

client = TestClient(app)


def setup_function():
    with store._connect() as connection:
        connection.execute("DELETE FROM chunks")
        connection.execute("DELETE FROM documents")
    store.documents.clear()
    store.retriever.replace([])
    with store._connect() as connection:
        connection.execute("DELETE FROM users")


def test_upload_and_query():
    auth = client.post("/api/auth/register", json={"email": "test@example.com", "password": "secure-pass-123"}).json()
    headers = {"Authorization": f"Bearer {auth['token']}"}
    response = client.post("/api/documents/upload", files={"file": ("handbook.txt", b"Remote work is available three days per week. Team leads approve exceptions.", "text/plain")}, headers=headers)
    assert response.status_code == 200
    response = client.post("/api/query", json={"question": "How often is remote work available?"}, headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert "three days" in body["answer"]
    assert body["citations"][0]["document"] == "handbook.txt"


def test_documents_survive_store_reload():
    store.add_text("persistent.txt", "The incident response owner is the platform team.", 52)
    from app.store import DocumentStore
    reloaded = DocumentStore()
    assert reloaded.list_documents()[0]["name"] == "persistent.txt"
    assert reloaded.search("Who owns incident response?", 1)[0].chunk.document == "persistent.txt"
