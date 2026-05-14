from fastapi import APIRouter

from app.schemas import ChatRequest
from app.agent import generate_reply

router = APIRouter()


@router.get("/health")
def health():
    return {
        "status": "ok"
    }


@router.post("/chat")
def chat(request: ChatRequest):
    messages = [m.dict() for m in request.messages]

    return generate_reply(messages)