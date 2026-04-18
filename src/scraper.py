"""Instagram scraping via instaloader (public profiles, no login)."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from typing import Any

import instaloader

log = logging.getLogger(__name__)


@dataclass
class Post:
    shortcode: str
    url: str
    caption: str
    posted_at: str
    likes: int
    comments: int
    is_video: bool
    video_view_count: int | None
    hashtags: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CompetitorData:
    name: str
    username: str
    followers: int | None
    posts: list[Post]
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "username": self.username,
            "followers": self.followers,
            "posts": [p.to_dict() for p in self.posts],
            "error": self.error,
        }


def _build_loader() -> instaloader.Instaloader:
    return instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        quiet=True,
        request_timeout=30.0,
    )


def scrape_competitor(
    name: str,
    username: str,
    lookback_days: int,
    max_posts: int,
) -> CompetitorData:
    """Fetch recent public posts for a single Instagram username."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
    loader = _build_loader()

    try:
        profile = instaloader.Profile.from_username(loader.context, username)
    except Exception as e:
        log.warning("Failed to load profile %s: %s", username, e)
        return CompetitorData(name=name, username=username, followers=None, posts=[], error=str(e))

    posts: list[Post] = []
    try:
        for idx, post in enumerate(profile.get_posts()):
            if idx >= max_posts:
                break
            posted_at = post.date_utc.replace(tzinfo=timezone.utc)
            if posted_at < cutoff:
                break
            posts.append(
                Post(
                    shortcode=post.shortcode,
                    url=f"https://www.instagram.com/p/{post.shortcode}/",
                    caption=(post.caption or "")[:2000],
                    posted_at=posted_at.isoformat(),
                    likes=post.likes,
                    comments=post.comments,
                    is_video=post.is_video,
                    video_view_count=post.video_view_count if post.is_video else None,
                    hashtags=list(post.caption_hashtags) if post.caption else [],
                )
            )
            time.sleep(2)
    except Exception as e:
        log.warning("Error iterating posts for %s: %s", username, e)
        return CompetitorData(
            name=name,
            username=username,
            followers=getattr(profile, "followers", None),
            posts=posts,
            error=str(e),
        )

    return CompetitorData(
        name=name,
        username=username,
        followers=profile.followers,
        posts=posts,
    )


def scrape_all(competitors: list[dict[str, str]], lookback_days: int, max_posts: int) -> list[CompetitorData]:
    results: list[CompetitorData] = []
    for c in competitors:
        log.info("Scraping %s (@%s)", c["name"], c["username"])
        results.append(scrape_competitor(c["name"], c["username"], lookback_days, max_posts))
        time.sleep(10)
    return results
