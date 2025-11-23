from flowc.services.notion_service import NotionService
from flowc.services.telegram_digest_service import TelegramDigestService
from flowc.ai.summary import rewrite_daily_todo


class MorningFlow:
    def __init__(self):
        self.notion = NotionService()
        self.telegram = TelegramDigestService()

    def run(self) -> str:
        page = self.notion.get_today_page(self.notion.db_id)

        if not page:
            text = "No Notion daily page found for today."
            self.telegram.send(text)
            return text

        raw_todo = self.notion.read_todo(page)

        if not raw_todo.strip():
            text = "No TODO items for today."
            self.telegram.send(text)
            return text

        rewritten = rewrite_daily_todo(raw_todo)

        message = self.telegram.format_morning(rewritten)

        self.telegram.send(message)

        return message
