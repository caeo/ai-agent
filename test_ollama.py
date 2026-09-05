import httpx

response = httpx.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "qwen3:1.7b",
        "prompt": "Responda em português e em 5 linhas, organize esses requisitos: login, cadastro de clientes, relatórios",
        "stream": False,
    },
    timeout=300,
)

data = response.json()

generated_text = data["response"]

print(response.status_code)
print(generated_text)
