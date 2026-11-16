## AI-AGENT

## Descrição

API para geração de documentos de requisitos de software a partir de
um contexto informado pelo usuário e de documentos de apoio recuperados
de uma base de conhecimento.

A aplicação utiliza um modelo local via Ollama, organiza o resultado
em dados estruturados e gera um arquivo DOCX, com possibilidade de
utilizar um template.

## Fluxo de geração de documentos

1. O usuário envia título e contexto para a API.
2. A aplicação gera o embedding do contexto e busca trechos semelhantes
   na base de conhecimento, considerando os tipos de fonte configurados.
3. O contexto do usuário e os trechos recuperados são incorporados
   ao prompt de geração.
4. O modelo local retorna o conteúdo em JSON.
5. A aplicação interpreta o JSON e valida sua estrutura com Pydantic.
6. O conteúdo é utilizado para gerar um DOCX, com ou sem template.
7. Os metadados, o conteúdo estruturado e o caminho do arquivo
   são persistidos no PostgreSQL.
8. A API retorna o identificador, o conteúdo e a URL para download.

A validação com Pydantic verifica a estrutura dos dados.

A seleção de contexto e a revisão por IA foram experimentadas,
mas estão desativadas no fluxo atual.

## Como executar

### Pré-requisitos

- Python instalado
- Git
- Docker Desktop em execução
- Ollama instalado e em execução

### 1. Clonar o repositório

```powershell
git clone https://github.com/caeo/ai-agent.git
cd ai-agent
```

### 2. Criar e ativar o ambiente virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar as dependências

```powershell
python -m pip install -r requirements.txt
```

### 4. Configurar as variáveis de ambiente

Copie o arquivo de exemplo:

```powershell
Copy-Item .env.example .env
```

Edite o `.env` com as configurações locais.

- `POSTGRES_DB`: nome do banco.
- `POSTGRES_USER`: usuário do banco.
- `POSTGRES_PASSWORD`: senha do banco.
- `POSTGRES_PORT`: porta disponibilizada no computador.
- `DATABASE_URL`: conexão utilizada pela aplicação e pelas migrations.
- `ACTIVE_TEMPLATE_PATH`: caminho do template DOCX.

Os dados da `DATABASE_URL` devem corresponder às variáveis do PostgreSQL.
Como a API é executada fora do Docker, utilize `127.0.0.1` e a porta
definida em `POSTGRES_PORT`.

Para utilizar um template, coloque o arquivo no caminho configurado.
Para gerar sem template, deixe `ACTIVE_TEMPLATE_PATH` vazio.

### 5. Iniciar o PostgreSQL com pgvector

Na pasta que contém o arquivo do Docker Compose:

```powershell
docker compose up -d
```

Os dados do banco são mantidos no volume `postgres_data`.

### 6. Aplicar as migrations

Com o banco disponível, execute na raiz do projeto:

```powershell
alembic upgrade head
```

### 7. Preparar os modelos locais

Com o Ollama em execução, baixe os modelos utilizados:

```powershell
ollama pull qwen3:4b-instruct
ollama pull qwen3-embedding:0.6b
```

- `qwen3:4b-instruct`: geração dos documentos.
- `qwen3-embedding:0.6b`: embeddings para recuperação de contexto.

A aplicação espera encontrar o Ollama em `http://localhost:11434`.
O tempo de geração depende dos recursos disponíveis no computador.

### 8. Iniciar a API

Execute na raiz do projeto, com o ambiente virtual ativado:

```powershell
python -m uvicorn app.main:app --reload
```

### 9. Acessar a documentação interativa

Abra no navegador:

http://localhost:8000/docs

Use `POST /documents` para gerar um documento e `GET /documents`
para consultar a listagem dos documentos salvos.

## Funcionalidades atuais

- Geração de objetivo, requisitos funcionais, requisitos não funcionais
  e restrições técnicas.
- Recuperação de trechos da base de conhecimento por similaridade.
- Cadastro de fontes com classificação e descrição de aplicabilidade.
- Geração de DOCX com ou sem template.
- Configuração do caminho do template por variável de ambiente.
- Persistência dos documentos e de seu conteúdo estruturado no PostgreSQL.
- Listagem resumida dos documentos, com os mais recentes primeiro.
- Consulta de documento por identificador.
- Download do arquivo DOCX.

Os documentos gerados são rascunhos e precisam de revisão humana,
pois o modelo pode omitir informações ou interpretar incorretamente
o contexto e as fontes recuperadas.

## Arquitetura

A aplicação utiliza uma arquitetura em camadas:

- **Routes:** recebe requisições HTTP e retorna respostas.
- **Services:** coordena os serviços da aplicação.
- **Repositories:** concentra o acesso aos dados.
- **Schemas:** validação de entrada e saída dos dados.
- **Models:** entidades do banco de dados.
- **Renderers:** gera os documentos documentos.
- **Prompts:** instruções enviadas ao modelo de IA.

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

| Caminho | Responsabilidade |
| ------- | ---------------- |
| `alembic/` | Migrations do banco de dados |
| `app/api/routes/` | Endpoints da API |
| `app/core/` | Configurações, enums e exceções |
| `app/db/` | Conexão, base e modelos do banco |
| `app/prompts/` | Instruções enviadas ao modelo de IA |
| `app/renderers/` | Geração e preenchimento de arquivos DOCX |
| `app/repositories/` | Acesso aos dados persistidos |
| `app/schemas/` | Estruturas de entrada e saída com Pydantic |
| `app/services/` | Serviços da aplicação |
| `app/main.py` | Inicialização da API |
| `experiments/` | Experimentos fora do fluxo principal |
| `generated_documents/` | Documentos gerados |
| `tests/` | Testes automatizados |
| `uploads/` | Arquivos enviados à aplicação |
| `.env.example` | Exemplo das variáveis de ambiente |
| `docker-compose.yml` | Configuração do container PostgreSQL com pgvector |
| `alembic.ini` | Configuração do Alembic |
| `requirements.txt` | Dependências Python |

## Endpoints



| Método | Endpoint | Função |
| ------ | -------- | ------ |
| GET | /health | Verifica o estado da API |
| POST | /documents | Gera e persiste um documento |
| GET | /documents | Lista documentos, dos mais recentes para os mais antigos |
| GET | /documents/{id} | Consulta um documento pelo UUID |
| GET | /documents/{id}/download | Faz o download do DOCX |
| POST | /source-documents | Envia um DOCX como fonte de conhecimento ou template |

### Upload de fontes

O endpoint POST /source-documents recebe multipart/form-data.
No Swagger, utilize “Try it out” para selecionar o arquivo e preencher
os campos.

| Campo | Descrição |
| ----- | --------- |
| file | Arquivo DOCX obrigatório, não vazio e com texto extraível |
| source_type | Tipo da fonte; o padrão é knowledge |
| knowledge_role | Papel do conhecimento: norm, guideline ou example |
| applicability | Descrição de quando o conhecimento se aplica, com até 1000 caracteres |

Para fontes do tipo knowledge, knowledge_role e applicability
são obrigatórios.

Para templates, não envie knowledge_role nem applicability.
O upload de um template não o torna automaticamente ativo:
o arquivo utilizado na geração é definido por ACTIVE_TEMPLATE_PATH.

Os papéis de conhecimento são:

- norm: exigências aplicáveis à demanda.
- guideline: orientações de redação e organização.
- example: exemplos de referência.

Atualmente, a recuperação para geração utiliza norm e guideline.
Fontes example podem ser cadastradas, mas não participam desse fluxo.

## Roadmap

### Implementado

- [x] API com FastAPI
- [x] Integração com modelo local via Ollama
- [x] Geração de conteúdo em JSON e validação estrutural com Pydantic
- [x] Geração de documentos de requisitos em DOCX
- [x] Preenchimento de template DOCX
- [x] Configuração do caminho do template por variável de ambiente
- [x] Persistência com PostgreSQL
- [x] Migrations com Alembic
- [x] Cadastro de documentos como fontes de conhecimento
- [x] Metadados de classificação e aplicabilidade das fontes
- [x] Recuperação de contexto com embeddings e pgvector
- [x] Uso de fontes norm e guideline na recuperação para geração
- [x] Consulta de documentos por UUID
- [x] Listagem resumida dos documentos, dos mais recentes aos mais antigos
- [x] Download de documentos DOCX
- [x] Testes iniciais da API

### Experimentos desativados

- Seleção de contexto por IA antes da geração
- Revisão do documento por IA após a geração
- Uso de fontes example na recuperação para geração

Esses recursos precisam de avaliação antes de serem incorporados
ao fluxo principal.

### Após a primeira entrega

- [ ] Expandir os testes automatizados
- [ ] Ampliar o tratamento de erros
- [ ] Melhorar a qualidade e a completude dos documentos gerados
- [ ] Desenvolver a interface de utilização
- [ ] Avaliar suporte a novos tipos de documentos
- [ ] Avaliar geração de PDF
- [ ] Avaliar uma biblioteca de prompts