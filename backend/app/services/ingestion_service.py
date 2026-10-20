
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.document import Document
from app.services.chunk_storage import save_chunks
from app.services.document_processor import process_document


def ingest_document(
    db: Session,
    file_path: str | Path,
    content_type: str,
    original_filename: str | None = None,
) -> Document:
    """Process a document and save its chunks and embeddings."""
    path = Path(file_path)

    document = Document(
        filename=original_filename or path.name,
        content_type=content_type,
        file_size=path.stat().st_size,
        status="processing",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    try:
        chunks = process_document(path)
        save_chunks(db, document.id, chunks)

        document.status = "processed"
        db.commit()
        db.refresh(document)
        return document

    except Exception:
        db.rollback()

        failed_document = db.get(Document, document.id)
        if failed_document is not None:
            failed_document.status = "failed"
            db.commit()

        raise
