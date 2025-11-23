import requests
from datetime import datetime, timedelta

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

        resp = requests.get(self.BASE_URL, params=params, timeout=10)
        try:
            resp.raise_for_status()
        except Exception as e:
            print("[ArxivAPI] HTTP error:", e)
            print(resp.text[:200])
            return ""

        return resp.text