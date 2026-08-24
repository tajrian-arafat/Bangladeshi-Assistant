#!/usr/bin/env python3
"""Build master service catalogue from discovery sources.

Discovery phase only — no requirements/fees/procedures.
Outputs to /data/service_catalogue/
"""

from __future__ import annotations

import json
import re
import uuid
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CATALOGUE_DIR = REPO_ROOT / "data" / "service_catalogue"
SOURCES_DIR = CATALOGUE_DIR / "sources"
BY_CATEGORY_DIR = CATALOGUE_DIR / "by_category"
CATALOGUE_VERSION = "0.1.0-discovery"
DISCOVERED_AT = "2026-08-24"

# Canonical duplicate mappings (legacy/MVP slug -> canonical service_id)
DUPLICATE_ALIASES: dict[str, str] = {
    "passport-renewal": "epassport-reissue",
    "passport-reissue": "epassport-reissue",
    "driving-licence-renewal": "brta-driving-license-renewal",
    "nid-correction": "nid-card-info-correction",
    "birth-registration": "civil-birth-registration",
    "tin-registration": "tax-etin-registration",
    "birth-certificate": "civil-birth-registration",
    "death-certificate-bris": "civil-death-registration",
    "death-certificate-union": "local-death-certificate-union",
    "voter-registration": "nid-new-voter-registration",
    "e-passport-renewal": "epassport-reissue",
    "e-passport-application": "epassport-new-application",
    "mrp-passport-initial": "passport-mrp-initial",
    "mrp-passport-reissue": "passport-mrp-reissue",
    "agri-livestock-registration": "agriculture-livestock-farm-registration",
}

AUTHORITY_SLUG_MAP: dict[str, str] = {
    "Department of Immigration and Passports (DIP)": "dip",
    "Department of Immigration and Passports": "dip",
    "Bangladesh Election Commission (NID Wing)": "ec-nid",
    "Bangladesh Election Commission": "ec-nid",
    "Bangladesh Road Transport Authority (BRTA)": "brta",
    "Bangladesh Road Transport Authority": "brta",
    "Office of the Registrar General, Birth and Death Registration": "bdris",
    "Office of the Registrar General, Birth and Death Registration (Local Government Division)": "bdris",
    "National Board of Revenue (NBR)": "nbr",
    "National Board of Revenue - Customs": "nbr",
    "Ministry of Land": "ministry-land",
    "Ministry of Land (DLRMS)": "ministry-land",
    "Registrar of Joint Stock Companies and Firms (RJSC)": "rjsc",
    "Bangladesh Police": "police",
    "Directorate General of Health Services (DGHS)": "dghs",
    "Bangladesh Medical and Dental Council (BMDC)": "bmdc",
    "Bureau of Manpower, Employment and Training (BMET)": "bmet",
    "Department of Social Services (DSS)": "dss",
    "Union Parishad": "union-parishad",
    "Dhaka North City Corporation (DNCC)": "dncc",
    "Dhaka South City Corporation (DSCC)": "dscc",
}


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:128]


def normalize_entry(raw: dict) -> dict:
    """Normalize raw discovery record to catalogue schema."""
    service_id = raw.get("service_id") or slugify(raw.get("service_name_en", "unknown"))
    target = raw.get("target_user", ["citizen"])
    if isinstance(target, str):
        target = [target]

    official = raw.get("official_source")
    discovery = raw.get("discovery_sources") or []
    if official and official not in discovery:
        discovery = [official, *discovery]

    status = raw.get("status") or raw.get("discovery_status", "NEEDS_VERIFICATION")
    if status not in {"CONFIRMED", "LIKELY", "NEEDS_VERIFICATION", "DEPRECATED", "DUPLICATE"}:
        status_map = {
            "CONFIRMED": "CONFIRMED",
            "LIKELY": "LIKELY",
            "NEEDS_VERIFICATION": "NEEDS_VERIFICATION",
        }
        status = status_map.get(raw.get("discovery_status", ""), "NEEDS_VERIFICATION")

    authority = raw.get("responsible_authority", "Unknown")
    entry = {
        "service_id": service_id,
        "uuid": str(uuid.uuid5(uuid.NAMESPACE_URL, f"bd-gov-service:{service_id}")),
        "service_name_bn": raw.get("service_name_bn"),
        "service_name_en": raw.get("service_name_en", service_id),
        "aliases": list(dict.fromkeys(raw.get("aliases") or [])),
        "category": raw.get("category", "OTHER"),
        "subcategory": raw.get("subcategory", "general"),
        "responsible_authority": authority,
        "authority_id": raw.get("authority_id") or AUTHORITY_SLUG_MAP.get(authority),
        "target_user": target,
        "geographic_scope": raw.get("geographic_scope", "NATIONAL"),
        "lifecycle_stage": raw.get("lifecycle_stage") or [],
        "official_source": official,
        "discovery_sources": discovery,
        "status": status,
        "canonical_service_id": raw.get("canonical_service_id"),
        "notes": raw.get("notes"),
        "discovered_at": raw.get("discovered_at", DISCOVERED_AT),
        "catalogue_version": CATALOGUE_VERSION,
    }
    return entry


def load_json_sources() -> list[dict]:
    records: list[dict] = []
    for path in sorted(SOURCES_DIR.glob("*.json")):
        if path.name == "social_protection_programs.json":
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            records.extend(data)
        elif isinstance(data, dict) and "services" in data:
            records.extend(data["services"])
    return records


def load_social_protection_programs() -> list[dict]:
    path = SOURCES_DIR / "social_protection_programs.json"
    if not path.exists():
        return []
    programs = json.loads(path.read_text(encoding="utf-8"))
    services: list[dict] = []
    for item in programs:
        prog = item["program"]
        ministry = item["ministry"]
        sid = f"snp-{slugify(prog)}"
        services.append(
            {
                "service_id": sid,
                "service_name_bn": None,
                "service_name_en": prog,
                "aliases": [prog],
                "category": "SOCIAL_PROTECTION",
                "subcategory": "social_security_program",
                "responsible_authority": ministry,
                "target_user": ["citizen"],
                "geographic_scope": "NATIONAL",
                "lifecycle_stage": ["social_protection"],
                "official_source": "https://socialprotection.gov.bd/all-social-security-programmes-implemented-by-ministriesdivisions/",
                "discovery_sources": [
                    "https://socialprotection.gov.bd/all-social-security-programmes-implemented-by-ministriesdivisions/",
                ],
                "status": "CONFIRMED",
                "notes": "Listed on official SSPS programme inventory (NSSS). Name-only discovery; eligibility not catalogued.",
            }
        )
    return services


def load_curated_extensions() -> list[dict]:
    """Additional lifecycle and cross-cutting services from official discovery."""
    path = SOURCES_DIR / "curated_extensions.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return []


def deduplicate_services(services: list[dict]) -> tuple[list[dict], list[dict]]:
    """Aggressive deduplication. Returns (canonical_services, duplicate_records)."""
    by_id: dict[str, dict] = {}
    duplicates: list[dict] = []

    def merge(existing: dict, incoming: dict) -> dict:
        merged = existing.copy()
        merged["aliases"] = list(
            dict.fromkeys(
                (existing.get("aliases") or [])
                + (incoming.get("aliases") or [])
                + [incoming.get("service_name_en", "")]
            )
        )
        if incoming.get("service_name_bn") and not existing.get("service_name_bn"):
            merged["service_name_bn"] = incoming["service_name_bn"]
        # Prefer CONFIRMED > LIKELY > NEEDS_VERIFICATION
        rank = {"CONFIRMED": 3, "LIKELY": 2, "NEEDS_VERIFICATION": 1, "DEPRECATED": 0, "DUPLICATE": 0}
        if rank.get(incoming["status"], 0) > rank.get(existing["status"], 0):
            merged["status"] = incoming["status"]
        if not merged.get("official_source") and incoming.get("official_source"):
            merged["official_source"] = incoming["official_source"]
        merged["discovery_sources"] = list(
            dict.fromkeys((existing.get("discovery_sources") or []) + (incoming.get("discovery_sources") or []))
        )
        return merged

    for svc in services:
        sid = svc["service_id"]
        if sid in DUPLICATE_ALIASES:
            canonical = DUPLICATE_ALIASES[sid]
            dup = svc.copy()
            dup["status"] = "DUPLICATE"
            dup["canonical_service_id"] = canonical
            duplicates.append(dup)
            continue

        if sid in by_id:
            by_id[sid] = merge(by_id[sid], svc)
        else:
            by_id[sid] = svc

    # Second pass: alias-based merge hints (same English name)
    name_index: dict[str, str] = {}
    for sid, svc in list(by_id.items()):
        key = re.sub(r"[^a-z0-9]", "", svc["service_name_en"].lower())
        if key in name_index and name_index[key] != sid:
            # Mark lower-confidence as duplicate if same normalized name
            other_sid = name_index[key]
            other = by_id[other_sid]
            rank = {"CONFIRMED": 3, "LIKELY": 2, "NEEDS_VERIFICATION": 1}
            if rank.get(svc["status"], 0) < rank.get(other["status"], 0):
                dup = svc.copy()
                dup["status"] = "DUPLICATE"
                dup["canonical_service_id"] = other_sid
                duplicates.append(dup)
                del by_id[sid]
            elif rank.get(svc["status"], 0) == rank.get(other["status"], 0) and sid != other_sid:
                # Keep both but note potential overlap in notes
                svc["notes"] = (svc.get("notes") or "") + f" Potential overlap with {other_sid}."
        else:
            name_index[key] = sid

    # Explicit duplicate entries for MVP seed slugs not in catalogue
    for alias_id, canonical_id in DUPLICATE_ALIASES.items():
        if alias_id not in by_id and canonical_id in by_id:
            canonical = by_id[canonical_id]
            duplicates.append(
                {
                    **canonical,
                    "service_id": alias_id,
                    "status": "DUPLICATE",
                    "canonical_service_id": canonical_id,
                    "notes": f"MVP/legacy alias merged into {canonical_id}.",
                }
            )

    canonical = sorted(by_id.values(), key=lambda x: x["service_id"])
    return canonical, duplicates


def build_authorities(services: list[dict]) -> list[dict]:
    auth_map: dict[str, dict] = {}
    for svc in services:
        name = svc["responsible_authority"]
        slug = svc.get("authority_id") or slugify(name)[:64]
        if slug not in auth_map:
            auth_map[slug] = {
                "authority_id": slug,
                "name_en": name,
                "name_bn": None,
                "service_count": 0,
                "categories": set(),
            }
        auth_map[slug]["service_count"] += 1
        auth_map[slug]["categories"].add(svc["category"])

    authorities = []
    for a in sorted(auth_map.values(), key=lambda x: x["authority_id"]):
        a["categories"] = sorted(a["categories"])
        authorities.append(a)
    return authorities


def write_outputs(services: list[dict], duplicates: list[dict], authorities: list[dict]) -> dict:
    CATALOGUE_DIR.mkdir(parents=True, exist_ok=True)
    BY_CATEGORY_DIR.mkdir(parents=True, exist_ok=True)

    catalogue = {
        "catalogue_version": CATALOGUE_VERSION,
        "discovered_at": DISCOVERED_AT,
        "disclaimer": (
            "This is a discovery-phase inventory. It does NOT claim to list all Bangladesh "
            "government services. Completeness is measured via coverage metrics, not asserted."
        ),
        "total_entries": len(services) + len(duplicates),
        "canonical_services": len(services),
        "duplicate_entries": len(duplicates),
        "services": services,
    }
    (CATALOGUE_DIR / "services.json").write_text(
        json.dumps(catalogue, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    (CATALOGUE_DIR / "duplicates.json").write_text(
        json.dumps({"duplicates": duplicates}, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    (CATALOGUE_DIR / "authorities.json").write_text(
        json.dumps({"authorities": authorities}, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Split by category
    by_cat: dict[str, list] = defaultdict(list)
    for svc in services:
        by_cat[svc["category"]].append(svc)
    for cat, items in sorted(by_cat.items()):
        (BY_CATEGORY_DIR / f"{cat.lower()}.json").write_text(
            json.dumps({"category": cat, "count": len(items), "services": items}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    status_counts = Counter(s["status"] for s in services)
    category_counts = Counter(s["category"] for s in services)

    metadata = {
        "catalogue_version": CATALOGUE_VERSION,
        "discovered_at": DISCOVERED_AT,
        "canonical_services": len(services),
        "duplicate_entries": len(duplicates),
        "status_counts": dict(status_counts),
        "category_counts": dict(category_counts),
        "authority_count": len(authorities),
    }
    (CATALOGUE_DIR / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return metadata


def main() -> None:
    raw_records = []
    raw_records.extend(load_json_sources())
    raw_records.extend(load_social_protection_programs())
    raw_records.extend(load_curated_extensions())

    normalized = [normalize_entry(r) for r in raw_records]
    services, duplicates = deduplicate_services(normalized)
    authorities = build_authorities(services)
    metadata = write_outputs(services, duplicates, authorities)

    print(f"Built catalogue: {metadata['canonical_services']} canonical services")
    print(f"Duplicates: {metadata['duplicate_entries']}")
    print(f"Status: {metadata['status_counts']}")
    print(f"Categories: {len(metadata['category_counts'])}")


if __name__ == "__main__":
    main()
