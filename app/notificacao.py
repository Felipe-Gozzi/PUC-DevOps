""" Notificações de tarefas """

from fastapi import FastAPI

NOTIFICACAO = FastAPI()

@NOTIFICACAO.post("/notificar")
async def notificar(incoming_id: int, titulo: str):
    """ Endpoint para notificar que uma tarefa foi concluída """
    print(f"Tarefa '{titulo}' (id={incoming_id}) finalizada!")
    return {"mensagem": "OK"}
