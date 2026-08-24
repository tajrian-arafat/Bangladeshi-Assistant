"""Load data-driven routing configuration from data/routing/."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


def _repo_root() -> Path:
    # backend/app/ai/routing/loader.py → repo root is 4 levels up from app/
    return Path(__file__).resolve().parents[4]


def _load_json(name: str) -> dict[str, Any]:
    path = _repo_root() / "data" / "routing" / name
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


@lru_cache(maxsize=1)
def load_intent_taxonomy() -> dict[str, Any]:
    return _load_json("intent_taxonomy.json")


@lru_cache(maxsize=1)
def load_capability_aliases() -> dict[str, Any]:
    return _load_json("capability_aliases.json")


@lru_cache(maxsize=1)
def load_service_capabilities() -> dict[str, Any]:
    return _load_json("service_capabilities.json")


@lru_cache(maxsize=1)
def load_phrase_hints() -> list[tuple[str, str]]:
    data = _load_json("phrase_hints.json")
    hints = [(phrase, slug) for phrase, slug in data.get("hints", [])]
    # Longest phrase first so specific hints beat generic substrings.
    return sorted(hints, key=lambda item: len(item[0]), reverse=True)


def capability_profiles_by_slug() -> dict[str, dict[str, Any]]:
    data = load_service_capabilities()
    return {entry["service_slug"]: entry for entry in data.get("services", [])}


def intent_claim_types(intent: str) -> list[str]:
    taxonomy = load_intent_taxonomy()
    entry = taxonomy.get("intents", {}).get(intent, {})
    return list(entry.get("claim_types") or [])


def intent_legacy_alias(intent: str) -> str:
    taxonomy = load_intent_taxonomy()
    entry = taxonomy.get("intents", {}).get(intent, {})
    return str(entry.get("legacy_alias") or intent)


def domain_category(domain: str) -> str | None:
    taxonomy = load_intent_taxonomy()
    return taxonomy.get("domain_categories", {}).get(domain)
