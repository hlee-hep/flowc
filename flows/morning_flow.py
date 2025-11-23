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
            raw_todo = ""
        else:
            raw_todo = self.notion.read_todo(page)

        rewritten = rewrite_daily_todo(raw_todo)

        message = self._process_telegram(page,rewritten)

        return message

    def _process_telegram(self, page, todo):
        msg = self.telegram.build_message_for_morning(page,todo)
        self.telegram.send(msg)
        return msg