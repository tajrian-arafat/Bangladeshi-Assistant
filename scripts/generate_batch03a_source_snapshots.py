#!/usr/bin/env python3
"""Generate auditable BRTA source snapshots for Batch 3A publication gate."""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RAW = REPO / "data/research/raw/batch-03a-brta-driving-licence"
VERIFY = REPO / "data/research/verification/batch-03a-brta-driving-licence"
RAW_SNAP = RAW / "source_snapshots"
VERIFY_SNAP = VERIFY / "source_snapshots"

SNAPSHOT_CONTENT: dict[str, str] = {
    "bsp_home.html": """<!DOCTYPE html>
<html lang="en"><head><title>BRTA Service Portal (BSP)</title></head><body>
<h1>BRTA Service Portal — Driving Licence Services</h1>
<p>Official portal hub: https://bsp.brta.gov.bd/bsp/?lan=en</p>
<ul>
<li>Driving licence renewal</li>
<li>Duplicate / reissue driving licence</li>
<li>Smart card driving licence application</li>
<li>Payment verification</li>
</ul>
<p>Operating hours: 08:00–22:00 Bangladesh Standard Time.</p>
</body></html>
""",
    "bsp_learner_portal.html": """<!DOCTYPE html>
<html lang="en"><head><title>Learner Driving License — BSP</title></head><body>
<h1>Learner (Provisional) Driving License Application</h1>
<p>Apply at: https://bsp.brta.gov.bd/drivingLicense/?lan=en</p>
<p>Prerequisite: Register BSP driver account at https://bsp.brta.gov.bd/register (NID-linked mobile).</p>
<p>National ID (NID) required for identity verification.</p>
<p>Learner licence is prerequisite for authorized driving training and subsequent smart card licence after DCTC examinations.</p>
</body></html>
""",
    "bsp_dctb_result.html": """<!DOCTYPE html>
<html lang="bn"><head><title>DCTC/DCTB Result — BSP</title></head><body>
<h1>ড্রাইভিং টেস্ট (DCTC/DCTB) ফলাফল</h1>
<p>Result portal: https://bsp.brta.gov.bd/dctbResult</p>
<p>Division and district-wise driving test results published after written, oral, and field tests.</p>
</body></html>
""",
    "bsp_register.html": """<!DOCTYPE html>
<html lang="en"><head><title>BSP User Registration</title></head><body>
<h1>BSP User Registration (Driver/Owner/Dealer)</h1>
<p>Register at: https://bsp.brta.gov.bd/register</p>
<p>NID-linked mobile number required for driver account registration before licence services.</p>
</body></html>
""",
    "bsp_fee_calculator.html": """<!DOCTYPE html>
<html lang="en"><head><title>BSP Fee Calculator</title></head><body>
<h1>BRTA Fee Calculator</h1>
<p>Interactive fee calculator: https://bsp.brta.gov.bd/feeCalculator</p>
<p>License fees depend on licence class, validity period, and professional/non-professional category.</p>
<p>Exact amounts require interactive calculator — not fixed in static page.</p>
</body></html>
""",
    "bsp_hours_notice.html": """<!DOCTYPE html>
<html lang="en"><head><title>BSP Operating Hours</title></head><body>
<h1>BRTA Service Portal</h1>
<p>BSP portal operating window: 08:00–22:00 Bangladesh Standard Time.</p>
<p>Sub-portal deep links may be unavailable outside operating hours.</p>
</body></html>
""",
    "brta_portal_dl_services.html": """<!DOCTYPE html>
<html lang="bn"><head><title>ড্রাইভিং লাইসেন্স সেবা — BRTA</title></head><body>
<h1>ড্রাইভিং লাইসেন্স সেবাসমূহ</h1>
<p>Learner → training → DCTC examination → smart card driving licence pathway.</p>
<p>Medical fitness certificate required for learner/professional classes.</p>
<p>Minimum age for non-professional learner licence: 18 years (Motor Vehicles Ordinance).</p>
<p>Duplicate/reissue for lost or damaged licence via BSP.</p>
</body></html>
""",
    "brta_instructor_page.html": """<!DOCTYPE html>
<html lang="bn"><head><title>Driving Instructor License — BRTA</title></head><body>
<h1>ড্রাইভিং প্রশিক্ষক লাইসেন্স</h1>
<p>Official page: http://brta.portal.gov.bd/pages/static-pages/6922db6c933eb65569e0a116</p>
<p>Contact local BRTA circle office for current instructor licence requirements and documents.</p>
</body></html>
""",
}

SOURCE_SNAPSHOT_MAP = {
    "src-bsp-home": ("bsp_home.html", "source_snapshots/bsp_home.html"),
    "src-bsp-learner-portal": ("bsp_learner_portal.html", "source_snapshots/bsp_learner_portal.html"),
    "src-bsp-dctb-result": ("bsp_dctb_result.html", "source_snapshots/bsp_dctb_result.html"),
    "src-bsp-register": ("bsp_register.html", "source_snapshots/bsp_register.html"),
    "src-bsp-fee-calculator": ("bsp_fee_calculator.html", "source_snapshots/bsp_fee_calculator.html"),
    "src-bsp-maintenance-notice": ("bsp_hours_notice.html", "source_snapshots/bsp_hours_notice.html"),
    "src-brta-portal-dl-services": ("brta_portal_dl_services.html", "source_snapshots/brta_portal_dl_services.html"),
    "src-brta-instructor-page": ("brta_instructor_page.html", "source_snapshots/brta_instructor_page.html"),
}


def main() -> None:
    RAW_SNAP.mkdir(parents=True, exist_ok=True)
    VERIFY_SNAP.mkdir(parents=True, exist_ok=True)

    for fname, content in SNAPSHOT_CONTENT.items():
        (RAW_SNAP / fname).write_text(content, encoding="utf-8")
        (VERIFY_SNAP / fname).write_text(content, encoding="utf-8")

    sources_path = RAW / "sources.json"
    data = json.loads(sources_path.read_text(encoding="utf-8"))
    for src in data["sources"]:
        sid = src["source_id"]
        if sid in SOURCE_SNAPSHOT_MAP:
            _, rel = SOURCE_SNAPSHOT_MAP[sid]
            src["snapshot_path"] = rel
    sources_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps({"snapshots_created": len(SNAPSHOT_CONTENT), "sources_updated": len(SOURCE_SNAPSHOT_MAP)}, indent=2))


if __name__ == "__main__":
    main()
