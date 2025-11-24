import logging
from datetime import datetime, date, timedelta
from flowc.connectors.notion import NotionClient
from flowc.config import Config
from flowc.utils.markdown_to_rich_text import markdown_to_rich_text

logger = logging.getLogger(__name__)

class NotionService:
    """
    Notion service
    """
    def __init__(self):
        self.client = NotionClient()
        self.db_id = Config.NOTION_DAILY_DB
    
    def get_today_page(self, db_id: str):
        today = datetime.now().strftime("%Y-%m-%d")
        logger.info("Querying Notion for page with date %s", today)
        return self.client.query_by_date(db_id, today)

    def read_field(self, page, name: str) -> str:
        return NotionClient.get_text(page["properties"], name)

    def write_field(self, page_id: str, field: str, text: str, markdown: bool = True):
        if markdown:
            rich = markdown_to_rich_text(text)
        else:
            rich = [{"text": {"content": text}}]

        return self.client.update_page(
            page_id,
            {
                field: {
                    "rich_text": rich,
                }
            }
        )

    def read_todo(self, page) -> str:
        return self.read_field(page, "TODO")

    def read_summary(self, page) -> str:
        return self.read_field(page, "Summary")

    def read_time_summary(self, page) -> str:
        return self.read_field(page, "TimeSummary")

    def write_ai_summary(self, page_id: str, summary: str):
        return self.write_field(page_id, "AISummary", summary)

    def write_git_summary(self, page_id: str, summary: str):
        return self.write_field(page_id, "GitSummary", summary)

    def write_tomorrow(self, page_id: str, plan: str):
        return self.write_field(page_id, "Tomorrow", plan)

    def carry_over(self):
        """Yesterday.Tomorrow -> Today's TODO."""
        today = date.today().isoformat()
        yesterday = (date.today() - timedelta(days=1)).isoformat()

        y_page = self.client.query_by_date(self.db_id, yesterday)
        if not y_page:
            logger.warning("No Notion page found for yesterday; skipping carry-over")
            return

        carry_text = self.client.get_text(y_page["properties"], "Tomorrow")
        if not carry_text:
            logger.info("No 'Tomorrow' items to carry over from yesterday")
            return

        t_page = self.client.query_by_date(self.db_id, today)

        if t_page:
            logger.info("Updating today's TODO from yesterday's 'Tomorrow' field")
            self.client.update_page(
                t_page["id"],
                {
                    "TODO": {
                        "rich_text": [{"text": {"content": carry_text}}]
                    }
                }
            )
            logger.info("Updated today's TODO with carried-over items")
            return

        props = {
            "Name": {"title": [{"text": {"content": f"Daily Log — {today}"}}]},
            "Date": {"date": {"start": today}},
            "TODO": {"rich_text": [{"text": {"content": carry_text}}]},
            "Summary": {"rich_text": []},
            "GitSummary": {"rich_text": []},
            "AISummary": {"rich_text": []},
            "Tomorrow": {"rich_text": []}
        }
        new_page = self.client.create_page(self.db_id, props)
        logger.info("Created new Notion page for today with carried TODO items")