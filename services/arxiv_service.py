import logging
import xml.etree.ElementTree as ET
import os
import yaml

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

    def parse(self, raw: str) -> list[dict]:
        if not raw:
            logger.warning("Empty arXiv payload received; skipping parse")
            return []

        try:
            root = ET.fromstring(raw)
        except ET.ParseError as exc:
            logger.error("Failed to parse arXiv feed: %s", exc)
            return []

        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = []
        for entry in root.findall("atom:entry", ns):
            title = entry.find("atom:title", ns).text
            summary = entry.find("atom:summary", ns).text
            link = entry.find("atom:link", ns).attrib.get("href")
            idx = entry.find("atom:id", ns).text
            entries.append({
                "id": idx,
                "title": title,
                "summary": summary,
                "link": link,
            })
        logger.info("Parsed %d arXiv entries", len(entries))
        return entries

    def filter_interesting(self, papers: list[dict]) -> list[dict]:
        dynamic_keywords = self.keyword_engine.generate(papers[:20]) 

        filtered = []
        for p in papers:
            title_lower = p["title"].lower()

            all_keywords = set(dynamic_keywords) | set(self.keyword_engine.base_keywords)
            #all_keywords = dynamic_keywords

            if any(kw in title_lower for kw in all_keywords):
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
        papers = self.parse(raw)
        interesting = self.filter_interesting(papers)
        logger.info("ArxivService run completed with %d papers", len(interesting))
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