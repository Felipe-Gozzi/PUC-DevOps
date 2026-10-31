"""
Aplicativo de gestão de tarefas simples, utilizando FastAPI.
"""
from datetime import datetime, timezone
from typing import Annotated

import os
import requests
from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, Session, create_engine, select
from requests.exceptions import ConnectionError as RequestConnectionError

from .modelo import Tarefa

DATABASE_USERNAME = os.environ.get("DATABASE_USERNAME")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
DATABASE_HOST = os.environ.get("DATABASE_HOST")
DATABASE_PORT = os.environ.get("DATABASE_PORT")
DATABASE_NAME = os.environ.get("DATABASE_NAME")

if  DATABASE_USERNAME is None or \
    DATABASE_PASSWORD is None or \
    DATABASE_HOST is None or \
    DATABASE_PORT is None or \
    DATABASE_NAME is None:
    raise ValueError("Configuração do banco de dados incompleta")

DB_STRING_CREDENTIALS = f"mysql+pymysql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}"
DB_STRING_ADDRESS = f"@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

ENGINE = create_engine(f"{DB_STRING_CREDENTIALS}{DB_STRING_ADDRESS}")

def create_session():
    """ Cria uma nova sessão para o banco de dados """
    with Session(ENGINE) as session:
        yield session

SESSAO = Annotated[Session, Depends(create_session)]

async def inicializacao(_app: FastAPI):
    """ Função de inicialização da aplicação FastAPI """
    SQLModel.metadata.create_all(ENGINE)
    yield

APP = FastAPI(lifespan=inicializacao)
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
async def tarefas(sessao: SESSAO) -> list[dict[int, str]]:
    """ 
    GET /tarefas: Lista todas as tarefas
    @return: Lista de objetos Tarefa
    """
    lista_tarefas = sessao.exec(select(Tarefa).offset(0)).all()

    return [tarefa.resumir() for tarefa in lista_tarefas]

@APP.post("/tarefas", status_code=201)
async def post_tarefa(sessao: SESSAO, titulo: str, descricao: str = None) -> Tarefa:
    """ POST /tarefas: Cria tarefa """
    tarefa_nova = Tarefa(
        titulo=titulo,
        descricao=descricao,
        data_criacao=datetime.now(timezone.utc),
    )

    sessao.add(tarefa_nova)
    sessao.commit()
    sessao.refresh(tarefa_nova)

    return tarefa_nova

@APP.get("/tarefas/{incoming_id}")
async def tarefa_especifica(
    sessao: SESSAO, incoming_id: int
) -> Tarefa | dict[str, str]:
    """ GET /tarefas/{incoming_id}: Visualizar tarefa específica """
    regra = select(Tarefa).where(Tarefa.id == incoming_id)
    tarefa = sessao.exec(regra).first()
    if tarefa:
        return tarefa

    return {"mensagem": "Tarefa não existe"}

@APP.put("/tarefas/{incoming_id}")
async def concluir_tarefa(sessao: SESSAO, incoming_id: int) -> dict:
    """ PUT /tarefas/{incoming_id}: Atualiza tarefa específica """
    regra = select(Tarefa).where(Tarefa.id == incoming_id)
    tarefa = sessao.exec(regra).first()
    if tarefa and tarefa.concluida is False:
        tarefa.finalizar()

        url = "http://localhost:8002/notificar"
        params = {
            "incoming_id": incoming_id,
            "titulo": tarefa.titulo,
        }
        sessao.add(tarefa)
        sessao.commit()
        sessao.refresh(tarefa)

        try:
            _ = requests.post( url, params=params, timeout=5 )
        except RequestConnectionError as e:
            print(e)

        return {"mensagem": "Tarefa concluída"}

    return {"mensagem": "Tarefa não existe ou já concluída"}

@APP.delete("/tarefas/{incoming_id}")
async def apagar_tarefa(sessao: SESSAO, incoming_id: int) -> dict:
    """ DELETE /tarefas/{incoming_id}: Exclui tarefa específica """
    regra = select(Tarefa).where(Tarefa.id == incoming_id)
    tarefa = sessao.exec(regra).first()
    if tarefa:
        sessao.delete(tarefa)
        sessao.commit()
        return {"mensagem": "Tarefa removida"}

    return {"mensagem": "Tarefa não existe"}
