from datetime import UTC, datetime

from app.modelo import Tarefa


def criar_tarefa_mock():
    return Tarefa(
        id=0,
        titulo="Tarefa teste",
        data_criacao=datetime(2026, 1, 1, tzinfo=UTC),
    )


def test_nova_tarefa():
    tarefa = criar_tarefa_mock()

    assert tarefa.id == 0
    assert tarefa.titulo == "Tarefa teste"
    assert tarefa.descricao is None
    assert tarefa.data_criacao == datetime(2026, 1, 1, tzinfo=UTC)
    assert tarefa.data_conclusao is None
    assert tarefa.concluida is False


def test_resumir_tarefa():
    tarefa = criar_tarefa_mock()

    assert tarefa.resumir() == {0: "Tarefa teste"}


def test_obter_id_da_tarefa():
    tarefa = criar_tarefa_mock()

    assert tarefa.get_id() == 0


def test_finalizar_tarefa():
    tarefa = criar_tarefa_mock()

    tarefa.finalizar()

    assert tarefa.concluida is True
    assert isinstance(tarefa.data_conclusao, datetime)
    assert tarefa.data_conclusao.tzinfo == UTC
