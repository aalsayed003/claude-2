"""Send reports via Gmail using OAuth refresh token."""

from __future__ import annotations

import base64
import logging
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

log = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def _build_service():
    creds = Credentials(
        token=None,
        refresh_token=os.environ["GMAIL_REFRESH_TOKEN"],
        client_id=os.environ["GMAIL_CLIENT_ID"],
        client_secret=os.environ["GMAIL_CLIENT_SECRET"],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
    )
    creds.refresh(Request())
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def send_report(
    to_email: str,
    subject: str,
    html_body: str,
    plain_body: str,
    sender_name: str,
) -> None:
    service = _build_service()
    sender_email = os.environ.get("GMAIL_SENDER_EMAIL", "me")

    msg = MIMEMultipart("alternative")
    msg["To"] = to_email
    msg["From"] = f"{sender_name} <{sender_email}>" if sender_email != "me" else sender_name
    msg["Subject"] = subject
    msg.attach(MIMEText(plain_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw}).execute()
    log.info("Sent report to %s", to_email)
