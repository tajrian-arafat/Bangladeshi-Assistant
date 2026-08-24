"""Entity extraction — delegates service routing to intent-aware ServiceRouter."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.routing.domain_entities import extract_domain_entities
from app.ai.routing.intent_classifier import IntentResult, classify_intents
from app.ai.routing.service_router import ServiceRouter
from app.domain.models.geography import District
from app.domain.models.knowledge import Agency


async def extract_entities(
    session: AsyncSession,
    message: str,
    *,
    intents: IntentResult | None = None,
    clarifications: dict[str, Any] | None = None,
) -> dict[str, Any]:
    text = message.lower()
    entities: dict[str, Any] = {}

    intent_result = intents or classify_intents(message, clarifications)
    domain_entities = extract_domain_entities(message)
    entities["intents"] = {
        "primary": intent_result.primary,
        "secondary": intent_result.secondary,
        "legacy": intent_result.legacy_primary(),
    }
    entities["intent_primary"] = intent_result.primary
    entities["intent_secondary"] = intent_result.secondary
    entities["domain_entities"] = domain_entities.to_dict()

    router = ServiceRouter(session)
    routing = await router.route(
        message,
        intents=intent_result,
        clarifications=clarifications,
    )

    entities["routing_candidates"] = [
        {
            "slug": c.service.slug,
            "score": round(c.score, 2),
            "reasons": c.reasons[:6],
        }
        for c in routing.candidates[:5]
    ]

    if routing.clarification:
        entities["routing_clarification"] = routing.clarification

    if routing.service:
        entities["service"] = routing.service
        entities["service_slug"] = routing.service.slug
        entities["service_match_score"] = routing.score
        entities["service_match_method"] = routing.method

    agencies = (await session.execute(select(Agency))).scalars().all()
    for agency in agencies:
        if agency.slug in text or agency.name_en.lower() in text:
            entities["agency"] = agency
            entities["agency_slug"] = agency.slug
            break

    districts = (await session.execute(select(District))).scalars().all()
    for district in districts:
        if district.name_en.lower() in text or district.slug in text:
            entities["district"] = district.name_en
            break

    if "mirpur" in text:
        entities["location"] = {"name": "Mirpur", "district": "Dhaka", "confidence": 0.82}

    return entities
