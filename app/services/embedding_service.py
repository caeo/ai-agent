import httpx


class EmbeddingService:
    def embed(self, text: str) -> list[float]:

        response = httpx.post(
            "http://localhost:11434/api/embed",
            json={"model": "qwen3-embedding:0.6b", "input": text},
            timeout=300,
        )

        response.raise_for_status()

        data = response.json()

        return data["embeddings"][0]
