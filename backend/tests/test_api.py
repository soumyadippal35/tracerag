from fastapi.testclient import TestClient
from app.main import app, store

client = TestClient(app)


def setup_function():
    with store._connect() as connection:
        connection.execute("DELETE FROM chunks")
        connection.execute("DELETE FROM documents")
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


def test_documents_survive_store_reload():
    store.add_text("persistent.txt", "The incident response owner is the platform team.", 52)
    from app.store import DocumentStore
    reloaded = DocumentStore()
    assert reloaded.list_documents()[0]["name"] == "persistent.txt"
    assert reloaded.search("Who owns incident response?", 1)[0].chunk.document == "persistent.txt"
