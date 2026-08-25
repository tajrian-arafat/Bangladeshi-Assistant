"""Safe catalogue → runtime Service synchronization (no claim verification)."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationError
from app.domain.enums import (
    CatalogueMappingReviewStatus,
    CatalogueMappingStatus,
    CatalogueMappingType,
)
from app.domain.models.claims import ServiceCatalogueMapping
from app.domain.models.knowledge import Agency, Service
from app.domain.models.operations import AuditLog

EXCLUDED_CATALOGUE_STATUSES = {
    "UNVERIFIED",
    "NOT_A_SERVICE",
    "DUPLICATE",
    "DEPRECATED",
    "MERGED",
}

MVP_SEED_SLUGS_DEFAULT = {
    "passport-renewal",
    "nid-correction",
    "driving-licence-renewal",
    "birth-registration",
    "tin-registration",
}

TERMINAL_OK = {
    CatalogueMappingStatus.EXACT_MATCH.value,
    CatalogueMappingStatus.ALIAS_MATCH.value,
    CatalogueMappingStatus.MERGED_MATCH.value,
    CatalogueMappingStatus.NEW_RUNTIME_SERVICE.value,
    CatalogueMappingStatus.REVIEW_REQUIRED.value,
}


@dataclass
class SyncAction:
    action: str
    catalogue_service_id: str
    runtime_slug: str | None = None
    mapping_status: str | None = None
    detail: str | None = None


@dataclass
class SyncReport:
    dry_run: bool
    proposed_create_services: int = 0
    proposed_create_agencies: int = 0
    proposed_mappings: int = 0
    unchanged: int = 0
    review_required: int = 0
    excluded: int = 0
    errors: list[str] = field(default_factory=list)
    actions: list[SyncAction] = field(default_factory=list)
    status_counts: dict[str, int] = field(default_factory=dict)
    confirmed_total: int = 0
    mapped_or_review: int = 0

    @property
    def ok(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "dry_run": self.dry_run,
            "confirmed_total": self.confirmed_total,
            "mapped_or_review": self.mapped_or_review,
            "proposed_create_services": self.proposed_create_services,
            "proposed_create_agencies": self.proposed_create_agencies,
            "proposed_mappings": self.proposed_mappings,
            "unchanged": self.unchanged,
            "review_required": self.review_required,
            "excluded": self.excluded,
            "status_counts": self.status_counts,
            "errors": self.errors,
            "actions_sample": [asdict(a) for a in self.actions[:50]],
            "actions_total": len(self.actions),
        }


class CatalogueRuntimeSync:
    def __init__(
        self,
        session: AsyncSession,
        *,
        repo_root: Path,
        dry_run: bool = True,
    ) -> None:
        self.session = session
        self.repo_root = repo_root
        self.dry_run = dry_run
        self.catalogue_path = repo_root / "data" / "service_catalogue" / "services.json"
        self.redirects_path = repo_root / "data" / "service_catalogue" / "redirects.json"
        self.authorities_path = repo_root / "data" / "service_catalogue" / "authorities.json"
        self.mappings_path = repo_root / "data" / "research" / "catalogue_runtime_mappings.json"

    def _load_json(self, path: Path) -> Any:
        return json.loads(path.read_text(encoding="utf-8"))

    def _file_mappings(self) -> dict[str, dict[str, Any]]:
        if not self.mappings_path.exists():
            return {}
        data = self._load_json(self.mappings_path)
        return {m["catalogue_service_id"]: m for m in data.get("mappings", [])}

    def _mvp_slugs(self) -> set[str]:
        if not self.mappings_path.exists():
            return set(MVP_SEED_SLUGS_DEFAULT)
        data = self._load_json(self.mappings_path)
        return set(data.get("mvp_seed_slugs") or MVP_SEED_SLUGS_DEFAULT)

    async def _audit(self, action: str, resource_id: str, after: dict) -> None:
        if self.dry_run:
            return
        self.session.add(
            AuditLog(
                action=action,
                resource_type="catalogue_runtime_sync",
                resource_id=resource_id,
                after_json=after,
            )
        )

    async def ensure_agencies(
        self, authority_ids: set[str], report: SyncReport
    ) -> dict[str, UUIDLikeAgency]:
        auth_data = self._load_json(self.authorities_path)
        by_id = {a["authority_id"]: a for a in auth_data.get("authorities", [])}
        result = await self.session.execute(select(Agency))
        existing = {a.slug: a for a in result.scalars().all()}
        out: dict[str, UUIDLikeAgency] = dict(existing)

        needed = set(authority_ids) | {"catalogue-sync"}
        for aid in sorted(needed):
            if not aid or aid in out:
                continue
            meta = by_id.get(aid, {})
            name_en = meta.get("name_en") or (
                "Catalogue Sync Agency" if aid == "catalogue-sync" else aid
            )
            name_bn = meta.get("name_bn") or (
                "ক্যাটালগ সিঙ্ক" if aid == "catalogue-sync" else name_en
            )
            report.proposed_create_agencies += 1
            report.actions.append(
                SyncAction(
                    action="would_create_agency" if self.dry_run else "created_agency",
                    catalogue_service_id="*",
                    runtime_slug=aid,
                    detail=str(name_en),
                )
            )
            if self.dry_run:
                out[aid] = _DryAgency(slug=aid)
                continue
            agency = Agency(
                slug=aid,
                name_bn=str(name_bn)[:512],
                name_en=str(name_en)[:512],
                description_en=f"Imported from catalogue authority {aid}",
            )
            self.session.add(agency)
            await self.session.flush()
            out[aid] = agency
            await self._audit("create_agency", aid, {"slug": aid, "name_en": name_en})
        return out

    def _decide(
        self,
        entry: dict[str, Any],
        *,
        file_map: dict[str, Any] | None,
        by_slug: dict[str, Service],
        by_catalogue: dict[str, Service],
        mvp_slugs: set[str],
        existing_map: ServiceCatalogueMapping | None = None,
    ) -> tuple[str, str, str, str, str | None]:
        """Return mapping_status, mapping_type, review_status, target_slug, notes."""
        cid = entry["service_id"]
        notes = file_map.get("notes") if file_map else None

        if file_map and file_map.get("runtime_slug"):
            slug = file_map["runtime_slug"]
            mtype = file_map.get("mapping_type") or CatalogueMappingType.EXISTING_SEED.value
            review = file_map.get("review_status") or CatalogueMappingReviewStatus.APPROVED.value
            prior_status = file_map.get("mapping_status") or (
                existing_map.mapping_status if existing_map else None
            )
            if mtype == CatalogueMappingType.ALIAS.value:
                status = CatalogueMappingStatus.ALIAS_MATCH.value
            elif mtype == CatalogueMappingType.MERGE.value:
                status = CatalogueMappingStatus.MERGED_MATCH.value
            elif (
                prior_status == CatalogueMappingStatus.NEW_RUNTIME_SERVICE.value
                or (
                    mtype == CatalogueMappingType.NEW_CANONICAL.value
                    and slug == cid
                )
            ):
                # Synced shell created from catalogue — keep distinct from seed EXACT_MATCH
                status = CatalogueMappingStatus.NEW_RUNTIME_SERVICE.value
            else:
                status = CatalogueMappingStatus.EXACT_MATCH.value
            if slug not in by_slug:
                return (
                    CatalogueMappingStatus.REVIEW_REQUIRED.value,
                    mtype,
                    CatalogueMappingReviewStatus.NEEDS_REVIEW.value,
                    slug,
                    notes or "runtime_slug missing in DB",
                )
            return status, mtype, review, slug, notes

        # Idempotent: keep NEW_RUNTIME_SERVICE once created for this canonical id.
        if (
            existing_map
            and existing_map.mapping_status
            == CatalogueMappingStatus.NEW_RUNTIME_SERVICE.value
            and (existing_map.runtime_slug == cid or cid in by_slug)
        ):
            return (
                CatalogueMappingStatus.NEW_RUNTIME_SERVICE.value,
                CatalogueMappingType.NEW_CANONICAL.value,
                existing_map.review_status
                or CatalogueMappingReviewStatus.APPROVED.value,
                existing_map.runtime_slug or cid,
                notes or existing_map.notes,
            )

        if cid in by_catalogue:
            svc = by_catalogue[cid]
            # Created by prior sync (slug == catalogue id)
            if svc.slug == cid:
                return (
                    CatalogueMappingStatus.NEW_RUNTIME_SERVICE.value,
                    CatalogueMappingType.NEW_CANONICAL.value,
                    CatalogueMappingReviewStatus.APPROVED.value,
                    svc.slug,
                    notes,
                )
            return (
                CatalogueMappingStatus.EXACT_MATCH.value,
                CatalogueMappingType.NEW_CANONICAL.value,
                CatalogueMappingReviewStatus.APPROVED.value,
                svc.slug,
                notes,
            )

        if cid in by_slug:
            svc = by_slug[cid]
            if svc.catalogue_service_id == cid or svc.slug == cid:
                return (
                    CatalogueMappingStatus.NEW_RUNTIME_SERVICE.value,
                    CatalogueMappingType.NEW_CANONICAL.value,
                    CatalogueMappingReviewStatus.APPROVED.value,
                    cid,
                    notes,
                )
            return (
                CatalogueMappingStatus.EXACT_MATCH.value,
                CatalogueMappingType.NEW_CANONICAL.value,
                CatalogueMappingReviewStatus.APPROVED.value,
                cid,
                notes,
            )

        # New runtime service — refuse colliding with MVP seed slug
        if cid in mvp_slugs:
            return (
                CatalogueMappingStatus.REVIEW_REQUIRED.value,
                CatalogueMappingType.NEW_CANONICAL.value,
                CatalogueMappingReviewStatus.NEEDS_REVIEW.value,
                cid,
                "catalogue id collides with MVP slug; add explicit mapping",
            )

        return (
            CatalogueMappingStatus.NEW_RUNTIME_SERVICE.value,
            CatalogueMappingType.NEW_CANONICAL.value,
            CatalogueMappingReviewStatus.APPROVED.value,
            cid,
            notes,
        )

    async def sync(self) -> SyncReport:
        report = SyncReport(dry_run=self.dry_run)
        catalogue = self._load_json(self.catalogue_path)
        services = catalogue.get("services", [])
        redirects = []
        if self.redirects_path.exists():
            redirects = self._load_json(self.redirects_path).get("redirects", [])

        for r in redirects:
            if r.get("status") in EXCLUDED_CATALOGUE_STATUSES:
                report.excluded += 1
        unverified = [s for s in services if s.get("status") == "UNVERIFIED"]
        report.excluded += len(unverified)

        confirmed = [s for s in services if s.get("status") == "CONFIRMED"]
        report.confirmed_total = len(confirmed)

        # Never create from excluded statuses
        for s in services:
            if s.get("status") in EXCLUDED_CATALOGUE_STATUSES and s.get("status") != "UNVERIFIED":
                # UNVERIFIED already counted; other excluded shouldn't be in services.json
                # but guard anyway
                pass

        file_maps = self._file_mappings()
        mvp_slugs = self._mvp_slugs()
        authority_ids = {s.get("authority_id") for s in confirmed if s.get("authority_id")}
        agencies = await self.ensure_agencies(authority_ids, report)

        result = await self.session.execute(select(Service))
        runtime_services = list(result.scalars().all())
        by_slug: dict[str, Service] = {s.slug: s for s in runtime_services}
        by_catalogue: dict[str, Service] = {
            s.catalogue_service_id: s for s in runtime_services if s.catalogue_service_id
        }

        map_result = await self.session.execute(select(ServiceCatalogueMapping))
        existing_maps = {m.catalogue_service_id: m for m in map_result.scalars().all()}

        # Preserve MVP: never delete/replace
        for slug in mvp_slugs:
            if slug not in by_slug and not self.dry_run:
                # Missing seed is not fatal for catalogue sync, but note it
                report.actions.append(
                    SyncAction(
                        action="mvp_seed_missing",
                        catalogue_service_id="*",
                        runtime_slug=slug,
                        detail="MVP seed not present; sync will not create it",
                    )
                )

        planned_new_slugs: set[str] = set()

        for entry in confirmed:
            cid = entry["service_id"]
            if entry.get("status") != "CONFIRMED":
                report.errors.append(f"Non-confirmed reached sync loop: {cid}")
                continue

            status, mtype, review, target_slug, notes = self._decide(
                entry,
                file_map=file_maps.get(cid),
                by_slug=by_slug,
                by_catalogue=by_catalogue,
                mvp_slugs=mvp_slugs,
                existing_map=existing_maps.get(cid),
            )

            runtime_service = by_slug.get(target_slug) if target_slug else None

            if status == CatalogueMappingStatus.NEW_RUNTIME_SERVICE.value:
                if target_slug in by_slug:
                    runtime_service = by_slug[target_slug]
                    owner = runtime_service.catalogue_service_id
                    if owner and owner != cid:
                        report.errors.append(
                            f"Duplicate slug conflict: {target_slug} owned by {owner}"
                        )
                        continue
                    # Already created by a prior sync — mapping only (idempotent)
                elif target_slug in planned_new_slugs:
                    report.errors.append(f"Duplicate slug prevented: {target_slug}")
                    continue
                else:
                    agency = agencies.get(entry.get("authority_id") or "") or agencies.get(
                        "catalogue-sync"
                    )
                    if agency is None:
                        report.errors.append(f"No agency available for {cid}")
                        continue
                    report.proposed_create_services += 1
                    planned_new_slugs.add(target_slug)
                    report.actions.append(
                        SyncAction(
                            action="would_create_service" if self.dry_run else "created_service",
                            catalogue_service_id=cid,
                            runtime_slug=target_slug,
                            mapping_status=status,
                            detail=entry.get("service_name_en"),
                        )
                    )
                    if not self.dry_run:
                        runtime_service = Service(
                            slug=target_slug,
                            name_bn=(
                                entry.get("service_name_bn")
                                or entry.get("service_name_en")
                                or cid
                            )[:512],
                            name_en=(entry.get("service_name_en") or cid)[:512],
                            aliases=entry.get("aliases") or [],
                            agency_id=agency.id,  # type: ignore[attr-defined]
                            category=entry.get("category") or "OTHER",
                            catalogue_service_id=cid,
                            status="UNDER_REVIEW",
                            review_state="DRAFT",
                            source_provenance=[
                                {
                                    "catalogue_service_id": cid,
                                    "synced_at": datetime.now(timezone.utc).isoformat(),
                                    "source": "catalogue_runtime_sync",
                                }
                            ],
                        )
                        self.session.add(runtime_service)
                        await self.session.flush()
                        by_slug[target_slug] = runtime_service
                        by_catalogue[cid] = runtime_service
                        await self._audit(
                            "create_service",
                            cid,
                            {"slug": target_slug, "catalogue_service_id": cid},
                        )

            if status == CatalogueMappingStatus.REVIEW_REQUIRED.value:
                report.review_required += 1

            # Back-link only (never rewrite MVP name/category/checklist/fees).
            # Alias/merge must not steal Service.catalogue_service_id (unique).
            if (
                runtime_service
                and not self.dry_run
                and not runtime_service.catalogue_service_id
                and status
                in {
                    CatalogueMappingStatus.EXACT_MATCH.value,
                    CatalogueMappingStatus.NEW_RUNTIME_SERVICE.value,
                }
                and mtype
                not in {
                    CatalogueMappingType.ALIAS.value,
                    CatalogueMappingType.MERGE.value,
                }
            ):
                runtime_service.catalogue_service_id = cid

            changed = await self._upsert_mapping(
                existing_maps,
                catalogue_service_id=cid,
                runtime_service=runtime_service if not self.dry_run else None,
                runtime_slug=target_slug,
                runtime_service_id_dry=None,
                mapping_type=mtype,
                mapping_status=status,
                review_status=review,
                notes=notes,
                provenance={
                    "reason": "catalogue_runtime_sync",
                    "catalogue_version": entry.get("catalogue_version"),
                    "authority_id": entry.get("authority_id"),
                    "official_source": entry.get("official_source"),
                    "synced_at": datetime.now(timezone.utc).isoformat(),
                    "dry_run": self.dry_run,
                },
            )
            if changed:
                report.proposed_mappings += 1
            else:
                report.unchanged += 1
            report.status_counts[status] = report.status_counts.get(status, 0) + 1

        # Validation
        for entry in confirmed:
            cid = entry["service_id"]
            m = existing_maps.get(cid)
            if not m:
                report.errors.append(f"Confirmed service not mapped: {cid}")
            elif m.mapping_status not in TERMINAL_OK:
                report.errors.append(
                    f"Confirmed service {cid} has non-terminal status {m.mapping_status}"
                )

        # No duplicate catalogue ids (unique constraint) — check alias groups don't
        # point one catalogue at two runtimes (impossible via our upsert)

        report.mapped_or_review = sum(
            1
            for entry in confirmed
            if (m := existing_maps.get(entry["service_id"])) and m.mapping_status in TERMINAL_OK
        )

        if report.errors:
            if not self.dry_run:
                await self.session.rollback()
            raise ValidationError(
                "Catalogue runtime sync validation failed: " + "; ".join(report.errors[:30])
            )

        if not self.dry_run:
            await self.session.flush()
            # reload maps for export
            map_result = await self.session.execute(select(ServiceCatalogueMapping))
            maps_now = {m.catalogue_service_id: m for m in map_result.scalars().all()}
            self._export_mappings_file(maps_now)

        return report

    async def _upsert_mapping(
        self,
        existing_maps: dict[str, ServiceCatalogueMapping],
        *,
        catalogue_service_id: str,
        runtime_service: Service | None,
        runtime_slug: str | None,
        runtime_service_id_dry: Any,
        mapping_type: str,
        mapping_status: str,
        review_status: str,
        notes: str | None,
        provenance: dict[str, Any],
    ) -> bool:
        row = existing_maps.get(catalogue_service_id)
        target_id = runtime_service.id if runtime_service else None
        if row is not None and (
            row.runtime_slug == runtime_slug
            and row.mapping_status == mapping_status
            and row.mapping_type == mapping_type
            and (self.dry_run or row.runtime_service_id == target_id)
        ):
            return False

        if self.dry_run:
            if row is None:
                existing_maps[catalogue_service_id] = ServiceCatalogueMapping(
                    catalogue_service_id=catalogue_service_id,
                    runtime_slug=runtime_slug,
                    mapping_type=mapping_type,
                    mapping_status=mapping_status,
                    review_status=review_status,
                    notes=notes,
                    provenance_json=provenance,
                )
            else:
                row.runtime_slug = runtime_slug
                row.mapping_type = mapping_type
                row.mapping_status = mapping_status
                row.review_status = review_status
            return True

        if row is None:
            row = ServiceCatalogueMapping(
                catalogue_service_id=catalogue_service_id,
                runtime_service_id=target_id,
                runtime_slug=runtime_slug,
                mapping_type=mapping_type,
                mapping_status=mapping_status,
                review_status=review_status,
                notes=notes,
                allow_overwrite_seed=False,
                provenance_json=provenance,
            )
            self.session.add(row)
            existing_maps[catalogue_service_id] = row
        else:
            row.runtime_service_id = target_id
            row.runtime_slug = runtime_slug
            row.mapping_type = mapping_type
            row.mapping_status = mapping_status
            row.review_status = review_status
            if notes:
                row.notes = notes
            row.provenance_json = provenance
        await self.session.flush()
        await self._audit(
            "upsert_mapping",
            catalogue_service_id,
            {
                "runtime_slug": runtime_slug,
                "mapping_status": mapping_status,
                "runtime_service_id": str(target_id) if target_id else None,
            },
        )
        return True

    def _export_mappings_file(self, maps: dict[str, ServiceCatalogueMapping]) -> None:
        # Preserve explicit seed/alias notes from prior file where possible
        prior = self._file_mappings()
        payload = {
            "version": "1.1.0",
            "description": (
                "Bidirectional catalogue↔runtime mappings maintained by "
                "scripts/sync_catalogue_runtime.py. Not claim verification."
            ),
            "mvp_seed_slugs": sorted(self._mvp_slugs()),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "mappings": [
                {
                    "catalogue_service_id": m.catalogue_service_id,
                    "runtime_slug": m.runtime_slug,
                    "runtime_service_id": str(m.runtime_service_id)
                    if m.runtime_service_id
                    else None,
                    "mapping_type": m.mapping_type,
                    "mapping_status": m.mapping_status,
                    "review_status": m.review_status,
                    "allow_overwrite_seed": m.allow_overwrite_seed,
                    "notes": m.notes
                    or (prior.get(m.catalogue_service_id) or {}).get("notes"),
                    "provenance": m.provenance_json,
                }
                for m in sorted(maps.values(), key=lambda x: x.catalogue_service_id)
            ],
        }
        self.mappings_path.parent.mkdir(parents=True, exist_ok=True)
        self.mappings_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )


class _DryAgency:
    def __init__(self, slug: str) -> None:
        self.slug = slug
        self.id = None


UUIDLikeAgency = Agency | _DryAgency
