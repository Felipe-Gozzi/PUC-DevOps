from unittest.mock import Mock

import app as app_module
import pytest

from fastapi.testclient import TestClient
from app import APP

CLIENT = TestClient(APP)

@pytest.fixture(autouse=True)
def reset_tarefas():
    app_module.TAREFAS.clear()
    yield
    app_module.TAREFAS.clear()


def test_index():
    response = CLIENT.get("/")
    assert response.status_code == 200
    assert response.json() == {"mensagem": "Olá, mundo!"}


def test_listar_tarefas():
    CLIENT.post("/tarefas", params={"titulo": "Estudar", "descricao": "Revisar testes"})
    CLIENT.post("/tarefas", params={"titulo": "Entregar", "descricao": "Enviar atividade"})

    response = CLIENT.get("/tarefas")

    assert response.status_code == 200
    assert response.json() == [{"0": "Estudar"}, {"1": "Entregar"}]


def test_criar_tarefa():
    response = CLIENT.post(
        "/tarefas",
        params={"titulo": "Estudar", "descricao": "Revisar testes"},
    )

    assert response.status_code == 201
    assert response.json() == {"mensagem": "OK"}
    assert len(app_module.TAREFAS) == 1
    assert app_module.TAREFAS[0]["titulo"] == "Estudar"
    assert app_module.TAREFAS[0]["descricao"] == "Revisar testes"
    assert app_module.TAREFAS[0]["concluida"] is False


def test_concluir_tarefa(monkeypatch):
    CLIENT.post(
        "/tarefas",
        params={"titulo": "Estudar", "descricao": "Revisar testes"},
    )
    mock_post = Mock(return_value=Mock(json=Mock(return_value={"mensagem": "OK"})))
    monkeypatch.setattr(app_module.requests, "post", mock_post)

    response = CLIENT.put("/tarefas/0")

    assert response.status_code == 200
    assert response.json() == {"mensagem": "Tarefa concluída"}
    assert app_module.TAREFAS[0]["concluida"] is True
    assert app_module.TAREFAS[0]["concluida_em"] is not None
    mock_post.assert_called_once_with(
        "http://localhost:8002/notificar?id=0&titulo=Estudar"
    )

def test_concluir_tarefa_nao_existe(monkeypatch):

    mock_post = Mock(return_value=Mock(json=Mock(return_value={"mensagem": "OK"})))
    monkeypatch.setattr(app_module.requests, "post", mock_post)

    response = CLIENT.put("/tarefas/0")

    assert response.status_code == 200
    assert response.json() == {"mensagem": "Tarefa não existe ou já concluída"}

def test_obter_tarefa_por_id():
    CLIENT.post(
        "/tarefas",
        params={"titulo": "Estudar", "descricao": "Revisar testes"},
    )

    response = CLIENT.get("/tarefas/0")

    assert response.status_code == 200
    assert response.json()["id"] == 0
    assert response.json()["titulo"] == "Estudar"
    assert response.json()["descricao"] == "Revisar testes"
    assert response.json()["concluida"] is False
    assert response.json()["concluida_em"] is None

def test_obter_tarefa_por_id_nao_existe():
    
    response = CLIENT.get("/tarefas/0")
    assert response.status_code == 200
    assert response.json() == {"mensagem": "Tarefa não existe"}

def test_excluir_tarefa():
    CLIENT.post(
        "/tarefas",
        params={"titulo": "Estudar", "descricao": "Revisar testes"},
    )

    response = CLIENT.delete("/tarefas/0")

    assert response.status_code == 200
    assert response.json() == {"mensagem": "Tarefa removida"}
    assert app_module.TAREFAS == []
    
def test_excluir_tarefa_nao_existe():

    response = CLIENT.delete("/tarefas/0")

    assert response.status_code == 200
    assert response.json() == {"mensagem": "Tarefa não existe"}
    assert app_module.TAREFAS == []