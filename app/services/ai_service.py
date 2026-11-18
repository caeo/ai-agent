import httpx

from app.core.exceptions import AIServiceUnavailableError
from app.core.config import OLLAMA_BASE_URL


class AIService:
    def generate(self, prompt: str) -> str:
        context_window = 8192

        # print("===== PROMPT ENVIADO =====")
        # print(prompt, flush=True)
        # print("=========================")

        try:
            response = httpx.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": "qwen3:1.7b",
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    # temperature controla a variação na escolha do próximo token
                    "options": {"num_ctx": context_window, "temperature": 0},
                },
                timeout=300,
            )

        except httpx.ConnectError as error:
            raise AIServiceUnavailableError(
                "Não foi possível conectar ao serviço de IA."
            ) from error

        response.raise_for_status()

        data = response.json()

        input_tokens = data.get("prompt_eval_count")
        output_tokens = data.get("eval_count")

        print("===== USO DE TOKENS =====")
        print(f"Janela configurada: {context_window}")
        print(f"Tokens de entrada: {input_tokens}")
        print(f"Tokens gerados: {output_tokens}")
        print(f"Motivo do encerramento: {data.get('done_reason')}")

        if input_tokens is not None and output_tokens is not None:
            total_tokens = input_tokens + output_tokens

            print(f"Entrada + geração: {total_tokens}")
            print(
                "Relação com a janela configurada: "
                f"{total_tokens / context_window:.1%}"
            )

        print("========================")

        return data["response"]
