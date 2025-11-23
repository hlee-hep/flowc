import requests
from flowc.config import Config

class NotionClient:
    def __init__(self):
        if not Config.NOTION_TOKEN:
            raise RuntimeError("NOTION_TOKEN not set")
        self.headers = {
            "Authorization": f"Bearer {Config.NOTION_TOKEN}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        }

    def query_by_date(self, db_id, date_str):
        url = f"https://api.notion.com/v1/databases/{db_id}/query"
        payload = {"filter": {"property": "Date", "date": {"equals": date_str}}}
        res = requests.post(url, headers=self.headers, json=payload)
        res.raise_for_status()
        results = res.json().get("results", [])
        return results[0] if results else None

    def update_page(self, page_id, properties):
        url = f"https://api.notion.com/v1/pages/{page_id}"
        res = requests.patch(url, headers=self.headers,
                             json={"properties": properties})
        res.raise_for_status()
        return res.json()

    def create_page(self, db_id, properties):
        url = "https://api.notion.com/v1/pages"
        payload = {"parent": {"database_id": db_id}, "properties": properties}
        res = requests.post(url, headers=self.headers, json=payload)
        res.raise_for_status()
        return res.json()

    @staticmethod
    def get_text(props, field):
        try:
            blocks = props[field]["rich_text"]
            return "\n".join(b.get("plain_text", "") for b in blocks).strip()
        except Exception:
            return ""
