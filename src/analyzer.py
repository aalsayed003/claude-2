"""Turn scraped competitor data into actionable insights via Claude."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass

from anthropic import Anthropic

from .scraper import CompetitorData

log = logging.getLogger(__name__)

MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """You are a marketing strategist for Al Salam, a Bahrain healthcare provider.
You analyze competitor Instagram activity and write concise, actionable intelligence briefings
for the CEO.

Your tone: direct, executive, specific. No filler. No hedging. Use plain language.

For each competitor you receive raw post data (caption, likes, comments, posted_at, video views).
You must identify:
- NEW offerings, services, campaigns, or partnerships mentioned in captions
- The single top-performing post by engagement (likes + comments)
- Content themes that drove engagement

Then synthesize cross-competitor patterns and give Al Salam 3-5 concrete recommendations.
Recommendations must be specific actions, not platitudes."""


@dataclass
class AnalysisResult:
    html_report: str
    plain_summary: str


def _format_competitor_block(c: CompetitorData) -> str:
    if c.error and not c.posts:
        return f"## {c.name} (@{c.username})\nERROR: {c.error}\n"

    lines = [f"## {c.name} (@{c.username})"]
    if c.followers is not None:
        lines.append(f"Followers: {c.followers:,}")
    lines.append(f"Posts in window: {len(c.posts)}")
    if c.error:
        lines.append(f"Partial data (error: {c.error})")
    lines.append("")
    for p in c.posts:
        lines.append(
            f"- [{p.posted_at}] likes={p.likes} comments={p.comments}"
            f"{' views=' + str(p.video_view_count) if p.video_view_count else ''}"
        )
        lines.append(f"  url: {p.url}")
        if p.caption:
            lines.append(f"  caption: {p.caption}")
        if p.hashtags:
            lines.append(f"  hashtags: {', '.join('#' + h for h in p.hashtags[:15])}")
        lines.append("")
    return "\n".join(lines)


def _top_post_summary(competitors: list[CompetitorData]) -> list[dict]:
    """Deterministic leaderboard so the email always includes hard numbers."""
    rows = []
    for c in competitors:
        if not c.posts:
            continue
        top = max(c.posts, key=lambda p: p.likes + p.comments)
        rows.append({
            "competitor": c.name,
            "username": c.username,
            "likes": top.likes,
            "comments": top.comments,
            "url": top.url,
            "posted_at": top.posted_at,
            "caption_preview": (top.caption or "")[:200],
        })
    rows.sort(key=lambda r: r["likes"] + r["comments"], reverse=True)
    return rows


def analyze(competitors: list[CompetitorData], lookback_days: int) -> AnalysisResult:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    competitor_blocks = "\n".join(_format_competitor_block(c) for c in competitors)
    leaderboard = _top_post_summary(competitors)

    user_prompt = f"""Analyze the last {lookback_days} days of Instagram activity from these competitors
and produce a weekly briefing for the Al Salam CEO.

Raw data:

{competitor_blocks}

Deterministic top-post leaderboard (sorted by likes + comments):
{json.dumps(leaderboard, indent=2)}

Output an HTML email body (no <html>/<head> tags, just the body content) with these sections:
1. <h2>Executive Summary</h2> — 2-3 sentences, what matters this week
2. <h2>Top Posts by Engagement</h2> — table of the leaderboard, linked
3. <h2>What Competitors Are Offering That's New</h2> — per competitor, bullet points of new services/campaigns/partnerships from captions. If nothing new, say so.
4. <h2>Content Themes Driving Engagement</h2> — cross-competitor patterns (video vs image, topics, hashtags)
5. <h2>Recommendations for Al Salam</h2> — 3-5 concrete, specific actions

Use inline styles only (email clients strip CSS). Use simple tables with border="1" cellpadding="6".
Keep it scannable. Total length under 800 words."""

    log.info("Calling Claude for analysis")
    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": user_prompt}],
    )
    html = response.content[0].text

    plain = _plain_summary(competitors, leaderboard)
    return AnalysisResult(html_report=html, plain_summary=plain)


def _plain_summary(competitors: list[CompetitorData], leaderboard: list[dict]) -> str:
    lines = ["Weekly competitor snapshot:", ""]
    for c in competitors:
        status = f"{len(c.posts)} posts" if not c.error else f"error: {c.error}"
        lines.append(f"- {c.name}: {status}")
    lines.append("")
    if leaderboard:
        top = leaderboard[0]
        lines.append(f"Top post: {top['competitor']} — {top['likes']} likes, {top['comments']} comments")
        lines.append(top["url"])
    return "\n".join(lines)
