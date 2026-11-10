# PUC DevOps — API de tarefas

## Descrição

Esta aplicação é uma API REST para gerenciamento de tarefas. Ela permite criar,
listar, consultar, concluir e remover tarefas. Cada tarefa armazena título,
descrição opcional, estado de conclusão e datas de criação e conclusão. A
documentação interativa dos endpoints fica disponível pelo Swagger UI.

Principais rotas:

| Método | Rota | Descrição |
| --- | --- | --- |
| `GET` | `/` | Verifica se o servidor está em execução |
| `GET` | `/autor` | Retorna o nome do autor |
| `GET` | `/tarefas` | Lista as tarefas |
| `POST` | `/tarefas` | Cria uma tarefa (`titulo` obrigatório e `descricao` opcional) |
| `GET` | `/tarefas/{id}` | Consulta uma tarefa |
| `PUT` | `/tarefas/{id}` | Conclui uma tarefa |
| `DELETE` | `/tarefas/{id}` | Remove uma tarefa |

## Execução local

### Pré-requisitos

- Python 3.14
- PostgreSQL (local ou via Docker)
- Docker, caso escolha executar o PostgreSQL em contêiner

### 1. Configure o banco de dados

Uma opção é iniciar um contêiner PostgreSQL:

```bash
docker run --name tarefas-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=tarefas \
  -p 5432:5432 \
  -d postgres:16
```

O banco `tarefas` precisa existir antes de iniciar a API. As tabelas da
aplicação são criadas automaticamente na inicialização.

### 2. Instale as dependências

Na raiz do repositório, crie e ative um ambiente virtual e instale os pacotes:

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

No Windows PowerShell, ative o ambiente com:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Inicie a API

Inicie a API principal em um terminal, definindo as credenciais do PostgreSQL:

```bash
export DATABASE_USERNAME=postgres
export DATABASE_PASSWORD=postgres
export DATABASE_HOST=localhost
export DATABASE_PORT=5432
export DATABASE_NAME=tarefas
uvicorn app.api:APP --reload --host 0.0.0.0 --port 8001
```

A API principal estará em <http://localhost:8001> e o Swagger UI em
<http://localhost:8001/docs>.

### Testes

Com as dependências instaladas, execute os testes na raiz do repositório:

```bash
pytest tests/
```

Para gerar um relatório de cobertura HTML:

```bash
pytest --cov --cov-report=html
```

## Tecnologias utilizadas

- **Python 3.14** — linguagem e runtime.
- **FastAPI** — implementação das APIs REST e documentação OpenAPI/Swagger.
- **SQLModel** e **SQLAlchemy** — modelos e acesso ao banco de dados.
- **PostgreSQL** e **psycopg2** — persistência das tarefas.
- **Uvicorn** — servidor ASGI usado para executar os serviços localmente.
- **Pytest** e **pytest-cov** — testes automatizados e cobertura.
- **Docker** — execução opcional do banco de dados em contêiner.
- **NGINX** — configuração de proxy reverso disponível em `default.conf`.
