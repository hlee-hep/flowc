import requests
import time
import logging
from flowc.config import Config

logger = logging.getLogger(__name__)

class TelegramClient:
    def __init__(self):
        if not Config.TELEGRAM_BOT_TOKEN or not Config.TELEGRAM_CHAT_ID:
            raise RuntimeError("Telegram config not set")
        self.base_url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}"

    def send(
        self,
        text: str,
        parse_mode: str = "Markdown",
        retries: int = 3,
        retry_delay: float = 2.0,
        fallback_ok: bool = True,
    ):
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": Config.TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": parse_mode,
        }

        last_error = None

        for attempt in range(1, retries + 1):
            try:
                res = requests.post(url, json=payload, timeout=10)
                res.raise_for_status()
                logger.info("Telegram message sent successfully (attempt %s)", attempt)
                return res.json()

            except Exception as exc:
                last_error = exc
                logger.warning(
                    "Telegram send failed (attempt %s/%s): %s",
                    attempt, retries, exc
                )
                if attempt < retries:
                    time.sleep(retry_delay * attempt)

        logger.error("Telegram send failed after %s attempts: %s", retries, last_error)

        if fallback_ok:
            return {"ok": False, "error": str(last_error)}

        raise last_error
