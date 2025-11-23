import logging
import time
from datetime import datetime, timedelta

import requests


logger = logging.getLogger(__name__)

class ArxivAPI:
    BASE_URL = "https://export.arxiv.org/api/query"

    def fetch(self, days=1, max_results=30) -> str:
        end = datetime.utcnow()
        start = end - timedelta(days=days)

        start_str = start.strftime("%Y%m%d0000")
        end_str   = end.strftime("%Y%m%d2359")

        query = (
            f"(cat:hep-ex OR cat:hep-ph) AND "
            f"submittedDate:[{start_str} TO {end_str}]"
        )

        params = {
            "search_query": query,
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }

        last_error = None
        for attempt in range(1, 4):
            try:
                resp = requests.get(self.BASE_URL, params=params, timeout=10)
                resp.raise_for_status()
                return resp.text
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                logger.warning(
                    "Arxiv fetch failed (attempt %s/3): %s", attempt, exc
                )
                if attempt < 3:
                    time.sleep(attempt)

        logger.error("Arxiv fetch failed after retries: %s", last_error)
        return ""