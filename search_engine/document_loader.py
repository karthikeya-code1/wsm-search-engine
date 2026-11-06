"""Module 1: Document loading.

Reads every ``.txt`` file from a folder and assigns each one an integer
document ID. IDs are given in sorted filename order so they are stable
between runs.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Document:
    doc_id: int
    name: str
    text: str


def load_documents(folder: str | Path, pattern: str = "*.txt") -> list[Document]:
    """Load all files matching ``pattern`` in ``folder`` as Documents."""
    folder = Path(folder)
    if not folder.is_dir():
        raise FileNotFoundError(f"Document folder not found: {folder}")

    documents = []
    for doc_id, path in enumerate(sorted(folder.glob(pattern)), start=1):
        text = path.read_text(encoding="utf-8", errors="replace")
        documents.append(Document(doc_id=doc_id, name=path.name, text=text))
    return documents
