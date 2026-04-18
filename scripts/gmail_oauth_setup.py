"""One-time helper: run locally to obtain a Gmail refresh token.

Usage:
    1. Create a Google Cloud project, enable Gmail API.
    2. Create an OAuth 2.0 Client ID (Desktop app) — download the JSON.
    3. pip install google-auth-oauthlib
    4. python scripts/gmail_oauth_setup.py /path/to/client_secret.json

The script prints the refresh token, client ID, and client secret.
Copy these into your GitHub repo secrets as:
  GMAIL_CLIENT_ID
  GMAIL_CLIENT_SECRET
  GMAIL_REFRESH_TOKEN
  GMAIL_SENDER_EMAIL   (the gmail address you authorized)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 1

    secret_path = Path(sys.argv[1])
    if not secret_path.exists():
        print(f"Not found: {secret_path}")
        return 1

    flow = InstalledAppFlow.from_client_secrets_file(str(secret_path), SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")

    data = json.loads(secret_path.read_text())
    installed = data.get("installed") or data.get("web") or {}

    print("\n=== Copy these values into GitHub repo secrets ===")
    print(f"GMAIL_CLIENT_ID={installed.get('client_id', '')}")
    print(f"GMAIL_CLIENT_SECRET={installed.get('client_secret', '')}")
    print(f"GMAIL_REFRESH_TOKEN={creds.refresh_token}")
    print("GMAIL_SENDER_EMAIL=<the gmail address you just authorized>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
