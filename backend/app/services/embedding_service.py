
import httpx

from app.core.config import settings


def generate_embedding(text: str) -> list[float]:
    """Generate a vector using the local Ollama embedding model."""
    response = httpx.post(
        f"{settings.ollama_base_url}/api/embed",
        json={
            "model": settings.embedding_model,
            "input": text,
        },
        timeout=120.0,
    )
    response.raise_for_status()

    data = response.json()
    embeddings = data.get("embeddings", [])

    if not embeddings:
        raise ValueError("Ollama returned no embedding.")

    embedding = embeddings[0]

    if len(embedding) != 768:
        raise ValueError(
            f"Expected 768 dimensions, received {len(embedding)}."
        )

    return embedding
