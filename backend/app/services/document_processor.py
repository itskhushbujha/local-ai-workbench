
from pathlib import Path

from app.services.embedding_service import generate_embedding
from app.services.text_chunker import chunk_text
from app.services.text_extractor import extract_text


def process_document(
    file_path: str | Path,
) -> list[dict]:
    """Extract a document's text, split it, and generate embeddings."""
    text = extract_text(file_path)
    chunks = chunk_text(text)

    processed_chunks = []

    for index, content in enumerate(chunks):
        embedding = generate_embedding(content)

        processed_chunks.append(
            {
                "chunk_index": index,
                "content": content,
                "embedding": embedding,
            }
        )

    return processed_chunks
