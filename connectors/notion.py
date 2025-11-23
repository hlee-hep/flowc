import logging
import time

import requests
from flowc.config import Config


logger = logging.getLogger(__name__)

class NotionClient:
    def __init__(self):
        if not Config.NOTION_TOKEN:
            raise RuntimeError("NOTION_TOKEN not set")
        self.headers = {
            "Authorization": f"Bearer {Config.NOTION_TOKEN}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        }

    def _request(self, method: str, url: str, *, retries: int = 3, retry_delay: float = 1.0, fallback=None, **kwargs):
        last_error = None
        for attempt in range(1, retries + 1):
            try:
                res = requests.request(method, url, headers=self.headers, timeout=10, **kwargs)
                res.raise_for_status()
                return res.json()
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                logger.warning(
                    "Notion request failed (attempt %s/%s): %s", attempt, retries, exc
                )
                if attempt < retries:
                    time.sleep(retry_delay * attempt)

        logger.error("Notion request failed after %s attempts: %s", retries, last_error)
        return fallback

    def query_by_date(self, db_id, date_str):
        url = f"https://api.notion.com/v1/databases/{db_id}/query"
        payload = {"filter": {"property": "Date", "date": {"equals": date_str}}}
        res = self._request("POST", url, json=payload, fallback={"results": []})
        results = res.get("results", []) if res else []
        return results[0] if results else None

    def update_page(self, page_id, properties):
        url = f"https://api.notion.com/v1/pages/{page_id}"
        return self._request(
            "PATCH",
            url,
            json={"properties": properties},
            fallback={},
        )

    def create_page(self, db_id, properties):
        url = "https://api.notion.com/v1/pages"
        payload = {"parent": {"database_id": db_id}, "properties": properties}
        return self._request("POST", url, json=payload, fallback={})

    @staticmethod
    def get_text(props, field):
        try:
            blocks = props[field]["rich_text"]
            return "\n".join(b.get("plain_text", "") for b in blocks).strip()
        except Exception:
            return ""
