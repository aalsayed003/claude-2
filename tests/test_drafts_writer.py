from __future__ import annotations

import json

from src.drafts_writer import write_drafts
from src.models import (
    Campaign,
    CampaignPosts,
    DoctorShortfall,
    InstagramPost,
    LinkedInPost,
    ShortfallReport,
    Variance,
)


def _report() -> ShortfallReport:
    return ShortfallReport(
        week="2026-W16",
        threshold_pct=10.0,
        clinic_revenue=Variance(actual=28000, target=31550, variance_pct=-11.25),
        clinic_patients=Variance(actual=150, target=165, variance_pct=-9.09),
        doctors=[
            DoctorShortfall(
                doctor_id="doc_smith",
                doctor_name="Dr. Smith",
                patients=Variance(actual=40, target=50, variance_pct=-20.0),
                avg_revenue=Variance(actual=180, target=200, variance_pct=-10.0),
                revenue=Variance(actual=7200, target=10000, variance_pct=-28.0),
                cash_mix_pct=25.0,
                insurance_mix_pct=75.0,
                flagged=True,
            )
        ],
        flagged_doctors=["doc_smith"],
    )


def _campaign() -> Campaign:
    return Campaign(
        week="2026-W16",
        diagnosis="Dr. Smith revenue -28% due to lower volume",
        angle="promote same-week availability + cash pricing",
        posts=CampaignPosts(
            instagram=[
                InstagramPost(
                    day="Mon",
                    caption="Open chairs this week!",
                    hashtags=["#austin", "#dentist"],
                    image_prompt="bright clinic reception with a welcoming smile",
                )
            ],
            linkedin=[
                LinkedInPost(day="Tue", post_text="Community health means access...")
            ],
        ),
    )


def test_write_drafts_produces_all_files(tmp_path):
    out = write_drafts(tmp_path, _report(), _campaign())

    assert out.name == "2026-W16"
    assert (out / "report.json").exists()
    assert (out / "campaign.json").exists()
    assert (out / "instagram.md").exists()
    assert (out / "linkedin.md").exists()
    assert (out / "README.md").exists()

    report_raw = json.loads((out / "report.json").read_text())
    assert report_raw["flagged_doctors"] == ["doc_smith"]

    ig_md = (out / "instagram.md").read_text()
    assert "Open chairs this week!" in ig_md
    assert "#austin" in ig_md

    readme = (out / "README.md").read_text()
    assert "Dr. Smith" in readme
    assert "rotating_light" in readme  # flagged emoji tag
