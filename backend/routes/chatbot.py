from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List

from models.models import User
from services.auth_service import get_current_user
from services.groq_service import chat_response

router = APIRouter()


class ChatMessage(BaseModel):
    role: str        # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    career_path: str = "General Programming"
    history: List[ChatMessage] = []


@router.post("/message")
async def send_message(req: ChatRequest, current_user: User = Depends(get_current_user)):
    try:
        history = [{"role": m.role, "content": m.content} for m in req.history]
        response = chat_response(req.message, req.career_path, history)
        return {"response": response, "role": "assistant"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")
