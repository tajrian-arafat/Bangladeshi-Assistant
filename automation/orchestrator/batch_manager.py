"""Batch queue generation and batch lifecycle helpers."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# Completed batches — service IDs from authoritative scope/staging artifacts
BATCH_01_SERVICES = [
    "civil-bdris-application-print",
    "civil-birth-death-verify",
    "civil-birth-registration",
    "civil-birth-registration-correction",
    "civil-death-registration",
    "civil-divorce-registration",
    "civil-marriage-registration",
    "civil-marriage-registrar-hindu-list",
    "civil-marriage-registrar-muslim-list",
    "identity-nid-correction",
    "identity-nid-fee-calculator",
    "identity-nid-new-voter-registration",
    "identity-nid-reissue-lost",
    "identity-voter-area-change",
    "identity-voter-registration",
    "local-character-certificate",
    "local-citizenship-certificate",
    "local-inheritance-certificate",
    "local-warrior-family-certificate",
    "local-widow-certificate",
    "local-guardianship-certificate",
    "local-digital-union-certificate",
    "local-orphan-certificate",
    "local-temporary-resident-certificate",
    "local-attestation-union",
    "local-investor-certificate",
    "local-freedom-fighter-verification",
    "local-landless-certificate",
    "local-small-ethnic-certificate",
    "local-no-objection-certificate",
    "local-resident-certificate",
    "local-income-certificate",
    "local-tax-certificate",
    "local-travel-permit",
]

BATCH_02A_SERVICES = [
    "epassport-new-application",
    "epassport-reissue",
    "epassport-fee-payment",
    "epassport-enrollment-appointment",
    "epassport-application-status",
    "epassport-urgent-super-express",
    "epassport-rpo-secretariat",
    "passport-mrp-initial",
    "passport-mrp-reissue",
    "passport-application-status",
    "police-passport-police-verification",
    "police-passport-verification",
]

BATCH_02B_SERVICES = [
    "police-clearance-certificate",
    "police-cyber-support-women",
    "police-employment-verification",
    "police-general-diary",
    "police-general-diary-online",
    "police-nid-address-verification",
    "police-passport-police-verification",
    "police-passport-verification",
    "migration-visa-application-dip",
    "police-expatriate-services",
    "police-firearms-license",
]

BATCH_03A_SERVICES = [
    "brta-learner-driving-license",
    "brta-driving-license-renewal",
    "brta-duplicate-driving-license",
    "brta-smart-card-driving-license",
    "brta-driving-instructor-license",
    "brta-dctc-exam-result",
]

# Batch grouping rules derived from catalogue category_id / authority patterns
BATCH_GROUP_RULES: list[dict[str, Any]] = [
    {
        "batch_id": "BATCH_03B",
        "slug": "batch-03b-brta-vehicle",
        "name": "BRTA Vehicle Registration / Ownership / Fitness",
        "category_ids": ["transport"],
        "subcategory_any": ["vehicle_registration", "vehicle_fitness", "vehicle_ownership", "vehicle_tax_token"],
        "exclude_service_ids": BATCH_03A_SERVICES,
    },
    {
        "batch_id": "BATCH_03C",
        "slug": "batch-03c-brta-other",
        "name": "BRTA Tax Token / Route Permit / Other BRTA",
        "authority_ids": ["brta"],
        "exclude_service_ids": BATCH_03A_SERVICES,
    },
    {"batch_id": "BATCH_04", "slug": "batch-04-tax-vat-customs", "name": "Tax / VAT / Customs", "category_ids": ["tax", "vat", "customs"]},
    {"batch_id": "BATCH_05", "slug": "batch-05-land", "name": "Land & Property Records", "category_ids": ["land"]},
    {"batch_id": "BATCH_06", "slug": "batch-06-education", "name": "Education", "category_ids": ["education"]},
    {"batch_id": "BATCH_07", "slug": "batch-07-health", "name": "Health", "category_ids": ["health"]},
    {
        "batch_id": "BATCH_08",
        "slug": "batch-08-social-protection",
        "name": "Social Protection / Disability / Allowances",
        "category_ids": ["social_protection", "disability", "women_children"],
    },
    {
        "batch_id": "BATCH_09",
        "slug": "batch-09-agriculture",
        "name": "Agriculture / Fisheries / Livestock",
        "category_ids": ["agriculture", "fisheries", "livestock"],
    },
    {
        "batch_id": "BATCH_10",
        "slug": "batch-10-employment-migration",
        "name": "Employment / Labour / Expatriate / Migration",
        "category_ids": ["employment", "expatriate", "passport_immigration"],
    },
    {
        "batch_id": "BATCH_11",
        "slug": "batch-11-business-trade",
        "name": "Business / Trade / Industry / Professional",
        "category_ids": ["business", "trade", "investment", "professional", "registrations"],
    },
    {"batch_id": "BATCH_12", "slug": "batch-12-local-gov", "name": "Local Government", "category_ids": ["local_government"]},
    {"batch_id": "BATCH_13", "slug": "batch-13-judiciary", "name": "Judiciary / Legal / Courts", "category_ids": ["judiciary", "legal_aid"]},
]


class BatchManager:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.catalogue_path = repo_root / "data" / "service_catalogue" / "services.json"
        self.queue_path = repo_root / ".automation" / "batch_queue.json"

    def load_catalogue(self) -> list[dict[str, Any]]:
        data = json.loads(self.catalogue_path.read_text(encoding="utf-8"))
        return data.get("services") or data if isinstance(data, list) else data.get("services", [])

    def _service_matches_rule(self, service: dict[str, Any], rule: dict[str, Any]) -> bool:
        sid = service.get("service_id") or service.get("id")
        if sid in rule.get("exclude_service_ids", []):
            return False
        if sid in rule.get("include_service_ids", []):
            return True
        cat = service.get("category_id") or service.get("category")
        if rule.get("category_ids") and cat not in rule["category_ids"]:
            return False
        sub = service.get("subcategory")
        if rule.get("subcategory_any") and sub not in rule["subcategory_any"]:
            return False
        auth = service.get("authority_id")
        if rule.get("authority_ids") and auth not in rule["authority_ids"]:
            return False
        if rule.get("category_ids") or rule.get("authority_ids") or rule.get("subcategory_any"):
            return True
        return False

    def generate_queue(self) -> dict[str, Any]:
        services = self.load_catalogue()
        confirmed = [s for s in services if (s.get("status") or s.get("catalogue_status")) == "CONFIRMED"]
        assigned: set[str] = set()

        def ids_for(slist: list[dict]) -> list[str]:
            return sorted({s.get("service_id") or s.get("id") for s in slist if s.get("service_id") or s.get("id")})

        batches: list[dict[str, Any]] = [
            {
                "batch_id": "BATCH_01",
                "slug": "batch-01-identity-civil-registration",
                "name": "Identity / Civil Registration",
                "status": "COMPLETE",
                "service_ids": BATCH_01_SERVICES,
                "service_count": len(BATCH_01_SERVICES),
                "phases_completed": ["RESEARCH", "VERIFICATION", "PUBLICATION", "E2E", "REGRESSION"],
            },
            {
                "batch_id": "BATCH_02A",
                "slug": "batch-02a-passport",
                "name": "Passport",
                "status": "COMPLETE",
                "service_ids": BATCH_02A_SERVICES,
                "service_count": len(BATCH_02A_SERVICES),
                "phases_completed": ["RESEARCH", "VERIFICATION", "PUBLICATION", "E2E", "REGRESSION"],
            },
            {
                "batch_id": "BATCH_02B",
                "slug": "batch-02b-police-immigration",
                "name": "Police / Immigration",
                "status": "COMPLETE",
                "service_ids": BATCH_02B_SERVICES,
                "service_count": len(BATCH_02B_SERVICES),
                "phases_completed": ["RESEARCH", "VERIFICATION", "PUBLICATION", "E2E", "REGRESSION", "STABILIZATION"],
            },
            {
                "batch_id": "BATCH_03A",
                "slug": "batch-03a-brta-driving-licence",
                "name": "BRTA Driving Licence",
                "status": "READY",
                "service_ids": BATCH_03A_SERVICES,
                "service_count": len(BATCH_03A_SERVICES),
                "phases_completed": [],
                "authority_id": "brta",
                "category_id": "transport",
            },
        ]
        for bid_list in (BATCH_01_SERVICES, BATCH_02A_SERVICES, BATCH_02B_SERVICES, BATCH_03A_SERVICES):
            assigned.update(bid_list)

        for rule in BATCH_GROUP_RULES:
            matched = [s for s in confirmed if self._service_matches_rule(s, rule)]
            service_ids = ids_for(matched)
            service_ids = [sid for sid in service_ids if sid not in assigned]
            if not service_ids and rule["batch_id"] not in {"BATCH_03B", "BATCH_03C"}:
                continue
            batches.append(
                {
                    "batch_id": rule["batch_id"],
                    "slug": rule["slug"],
                    "name": rule["name"],
                    "status": "PLANNED",
                    "service_ids": service_ids,
                    "service_count": len(service_ids),
                    "phases_completed": [],
                }
            )
            assigned.update(service_ids)

        remaining = [
            s.get("service_id") or s.get("id")
            for s in confirmed
            if (s.get("service_id") or s.get("id")) not in assigned
        ]
        if remaining:
            batches.append(
                {
                    "batch_id": "BATCH_14",
                    "slug": "batch-14-remaining",
                    "name": "Remaining Government / Public Services",
                    "status": "PLANNED",
                    "service_ids": sorted(remaining),
                    "service_count": len(remaining),
                    "phases_completed": [],
                }
            )

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "catalogue_source": str(self.catalogue_path.relative_to(self.repo_root)),
            "total_batches": len(batches),
            "confirmed_services_in_catalogue": len(confirmed),
            "assigned_services": len(assigned) + len(remaining),
            "batches": batches,
        }

    def write_queue(self) -> Path:
        payload = self.generate_queue()
        self.queue_path.parent.mkdir(parents=True, exist_ok=True)
        self.queue_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return self.queue_path

    def load_queue(self) -> dict[str, Any]:
        if not self.queue_path.exists():
            return self.generate_queue()
        return json.loads(self.queue_path.read_text(encoding="utf-8"))

    def get_batch(self, batch_id: str) -> dict[str, Any] | None:
        queue = self.load_queue()
        for batch in queue.get("batches", []):
            if batch["batch_id"] == batch_id:
                return batch
        return None

    def next_ready_batch(self) -> dict[str, Any] | None:
        queue = self.load_queue()
        for batch in queue.get("batches", []):
            if batch.get("status") == "READY":
                return batch
        return None

    def mark_batch_status(self, batch_id: str, status: str) -> None:
        queue = self.load_queue()
        for batch in queue.get("batches", []):
            if batch["batch_id"] == batch_id:
                batch["status"] = status
                break
        queue["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.queue_path.write_text(json.dumps(queue, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def mark_phase_complete(self, batch_id: str, phase: str) -> None:
        queue = self.load_queue()
        for batch in queue.get("batches", []):
            if batch["batch_id"] == batch_id:
                completed = list(batch.get("phases_completed") or [])
                if phase not in completed:
                    completed.append(phase)
                batch["phases_completed"] = completed
                break
        queue["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.queue_path.write_text(json.dumps(queue, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def is_phase_complete(self, batch_id: str, phase: str) -> bool:
        batch = self.get_batch(batch_id)
        if not batch:
            return False
        return phase in (batch.get("phases_completed") or [])

    def setup_research_artifacts(self, batch: dict[str, Any]) -> list[str]:
        """Deterministic research kickoff — scope + services_index from catalogue."""
        slug = batch["slug"]
        raw_dir = self.repo_root / "data" / "research" / "raw" / slug
        raw_dir.mkdir(parents=True, exist_ok=True)
        services = self.load_catalogue()
        by_id = {s.get("service_id") or s.get("id"): s for s in services}
        in_scope = batch.get("service_ids") or []
        scope = {
            "batch_id": batch["batch_id"],
            "slug": slug,
            "name": batch["name"],
            "in_scope": in_scope,
            "out_of_scope_noted": [],
            "generated_by": "automation.orchestrator",
        }
        services_index = {
            "batch_id": batch["batch_id"],
            "services": [
                {
                    "service_id": sid,
                    "catalogue_status": (by_id.get(sid) or {}).get("status", "CONFIRMED"),
                    "authority_id": (by_id.get(sid) or {}).get("authority_id"),
                    "category_id": (by_id.get(sid) or {}).get("category_id"),
                    "official_source": (by_id.get(sid) or {}).get("official_source"),
                }
                for sid in in_scope
                if sid in by_id
            ],
        }
        scope_path = raw_dir / "scope.json"
        index_path = raw_dir / "services_index.json"
        scope_path.write_text(json.dumps(scope, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        index_path.write_text(json.dumps(services_index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return [str(scope_path.relative_to(self.repo_root)), str(index_path.relative_to(self.repo_root))]
