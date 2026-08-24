"""Banglish normalization pipeline."""

from __future__ import annotations

import re

from rapidfuzz import fuzz

DOMAIN_MAP: dict[str, str] = {
    "passport": "passport",
    "pasport": "passport",
    "nid": "nid",
    "national id": "nid",
    "brta": "brta",
    "license": "licence",
    "licence": "licence",
    "driving": "driving",
    "renew": "renewal",
    "renewal": "renewal",
    "korte": "",
    "lagbe": "",
    "ki": "",
    "korbo": "",
    "kivabe": "",
    "kothay": "where",
    "tin": "tin",
    "tax": "tax",
    "birth": "birth",
    "registration": "registration",
    "janmo": "birth",
    "nibondhon": "registration",
    "ssc": "ssc",
    "hsc": "hsc",
    "university": "university",
    "admission": "admission",
}


def normalize_banglish(message: str) -> str:
    text = message.lower().strip()
    tokens = re.findall(r"[\u0980-\u09FF]+|[a-z0-9']+", text)
    normalized: list[str] = []
    for token in tokens:
        mapped = DOMAIN_MAP.get(token, token)
        if mapped:
            normalized.append(mapped)
    if not normalized:
        return text
    return " ".join(normalized)
