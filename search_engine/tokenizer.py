"""Module 2: Tokenization.

Splits raw text into word tokens. A token is a run of letters/digits,
optionally joined by internal apostrophes or hyphens (e.g. "don't",
"state-of-the-art"). Punctuation and whitespace are discarded.
"""

import re

_TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:['\-][A-Za-z0-9]+)*")


def tokenize(text: str) -> list[str]:
    """Return the list of tokens in ``text`` (case is preserved)."""
    return _TOKEN_RE.findall(text)
