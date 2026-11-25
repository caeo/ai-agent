# AI-Agent

API para geração de documentos de requisitos de software a partir de um contexto informado pelo usuário e de documentos de apoio recuperados de uma base de conhecimento.

A aplicação utiliza um modelo local via Ollama, retorna conteúdo estruturado e gera arquivos DOCX, com possibilidade de preencher um template.

## Estado atual

- API FastAPI, PostgreSQL com pgvector e Ollama executados em containers pelo Docker Compose.
- Modelo de geração `qwen3:1.7b`, com janela configurada de 8192 tokens.
- Modelo de embeddings `qwen3-embedding:0.6b`.
- Geração, persistência, listagem, consulta e download de documentos implementados.
- Recuperação de conhecimento com embeddings e busca por similaridade.
- Seleção de contexto e revisão por IA experimentadas, mas desativadas no fluxo principal.
- Exportação disponível somente em DOCX.

A implantação no servidor, a execução de `alembic upgrade head`, a geração de documentos e o funcionamento dos endpoints foram validados manualmente pelo responsável pelo projeto. Repositório do projeto: [caeo/ai-agent](https://github.com/caeo/ai-agent).

## Fluxo de geração

1. O usuário envia título e contexto para a API.
2. A aplicação gera o embedding do contexto e busca trechos semelhantes na base, considerando os papéis de conhecimento configurados.
3. O contexto do usuário e os trechos recuperados são incorporados ao prompt.
4. O modelo local retorna o conteúdo em JSON.
5. A aplicação interpreta o JSON e valida sua estrutura com Pydantic.
6. O conteúdo é utilizado para gerar um DOCX, com ou sem template.
7. Os metadados, o conteúdo estruturado e o caminho do arquivo são persistidos no PostgreSQL.
8. A API retorna o identificador, o conteúdo e a URL para download.

A validação com Pydantic verifica a estrutura dos dados. Os documentos gerados são rascunhos e precisam de revisão humana: o modelo pode omitir informações ou interpretar incorretamente a demanda e as fontes.

## Como executar com Docker Compose

### Pré-requisitos

- Git.
- Docker e Docker Compose disponíveis no computador ou servidor.
- Docker Desktop com containers Linux, caso utilize Windows.
- Recursos de CPU e memória suficientes para executar os modelos.
- Acesso à internet na primeira instalação para obter imagens, dependências e modelos.

API, banco e Ollama executam em containers. Python, ambiente virtual e Ollama instalados diretamente no host não são necessários para esse fluxo.

### 1. Clonar o repositório

```bash
git clone --branch develop https://github.com/caeo/ai-agent.git
cd ai-agent
```

Execute os próximos comandos na raiz do projeto.

### 2. Configurar as variáveis de ambiente

No Linux:

```bash
cp .env.example .env
```

No PowerShell:

```powershell
Copy-Item .env.example .env
```

Edite o `.env`. Exemplo:

```dotenv
POSTGRES_DB=ai_agent
POSTGRES_USER=seu_usuario
POSTGRES_PASSWORD=sua_senha
POSTGRES_PORT=55432

DATABASE_URL=postgresql+psycopg2://seu_usuario:sua_senha@127.0.0.1:55432/ai_agent
ACTIVE_TEMPLATE_PATH=
```

| Variável | Finalidade |
| --- | --- |
| `POSTGRES_DB` | Nome do banco |
| `POSTGRES_USER` | Usuário do PostgreSQL |
| `POSTGRES_PASSWORD` | Senha do PostgreSQL |
| `POSTGRES_PORT` | Porta do banco disponibilizada no host |
| `DATABASE_URL` | Conexão utilizada caso a aplicação ou o Alembic sejam executados fora do Docker |
| `ACTIVE_TEMPLATE_PATH` | Caminho do template DOCX; vazio para gerar sem template |

O Compose monta a conexão interna da API com as variáveis do PostgreSQL e sobrescreve `DATABASE_URL` para utilizar `postgres:5432`. Também define `OLLAMA_BASE_URL=http://ollama:11434` dentro da API.

Assim, não é necessário configurar o endereço do Ollama no `.env` para executar pelo Compose. Os serviços se comunicam pelos nomes `postgres` e `ollama` na rede interna.

As credenciais interpoladas na URL de conexão devem ser compatíveis com esse formato; caracteres reservados de URL exigem codificação adequada. O `.env` contém configurações locais e não deve ser versionado.

### 3. Preparar o template, se utilizado

Para gerar com template, coloque um DOCX compatível com o renderer na pasta `uploads` e configure seu caminho relativo:

```dotenv
ACTIVE_TEMPLATE_PATH=uploads/template_requisitos_mvp.docx
```

O arquivo precisa existir nesse caminho. O upload pode salvar o arquivo com um nome diferente do original; configure o caminho do arquivo efetivamente salvo.

Um caminho configurado para um arquivo inexistente não ativa automaticamente o renderer sem template. Para gerar sem template, deixe `ACTIVE_TEMPLATE_PATH` vazio. O `.env.example` atual contém um caminho de exemplo que deve ser ajustado ou esvaziado na instalação.

### 4. Construir e iniciar os containers

```bash
docker compose config --quiet
docker compose up -d --build
docker compose ps
```

O Compose inicia três serviços:

| Serviço | Função |
| --- | --- |
| `api` | Executa a API FastAPI na porta 8000 |
| `postgres` | Executa PostgreSQL 16 com pgvector |
| `ollama` | Executa os modelos de geração e embeddings |

A porta 8000 do host deve estar disponível. O Compose atual não configura acesso à GPU; o desempenho depende dos recursos de CPU e memória disponíveis ao container.

### 5. Baixar os modelos no container do Ollama

Com o serviço `ollama` em execução:

```bash
docker compose exec ollama ollama pull qwen3:1.7b
docker compose exec ollama ollama pull qwen3-embedding:0.6b
```

Confira os modelos disponíveis:

```bash
docker compose exec ollama ollama list
```

Os downloads ficam no volume `ollama_data` e são preservados ao recriar o container. Baixar um modelo no Ollama instalado no host não o disponibiliza automaticamente neste volume.

Os nomes dos modelos estão definidos em `AIService` e `EmbeddingService`. O serviço de geração utiliza `temperature=0` e `num_ctx=8192`.

### 6. Aplicar as migrations

Com o banco disponível e o container da API em execução:

```bash
docker compose exec api alembic upgrade head
```

Execute esse comando na primeira instalação e quando novas migrations forem adicionadas, antes de utilizar os endpoints que acessam o banco.

A migration de criação dos chunks habilita a extensão `vector` antes de criar a coluna de embeddings. Os chunks possuem chave estrangeira para `source_documents`.

O início dos containers não aplica migrations automaticamente. O Compose atual não inclui uma espera automática pela prontidão do banco; se ele ainda estiver inicializando, aguarde sua disponibilidade e repita o comando.

### 7. Acessar a API

No mesmo computador em que os containers executam:

- Saúde: [http://localhost:8000/health](http://localhost:8000/health).
- Swagger: [http://localhost:8000/docs](http://localhost:8000/docs).

Para acessar a partir de outro computador, utilize o endereço do servidor na porta 8000, conforme as permissões de rede do ambiente. `localhost` sempre representa o computador de onde parte o acesso.

No Swagger, utilize `POST /documents` para gerar e `GET /documents` para listar documentos salvos.

Exemplo:

```json
{
  "title": "Sistema de Reserva de Salas",
  "context": "O sistema deve permitir cadastrar salas com nome e capacidade e reservar uma sala informando data, horário de início e horário de término. Uma sala não pode ter reservas com horários sobrepostos. A confirmação da reserva deve ser exibida em até 2 segundos. O banco de dados deve ser PostgreSQL."
}
```

## Comandos de uso diário

| Ação | Comando |
| --- | --- |
| Iniciar ou atualizar os containers conforme o Compose | `docker compose up -d` |
| Reconstruir e atualizar a API após alterar o código | `docker compose up -d --build api` |
| Verificar os containers do projeto | `docker compose ps` |
| Consultar os últimos logs da API | `docker compose logs --tail 80 api` |
| Acompanhar os logs da API | `docker compose logs -f api` |
| Parar os containers | `docker compose stop` |
| Iniciar containers já criados e parados | `docker compose start` |
| Aplicar migrations | `docker compose exec api alembic upgrade head` |

O código é copiado para a imagem durante a construção. A configuração atual não utiliza recarga automática: alterações no código exigem reconstruir a imagem e atualizar o container. Após mudar variáveis de ambiente, utilize `docker compose up -d api` para recriar o container quando necessário.

## Armazenamento e portas

| Recurso | Armazenamento |
| --- | --- |
| PostgreSQL | Volume nomeado `postgres_data` |
| Modelos do Ollama | Volume nomeado `ollama_data`, montado em `/root/.ollama` |
| Arquivos enviados e templates | Pasta local `uploads`, montada em `/app/uploads` |
| DOCX gerados | Pasta local `generated_documents`, montada em `/app/generated_documents` |

As pastas de arquivos são compartilhadas por bind mounts. Os arquivos e o volume do banco são preservados ao recriar o container. A remoção explícita dos volumes, como em `docker compose down -v`, apaga os volumes do banco e dos modelos do Ollama.

| Conexão | Endereço |
| --- | --- |
| Navegador no host → API | `localhost:8000` |
| Navegador em outra máquina → API | Endereço do servidor, porta 8000 |
| Ferramenta no host → banco | `127.0.0.1`, na porta definida em `POSTGRES_PORT` |
| API no container → banco | `postgres:5432` |
| API no container → Ollama | `ollama:11434` |

A porta do Ollama não é publicada no host pelo Compose atual. Os comandos de administração dos modelos são executados com `docker compose exec ollama ollama ...`.

## Endpoints

| Método | Endpoint | Função |
| --- | --- | --- |
| GET | `/health` | Verifica se a API responde |
| POST | `/documents` | Gera e persiste um documento |
| GET | `/documents` | Lista documentos, dos mais recentes para os mais antigos |
| GET | `/documents/{id}` | Consulta um documento pelo UUID |
| GET | `/documents/{id}/download` | Faz o download do DOCX |
| POST | `/source-documents` | Envia um DOCX como fonte de conhecimento ou template |

### Upload de fontes

`POST /source-documents` recebe `multipart/form-data`. No Swagger, utilize **Try it out** para selecionar o arquivo e preencher os campos.

| Campo | Descrição |
| --- | --- |
| `file` | DOCX obrigatório, não vazio e com texto extraível |
| `source_type` | Tipo da fonte; o padrão é `knowledge` |
| `knowledge_role` | Papel do conhecimento: `norm`, `guideline` ou `example` |
| `applicability` | Descrição de quando o conhecimento se aplica, com até 1000 caracteres |

Para fontes de conhecimento, `knowledge_role` e `applicability` são obrigatórios. Para templates, não envie esses metadados.

O upload de um template não o torna automaticamente ativo. O arquivo utilizado na geração é definido por `ACTIVE_TEMPLATE_PATH`.

Os papéis de conhecimento são:

- `norm`: exigências aplicáveis à demanda.
- `guideline`: orientações de redação e organização.
- `example`: exemplos de referência.

Atualmente, a recuperação para geração utiliza `norm` e `guideline`. Fontes `example` podem ser cadastradas, mas não participam desse fluxo.

## Arquitetura e estrutura

A aplicação utiliza uma arquitetura em camadas:

| Caminho | Responsabilidade |
| --- | --- |
| `app/api/routes/` | Receber requisições HTTP e retornar respostas |
| `app/core/` | Configurações, enums e exceções |
| `app/db/` | Conexão, base e modelos do banco |
| `app/prompts/` | Instruções enviadas ao modelo de IA |
| `app/renderers/` | Geração e preenchimento de arquivos DOCX |
| `app/repositories/` | Acesso aos dados persistidos |
| `app/schemas/` | Estruturas de entrada e saída com Pydantic |
| `app/services/` | Serviços e coordenação do fluxo da aplicação |
| `app/main.py` | Inicialização da API |
| `alembic/` | Migrations do banco |
| `experiments/` | Experimentos fora do fluxo principal |
| `tests/` | Testes automatizados |
| `uploads/` | Arquivos enviados e templates |
| `generated_documents/` | Documentos gerados |
| `Dockerfile` | Construção da imagem da API |
| `.dockerignore` | Arquivos excluídos do contexto de construção |
| `docker-compose.yml` | Serviços, conexões e montagens dos containers |
| `.env.example` | Exemplo das variáveis de ambiente |
| `alembic.ini` | Configuração do Alembic |
| `requirements.txt` | Dependências Python |

## Tecnologias

- Python 3.14 na imagem da API.
- FastAPI e Uvicorn.
- Pydantic.
- SQLAlchemy e Alembic.
- PostgreSQL 16 com pgvector.
- Docker e Docker Compose.
- Ollama e modelos Qwen.
- HTTPX.
- python-docx.
- Pytest para os testes iniciais existentes.

O pgvector permite armazenar embeddings e realizar buscas por similaridade no mesmo PostgreSQL utilizado pela aplicação.

## Roadmap

### Implementado

- [x] API com FastAPI.
- [x] Integração com modelo local via Ollama.
- [x] Geração em JSON e validação estrutural com Pydantic.
- [x] Geração de requisitos em DOCX, com ou sem template.
- [x] Configuração do caminho do template por variável de ambiente.
- [x] Persistência com PostgreSQL e migrations com Alembic.
- [x] Cadastro de fontes com classificação e aplicabilidade.
- [x] Recuperação de contexto com embeddings e pgvector.
- [x] Uso de fontes `norm` e `guideline` na geração.
- [x] Listagem, consulta por UUID e download dos documentos.
- [x] Testes iniciais da API.
- [x] API, banco e Ollama em containers pelo Docker Compose.
- [x] Implantação e validação manual dos endpoints no servidor.
- [x] Persistência dos modelos no volume `ollama_data`.
- [x] Endereço do Ollama configurável por variável de ambiente.
- [x] Montagem das pastas de uploads e documentos gerados.

### Experimentos desativados

- Seleção de contexto por IA antes da geração.
- Revisão do documento por IA após a geração.
- Uso de fontes `example` na recuperação para geração.

Esses recursos precisam de avaliação antes de serem incorporados ao fluxo principal.

### Próximas etapas

- [ ] Expandir os testes automatizados após a primeira entrega do MVP.
- [ ] Ampliar o tratamento de erros.
- [ ] Melhorar a qualidade e a completude dos documentos gerados.
- [ ] Desenvolver a interface de utilização.
- [ ] Avaliar suporte a novos tipos de documentos.
- [ ] Avaliar geração de PDF.
- [ ] Avaliar uma biblioteca de prompts.
