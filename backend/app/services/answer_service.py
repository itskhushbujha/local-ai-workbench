
import httpx

from app.core.config import settings
from app.core.database import SessionLocal
from app.services.retrieval_service import search_chunks


def generate_answer(
    question: str,
    conversation_history: list[dict] | None = None,
) -> dict:
    """Generate an answer using conversation history and retrieved documents."""

    # Retrieve relevant document chunks.
    with SessionLocal() as db:
        chunks = search_chunks(db, question, limit=5)

    # Format recent conversation history.
    history = conversation_history or []
    history_text = "\n".join(
        f"{message['role'].capitalize()}: {message['content']}"
        for message in history
        if message["role"] in {"user", "assistant"}
    )

    # Format document context with source labels.
    context = "\n\n".join(
        f"[Source {i + 1} | File: {chunk['filename']}]\n{chunk['content']}"
        for i, chunk in enumerate(chunks)
    )

    prompt = f"""You are a helpful assistant that can use conversation history
and uploaded documents.

Use the conversation history to understand follow-up questions and refer
to earlier messages when relevant.

Use conversation history to understand context and follow-up questions.

When relevant uploaded document context is available, prioritize it.
Do not claim that a fact comes from an uploaded document unless the
provided document context supports that fact.

If no relevant document context is available, clearly state that the
uploaded documents do not contain enough information to answer.
You may provide an answer from general knowledge, but explicitly label
it as general knowledge rather than information from the documents.

Cite document-based claims using labels like [Source 1].
Never invent document citations or source labels.
Do not cite conversation history as a document source.

Conversation history:
{history_text or "(No previous messages)"}

Document context:
{context or "(No relevant document context found)"}

Current question:
{question}

Answer:"""

    # Generate the answer using the locally running Ollama model.
    response = httpx.post(
        f"{settings.ollama_base_url}/api/generate",
        json={
            "model": settings.chat_model,
            "prompt": prompt,
            "stream": False,
        },
        timeout=180.0,
    )
    response.raise_for_status()

    answer = response.json().get("response", "").strip()

    # Return source metadata, including the original filename.
    return {
        "answer": answer,
        "sources": [
            {
                "document_id": chunk["document_id"],
                "filename": chunk["filename"],
                "chunk_index": chunk["chunk_index"],
                "content": chunk["content"],
            }
            for chunk in chunks
        ],
    }
