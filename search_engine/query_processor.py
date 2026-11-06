"""Module 5: Query processing.

Evaluates Boolean queries against the inverted index.

Grammar (operators are case-insensitive; precedence NOT > AND > OR):

    query   := or_expr
    or_expr := and_expr ("OR" and_expr)*
    and_expr:= not_expr (["AND"] not_expr)*     # adjacent terms = implicit AND
    not_expr:= "NOT" not_expr | atom
    atom    := "(" or_expr ")" | TERM | WILDCARD_TERM

A wildcard term such as ``comp*`` is expanded through the k-gram index
into an OR of every matching vocabulary term.
"""

import re
from dataclasses import dataclass, field

from .inverted_index import InvertedIndex
from .normalizer import normalize
from .wildcard import KGramIndex, is_wildcard

_QUERY_TOKEN_RE = re.compile(r"\(|\)|[^\s()]+")
_OPERATORS = {"AND", "OR", "NOT"}


class QuerySyntaxError(ValueError):
    pass


@dataclass
class QueryResult:
    doc_ids: list[int]
    expansions: dict[str, list[str]] = field(default_factory=dict)


# ---- postings list operations (linear merges over sorted lists) ----------

def intersect(a: list[int], b: list[int]) -> list[int]:
    i = j = 0
    out = []
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            out.append(a[i]); i += 1; j += 1
        elif a[i] < b[j]:
            i += 1
        else:
            j += 1
    return out


def union(a: list[int], b: list[int]) -> list[int]:
    i = j = 0
    out = []
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            out.append(a[i]); i += 1; j += 1
        elif a[i] < b[j]:
            out.append(a[i]); i += 1
        else:
            out.append(b[j]); j += 1
    out.extend(a[i:])
    out.extend(b[j:])
    return out


def difference(a: list[int], b: list[int]) -> list[int]:
    """Docs in ``a`` that are not in ``b``."""
    i = j = 0
    out = []
    while i < len(a):
        if j >= len(b) or a[i] < b[j]:
            out.append(a[i]); i += 1
        elif a[i] == b[j]:
            i += 1; j += 1
        else:
            j += 1
    return out


# ---- parser / evaluator --------------------------------------------------

class QueryProcessor:
    def __init__(self, index: InvertedIndex, kgram_index: KGramIndex | None = None):
        self.index = index
        self.kgram_index = kgram_index or KGramIndex(index.vocabulary)

    def search(self, query: str) -> QueryResult:
        self._tokens = _QUERY_TOKEN_RE.findall(query)
        self._pos = 0
        self._expansions: dict[str, list[str]] = {}
        if not self._tokens:
            return QueryResult(doc_ids=[])

        doc_ids = self._parse_or()
        if self._pos < len(self._tokens):
            raise QuerySyntaxError(f"Unexpected '{self._tokens[self._pos]}'")
        return QueryResult(doc_ids=doc_ids, expansions=self._expansions)

    # token helpers
    def _peek(self) -> str | None:
        return self._tokens[self._pos] if self._pos < len(self._tokens) else None

    def _peek_op(self) -> str | None:
        tok = self._peek()
        return tok.upper() if tok and tok.upper() in _OPERATORS else None

    def _advance(self) -> str:
        tok = self._tokens[self._pos]
        self._pos += 1
        return tok

    # grammar rules
    def _parse_or(self) -> list[int]:
        result = self._parse_and()
        while self._peek_op() == "OR":
            self._advance()
            result = union(result, self._parse_and())
        return result

    def _parse_and(self) -> list[int]:
        result = self._parse_not()
        while True:
            op = self._peek_op()
            if op == "AND":
                self._advance()
            elif op == "OR" or self._peek() in (None, ")"):
                return result
            # otherwise: implicit AND between adjacent terms
            result = intersect(result, self._parse_not())

    def _parse_not(self) -> list[int]:
        if self._peek_op() == "NOT":
            self._advance()
            return difference(self.index.all_doc_ids, self._parse_not())
        return self._parse_atom()

    def _parse_atom(self) -> list[int]:
        tok = self._peek()
        if tok is None:
            raise QuerySyntaxError("Query ended unexpectedly")
        if tok == ")" or tok.upper() in _OPERATORS:
            raise QuerySyntaxError(f"Expected a term but found '{tok}'")
        self._advance()

        if tok == "(":
            result = self._parse_or()
            if self._peek() != ")":
                raise QuerySyntaxError("Missing closing ')'")
            self._advance()
            return result

        return self._term_postings(tok)

    def _term_postings(self, raw: str) -> list[int]:
        if is_wildcard(raw):
            terms = self.kgram_index.expand(raw)
            self._expansions[raw] = terms
            result: list[int] = []
            for term in terms:
                result = union(result, self.index.postings(term))
            return result
        return self.index.postings(normalize(raw))
