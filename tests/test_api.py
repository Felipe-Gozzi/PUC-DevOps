import asyncio
import importlib
from unittest.mock import Mock, patch

import pytest
import requests
from fastapi.testclient import TestClient
from sqlalchemy import inspect
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine

from app.modelo import Tarefa

with patch.dict(
    "os.environ",
    {
        "DATABASE_USERNAME": "test",
        "DATABASE_PASSWORD": "test",
        "DATABASE_HOST": "localhost",
        "DATABASE_PORT": "3306",
        "DATABASE_NAME": "test",
    },
):
    app_module = importlib.import_module("app.api")


def test_configuracao_banco_incompleta(monkeypatch):
    configuracao = {
        "DATABASE_USERNAME": "test",
        "DATABASE_PASSWORD": "test",
        "DATABASE_HOST": "localhost",
        "DATABASE_PORT": "3306",
        "DATABASE_NAME": "test",
    }
    for variavel, valor in configuracao.items():
        monkeypatch.setenv(variavel, valor)
    monkeypatch.delenv("DATABASE_USERNAME")

    with pytest.raises(ValueError, match="Configuração do banco de dados incompleta"):
        importlib.reload(app_module)

    monkeypatch.setenv("DATABASE_USERNAME", configuracao["DATABASE_USERNAME"])
    importlib.reload(app_module)


@pytest.fixture
def client(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    monkeypatch.setattr(app_module, "ENGINE", engine)

    yield TestClient(app_module.APP)

    engine.dispose()


def criar_tarefa(client, titulo="Estudar", descricao="Revisar testes"):
    response = client.post(
        "/tarefas",
        params={"titulo": titulo, "descricao": descricao},
    )
    assert response.status_code == 201
    return response.json()


def test_inicializacao_cria_tabelas(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    monkeypatch.setattr(app_module, "ENGINE", engine)

    async def executar_lifespan():
        inicializacao = app_module.inicializacao(app_module.APP)

        assert not inspect(engine).has_table(Tarefa.__tablename__)
        await anext(inicializacao)
        assert inspect(engine).has_table(Tarefa.__tablename__)

        with pytest.raises(StopAsyncIteration):
            await anext(inicializacao)

    try:
        asyncio.run(executar_lifespan())
    finally:
        engine.dispose()


def test_index(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"mensagem": "Servidor rodando!"}


def test_autor(client):
    response = client.get("/autor")

    assert response.status_code == 200
    assert response.json() == {"mensagem": "Felipe Gozzi da Cruz"}


def test_listar_tarefas(client):
    criar_tarefa(client, "Estudar", "Revisar testes")
    criar_tarefa(client, "Entregar", "Enviar atividade")

    response = client.get("/tarefas")

    assert response.status_code == 200
    assert response.json() == [{"1": "Estudar"}, {"2": "Entregar"}]


def test_criar_tarefa(client):
    response = client.post(
        "/tarefas",
        params={"titulo": "Estudar", "descricao": "Revisar testes"},
    )

    assert response.status_code == 201
    tarefa = response.json()
    assert tarefa["_id"] == 1
    assert tarefa["titulo"] == "Estudar"
    assert tarefa["descricao"] == "Revisar testes"
    assert tarefa["concluida"] is False
    assert tarefa["data_conclusao"] is None


def test_concluir_tarefa(client, monkeypatch):
    tarefa_criada = criar_tarefa(client)
    incoming_id = tarefa_criada["_id"]
    mock_post = Mock()
    monkeypatch.setattr(app_module.requests, "post", mock_post)

    response = client.put(f"/tarefas/{incoming_id}")

    assert response.status_code == 200
    assert response.json() == {"mensagem": "Tarefa concluída"}
    tarefa_atualizada = client.get(f"/tarefas/{incoming_id}").json()
    assert tarefa_atualizada["concluida"] is True
    assert tarefa_atualizada["data_conclusao"] is not None
    mock_post.assert_called_once_with(
        "http://localhost:8002/notificar",
        params={"incoming_id": incoming_id, "titulo": "Estudar"},
        timeout=5,
    )


def test_concluir_tarefa_quando_notificacao_falha(client, monkeypatch):
    tarefa_criada = criar_tarefa(client)
    incoming_id = tarefa_criada["_id"]
    mock_post = Mock(side_effect=requests.exceptions.ConnectionError)
    monkeypatch.setattr(app_module.requests, "post", mock_post)

    response = client.put(f"/tarefas/{incoming_id}")

    assert response.status_code == 200
    assert response.json() == {"mensagem": "Tarefa concluída"}
    tarefa_atualizada = client.get(f"/tarefas/{incoming_id}").json()
    assert tarefa_atualizada["concluida"] is True
    assert tarefa_atualizada["data_conclusao"] is not None
    mock_post.assert_called_once()


def test_concluir_tarefa_inexistente(client, monkeypatch):
    mock_post = Mock()
    monkeypatch.setattr(app_module.requests, "post", mock_post)

    response = client.put("/tarefas/999")

    assert response.status_code == 200
    assert response.json() == {"mensagem": "Tarefa não existe ou já concluída"}
    mock_post.assert_not_called()


def test_concluir_tarefa_ja_concluida(client, monkeypatch):
    tarefa = criar_tarefa(client)
    incoming_id = tarefa["_id"]
    mock_post = Mock()
    monkeypatch.setattr(app_module.requests, "post", mock_post)
    assert client.put(f"/tarefas/{incoming_id}").status_code == 200

    response = client.put(f"/tarefas/{incoming_id}")

    assert response.status_code == 200
    assert response.json() == {"mensagem": "Tarefa não existe ou já concluída"}
    mock_post.assert_called_once()


def test_obter_tarefa_por_id(client):
    tarefa_criada = criar_tarefa(client)
    incoming_id = tarefa_criada["_id"]

    response = client.get(f"/tarefas/{incoming_id}")

    assert response.status_code == 200
    assert response.json() == tarefa_criada


def test_obter_tarefa_inexistente(client):
    response = client.get("/tarefas/999")

    assert response.status_code == 200
    assert response.json() == {"mensagem": "Tarefa não existe"}


def test_excluir_tarefa(client):
    tarefa = criar_tarefa(client)
    incoming_id = tarefa["_id"]

    response = client.delete(f"/tarefas/{incoming_id}")

    assert response.status_code == 200
    assert response.json() == {"mensagem": "Tarefa removida"}
    assert client.get("/tarefas").json() == []
    assert client.get(f"/tarefas/{incoming_id}").json() == {
        "mensagem": "Tarefa não existe"
    }


def test_excluir_tarefa_inexistente(client):
    response = client.delete("/tarefas/999")

    assert response.status_code == 200
    assert response.json() == {"mensagem": "Tarefa não existe"}
