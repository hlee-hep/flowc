import logging

from flowc.services.notion_service import NotionService
from flowc.services.telegram_digest_service import TelegramDigestService
from flowc.services.arxiv_service import ArxivService
from flowc.ai.summary import rewrite_daily_todo

logger = logging.getLogger(__name__)


class MorningFlow:
    def __init__(self):
        self.notion = NotionService()
        self.telegram = TelegramDigestService()
        self.arxiv = ArxivService()  # ★ 추가

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
        logger.info("Rewrote TODO list with AI; preparing morning Telegram digest")

        # ★ NEW: Load today's HotPaper
        hot = self.arxiv.get_hot_pick()
        if hot:
            logger.info("Loaded today's HotPaper for morning digest")
        else:
            logger.warning("No HotPaper available for today")
            hot = None

        # Send message (includes TODO + HotPaper)
        message = self._process_telegram(page, rewritten, hot)

        return message

    def _process_telegram(self, page, todo, hot):
        msg = self.telegram.build_message_for_morning(page, todo, hot)
        self.telegram.send(msg)
        logger.info("Sent morning Telegram digest")
        return msg
