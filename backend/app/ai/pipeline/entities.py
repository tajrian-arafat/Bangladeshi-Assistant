"""Entity extraction using gazetteers and fuzzy matching."""

from __future__ import annotations

from typing import Any

from rapidfuzz import fuzz
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.geography import District
from app.domain.models.knowledge import Agency, Service


async def extract_entities(session: AsyncSession, message: str) -> dict[str, Any]:
    text = message.lower()
    entities: dict[str, Any] = {}

    services = (await session.execute(select(Service))).scalars().all()
    best_service: Service | None = None
    best_score = 0
    for service in services:
        candidates = [service.slug.replace("-", " "), service.name_en.lower(), *(
            (service.aliases or [])
        )]
        for candidate in candidates:
            score = fuzz.partial_ratio(candidate.lower(), text)
            if score > best_score and score >= 75:
                best_score = score
                best_service = service
    if best_service:
        entities["service"] = best_service
        entities["service_slug"] = best_service.slug

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
