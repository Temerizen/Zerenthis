from fastapi import APIRouter
from pydantic import BaseModel
from backend.app.core.interpreter import interpret
from backend.app.engines.autonomous_executor import run as execute

router = APIRouter()

class ChatInput(BaseModel):
    message: str

@router.post("/chat")
def chat(input: ChatInput):
    task = interpret(input.message)
    result = execute({"task": task})
    return {
        "task": task,
        "result": result
    }
