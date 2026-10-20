
import uuid

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.conversation import Conversation
from app.models.message import Message
from app.services.answer_service import generate_answer


def create_conversation(title: str = "New conversation") -> Conversation:
    """Create and persist a new conversation."""
    title = title.strip()
    if not title:
        raise ValueError("Conversation title cannot be empty.")

    with SessionLocal() as db:
        conversation = Conversation(title=title)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        db.expunge(conversation)
        return conversation


def get_conversation_history(
    conversation_id: uuid.UUID,
    limit: int = 10,
) -> list[dict]:
    """Return recent conversation messages in chronological order."""
    if limit < 1:
        raise ValueError("Limit must be at least 1.")

    with SessionLocal() as db:
        conversation = db.get(Conversation, conversation_id)
        if conversation is None:
            raise ValueError("Conversation not found.")

        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc(), Message.id.desc())
            .limit(limit)
        )

        messages = list(db.scalars(statement).all())
        messages.reverse()

        return [
            {"role": message.role, "content": message.content}
            for message in messages
        ]


def get_first_user_question(conversation_id: uuid.UUID) -> str:
    """Return the exact text of the first user message."""
    with SessionLocal() as db:
        conversation = db.get(Conversation, conversation_id)
        if conversation is None:
            raise ValueError("Conversation not found.")

        statement = (
            select(Message)
            .where(
                Message.conversation_id == conversation_id,
                Message.role == "user",
            )
            .order_by(Message.created_at, Message.id)
            .limit(1)
        )

        message = db.scalars(statement).first()

        if message is None:
            raise ValueError("No user questions found in this conversation.")

        return message.content


def send_message(conversation_id: uuid.UUID, content: str) -> dict:
    """Persist a user message and generate an answer."""
    content = content.strip()
    if not content:
        raise ValueError("Message cannot be empty.")

    with SessionLocal() as db:
        conversation = db.get(Conversation, conversation_id)
        if conversation is None:
            raise ValueError("Conversation not found.")

        # Load previous messages before saving the current question.
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc(), Message.id.desc())
            .limit(10)
        )
        previous_messages = list(db.scalars(statement).all())
        previous_messages.reverse()

        history = [
            {"role": message.role, "content": message.content}
            for message in previous_messages
        ]

        # Save the user's message first.
        user_message = Message(
            conversation_id=conversation_id,
            role="user",
            content=content,
        )
        db.add(user_message)
        db.commit()

        # Handle exact-history recall directly from the database.
        normalized_content = content.lower().strip().rstrip("?.!")

        first_question_patterns = {
            "what was my first question in this conversation",
            "what was the exact text of my first question in this conversation",
        }

        if normalized_content in first_question_patterns:
            answer = get_first_user_question(conversation_id)
            sources = []
        else:
            result = generate_answer(
                content,
                conversation_history=history,
            )
            answer = result["answer"]
            sources = result["sources"]

        # Persist the assistant's answer.
        assistant_message = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=answer,
        )
        db.add(assistant_message)
        db.commit()

        return {
            "conversation_id": str(conversation_id),
            "answer": answer,
            "sources": sources,
        }


def get_messages(conversation_id: uuid.UUID) -> list[dict]:
    """Return all messages in chronological order."""
    with SessionLocal() as db:
        conversation = db.get(Conversation, conversation_id)
        if conversation is None:
            raise ValueError("Conversation not found.")

        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at, Message.id)
        )
        messages = db.scalars(statement).all()

        return [
            {
                "id": str(message.id),
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at.isoformat(),
            }
            for message in messages
        ]
