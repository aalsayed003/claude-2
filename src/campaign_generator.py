from __future__ import annotations

import json
import os
from typing import Any, Protocol

from .models import Campaign, CampaignPosts, ShortfallReport


SYSTEM_PROMPT_TEMPLATE = """\
You are the in-house marketing strategist for {clinic_name}, a healthcare
practice located in {clinic_location}. You write weekly social campaigns that
respond to measured revenue shortfalls.

Clinic services:
{services_bullets}

Brand tone: {tone}. Never make medical claims, never guarantee outcomes, never
name individual patients, never discount care quality. Always stay HIPAA-safe:
do not reference specific patients, procedures, or identifying details.

Channel rules:
- Instagram: visual-first, max ~2200 chars, 5-10 hashtags, a vivid image_prompt
  describing the visual (photography style, subject, mood, palette). Captions
  should hook in the first line.
- LinkedIn: professional, 150-300 words, no hashtags inside sentences (1-3 at
  the end are fine), lead with an insight or community angle, not a hard sell.

You produce exactly {instagram_count} Instagram posts and {linkedin_count}
LinkedIn posts for the week. Distribute them across weekdays (Mon-Fri).

Your response MUST be valid JSON matching this schema exactly, with no prose
before or after:

{{
  "diagnosis": "one-sentence plain-English read of the shortfall",
  "angle": "the marketing angle you chose to address it",
  "posts": {{
    "instagram": [
      {{"day": "Mon", "caption": "...", "hashtags": ["#x", "#y"], "image_prompt": "..."}}
    ],
    "linkedin": [
      {{"day": "Tue", "post_text": "..."}}
    ]
  }}
}}
"""


class _AnthropicLike(Protocol):
    class messages:  # noqa: N801
        @staticmethod
        def create(**kwargs: Any) -> Any: ...


def _build_system_prompt(config: dict[str, Any]) -> str:
    clinic = config.get("clinic", {})
    campaign = config.get("campaign", {})
    services = clinic.get("services", [])
    services_bullets = "\n".join(f"- {s}" for s in services) or "- (none configured)"
    return SYSTEM_PROMPT_TEMPLATE.format(
        clinic_name=clinic.get("name", "the clinic"),
        clinic_location=clinic.get("location", "our community"),
        services_bullets=services_bullets,
        tone=clinic.get("tone", "warm, professional"),
        instagram_count=campaign.get("instagram_posts_per_week", 3),
        linkedin_count=campaign.get("linkedin_posts_per_week", 2),
    )


def _build_user_prompt(report: ShortfallReport) -> str:
    return (
        "Weekly shortfall report (JSON):\n"
        f"{report.model_dump_json(indent=2)}\n\n"
        "Draft this week's Instagram + LinkedIn campaign targeting the "
        "flagged doctors and, where relevant, the cash vs. insurance mix. "
        "Return JSON only."
    )


def _extract_text(response: Any) -> str:
    content = response.content
    parts: list[str] = []
    for block in content:
        text = getattr(block, "text", None)
        if text is None and isinstance(block, dict):
            text = block.get("text")
        if text:
            parts.append(text)
    return "".join(parts).strip()


def generate_campaign(
    report: ShortfallReport,
    config: dict[str, Any],
    *,
    client: _AnthropicLike | None = None,
) -> Campaign:
    """Call Claude to turn a shortfall report into a structured weekly campaign.

    The system prompt carries the stable brand/channel rules and is marked
    with ephemeral prompt caching so repeated weekly runs reuse the cache.
    """
    if client is None:
        from anthropic import Anthropic  # lazy import so tests don't need the SDK

        client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    model = config.get("campaign", {}).get("model", "claude-sonnet-4-6")
    system_prompt = _build_system_prompt(config)
    user_prompt = _build_user_prompt(report)

    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw = _extract_text(response)
    payload = json.loads(raw)

    return Campaign(
        week=report.week,
        diagnosis=payload["diagnosis"],
        angle=payload["angle"],
        posts=CampaignPosts.model_validate(payload.get("posts", {})),
    )
