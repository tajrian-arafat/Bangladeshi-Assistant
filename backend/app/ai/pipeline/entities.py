"""Entity extraction using gazetteers and fuzzy matching."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

from rapidfuzz import fuzz
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models.claims import Claim
from app.domain.models.geography import District
from app.domain.models.knowledge import Agency, Service, ServiceLink


# Explicit phrase → preferred runtime slug (Batch 1 + MVP seeds).
# Longer / more specific phrases MUST come first.
PHRASE_SERVICE_HINTS: list[tuple[str, str]] = [
    ("everify.bdris.gov.bd", "civil-birth-death-verify"),
    ("everify", "civil-birth-death-verify"),
    ("birth and death verify", "civil-birth-death-verify"),
    ("birth death verify", "civil-birth-death-verify"),
    ("verify birth", "civil-birth-death-verify"),
    ("verify death", "civil-birth-death-verify"),
    ("birth certificate online", "civil-birth-death-verify"),
    ("জন্ম সনদ অনলাইন", "civil-birth-death-verify"),
    ("যাচাই", "civil-birth-death-verify"),
    ("জন্ম মৃত্যু যাচাই", "civil-birth-death-verify"),
    ("birth registration correction", "civil-birth-registration-correction"),
    ("birth registration dob correction", "civil-birth-registration-correction"),
    ("birth date", "civil-birth-registration-correction"),
    ("dob correction", "civil-birth-registration-correction"),
    ("birth correction", "civil-birth-registration-correction"),
    ("জন্ম সংশোধন", "civil-birth-registration-correction"),
    ("জন্ম তথ্য সংশোধন", "civil-birth-registration-correction"),
    ("জন্ম সনদে নাম", "civil-birth-registration-correction"),
    ("birth registration copy", "civil-birth-registration-copy"),
    ("birth cert copy", "civil-birth-registration-copy"),
    ("birth certificate copy", "civil-birth-registration-copy"),
    ("duplicate birth", "civil-birth-registration-copy"),
    ("death registration correction", "civil-death-registration-correction"),
    ("death registration other info correction", "civil-death-registration-correction"),
    ("death correction", "civil-death-registration-correction"),
    ("death registration copy", "civil-death-registration-copy"),
    ("death certificate copy", "civil-death-registration-copy"),
    ("death registration", "civil-death-registration"),
    ("মৃত্যু নিবন্ধন", "civil-death-registration"),
    ("nid claim", "nid-claim-account"),
    ("claim account", "nid-claim-account"),
    ("ক্লেইম", "nid-claim-account"),
    ("অ্যাকাউন্ট ক্লেইম", "nid-claim-account"),
    ("online account registration", "nid-online-account-registration"),
    ("nid portal account", "nid-online-account-registration"),
    ("photo signature", "nid-photo-signature-appointment"),
    ("signature appointment", "nid-photo-signature-appointment"),
    ("voter area change", "nid-voter-area-change"),
    ("birth registration", "birth-registration"),
    ("জন্ম নিবন্ধন", "birth-registration"),
    ("জন্ম সনদ", "birth-registration"),
    ("nid reissue", "nid-reissue-lost"),
    ("lost nid", "nid-reissue-lost"),
    ("nid lost", "nid-reissue-lost"),
    ("হারানো এনআইডি", "nid-reissue-lost"),
    ("nid correction", "nid-correction"),
    ("nid card correction", "nid-correction"),
    ("এনআইডি সংশোধন", "nid-correction"),
    ("nid fee calculator", "nid-fee-calculator"),
    ("fee calculator", "nid-fee-calculator"),
    ("voter slip", "identity-voter-slip-download"),
    ("marriage registration", "civil-marriage-registration"),
    ("বিবাহ নিবন্ধন", "civil-marriage-registration"),
    ("passport renew", "passport-renewal"),
    ("driving licence", "driving-licence-renewal"),
    ("tin registration", "tin-registration"),
]


async def extract_entities(session: AsyncSession, message: str) -> dict[str, Any]:
    text = message.lower()
    entities: dict[str, Any] = {}

    services = (
        await session.execute(select(Service).options(selectinload(Service.service_links)))
    ).scalars().all()
    by_slug = {s.slug: s for s in services}

    # Compound disambiguation before generic phrase match
    hinted: Service | None = None
    if ("birth" in text or "জন্ম" in text) and (
        "correct" in text or "correction" in text or "dob" in text or "সংশোধন" in text or "ভুল" in text
    ):
        hinted = by_slug.get("civil-birth-registration-correction")
    elif ("birth" in text or "জন্ম" in text) and (
        "copy" in text or "duplicate" in text or "অনুলিপি" in text
    ):
        hinted = by_slug.get("civil-birth-registration-copy")
    elif "birth certificate copy" in text or "birth cert copy" in text:
        hinted = by_slug.get("civil-birth-registration-copy")
    elif ("death" in text or "মৃত্যু" in text) and (
        "correct" in text or "correction" in text or "সংশোধন" in text
    ):
        hinted = by_slug.get("civil-death-registration-correction")
    elif ("death" in text or "মৃত্যু" in text) and ("copy" in text or "duplicate" in text):
        hinted = by_slug.get("civil-death-registration-copy")
    elif ("verify" in text or "verification" in text or "যাচাই" in text) and (
        "birth" in text or "death" in text or "জন্ম" in text or "সনদ" in text or "certificate" in text
    ):
        hinted = by_slug.get("civil-birth-death-verify")
    elif "claim" in text or "ক্লেইম" in text:
        hinted = by_slug.get("nid-claim-account")

    # 1) Explicit phrase / URL hints
    if not hinted:
        for phrase, slug in PHRASE_SERVICE_HINTS:
            if phrase in text and slug in by_slug:
                hinted = by_slug[slug]
                break
    if not hinted:
        for svc in services:
            for link in svc.service_links or []:
                host = urlparse(link.url).netloc.lower()
                if host and host in text:
                    hinted = svc
                    break
            if hinted:
                break

    # 2) Fuzzy / Bangla name match with published-claim boost
    published_ids = set(
        (
            await session.execute(
                select(Claim.service_id).where(Claim.is_published.is_(True)).distinct()
            )
        ).scalars().all()
    )

    best_service: Service | None = None
    best_score = 0.0
    for service in services:
        candidates = [
            service.slug.replace("-", " "),
            service.name_en.lower(),
            service.name_bn,
            *((service.aliases or [])),
        ]
        for candidate in candidates:
            cand = (candidate or "").lower()
            if not cand:
                continue
            # Exact / substring boost
            if cand in text or text in cand:
                score = 100.0
            else:
                score = float(fuzz.partial_ratio(cand, text))
            if service.id in published_ids:
                score += 5.0
            # Prefer longer exact slug token overlap
            slug_tokens = set(service.slug.split("-"))
            msg_tokens = set(re.findall(r"[\u0980-\u09FF]+|[a-z0-9]+", text))
            overlap = len(slug_tokens & msg_tokens)
            score += overlap * 3.0
            if score > best_score and score >= 75:
                best_score = score
                best_service = service

    chosen = hinted or best_service
    if chosen:
        entities["service"] = chosen
        entities["service_slug"] = chosen.slug
        entities["service_match_score"] = best_score if not hinted else 100.0
        entities["service_match_method"] = "phrase_hint" if hinted else "fuzzy"

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
