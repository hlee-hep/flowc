from flowc.services.notion_service import NotionService

class DawnFlow:
    def __init__(self):
        self.notion = NotionService()

    def run(self) -> str:
        self.notion.carry_over()