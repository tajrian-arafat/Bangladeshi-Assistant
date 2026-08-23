#!/usr/bin/env python3
"""Load seed data into the BDA database."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from uuid import uuid4

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import select  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.core.database import session_scope  # noqa: E402
from app.domain.models.auth import AdminUser, Permission, Role, RolePermission  # noqa: E402
from app.domain.models.geography import District, Division  # noqa: E402
from app.domain.models.knowledge import (  # noqa: E402
    Agency,
    ChecklistItem,
    Procedure,
    ProcedureStep,
    Service,
)
from app.domain.models.operations import FeatureFlag  # noqa: E402
from app.core.security import hash_password  # noqa: E402

SEEDS_DIR = REPO_ROOT / "data" / "seeds"


async def seed_divisions_districts() -> None:
    path = SEEDS_DIR / "divisions_districts.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    async with session_scope() as session:
        for div_data in data["divisions"]:
            existing = await session.execute(
                select(Division).where(Division.slug == div_data["slug"])
            )
            division = existing.scalar_one_or_none()
            if not division:
                division = Division(
                    id=uuid4(),
                    slug=div_data["slug"],
                    name_bn=div_data["name_bn"],
                    name_en=div_data["name_en"],
                )
                session.add(division)
                await session.flush()

            for dist_data in div_data["districts"]:
                dist_exists = await session.execute(
                    select(District).where(District.slug == dist_data["slug"])
                )
                if dist_exists.scalar_one_or_none():
                    continue
                session.add(
                    District(
                        id=uuid4(),
                        division_id=division.id,
                        slug=dist_data["slug"],
                        name_bn=dist_data["name_bn"],
                        name_en=dist_data["name_en"],
                    )
                )
    print(f"Seeded divisions and districts from {path.name}")


async def seed_agencies() -> dict[str, Agency]:
    path = SEEDS_DIR / "agencies.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    agencies: dict[str, Agency] = {}

    async with session_scope() as session:
        for agency_data in data["agencies"]:
            result = await session.execute(
                select(Agency).where(Agency.slug == agency_data["slug"])
            )
            agency = result.scalar_one_or_none()
            if not agency:
                agency = Agency(
                    id=uuid4(),
                    slug=agency_data["slug"],
                    name_bn=agency_data["name_bn"],
                    name_en=agency_data["name_en"],
                    acronym=agency_data.get("acronym"),
                    description_bn=agency_data.get("description_bn"),
                    description_en=agency_data.get("description_en"),
                    website_url=agency_data.get("website_url"),
                    is_active=True,
                )
                session.add(agency)
                await session.flush()
            agencies[agency.slug] = agency
    print(f"Seeded {len(agencies)} agencies from {path.name}")
    return agencies


async def seed_services() -> None:
    path = SEEDS_DIR / "mvp_services.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    async with session_scope() as session:
        agency_map: dict[str, Agency] = {}
        agency_result = await session.execute(select(Agency))
        for agency in agency_result.scalars().all():
            agency_map[agency.slug] = agency

        for svc_data in data["services"]:
            existing = await session.execute(
                select(Service).where(Service.slug == svc_data["slug"])
            )
            if existing.scalar_one_or_none():
                continue

            agency = agency_map.get(svc_data["agency_slug"])
            if not agency:
                print(f"Warning: agency {svc_data['agency_slug']} not found, skipping {svc_data['slug']}")
                continue

            service = Service(
                id=uuid4(),
                slug=svc_data["slug"],
                name_bn=svc_data["name_bn"],
                name_en=svc_data["name_en"],
                aliases=svc_data.get("aliases"),
                agency_id=agency.id,
                category=svc_data["category"],
                status=svc_data.get("status", "UNDER_REVIEW"),
                eligibility=svc_data.get("eligibility"),
                review_state="DRAFT",
                version=1,
            )
            session.add(service)
            await session.flush()

            proc_data = svc_data.get("procedure")
            if proc_data:
                procedure = Procedure(
                    id=uuid4(),
                    service_id=service.id,
                    version=1,
                    key=proc_data["key"],
                    title_bn=proc_data["title_bn"],
                    title_en=proc_data["title_en"],
                    is_active=True,
                )
                session.add(procedure)
                await session.flush()

                for step_data in proc_data.get("steps", []):
                    session.add(
                        ProcedureStep(
                            id=uuid4(),
                            procedure_id=procedure.id,
                            order=step_data["order"],
                            key=step_data["key"],
                            title_bn=step_data["title_bn"],
                            title_en=step_data["title_en"],
                            description_bn=step_data.get("description_bn"),
                            description_en=step_data.get("description_en"),
                            official_url=step_data.get("official_url"),
                            status="active",
                        )
                    )

            for item_data in svc_data.get("checklist_items", []):
                session.add(
                    ChecklistItem(
                        id=uuid4(),
                        service_id=service.id,
                        order=item_data["order"],
                        item_type=item_data["item_type"],
                        label_bn=item_data["label_bn"],
                        label_en=item_data["label_en"],
                        conditions=item_data.get("conditions"),
                    )
                )

    print(f"Seeded MVP services from {path.name}")


async def seed_roles_and_flags() -> None:
    async with session_scope() as session:
        roles_data = [
            ("super_admin", "Full system access"),
            ("knowledge_editor", "CRUD services and sources"),
            ("reviewer", "Approve/reject changes"),
            ("ops_admin", "Crawls and feature flags"),
            ("auditor", "Read-only audit access"),
        ]
        for name, desc in roles_data:
            result = await session.execute(select(Role).where(Role.name == name))
            if not result.scalar_one_or_none():
                session.add(Role(id=uuid4(), name=name, description=desc))

        flags_data = [
            ("FEATURE_DOCUMENT_UPLOAD", False, "Enable document upload and OCR"),
            ("FEATURE_PLAYWRIGHT_CRAWL", False, "Enable Playwright-based crawling"),
            ("FEATURE_LLM_ENABLED", True, "Enable local LLM for chat responses"),
        ]
        for key, enabled, description in flags_data:
            result = await session.execute(select(FeatureFlag).where(FeatureFlag.key == key))
            if not result.scalar_one_or_none():
                session.add(
                    FeatureFlag(id=uuid4(), key=key, enabled=enabled, description=description)
                )

        admin_result = await session.execute(
            select(AdminUser).where(AdminUser.email == "admin@example.local")
        )
        if not admin_result.scalar_one_or_none():
            admin = AdminUser(
                id=uuid4(),
                email="admin@example.local",
                password_hash=hash_password("change-me-admin"),
                display_name="Default Admin",
                is_active=True,
            )
            session.add(admin)

        perm_result = await session.execute(
            select(Permission).where(Permission.code == "admin.dashboard.read")
        )
        if not perm_result.scalar_one_or_none():
            perm = Permission(
                id=uuid4(), code="admin.dashboard.read", description="Read admin dashboard"
            )
            session.add(perm)
            await session.flush()
            role_result = await session.execute(select(Role).where(Role.name == "super_admin"))
            role = role_result.scalar_one_or_none()
            if role:
                session.add(
                    RolePermission(id=uuid4(), role_id=role.id, permission_id=perm.id)
                )

    print("Seeded roles, feature flags, and default admin user")


async def run_all() -> None:
    settings = get_settings()
    db_path = settings.database_url.replace("sqlite+aiosqlite:///", "")
    if db_path.startswith("./"):
        Path(BACKEND_DIR / db_path[2:]).parent.mkdir(parents=True, exist_ok=True)

    await seed_divisions_districts()
    await seed_agencies()
    await seed_services()
    await seed_roles_and_flags()
    print("Database seeding complete.")


def main() -> None:
    asyncio.run(run_all())


if __name__ == "__main__":
    main()
