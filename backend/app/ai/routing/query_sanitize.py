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


def sanitize_for_routing(message: str) -> str:
    """Remove unverified URLs from routing input; keep verified gov hosts as tokens."""
    text = message
    for match in _URLish.finditer(message):
        fragment = match.group(0).lower()
        if any(v in fragment for v in VERIFIED_HOST_FRAGMENTS):
            continue
        if ".example" in fragment or "fake-" in fragment or "localhost" in fragment:
            text = text.replace(match.group(0), " ")
    text = _FAKE_HOST.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()
