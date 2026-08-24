"""Extract domain entities and variant dimensions from user queries."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from app.ai.routing.loader import load_capability_aliases


@dataclass
class DomainEntities:
    domains: list[str] = field(default_factory=list)
    passport_type: str | None = None  # e_passport | mrp
    action: str | None = None
    speed: str | None = None  # regular | express | super_express
    channel: str | None = None  # domestic | mission
    applicant: str | None = None
    tokens: set[str] = field(default_factory=set)

    def to_dict(self) -> dict[str, Any]:
        return {
            "domains": self.domains,
            "passport_type": self.passport_type,
            "action": self.action,
            "speed": self.speed,
            "channel": self.channel,
            "applicant": self.applicant,
            "tokens": sorted(self.tokens),
        }


def extract_domain_entities(message: str) -> DomainEntities:
    text = message.lower()
    entities = DomainEntities()
    aliases = load_capability_aliases()

    # Tokenize for overlap scoring
    entities.tokens = set(re.findall(r"[\u0980-\u09FF]+|[a-z0-9]+", text))

    # Domain detection
    for domain, cfg in aliases.get("domain_triggers", {}).items():
        tokens = [t.lower() for t in cfg.get("tokens", [])]
        if _text_has_any(text, tokens):
            entities.domains.append(domain)

    groups = aliases.get("capability_groups", {})

    if _group_hit(text, groups.get("e_passport", {})):
        entities.passport_type = "e_passport"
    if re.search(r"\bpassport\s+e\b|\be[\s-]?passport\b", text):
        entities.passport_type = "e_passport"
    if _group_hit(text, groups.get("mrp", {})):
        entities.passport_type = "mrp" if entities.passport_type is None else entities.passport_type

    if _group_hit(text, groups.get("express", {})):
        if "super" in text or "সুপার" in text:
            entities.speed = "super_express"
        else:
            entities.speed = "express"

    if _group_hit(text, groups.get("reissue", {})):
        if any(w in text for w in ["renew", "renewal", "নবায়ন"]):
            entities.action = "renewal"
        else:
            entities.action = "reissue"

    if _group_hit(text, groups.get("lost", {})):
        entities.action = "lost"
    if _group_hit(text, groups.get("correction", {})):
        entities.action = "correction"
    if _group_hit(text, groups.get("firearms", {})):
        if "firearms" not in entities.domains:
            entities.domains.append("firearms")
        # Firearms licence is not transport/driving
        if "transport" in entities.domains:
            entities.domains.remove("transport")
    elif _group_hit(text, groups.get("driving_licence", {})):
        if "transport" not in entities.domains:
            entities.domains.append("transport")

    if _group_hit(text, groups.get("fee", {})):
        entities.action = entities.action or "fee"
    if _group_hit(text, groups.get("payment", {})):
        entities.action = entities.action or "payment"
    if _group_hit(text, groups.get("status", {})):
        entities.action = entities.action or "status"
    if _group_hit(text, groups.get("appointment", {})):
        entities.action = entities.action or "appointment"
    if _group_hit(text, groups.get("application", {})) or re.search(r"\bnew\b", text):
        entities.action = entities.action or "new"

    if _group_hit(text, groups.get("mission", {})):
        entities.channel = "mission"
    elif any(w in text for w in ["online", "অনলাইন", "অনলাইনে"]):
        entities.channel = "online"
    else:
        entities.channel = "domestic"

    if any(w in text for w in ["minor", "child", "children", "শিশু"]):
        entities.applicant = "minor"
    elif any(w in text for w in ["expatriate", "abroad", "bidesh", "mission", "dubai", "singapore"]):
        entities.applicant = "expatriate"

    return entities


def _text_has_any(text: str, tokens: list[str]) -> bool:
    return any(token in text for token in tokens if token)


def _group_hit(text: str, group: dict[str, Any]) -> bool:
    if not group:
        return False
    tokens: list[str] = []
    for key in ("synonyms_en", "synonyms_bn", "synonyms_banglish"):
        tokens.extend(group.get(key) or [])
    return _text_has_any(text, [t.lower() for t in tokens])
