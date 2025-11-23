import logging

from flowc.services.notion_service import NotionService

logger = logging.getLogger(__name__)


class DawnFlow:
    def __init__(self):
        self.notion = NotionService()

    def run(self) -> str:
        logger.info("Starting dawn flow: carrying TODO forward")
        self.notion.carry_over()
        logger.info("Dawn flow finished")