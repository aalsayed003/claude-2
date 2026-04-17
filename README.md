# Clinic Revenue → Weekly Social Campaign Builder

A small Python service that runs weekly, reads clinic actuals from InfinityDB,
compares them to the revenue budget in a Google Sheet, and — whenever any
doctor (or the clinic overall) lands **≥10% below budget** — drafts a targeted
weekly social-media campaign (Instagram + LinkedIn) via the Claude API for
human review before posting.

## How it runs

```
main.py  (weekly, e.g. Mon 08:00 via cron / GitHub Actions)
 ├─ infinitydb_client.py   → pull actuals via InfinityDB REST
 ├─ budget_sheet.py        → pull budget from Google Sheets
 ├─ analyzer.py            → compute variances, flag doctors <= -threshold%
 ├─ campaign_generator.py  → Claude API → Instagram + LinkedIn drafts
 └─ drafts_writer.py       → drafts/<ISO-week>/ for human review
```

Draft-only by design. Nothing is ever auto-posted.

## Setup

```bash
python -m venv .venv
.venv/bin/pip install -e '.[dev]'
cp .env.example .env            # fill in InfinityDB + Anthropic credentials
# drop a Google service-account JSON as ./google-credentials.json
```

Edit `config.yaml`:

- `clinic.*` — brand voice + services (feeds the campaign prompt)
- `infinitydb.actuals_path_template` — where weekly per-doctor rollups live
- `budget.sheet_id_env` + `budget.worksheet` — Google Sheet location
- `shortfall.threshold_pct` — default `10.0`
- `campaign.model` — default `claude-sonnet-4-6`

The service account must have read access to the budget sheet. The sheet
needs a `Weekly Budget` tab with columns: `doctor_id`, `doctor_name`, `week`,
`target_patients`, `target_avg_revenue`, `target_revenue`.

## Run

```bash
# Current ISO week, live
python -m src.main run

# Specific week, skip the Claude API call
python -m src.main run --week 2026-W16 --dry-run
```

Output lands in `drafts/<ISO-week>/`:

- `report.json` — raw variance + flag data
- `campaign.json` — raw Claude output
- `instagram.md`, `linkedin.md` — human-reviewable drafts
- `README.md` — one-page summary

## Testing

```bash
.venv/bin/python -m pytest -q
```

Unit tests cover the analyzer (including the exact -10% boundary), the
InfinityDB REST client (via `httpx.MockTransport`), the Google Sheets loader
(via a stub client), the Claude-backed generator (via a fake Anthropic
client that asserts prompt-caching is enabled), and an end-to-end fixture
run that exercises the flagging + drafts-writer pipeline without network.
