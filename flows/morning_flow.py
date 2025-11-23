import logging

from flowc.services.notion_service import NotionService
from flowc.services.telegram_digest_service import TelegramDigestService
from flowc.ai.summary import rewrite_daily_todo

logger = logging.getLogger(__name__)


class MorningFlow:
    def __init__(self):
        self.notion = NotionService()
        self.telegram = TelegramDigestService()

    def run(self) -> str:
        logger.info("Starting morning flow: preparing TODO digest")
        page = self.notion.get_today_page(self.notion.db_id)
        if not page:
            logger.info("No Notion page found for today; sending empty TODO list")
            raw_todo = ""
        else:
            logger.info("Fetched today's Notion page; reading TODO items")
            raw_todo = self.notion.read_todo(page)

        rewritten = rewrite_daily_todo(raw_todo)
        logger.info("Rewrote TODO list with AI; sending to Telegram")

        message = self._process_telegram(page, rewritten)

        return message

    def _process_telegram(self, page, todo):
        msg = self.telegram.build_message_for_morning(page, todo)
        self.telegram.send(msg)
        logger.info("Sent morning Telegram digest")
        return msg