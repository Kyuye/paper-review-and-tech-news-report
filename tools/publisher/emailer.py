from __future__ import annotations

from dataclasses import dataclass
from email.message import EmailMessage
import os
import smtplib


@dataclass(frozen=True)
class EmailSettings:
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_pass: str
    email_from: str
    email_to: str


def settings_from_env() -> EmailSettings:
    required = ["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASS", "EMAIL_FROM", "EMAIL_TO"]
    if not all(os.getenv(k) for k in required):
        missing = [k for k in required if not os.getenv(k)]
        raise RuntimeError(f"Missing email env: {', '.join(missing)}")
    return EmailSettings(
        smtp_host=os.environ["SMTP_HOST"],
        smtp_port=int(os.environ["SMTP_PORT"]),
        smtp_user=os.environ["SMTP_USER"],
        smtp_pass=os.environ["SMTP_PASS"],
        email_from=os.environ["EMAIL_FROM"],
        email_to=os.environ["EMAIL_TO"],
    )


def send_email(*, subject: str, body: str) -> None:
    s = settings_from_env()
    msg = EmailMessage()
    msg["From"] = s.email_from
    msg["To"] = s.email_to
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(s.smtp_host, s.smtp_port, timeout=30) as server:
        server.starttls()
        server.login(s.smtp_user, s.smtp_pass)
        server.send_message(msg)

