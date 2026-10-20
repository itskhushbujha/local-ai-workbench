
from typing import Annotated

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.answer_service import generate_answer

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


class Source(BaseModel):
    document_id: str
    filename: str
    chunk_index: int
    content: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]


@router.post("/ask", response_model=ChatResponse)
def ask_question(request: ChatRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=422,
            detail="Question cannot be empty.",
        )

    try:
        return generate_answer(question)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to generate an answer. Check the backend logs.",
        ) from exc
