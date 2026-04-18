"""Weekly Instagram competitor report orchestrator."""

from __future__ import annotations

import argparse
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
    parser = argparse.ArgumentParser(description="Weekly competitor Instagram report")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Scrape and analyze, but write report to report.html instead of emailing.",
    )
    args = parser.parse_args()

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

    if args.dry_run:
        out_path = Path(__file__).resolve().parent.parent / "report.html"
        out_path.write_text(result.html_report, encoding="utf-8")
        log.info("DRY RUN — would send to %s", recipient)
        log.info("DRY RUN — subject: %s", subject)
        log.info("DRY RUN — HTML written to %s", out_path)
        print("\n--- PLAIN SUMMARY ---")
        print(result.plain_summary)
        print("\n--- HTML REPORT ---")
        print(result.html_report)
        return 0

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
