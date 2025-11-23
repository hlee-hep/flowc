from flowc.connectors.telegram import TelegramClient

class TelegramDigestService:
    def __init__(self):
        self.client = TelegramClient()

    def format_morning(self, plan_text: str) -> str:
        return f"*Morning Plan*\n\n{plan_text}"

    def format_evening(self, summary_text: str) -> str:
        return f"*Evening Summary*\n\n{summary_text}"

    def send(self, text: str):
        self.client.send(text)
