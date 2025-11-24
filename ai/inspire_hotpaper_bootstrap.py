import logging
import hashlib

from flowc.connectors.inspire_api import InspireAPI
from flowc.connectors.hot_paper_pool import HotPaperPool
from flowc.ai.openai_client import AI

logger = logging.getLogger(__name__)


class InspireHotPaperBootstrap:
    """
    Use INSPIRE-HEP API to fill HotPaperPool with REAL experimental HEP landmark papers.
    """

    def __init__(self):
        self.api = InspireAPI()
        self.pool = HotPaperPool()

    # ----------------------------------------------------------
    # make persistent ID
    # ----------------------------------------------------------
    def _make_id(self, title: str, arxiv: str | None, year: int | None) -> str:
        if arxiv:
            return arxiv.strip()
        base = f"{title.strip()}::{year or ''}"
        return "inspire::" + hashlib.sha1(base.encode("utf-8")).hexdigest()[:12]

    # ----------------------------------------------------------
    # parse INSPIRE JSON
    # ----------------------------------------------------------
    def _extract_papers_from_page(self, data: dict) -> list[dict]:
        hits = data.get("hits", {}).get("hits", [])
        out: list[dict] = []

        for h in hits:
            md = h.get("metadata", {})

            # title
            titles = md.get("titles") or []
            if not titles:
                continue
            title = titles[0].get("title", "").strip()
            if not title:
                continue

            # abstract
            abstracts = md.get("abstracts") or []
            raw_summary = ""
            if abstracts:
                raw_summary = (abstracts[0].get("value") or "").strip()

            # year
            year = None
            earliest = md.get("earliest_date")
            if earliest:
                try:
                    year = int(str(earliest)[:4])
                except Exception:
                    year = None

            # arxiv
            arxiv_id = None
            arxivs = md.get("arxiv_eprints") or []
            if arxivs:
                arxiv_id = arxivs[0].get("value", None)

            if raw_summary:
                prompt = f"""
    Rewrite the following physics paper abstract into a short, clean summary
    for a daily digest. Keep it factual, concise, and accurate.

    Abstract:
    {raw_summary}

    Return only the rewritten summary.
    """
                clean_summary = AI.model("gpt-4o").ask(prompt, ttl=86400)
                if not clean_summary:
                    clean_summary = raw_summary
            else:
                clean_summary = ""

            out.append(
                {
                    "title": title,
                    "summary": clean_summary,   
                    "year": year,
                    "arxiv": arxiv_id,
                }
            )

        return out


    # ----------------------------------------------------------
    # fetch and insert
    # ----------------------------------------------------------
    def fetch_and_fill(self, query: str, *, pages: int, size: int,
                       target_size: int, sort: str = "mostcited") -> None:

        logger.info("INSPIRE query: %s", query)

        for page in range(1, pages + 1):
            if self.pool.remaining_count() >= target_size:
                logger.info("Target size reached. stopping.")
                return

            logger.info("Fetching page %d/%d", page, pages)

            data = self.api.fetch(
                query=query,
                size=size,
                page=page,
                sort=sort,
            )
            if not data:
                logger.warning("No data for page %d", page)
                continue

            papers = self._extract_papers_from_page(data)
            logger.info("Extracted %d papers", len(papers))

            for p in papers:
                pid = self._make_id(p["title"], p["arxiv"], p["year"])
                self.pool.add_paper(
                    pid=pid,
                    title=p["title"],
                    summary=p["summary"],
                    year=p["year"],
                    arxiv=p["arxiv"],
                )

            logger.info("Pool now has %d papers", self.pool.remaining_count())

    # ----------------------------------------------------------
    # FINAL: landmark bootstrap
    # ----------------------------------------------------------
    def bootstrap_default(self, target_size: int = 300):
        """
        Build landmark pool (ATLAS/CMS/CDF/D0/LHCb, Super-K/T2K/MINOS/NOvA,
        Belle/Belle-II/BaBar). Each query is real INSPIRE syntax.
        """

        logger.info("INSPIRE bootstrap to target=%d", target_size)

        # collider (LHC + Tevatron)
        collider = (
            "(collaboration:ATLAS OR collaboration:CMS OR "
            "collaboration:CDF OR collaboration:D0 OR collaboration:LHCb)"
        )
        self.fetch_and_fill(
            query=f"{collider} AND year:1970->2025",
            pages=5,
            size=25,
            target_size=target_size,
        )

        # neutrino (Super-K / T2K / MINOS / NOvA / K2K / IceCube)
        if self.pool.remaining_count() < target_size:
            neutrino = (
                "(collaboration:\"Super-Kamiokande\" OR collaboration:Kamiokande OR "
                "collaboration:T2K OR collaboration:MINOS OR collaboration:NOvA OR "
                "collaboration:K2K OR collaboration:IceCube)"
            )
            self.fetch_and_fill(
                query=f"{neutrino} AND year:1960->2025",
                pages=4,
                size=25,
                target_size=target_size,
            )

        # flavour (Belle / Belle II / BaBar)
        if self.pool.remaining_count() < target_size:
            flavour = (
                "(collaboration:Belle OR collaboration:\"Belle II\" OR collaboration:BaBar)"
            )
            self.fetch_and_fill(
                query=f"{flavour} AND year:1980->2025",
                pages=4,
                size=25,
                target_size=target_size,
            )

        logger.info(
            "INSPIRE bootstrap completed. pool=%d",
            self.pool.remaining_count(),
        )
