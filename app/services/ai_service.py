import httpx


class AIService:
    def generate(self, prompt: str) -> str:

        response = httpx.post(
            "http://localhost:11434/api/generate",
            json={"model": "qwen3:1.7b", "prompt": prompt, "stream": False},
            timeout=300,
        )

        data = response.json()

        # generated_text = data["response"]

        return data["response"]
