from fastapi import FastAPI
from datetime import datetime

APP = FastAPI()
TAREFAS = []

# {
#         "id" -> int,
#         "titulo" -> str,
#         "descricao" -> str,
#         "concluida" -> bool,
#         "criado_em" -> datetime
# }

async def criar_tarefa(titulo, descricao):
        return{
            "id": len(TAREFAS),
            "titulo": titulo,
            "descricao": descricao,
            "concluida": False,
            "criado_em": datetime.now() }

@APP.get("/")
async def index():
        return{ "mensagem": "Olá, mundo!" }

@APP.get("/tarefas")
async def tarefas():
        return TAREFAS
    
@APP.post("/tarefas")
async def post_tarefa(titulo:str, descricao:str):
    global TAREFAS
        
    tarefa_nova = await criar_tarefa(titulo, descricao)
    
    TAREFAS.append(tarefa_nova)
    
    return {"mensagem":"OK", "tarefa": tarefa_nova}