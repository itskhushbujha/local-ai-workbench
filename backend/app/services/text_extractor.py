
from pathlib import Path

import pymupdf


def extract_text(file_path: str | Path) -> str:
    """Extract text from a PDF or plain-text file."""
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        with pymupdf.open(path) as document:
            pages = [page.get_text() for page in document]
        text = "\n".join(pages)

    elif suffix == ".txt":
        text = path.read_text(encoding="utf-8")

    else:
        raise ValueError(f"Unsupported file type: {suffix}")

    text = text.strip()
    if not text:
        raise ValueError("No extractable text found in the file.")

    return text
