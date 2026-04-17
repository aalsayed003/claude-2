from __future__ import annotations

import json
from types import SimpleNamespace

from src.campaign_generator import generate_campaign
from src.models import DoctorShortfall, ShortfallReport, Variance


def _make_report() -> ShortfallReport:
    return ShortfallReport(
        week="2026-W16",
        threshold_pct=10.0,
        clinic_revenue=Variance(actual=28500, target=31550, variance_pct=-9.67),
        clinic_patients=Variance(actual=145, target=165, variance_pct=-12.12),
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


def _fake_response(payload: dict):
    body = json.dumps(payload)
    return SimpleNamespace(content=[SimpleNamespace(text=body)])


class _FakeMessages:
    def __init__(self):
        self.last_kwargs = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return _fake_response({
            "diagnosis": "Dr. Smith revenue -28% due to lower patient volume",
            "angle": "same-week availability + transparent cash pricing",
            "posts": {
                "instagram": [
                    {"day": "Mon", "caption": "c1", "hashtags": ["#a"], "image_prompt": "p1"},
                ],
                "linkedin": [
                    {"day": "Tue", "post_text": "hi"},
                ],
            },
        })


class _FakeClient:
    def __init__(self):
        self.messages = _FakeMessages()


def _config() -> dict:
    return {
        "clinic": {
            "name": "Acme Family Clinic",
            "services": ["General dentistry"],
            "tone": "warm, professional",
            "location": "Austin, TX",
        },
        "campaign": {
            "model": "claude-sonnet-4-6",
            "instagram_posts_per_week": 3,
            "linkedin_posts_per_week": 2,
        },
    }


def test_generate_campaign_builds_structured_output():
    client = _FakeClient()
    campaign = generate_campaign(_make_report(), _config(), client=client)

    assert campaign.week == "2026-W16"
    assert campaign.diagnosis.startswith("Dr. Smith")
    assert len(campaign.posts.instagram) == 1
    assert len(campaign.posts.linkedin) == 1


def test_system_prompt_has_ephemeral_cache_control():
    client = _FakeClient()
    generate_campaign(_make_report(), _config(), client=client)

    kwargs = client.messages.last_kwargs
    system_blocks = kwargs["system"]
    assert isinstance(system_blocks, list) and len(system_blocks) == 1
    assert system_blocks[0]["cache_control"] == {"type": "ephemeral"}
    # Channel rules baked into the prompt
    assert "Instagram" in system_blocks[0]["text"]
    assert "LinkedIn" in system_blocks[0]["text"]
    # Clinic name interpolated
    assert "Acme Family Clinic" in system_blocks[0]["text"]


def test_user_prompt_includes_flagged_doctor():
    client = _FakeClient()
    generate_campaign(_make_report(), _config(), client=client)

    user_msg = client.messages.last_kwargs["messages"][0]["content"]
    assert "doc_smith" in user_msg
    assert "2026-W16" in user_msg


def test_model_comes_from_config():
    client = _FakeClient()
    cfg = _config()
    cfg["campaign"]["model"] = "claude-opus-4-7"
    generate_campaign(_make_report(), cfg, client=client)
    assert client.messages.last_kwargs["model"] == "claude-opus-4-7"
