"""Module 6: Wildcard processing.

Uses a character k-gram index (bigrams by default) over the vocabulary.
Boundary marker ``$`` is added at both ends of each term, so "cat" yields
the bigrams ``$c ca at t$``.

To answer a pattern like ``re*ve``:
  1. Pad it with ``$`` and split on ``*``: ``$re`` and ``ve$``.
  2. Take the k-grams of each fixed piece (``$r re ve e$``) and intersect
     their term sets to get candidates.
  3. Post-filter candidates against the full pattern, because k-grams
     alone can give false positives (e.g. "retrieve" vs. "rev").
"""

import fnmatch
from collections import defaultdict

from .normalizer import normalize

WILDCARD = "*"
BOUNDARY = "$"


def is_wildcard(term: str) -> bool:
    return WILDCARD in term


def _kgrams(text: str, k: int) -> set[str]:
    return {text[i:i + k] for i in range(len(text) - k + 1)}


def normalize_pattern(pattern: str) -> str:
    """Case-fold each fixed piece of a wildcard pattern, keeping the ``*``s."""
    pieces = pattern.split(WILDCARD)
    return WILDCARD.join(normalize(p) for p in pieces)


class KGramIndex:
    def __init__(self, vocabulary: list[str], k: int = 2) -> None:
        self.k = k
        self._vocabulary = sorted(vocabulary)
        self._grams: dict[str, set[str]] = defaultdict(set)
        for term in self._vocabulary:
            for gram in _kgrams(f"{BOUNDARY}{term}{BOUNDARY}", k):
                self._grams[gram].add(term)

    def expand(self, pattern: str) -> list[str]:
        """Return all vocabulary terms matching a wildcard pattern."""
        pattern = normalize_pattern(pattern)
        if pattern.strip(WILDCARD) == "":
            return list(self._vocabulary)  # "*" matches everything

        padded = f"{BOUNDARY}{pattern}{BOUNDARY}"
        query_grams: set[str] = set()
        for piece in padded.split(WILDCARD):
            query_grams |= _kgrams(piece, self.k)

        if query_grams:
            candidate_sets = [self._grams.get(g, set()) for g in query_grams]
            candidates = set.intersection(*candidate_sets)
        else:
            # Fixed pieces are all shorter than k (e.g. "a*"): no usable
            # k-grams, so fall back to scanning the whole vocabulary.
            candidates = set(self._vocabulary)

        return sorted(t for t in candidates if fnmatch.fnmatchcase(t, pattern))
