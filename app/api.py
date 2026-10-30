"""
Aplicativo de gestão de tarefas simples, utilizando FastAPI.
"""
from datetime import datetime
from fastapi import FastAPI

import requests
from requests.exceptions import ConnectionError as RequestConnectionError

from app.modelo import Tarefa

APP = FastAPI()
TAREFAS = []

@APP.get("/")
async def index():
    """ GET /: Página inicial """
    return {"mensagem": "Servidor rodando!"}

@APP.get("/autor")
async def autor():
    """ GET /autor: Retorna o nome completo do autor """
    return {"mensagem": "Felipe Gozzi da Cruz"}

@APP.get("/tarefas")
async def tarefas():
    """ 
    GET /tarefas: Lista todas as tarefas
    @return: Lista de dicionários contendo apenas o ID e o título das tarefas
    """
    lista_somente_id_titulo = []

    for tarefa in TAREFAS:
        id_tarefa = tarefa.id
        titulo_tarefa = tarefa.titulo

        lista_somente_id_titulo.append({id_tarefa: titulo_tarefa})

    return lista_somente_id_titulo

@APP.post("/tarefas", status_code=201)
async def post_tarefa(titulo: str, descricao: str = None):
    """ POST /tarefas: Cria tarefa """
    tarefa_nova = Tarefa(
        id=len(TAREFAS),
        titulo=titulo,
        descricao=descricao,
        data_criacao=datetime.now().isoformat(timespec='seconds')
    )

    TAREFAS.append(tarefa_nova)

    return {"mensagem": "OK"}

@APP.get("/tarefas/{incoming_id}")
async def tarefa_especifica(incoming_id: int):
    """ GET /tarefas/{incoming_id}: Visualizar tarefa específica """
    for tarefa in TAREFAS:
        if incoming_id == int(tarefa.id):
            return tarefa

    return {"mensagem": "Tarefa não existe"}

@APP.put("/tarefas/{incoming_id}")
async def concluir_tarefa(incoming_id: int):
    """ PUT /tarefas/{incoming_id}: Atualiza tarefa específica """
    for tarefa in TAREFAS:
        if incoming_id == int(tarefa.id) and tarefa.concluida is False:
            tarefa.finalizar()

            url = "http://localhost:8002/notificar"
            params = {
                "incoming_id": incoming_id,
                "titulo": tarefa.titulo,
            }

            try:
                resp = requests.post( url, params=params, timeout=5 )
            except RequestConnectionError as e:
                print(e)

            print(resp.json())
            return {"mensagem": "Tarefa concluída"}

    return {"mensagem": "Tarefa não existe ou já concluída"}

@APP.delete("/tarefas/{incoming_id}")
async def apagar_tarefa(incoming_id: int):
    """ DELETE /tarefas/{incoming_id}: Exclui tarefa específica """
    for tarefa in TAREFAS.copy():
        if incoming_id == int(tarefa.id):
            TAREFAS.remove(tarefa)
            return {"mensagem": "Tarefa removida"}

    return {"mensagem": "Tarefa não existe"}
