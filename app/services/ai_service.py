import hashlib

import httpx


class AIService:
    def generate(self, prompt: str) -> str:

        # print("===== PROMPT ENVIADO =====")
        # print(prompt, flush=True)
        # print("=========================")

        # prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        # print("Hash do prompt:", prompt_hash, flush=True)

        response = httpx.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen3:1.7b",
                "prompt": prompt,
                "stream": False,
                # temperature controla a variação na escolha do próximo token
                "options": {"num_ctx": 8192, "temperature": 0},
            },
            timeout=300,
        )

        data = response.json()

        input_tokens = data.get("prompt_eval_count")
        output_tokens = data.get("eval_count")

        print("===== USO DE TOKENS =====")
        print("Janela configurada: 8192")
        print(f"Tokens de entrada: {input_tokens}")
        print(f"Tokens gerados: {output_tokens}")
        print(f"Motivo do encerramento: {data.get('done_reason')}")

        if input_tokens is not None and output_tokens is not None:
            total_tokens = input_tokens + output_tokens

            print(f"Entrada + geração: {total_tokens}")
            print("Relação com a janela configurada: " f"{total_tokens / 8192:.1%}")

        print("========================")

        # generated_text = data["response"]

        return data["response"]
