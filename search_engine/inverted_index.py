"""Module 4: Inverted index construction.

Maps each term to a sorted postings list of document IDs, and keeps the
document metadata needed to display results.
"""

from collections import defaultdict

from .document_loader import Document
from .normalizer import normalize_tokens
from .tokenizer import tokenize


class InvertedIndex:
    def __init__(self) -> None:
        self._postings: dict[str, list[int]] = {}
        self.documents: dict[int, Document] = {}

    @classmethod
    def build(cls, documents: list[Document]) -> "InvertedIndex":
        index = cls()
        postings: dict[str, set[int]] = defaultdict(set)
        for doc in documents:
            index.documents[doc.doc_id] = doc
            for term in normalize_tokens(tokenize(doc.text)):
                postings[term].add(doc.doc_id)
        index._postings = {term: sorted(ids) for term, ids in postings.items()}
        return index

    @property
    def vocabulary(self) -> list[str]:
        """All indexed terms, sorted."""
        return sorted(self._postings)

    @property
    def all_doc_ids(self) -> list[int]:
        return sorted(self.documents)

    def postings(self, term: str) -> list[int]:
        """Postings list for an already-normalized term (empty if unknown)."""
        return self._postings.get(term, [])

    def document_frequency(self, term: str) -> int:
        return len(self.postings(term))

    def __len__(self) -> int:
        return len(self._postings)
