import logging
import time
from datetime import datetime, timedelta

import requests


logger = logging.getLogger(__name__)

class ArxivAPI:
    BASE_URL = "https://export.arxiv.org/api/query"

    def fetch(self, max_results=50) -> str:
        params = {
            "search_query": "(cat:hep-ex OR cat:hep-ph)",
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }

        for attempt in range(1, 4):
            try:
                logger.info("arXiv fetch attempt %d", attempt)
                resp = requests.get(self.BASE_URL, params=params, timeout=10)
                resp.raise_for_status()
                return resp.text
            except Exception as e:
                logger.warning("arXiv attempt %d failed: %s", attempt, e)
                time.sleep(attempt)

        return ""
