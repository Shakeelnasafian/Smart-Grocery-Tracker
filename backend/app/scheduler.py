"""Background scheduler that sends expiry alert emails once per day."""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from apscheduler.schedulers.background import BackgroundScheduler
from app.config import settings
from app import models, crud

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def _send_email(to_email: str, subject: str, body: str) -> None:
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("SMTP not configured — skipping email to %s", to_email)
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.ALERT_FROM_EMAIL or settings.SMTP_USER
    msg["To"] = to_email
    msg.attach(MIMEText(body, "html"))

    try:
        # timeout=30 prevents the scheduler from blocking indefinitely
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(msg["From"], [to_email], msg.as_string())
        logger.info("Expiry alert email sent to %s", to_email)
    except Exception as exc:
        logger.error("Failed to send email to %s: %s", to_email, exc)


def _check_and_send_alerts() -> None:
    """Job that runs daily and emails users about expiring items."""
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        alert_settings = db.query(models.AlertSetting).filter_by(enabled=True).all()
        for setting in alert_settings:
            expiring = crud.get_expiring_items(db, setting.user_id, days=setting.days_before_expiry)
            if not expiring:
                continue

            rows = "".join(
                f"<tr><td>{i.name}</td><td>{i.category}</td>"
                f"<td>{i.expiry_date}</td><td>{i.quantity}</td></tr>"
                for i in expiring
            )
            body = (
                "<html><body>"
                "<h2>Grocery Expiry Alert</h2>"
                f"<p>The following items are expiring within "
                f"<strong>{setting.days_before_expiry} days</strong>:</p>"
                '<table border="1" cellpadding="6" cellspacing="0">'
                "<thead><tr><th>Name</th><th>Category</th>"
                "<th>Expiry Date</th><th>Quantity</th></tr></thead>"
                f"<tbody>{rows}</tbody></table>"
                "<p>Log in to your Smart Grocery Tracker to take action.</p>"
                "</body></html>"
            )
            _send_email(
                setting.email,
                f"[Smart Grocery] {len(expiring)} item(s) expiring soon!",
                body,
            )
    finally:
        db.close()


def start_scheduler() -> None:
    if scheduler.running:
        return
    # replace_existing=True makes the job idempotent (safe in multi-worker restarts)
    scheduler.add_job(
        _check_and_send_alerts,
        "cron",
        hour=8,
        minute=0,
        id="expiry_alerts",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Background scheduler started — expiry alerts at 08:00 daily")


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown()
