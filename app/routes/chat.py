from fastapi import APIRouter

from ..models import ChatRequest, ChatResponse
from ..services.llm import llm_client


router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    messages = [{"role": m.role, "content": m.content} for m in req.messages]
    reply = await llm_client.generate_reply(messages)
    return ChatResponse(reply=reply)

