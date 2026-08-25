"""Language detection utilities."""

from __future__ import annotations

import re

_BN_RE = re.compile(r"[\u0980-\u09FF]")
_BANGLISH_MARKERS = {"korte", "lagbe", "korbo", "kivabe", "kothay", "ki", "ami", "apnar", "somporke"}


def detect_language(message: str, preference: str = "auto") -> str:
    if preference in {"bn", "en"}:
        return preference
    has_bn = bool(_BN_RE.search(message))
    has_en = bool(re.search(r"[A-Za-z]", message))
    tokens = set(re.findall(r"[a-z']+", message.lower()))
    if has_bn and has_en:
        return "banglish"
    if has_bn:
        return "bn"
    if tokens & _BANGLISH_MARKERS:
        return "banglish"
    if has_en:
        return "en"
    return "banglish"
