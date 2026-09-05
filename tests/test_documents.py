from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_document():
    response = client.post("/documents", json={"title": "teste", "context": "teste"})
    assert response.status_code == 200
    assert response.json() == {
        "title": "teste",
        "content": "teste",
        "status": "generated",
    }


def test_create_document_without_context():
    response = client.post("/documents", json={"title": "teste"})
    assert response.status_code == 422
