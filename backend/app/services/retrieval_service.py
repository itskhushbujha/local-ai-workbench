
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.embedding_service import generate_embedding


def search_chunks(
    db: Session,
    query: str,
    limit: int = 5,
    max_distance: float = 0.45,
) -> list[dict]:
    """Search processed documents and return the best unique chunks."""

    query = query.strip()

    if not query:
        return []

    if limit < 1 or limit > 20:
        raise ValueError("limit must be between 1 and 20.")

    if not 0.0 < max_distance <= 2.0:
        raise ValueError(
            "max_distance must be greater than 0 and at most 2."
        )

    query_embedding = generate_embedding(query)
    distance = DocumentChunk.embedding.cosine_distance(query_embedding)

    # Retrieve more candidates so duplicates do not crowd out useful results.
    candidate_limit = min(limit * 5, 100)

    statement = (
        select(
            DocumentChunk,
            Document.filename,
            distance.label("distance"),
        )
        .join(
            Document,
            Document.id == DocumentChunk.document_id,
        )
        .where(
            distance <= max_distance,
            Document.status == "processed",
        )
        .order_by(distance)
        .limit(candidate_limit)
    )

    results = db.execute(statement).all()

    unique_results = []
    seen_content = set()

    for chunk, filename, distance_value in results:
        normalized_content = " ".join(chunk.content.split())

        if normalized_content in seen_content:
            continue

        seen_content.add(normalized_content)

        unique_results.append(
            {
                "document_id": str(chunk.document_id),
                "filename": filename,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "distance": float(distance_value),
            }
        )

        # Apply the requested limit after deduplication.
        if len(unique_results) >= limit:
            break

    return unique_results
