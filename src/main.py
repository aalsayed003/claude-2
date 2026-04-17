from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from rich.console import Console

from . import analyzer, budget_sheet, campaign_generator, drafts_writer
from .config import iso_week, load_config, resolve_env
from .infinitydb_client import InfinityDBClient


def _fetch_actuals(cfg: dict[str, Any], week: str):
    infcfg = cfg["infinitydb"]
    base_url = resolve_env(infcfg["base_url_env"], required=True)
    database = resolve_env(infcfg["database_env"], required=True)
    user = resolve_env(infcfg.get("user_env"))
    password = resolve_env(infcfg.get("password_env"))
    with InfinityDBClient(
        base_url=base_url, database=database, user=user, password=password
    ) as client:
        return client.fetch_weekly_actuals(week, infcfg["actuals_path_template"])


def _fetch_budget(cfg: dict[str, Any], week: str):
    bcfg = cfg["budget"]
    sheet_id = resolve_env(bcfg["sheet_id_env"], required=True)
    worksheet = bcfg["worksheet"]
    return budget_sheet.load_weekly_budget(sheet_id, worksheet, week)


def run(week: str | None, *, dry_run: bool, config_path: str, drafts_root: str) -> int:
    console = Console()
    load_dotenv()
    cfg = load_config(config_path)
    resolved_week = iso_week(week)

    console.print(f"[bold]Running for week:[/] {resolved_week}")
    actuals = _fetch_actuals(cfg, resolved_week)
    budget = _fetch_budget(cfg, resolved_week)

    report = analyzer.compare(
        actuals,
        budget,
        week=resolved_week,
        threshold_pct=float(cfg["shortfall"]["threshold_pct"]),
    )

    console.print(
        f"Clinic revenue variance: [bold]{report.clinic_revenue.variance_pct:+.2f}%[/]"
    )
    if report.flagged_doctors:
        console.print(f"[red]Flagged doctors:[/] {', '.join(report.flagged_doctors)}")
    else:
        console.print("[green]No doctor-level shortfall.[/]")

    campaign = None
    if report.has_shortfall and not dry_run:
        console.print("Generating campaign via Claude...")
        campaign = campaign_generator.generate_campaign(report, cfg)
    elif report.has_shortfall and dry_run:
        console.print("[yellow]Shortfall detected, but --dry-run skips campaign generation.[/]")
    else:
        console.print("[green]No shortfall — skipping campaign generation.[/]")

    out = drafts_writer.write_drafts(drafts_root, report, campaign)
    console.print(f"Drafts written to: [bold]{out}[/]")
    return 0


def cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="clinic-campaign")
    sub = parser.add_subparsers(dest="cmd", required=True)

    run_p = sub.add_parser("run", help="Run weekly analysis + campaign drafting")
    run_p.add_argument("--week", default=None, help="ISO week (e.g. 2026-W16). Defaults to current.")
    run_p.add_argument("--dry-run", action="store_true", help="Skip Claude API call")
    run_p.add_argument("--config", default="config.yaml")
    run_p.add_argument("--drafts-root", default="drafts")

    args = parser.parse_args(argv)
    if args.cmd == "run":
        return run(
            args.week,
            dry_run=args.dry_run,
            config_path=args.config,
            drafts_root=args.drafts_root,
        )
    parser.error(f"unknown command: {args.cmd}")
    return 2


if __name__ == "__main__":
    sys.exit(cli())
