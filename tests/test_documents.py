from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_document():
    response = client.post(
        "/documents",
        json={
            "title": "teste",
            "context": (
                "O sistema deve possuir sistema de login e agendamento "
                "e responder em no máximo 1 segundo"
            ),
        },
    )
    data = response.json()

    assert response.status_code == 200
    assert data["title"] == "teste"
    assert data["status"] == "generated"

    assert "content" in data
    assert "functional_requirements" in data["content"]
    assert "non_functional_requirements" in data["content"]

    assert len(data["content"]["functional_requirements"]) == 2
    assert len(data["content"]["non_functional_requirements"]) == 1


def test_create_document_without_context():
    response = client.post("/documents", json={"title": "teste"})
    assert response.status_code == 422
