# Instagram Competitor Analyzer

Weekly agent for Al Salam that scrapes public Instagram activity from listed competitors, uses Claude
to summarize what they're offering and which posts performed best, and emails the briefing
to the CEO. Runs on GitHub Actions — weekly on schedule or manually on demand.

## What it does

1. Pulls the last 7 days of public posts for each competitor in `config.yaml`
2. Captures likes, comments, captions, hashtags, and video view counts
3. Sends the data to Claude Sonnet 4.6 for analysis
4. Emails an HTML briefing with:
   - Executive summary
   - Top posts by engagement
   - New offerings / campaigns per competitor
   - Content themes driving engagement
   - Concrete recommendations for Al Salam

## Competitors tracked

Edit `config.yaml` to change. Currently:
- Ibn Al Nafees (`ibnalnafees`)
- Kindi Hospital (`alkindihospital`)
- American Mission Hospital (`american_mission_hospital`)
- Royal Bahrain Hospital (`royalbahrainhospital`)

## One-time setup

You need to configure four GitHub secrets. Open your repo → Settings → Secrets and variables → Actions.

### 1. `ANTHROPIC_API_KEY`

Get one at https://console.anthropic.com/settings/keys. Paste it as a repo secret.

### 2. Gmail OAuth credentials

Instagram email will be sent from your Gmail. To let GitHub Actions send on your behalf
without storing your password, do the following **once** on your local machine:

**a. Create a Google Cloud project**

1. Go to https://console.cloud.google.com/
2. Create a new project (any name, e.g. "competitor-report")
3. Search for "Gmail API" → Enable

**b. Configure the OAuth consent screen**

1. APIs & Services → OAuth consent screen
2. User Type: **External**, then Create
3. Fill in app name, support email, developer email → Save
4. Scopes: add `https://www.googleapis.com/auth/gmail.send`
5. Test users: add **your Gmail address** (the one that will send)
6. Save. Leave the app in "Testing" mode — no verification needed.

**c. Create OAuth credentials**

1. APIs & Services → Credentials → Create Credentials → OAuth client ID
2. Application type: **Desktop app**
3. Download the JSON file

**d. Run the local helper to get a refresh token**

```bash
pip install google-auth-oauthlib
python scripts/gmail_oauth_setup.py /path/to/client_secret.json
```

A browser window opens. Sign in with the Gmail account you want to send from,
approve the permission. The script prints four values.

**e. Add each value as a GitHub secret**

| Secret name | Value |
|---|---|
| `GMAIL_CLIENT_ID` | from script output |
| `GMAIL_CLIENT_SECRET` | from script output |
| `GMAIL_REFRESH_TOKEN` | from script output |
| `GMAIL_SENDER_EMAIL` | the Gmail address you authorized |

The refresh token is long-lived — you won't need to redo this unless you revoke access
or change the sender. While the OAuth app is in "Testing" mode Google expires refresh
tokens every 7 days; publish the app (or keep only yourself as a test user and re-run
the helper if it ever stops working) to make the token permanent.

## Running it

**Manually on demand:** Actions tab → "Weekly Competitor Report" → Run workflow.
Toggle the `dry_run` checkbox to preview without sending — the rendered HTML is
attached to the run as an artifact (`competitor-report-html`).

**Weekly automatic:** Already scheduled for Monday 06:00 UTC (09:00 Bahrain).
Edit the cron in `.github/workflows/weekly-report.yml` to change.

## Local testing

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...
# Dry run: skips email, writes report.html, prints output
python -m src.main --dry-run

# Real run: also needs the Gmail secrets
export GMAIL_CLIENT_ID=...
export GMAIL_CLIENT_SECRET=...
export GMAIL_REFRESH_TOKEN=...
export GMAIL_SENDER_EMAIL=...
python -m src.main
```

## Known limitations

- **Instagram scraping is best-effort.** `instaloader` reads public profiles without
  logging in, but Instagram aggressively rate-limits anonymous requests and may
  occasionally return nothing. The report still sends, noting which competitors failed.
- **No share counts.** Instagram does not expose share/forward counts publicly. The
  report uses likes + comments as the engagement metric.
- **No Stories or Reels Insights.** Only feed posts and Reels (as posts) are captured.
  Ephemeral Stories are not retrievable without the competitor's own access token.
- If Instagram starts blocking GitHub's IP range, switching to a paid scraper (Apify,
  ScrapeCreators) is a drop-in replacement — only `src/scraper.py` changes.

## Files

```
config.yaml                         competitors, recipient, lookback window
src/scraper.py                      instaloader-based Instagram fetch
src/analyzer.py                     Claude-powered insights
src/emailer.py                      Gmail OAuth send
src/main.py                         orchestrator
scripts/gmail_oauth_setup.py        one-time local helper for refresh token
.github/workflows/weekly-report.yml schedule + manual trigger
```
