"""Module 3: Text normalization / case folding.

Turns raw tokens into index terms:
  * case folding (``casefold`` handles more than ``lower``, e.g. German "ß")
  * removing apostrophes and hyphens so "e-mail"/"email" and
    "don't"/"dont" map to the same term
"""

_STRIP_CHARS = str.maketrans("", "", "'-")


def normalize(token: str) -> str:
    """Normalize a single token. Returns "" if nothing is left."""
    return token.casefold().translate(_STRIP_CHARS)


def normalize_tokens(tokens: list[str]) -> list[str]:
    """Normalize a list of tokens, dropping any that become empty."""
    terms = (normalize(t) for t in tokens)
    return [t for t in terms if t]
