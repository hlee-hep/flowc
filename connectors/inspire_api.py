# flowc/connectors/inspire_api.py

import logging
import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://inspirehep.net/api/literature"


class InspireAPI:
    """
    Thin wrapper around INSPIRE-HEP literature API.
    """

    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout

    def fetch(
        self,
        query: str,
        size: int = 25,
        page: int = 1,
        sort: str | None = None,
        fields: str | None = None,
    ) -> dict | None:
        """
        Fetch one page from INSPIRE.

        query: INSPIRE search query string
        size:  number of results per page
        page:  page number (1-based)
        sort:  e.g. 'mostcited' (optional)
        fields: comma-separated list of fields (optional)
        """
        params: dict[str, str | int] = {
            "q": query,
            "size": size,
            "page": page,
        }
        if sort:
            params["sort"] = sort
        if fields:
            params["fields"] = fields

        try:
            resp = requests.get(BASE_URL, params=params, timeout=self.timeout)
            resp.raise_for_status()
        except Exception as exc:
            logger.error("InspireAPI: request failed: %s", exc)
            return None

        try:
            data = resp.json()
        except Exception as exc:
            logger.error("InspireAPI: JSON decode failed: %s", exc)
            return None

        return data
