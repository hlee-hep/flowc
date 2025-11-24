import logging

from flowc.services.notion_service import NotionService
from flowc.services.arxiv_service import ArxivService
from flowc.connectors.hot_paper_pool import HotPaperPool
from flowc.connectors.hot_paper_history import HotPaperHistory
logger = logging.getLogger(__name__)


class DawnFlow:
    def __init__(self):
        self.notion = NotionService()
        self.arxiv = ArxivService()
        self.pool = HotPaperPool()
        self.history = HotPaperHistory()

    def run(self) -> str:
        logger.info("Starting dawn flow: carrying TODO forward")
        self.notion.carry_over()

        logger.info("Dawn flow: selecting today's hot paper from pool")
        paper = self.pool.get_one_unused()
        if not paper:
            logger.warning("Dawn flow: no unused hot papers left in pool")
            self.arxiv.save_hot_papers({"papers": []})
            return "No hot paper available."

        self.pool.mark_used(paper["id"])

        data = {
            "papers": [
                {
                    "title": paper["title"],
                    "summary": paper["summary"],
                    "year": paper.get("year"),
                    "arxiv": paper.get("arxiv"),
                }
            ]
        }

        logger.info("Dawn flow: saving today's hot paper")
        self.arxiv.save_hot_papers(data)
        self.history.save(data)
        logger.info("Dawn flow finished")
        return "OK"
