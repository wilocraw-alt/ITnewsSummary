"""
sender.py — Read Markdown, convert to HTML, send via SMTP (multipart)
"""
from __future__ import annotations
import os
import smtplib
import sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import markdown as md_lib


def _subject(period: str, date: datetime) -> str:
    label = "오전" if period == "morning" else "오후"
    return f"[AI 뉴스] {date.strftime('%Y-%m-%d')} {label}"


def _html_wrapper(body_html: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: -apple-system, sans-serif; max-width: 680px;
          margin: 0 auto; padding: 1.5em; color: #222; line-height: 1.6; }}
  h1 {{ font-size: 1.4em; border-bottom: 2px solid #0057b7; padding-bottom: .4em; }}
  h2 {{ font-size: 1.1em; margin-top: 1.5em; }}
  a  {{ color: #0057b7; }}
  code {{ background: #f4f4f4; padding: .1em .3em; border-radius: 3px; }}
  blockquote {{ border-left: 3px solid #ccc; margin: 0; padding-left: 1em; color: #555; }}
</style>
</head>
<body>
{body_html}
</body>
</html>"""


def send_email(
    md_path: str,
    period: str,
    smtp_host: str,
    smtp_port: int | str,
    smtp_user: str,
    smtp_password: str,
    recipients: list[str] | str,
    date: datetime | None = None,
    dry_run: bool = False,
) -> None:
    """Read *md_path*, build multipart email, send via SMTP-STARTTLS."""
    if date is None:
        date = datetime.now()
    if isinstance(recipients, str):
        recipients = [r.strip() for r in recipients.split(",") if r.strip()]
    if not recipients:
        raise ValueError("No recipients specified")

    text = Path(md_path).read_text(encoding="utf-8")
    body_html = md_lib.markdown(text, extensions=["tables", "fenced_code", "nl2br"])
    full_html = _html_wrapper(body_html)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = _subject(period, date)
    msg["From"] = smtp_user
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(text, "plain", "utf-8"))
    msg.attach(MIMEText(full_html, "html", "utf-8"))

    if dry_run:
        print(f"[sender] DRY RUN — would send '{msg['Subject']}' to {recipients}")
        return

    with smtplib.SMTP(smtp_host, int(smtp_port)) as server:
        server.ehlo()
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, recipients, msg.as_string())

    print(f"[sender] Sent '{msg['Subject']}' → {recipients}")


if __name__ == "__main__":
    import argparse
    from dotenv import load_dotenv

    load_dotenv()
    parser = argparse.ArgumentParser(description="Send AI news email")
    parser.add_argument("md_file", help="Markdown file to send")
    parser.add_argument("period", choices=["morning", "evening"])
    parser.add_argument("--dry-run", action="store_true", help="Print but do not send")
    args = parser.parse_args()

    send_email(
        md_path=args.md_file,
        period=args.period,
        smtp_host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
        smtp_port=os.getenv("SMTP_PORT", "587"),
        smtp_user=os.getenv("SMTP_USER", ""),
        smtp_password=os.getenv("SMTP_PASSWORD", ""),
        recipients=os.getenv("EMAIL_RECIPIENTS", ""),
        dry_run=args.dry_run,
    )
