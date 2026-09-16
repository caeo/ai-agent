from app.main import app

from unittest.mock import patch

from fastapi.testclient import TestClient

client = TestClient(app)


def test_create_document():

    with patch("app.services.document_service.AIService.generate") as mock_generate:
        mock_generate.return_value = """
        {
            "functional_requirements": [
                {
                "id": "RF01",
                "description": "descrição"
                }
            ],
            "non_functional_requirements": [
                {
                "id": "RNF01",
                "description": "descrição"
                }
            ],
            "technical_restrictions": [
                {
                "id": "RT01",
                "description": "descrição"
                }
            ]
        }
        
        """

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
        assert "id" in data["content"]["functional_requirements"][0]
        assert "description" in data["content"]["functional_requirements"][0]

        assert "non_functional_requirements" in data["content"]
        assert "id" in data["content"]["non_functional_requirements"][0]
        assert "description" in data["content"]["non_functional_requirements"][0]

        assert "technical_restrictions" in data["content"]
        assert "id" in data["content"]["technical_restrictions"][0]
        assert "description" in data["content"]["technical_restrictions"][0]

        assert len(data["content"]["functional_requirements"]) == 1
        assert (
            data["content"]["functional_requirements"][0]["description"] == "descrição"
        )

        assert len(data["content"]["non_functional_requirements"]) == 1
        assert (
            data["content"]["non_functional_requirements"][0]["description"]
            == "descrição"
        )

        assert len(data["content"]["technical_restrictions"]) == 1
        assert (
            data["content"]["technical_restrictions"][0]["description"] == "descrição"
        )


def test_create_document_without_context():
    response = client.post("/documents", json={"title": "teste"})
    assert response.status_code == 422
