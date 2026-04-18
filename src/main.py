"""Weekly Instagram competitor report orchestrator."""

from __future__ import annotations

import logging
import sys
from datetime import date
from pathlib import Path

import yaml

from .analyzer import analyze
from .emailer import send_report
from .scraper import scrape_all

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("main")


def main() -> int:
    config_path = Path(__file__).resolve().parent.parent / "config.yaml"
    config = yaml.safe_load(config_path.read_text())

    competitors = config["competitors"]
    lookback_days = int(config.get("lookback_days", 7))
    max_posts = int(config.get("max_posts_per_competitor", 30))
    recipient = config["recipient_email"]
    sender_name = config.get("sender_name", "Competitor Intelligence")

    log.info("Scraping %d competitors, %d day window", len(competitors), lookback_days)
    scraped = scrape_all(competitors, lookback_days, max_posts)

    total_posts = sum(len(c.posts) for c in scraped)
    log.info("Collected %d posts total", total_posts)

    if total_posts == 0:
        log.warning("No posts scraped. Instagram may be blocking unauthenticated access.")

    result = analyze(scraped, lookback_days)

    subject = f"Competitor Instagram Brief — week of {date.today().isoformat()}"
    send_report(
        to_email=recipient,
        subject=subject,
        html_body=result.html_report,
        plain_body=result.plain_summary,
        sender_name=sender_name,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
