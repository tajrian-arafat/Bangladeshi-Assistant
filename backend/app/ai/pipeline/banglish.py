"""Banglish normalization pipeline."""

from __future__ import annotations

import re

DOMAIN_MAP: dict[str, str] = {
    # Identity / civil
    "passport": "passport",
    "pasport": "passport",
    "nid": "nid",
    "national": "national",
    "id": "id",
    "voter": "voter",
    "brta": "brta",
    "license": "licence",
    "licence": "licence",
    "driving": "driving",
    "renew": "renewal",
    "renewal": "renewal",
    "reissue": "reissue",
    "correction": "correction",
    "correct": "correction",
    "soshodon": "correction",
    "shongshodhon": "correction",
    "lost": "lost",
    "damage": "damaged",
    "damaged": "damaged",
    "tin": "tin",
    "tax": "tax",
    "birth": "birth",
    "death": "death",
    "registration": "registration",
    "registraton": "registration",
    "brth": "birth",
    "janmo": "birth",
    "nibondon": "registration",
    "jonmo": "birth",
    "jonm": "birth",
    "nibondhon": "registration",
    "nibondon": "registration",
    "nibondhan": "registration",
    "character": "character",
    "certificate": "certificate",
    "muslim": "muslim",
    "hindu": "hindu",
    "mrityu": "death",
    "mrittu": "death",
    "verify": "verify",
    "verification": "verification",
    "jachai": "verify",
    "jachay": "verify",
    "everify": "everify",
    "bdris": "bdris",
    "marriage": "marriage",
    "bibaho": "marriage",
    "divorce": "divorce",
    "talak": "divorce",
    "fee": "fee",
    "fees": "fee",
    "koto": "fee",
    "charge": "fee",
    "calculator": "calculator",
    "ssc": "ssc",
    "hsc": "hsc",
    "university": "university",
    "admission": "admission",
    "document": "document",
    "documents": "document",
    "paper": "document",
    "required": "required",
    "office": "office",
    "location": "location",
    "where": "where",
    "kothay": "where",
    "kivabe": "how",
    "how": "how",
    "process": "procedure",
    "procedure": "procedure",
    "step": "procedure",
    "steps": "procedure",
    # Fillers removed (keep semantic tokens for intent classification)
    "ami": "",
    "bhai": "",
    "ache": "",
    "ase": "",
    "te": "",
    "lagbe": "required",
    "lage": "required",
    "korbo": "how",
    "korte": "apply",
    "ki": "what",
    "pari": "how",
    "chai": "apply",
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
