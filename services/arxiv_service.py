import logging
import xml.etree.ElementTree as ET
import os
import yaml
import dateutil.parser as dp
from datetime import datetime, timedelta, timezone

from flowc.connectors.arxiv_api import ArxivAPI
from flowc.connectors.db import PaperDatabase
from flowc.ai.keyword_engine import KeywordEngine

HOT_PAPER_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "hot_papers.yaml"
)

logger = logging.getLogger(__name__)

class ArxivService:
    def __init__(self):
        self.api = ArxivAPI()
        self.db = PaperDatabase()
        self.keyword_engine = KeywordEngine()

    def fetch_raw(self) -> str:
        logger.info("Fetching arXiv feed")
        return self.api.fetch()

    def parse(self, raw: str, days=1) -> list[dict]:
        if not raw:
            return []

        try:
            root = ET.fromstring(raw)
        except ET.ParseError:
            return []

        ns = {"atom": "http://www.w3.org/2005/Atom"}

        # UTC awareness
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        papers = []

        for entry in root.findall("atom:entry", ns):
            updated_str = entry.find("atom:updated", ns).text
            updated = dp.parse(updated_str)

            # ensure updated is aware (UTC)
            if updated.tzinfo is None:
                updated = updated.replace(tzinfo=timezone.utc)
            else:
                updated = updated.astimezone(timezone.utc)

            # filter
            if updated < cutoff:
                continue

            papers.append({
                "id": entry.find("atom:id", ns).text,
                "title": entry.find("atom:title", ns).text.strip(),
                "summary": entry.find("atom:summary", ns).text.strip(),
                "link": entry.find("atom:id", ns).text,
                "updated": updated,
            })

        logger.info("Parsed %d entries after date filter", len(papers))
        return papers

    def filter_interesting(self, papers: list[dict]) -> list[dict]:
        ai_keywords = self.keyword_engine.generate(papers[:20])

        all_keywords = set(self.keyword_engine.base_keywords) | set(ai_keywords)

        filtered = []
        for p in papers:
            title_lower = p["title"].lower()
            summary_lower = p["summary"].lower()

            k1 = any(kw in title_lower for kw in all_keywords)
            k2 = any(kw in summary_lower for kw in all_keywords)

            k3 = any(kw in title_lower for kw in self.keyword_engine.base_keywords)

            k4 = "phys" in title_lower or "hep" in title_lower

            if k1 or k2 or k3 or k4:
                if not self.db.paper_exists(p["id"]):
                    filtered.append(p)

        logger.info("Filtered %d interesting new arXiv papers", len(filtered))
        return filtered

    def save(self, paper_id: str, title: str, summary: str):
        logger.info("Persisting arXiv paper %s to database", paper_id)
        self.db.save_paper(paper_id, title, summary)

    def format_paper(self, p: dict, summary: str) -> str:
        return f"**{p['title']}**\n{summary}\n{p['link']}"

    def run(self) -> list[dict]:
        raw = self.fetch_raw()

        papers = self.parse(raw, days=1)

        if len(papers) == 0:
            logger.info("No papers in last 1 day, falling back to last 3 days")
            papers = self.parse(raw, days=3)

        interesting = self.filter_interesting(papers)
        return interesting
        
    def format_html(self, p: dict, summary: str) -> str:
        return f"<b>{p['title']}</b><br>{summary}<br><a href='{p['link']}'>[link]</a><br><br>"

    def load_hot_papers(self) -> dict:
        if not os.path.exists(HOT_PAPER_PATH):
            return {"papers": []}
        with open(HOT_PAPER_PATH, "r") as f:
            return yaml.safe_load(f) or {"papers": []}

    def save_hot_papers(self, data: dict):
        """data should be {"papers": [exactly one paper]}"""
        os.makedirs(os.path.dirname(HOT_PAPER_PATH), exist_ok=True)
        with open(HOT_PAPER_PATH, "w") as f:
            yaml.dump(data, f, allow_unicode=True)
        logger.info("ArxivService: saved today's hot paper → hot_papers.yaml")

    def get_hot_pick(self) -> dict | None:
        """Return today's saved paper (the only one)."""
        data = self.load_hot_papers()
        papers = data.get("papers", [])

        if not papers:
            logger.warning("Hot paper list is empty")
            return None

        # Since there is always exactly one, return it
        return papers[0]