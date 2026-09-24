## AI-AGENT

## Descrição

Api para geração de documentos padronizados baseado em context e informações prévias com um agente de inteligência artificial. É também uma biblioteca de prompts que os usuários possam ter acesso e sugerir atualizações no prompt de acordo com as suas necessidades. O projeto está sendo desenvolvido com foco no aprendizado de arquitetura de backend, integração com LLMs, persistência de dados e RAG.

## Como executar

1. git clone https://github.com/caeo/ai-agent.git
2. cd ai-agent/
3. Criar o ambiente virtual - python -m venv .venv
4. Ativar o ambiente virtual - ./.venv/Scripts/Activate.ps1
5. Para instalar as dependências - pip install -r requirements.txt
6. Iniciar o servidor - uvicorn app.main:app --reload
7. Ir para http://localhost:8000/docs#/

## Funcionalidades atuais

O agente recebe um contexto fornecido pelo usuário, conecta com o modelo de LLM atual e depois gera documentos estruturados com as informações providas no contexto

## Arquitetura

A aplicação utiliza uma arquitetura em camadas:

- **Routes:** recebe requisições HTTP e retorna respostas.
- **Services:** coordena os serviços da aplicação.
- **Repositories:** concentra o acesso aos dados.
- **Schemas:** validação de entrada e saída dos dados.
- **Models:** entidades do banco de dados.
- **Renderers:** gera os documentos documentos.
- **Prompts:** instruções enviadas ao modelo de IA.

## Fluxo de geração de documentos

1. O usuário envia título e contexto para a API.
2. O contexto é incorporado a um prompt especializado.
3. O modelo local processa o conteúdo.
4. A saída JSON é validada utilizando Pydantic.
5. A aplicação gera um documento DOCX.
6. Os metadados e o conteúdo estruturado são persistidos no PostgreSQL.
7. A API retorna o identificador e a URL para download.

## Tecnologias

- Python 3.12
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- Alembic
- Docker
- Ollama
- Qwen
- python-docx
- Pytest

## Estrutura do projeto

## Endpoints

| Método | Endpoint                   | Função                          |
| ------ | -------------------------- | ------------------------------- |
| `GET`  | `/health`                  | Verifica o estado da API        |
| `POST` | `/documents`               | Gera e persiste um documento    |
| `GET`  | `/documents/{id}`          | Consulta um documento pelo UUID |
| `GET`  | `/documents/{id}/download` | Faz o download do DOCX          |

## Roadmap

### Concluído

- [x] API inicial com FastAPI
- [x] Integração com modelo local via Ollama
- [x] Saída estruturada da LLM
- [x] Geração de documentos DOCX
- [x] Persistência com PostgreSQL
- [x] Migrations com Alembic
- [x] Consulta de documentos por UUID
- [x] Download de documentos
- [x] Testes iniciais com mock da LLM

### Próximas etapas

- [ ] Suportar novos tipos de documentos
- [ ] Implementar RAG
- [ ] Permitir utilização de documentos como fontes de contexto
- [ ] Expandir testes automatizados
- [ ] Melhorar tratamento de erros
- [ ] Adicionar geração de PDF


## Escolhas

### PGVECTOR

- O pgvector foi escolhido por ser uma extensão do PostgreSQL, que já está sendo utilizado. Ele permite armazenar vectors e permite fazer buscas por similaridade, que é justamente o que RAG(Retrieval-Augmented Generation) faz.