"""
Aplicativo de gestão de tarefas simples, utilizando FastAPI.
"""
from datetime import datetime
from fastapi import FastAPI

import requests

APP = FastAPI()

"""
Estrutura da tarefa
{
    "id" -> int,
    "titulo" -> str,
    "descricao" -> str,
    "concluida" -> bool,
    "criada_em" -> datetime,
    "concluida_em" -> datetime
}
"""
TAREFAS = []

def criar_tarefa(titulo, descricao):
    """
    Cria uma nova tarefa com os dados recebidos como parâmetro.
    @param titulo: Título da tarefa
    @param descricao: Descrição da tarefa
    @return: Dicionário representando a tarefa criada
    """
    return {
        "id": len(TAREFAS),
        "titulo": titulo,
        "descricao": descricao,
        "concluida": False,
        "criada_em": datetime.now(),
        "concluida_em": None
    }


@APP.get("/tarefas")
async def tarefas():
    """
    GET /tarefas: Lista todas as tarefas
    @return: Lista de dicionários contendo apenas o ID e o título das tarefas
    """
    lista_somente_id_titulo = []

    for tarefa in TAREFAS:
        id_tarefa = tarefa['id']
        titulo_tarefa = tarefa['titulo']

        lista_somente_id_titulo.append({id_tarefa: titulo_tarefa})

    return lista_somente_id_titulo

@APP.post("/tarefas", status_code=201)
async def post_tarefa(titulo: str, descricao: str):
    """
    POST /tarefas: Cria tarefa
    """
    # global TAREFAS

    tarefa_nova = criar_tarefa(titulo, descricao)

    TAREFAS.append(tarefa_nova)

    return {"mensagem": "OK"}

@APP.get("/tarefas/{incoming_id}")
async def tarefa_especifica(incoming_id: int):
    """
    GET /tarefas/{incoming_id}: Visualizar tarefa específica
    """
    for tarefa in TAREFAS:
        if incoming_id == int(tarefa["id"]):
            return tarefa

    return {"mensagem": "Tarefa não existe"}

@APP.put("/tarefas/{incoming_id}")
async def concluir_tarefa(incoming_id: int):
    """
    PUT /tarefas/{incoming_id}: Atualiza tarefa específica
    """
    for tarefa in TAREFAS:
        if incoming_id == int(tarefa['id']) and tarefa['concluida'] is False:
            tarefa["concluida"] = True
            tarefa["concluida_em"] = datetime.now()

            resp = requests.post(
                f"http://localhost:8002/notificar?id={incoming_id}&titulo={tarefa['titulo']}",
                timeout=5 )

            print(resp.json())
            return {"mensagem": "Tarefa concluída"}

    return {"mensagem": "Tarefa não existe ou já concluída"}

@APP.delete("/tarefas/{incoming_id}")
async def apagar_tarefa(incoming_id: int):
    """
    DELETE /tarefas/{incoming_id}: Exclui tarefa
    """
    for tarefa in TAREFAS.copy():
        if incoming_id == int(tarefa["id"]):
            TAREFAS.remove(tarefa)
            return {"mensagem": "Tarefa removida"}

    return {"mensagem": "Tarefa não existe"}

@APP.get("/")
async def index():
    """
    GET /: Página inicial
    """
    return {"mensagem": "Olá, mundo!"}
