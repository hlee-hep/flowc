import smtplib
import time
import logging
from email.mime.text import MIMEText
from flowc.config import Config

logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self):
        if not Config.SMTP_HOST:
            raise RuntimeError("SMTP config not set")

    def send(
        self,
        html: str,
        subject: str = "[FlowC] Daily Report",
        retries: int = 3,
        retry_delay: float = 2.0,
        fallback_ok: bool = True,
    ):
        msg = MIMEText(html, "html", "utf-8")
        msg["Subject"] = subject
        msg["From"] = Config.SMTP_FROM
        msg["To"] = Config.SMTP_TO

        last_error = None

        for attempt in range(1, retries + 1):
            try:
                with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT, timeout=10) as server:
                    server.starttls()
                    if Config.SMTP_USER:
                        server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
                    server.send_message(msg)

                logger.info("Email sent successfully via %s:%s", Config.SMTP_HOST, Config.SMTP_PORT)
                return True

            except Exception as exc:
                last_error = exc
                logger.warning(
                    "Email send failed (attempt %s/%s): %s",
                    attempt, retries, exc
                )
                if attempt < retries:
                    time.sleep(retry_delay * attempt)

        logger.error("Email send failed after %s attempts: %s", retries, last_error)

        if fallback_ok:
            return False

        raise last_error
