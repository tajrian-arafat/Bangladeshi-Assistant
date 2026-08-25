"""Sanitize user queries before routing — strip unverified URL noise."""

from __future__ import annotations

import re

# Known verified government host fragments (routing may use these).
VERIFIED_HOST_FRAGMENTS = (
    "everify.bdris.gov.bd",
    "bdris.gov.bd",
    "epassport.gov.bd",
    "passport.gov.bd",
    "nidw.gov.bd",
    "services.nidw.gov.bd",
    "bdris.gov.bd",
    "br.gov.bd",
    "brta.gov.bd",
)

_FAKE_HOST = re.compile(
    r"https?://[^\s]+|(?:[a-z0-9-]+\.)+(?:example|invalid|test|localhost)[^\s]*",
    re.IGNORECASE,
)
_URLish = re.compile(r"https?://[^\s]+|(?:[a-z0-9-]+\.)+[a-z]{2,}(?:/[^\s]*)?", re.IGNORECASE)
_PATH_HINT = re.compile(
    r"(?:learner|driving|instructor|duplicate|smart[- ]?card|dctc|dctb)[-_ ]?(?:licen[cs]e|licence|license)?",
    re.IGNORECASE,
)


def _path_hints_from_url(fragment: str) -> str:
    """Preserve service tokens from URL paths before stripping unverified hosts."""
    hints: list[str] = []
    for match in _PATH_HINT.finditer(fragment):
        token = match.group(0).replace("-", " ").replace("_", " ").strip()
        if token and token.lower() not in hints:
            hints.append(token.lower())
    return " ".join(hints)


def sanitize_for_routing(message: str) -> str:
    """Remove unverified URLs from routing input; keep verified gov hosts as tokens."""
    text = message
    preserved_hints: list[str] = []
    for match in _URLish.finditer(message):
        fragment = match.group(0).lower()
        if any(v in fragment for v in VERIFIED_HOST_FRAGMENTS):
            continue
        if ".example" in fragment or "fake-" in fragment or "localhost" in fragment:
            hint = _path_hints_from_url(match.group(0))
            if hint:
                preserved_hints.append(hint)
            text = text.replace(match.group(0), " ")
    text = _FAKE_HOST.sub(" ", text)
    if preserved_hints:
        text = f"{' '.join(preserved_hints)} {text}"
    return re.sub(r"\s+", " ", text).strip()
