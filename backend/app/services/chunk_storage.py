
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk


def save_chunks(
    db: Session,
    document_id: UUID,
    chunks: list[dict],
) -> int:
    """Save processed chunks and their embeddings to PostgreSQL."""
    records = [
        DocumentChunk(
            document_id=document_id,
            chunk_index=chunk["chunk_index"],
            content=chunk["content"],
            embedding=chunk["embedding"],
        )
        for chunk in chunks
    ]

    try:
        db.add_all(records)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return len(records)
