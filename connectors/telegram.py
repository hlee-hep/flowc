import requests
from flowc.config import Config

class TelegramClient:
    def __init__(self):
        if not Config.TELEGRAM_BOT_TOKEN or not Config.TELEGRAM_CHAT_ID:
            raise RuntimeError("Telegram config not set")
        self.base_url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}"

    def send(self, text: str, parse_mode: str = "Markdown"):
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": Config.TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": parse_mode,
        }
        res = requests.post(url, json=payload, timeout=10)
        res.raise_for_status()
        return res.json()
