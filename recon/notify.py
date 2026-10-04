"""Webhook and SMTP notifications for reconciliation results."""
from dataclasses import dataclass
from email.message import EmailMessage
import json
import smtplib
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class NotificationSettings:
    webhook_url: str | None = None
    smtp_host: str | None = None
    smtp_port: int = 25
    smtp_to: str | None = None
    smtp_from: str | None = None
    enabled: bool = False
    force_on_fatal: bool = True


def summarize(result):
    differences = result.get("differences", [])
    fatal = sum(item.get("status") in {"left_only", "right_only", "data_missing", "chain_mismatch"} for item in differences)
    serious = sum(item.get("status") in {"mismatch", "total_mismatch", "plugin_mismatch"} for item in differences)
    return {"differences": len(differences), "fatal": fatal, "serious": serious, "passed": not differences}


def notify_result(result, settings: NotificationSettings, opener=urlopen, smtp_factory=smtplib.SMTP):
    if not isinstance(settings, NotificationSettings):
        raise TypeError("settings 必须是 NotificationSettings")
    summary = summarize(result)
    should_send = settings.enabled or (settings.force_on_fatal and summary["fatal"] > 0)
    if not should_send:
        return {"sent": False, "summary": summary, "channels": {}}
    payload = {"event": "reconciliation.completed", "summary": summary}
    channels = {}
    if settings.webhook_url:
        request = Request(settings.webhook_url, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
        with opener(request, timeout=15) as response:
            channels["webhook"] = {"status": getattr(response, "status", 200)}
    if settings.smtp_host and settings.smtp_to:
        message = EmailMessage(); message["Subject"] = "recon-helper 核对结果"; message["From"] = settings.smtp_from or "recon-helper@localhost"; message["To"] = settings.smtp_to
        message.set_content(json.dumps(payload, ensure_ascii=False, indent=2))
        with smtp_factory(settings.smtp_host, settings.smtp_port, timeout=15) as client:
            client.send_message(message)
        channels["smtp"] = {"recipient": settings.smtp_to}
    return {"sent": bool(channels), "summary": summary, "channels": channels}
