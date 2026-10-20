
import uuid
from typing import Annotated

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.chat_service import (
    create_conversation,
    get_messages,
    send_message,
)

router = APIRouter(prefix="/conversations", tags=["conversations"])


class ConversationCreate(BaseModel):
    title: str = Field(default="New conversation", min_length=1, max_length=200)


class ConversationResponse(BaseModel):
    id: str
    title: str


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: str


@router.post("", response_model=ConversationResponse)
def create_new_conversation(request: ConversationCreate):
    conversation = create_conversation(request.title.strip())
    return {"id": str(conversation.id), "title": conversation.title}


@router.post("/{conversation_id}/messages")
def add_message(
    conversation_id: uuid.UUID,
    request: MessageCreate,
):
    try:
        return send_message(conversation_id, request.content)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
def list_messages(conversation_id: uuid.UUID):
    try:
        return get_messages(conversation_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
