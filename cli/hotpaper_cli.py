import logging
from flowc.connectors.hot_paper_pool import HotPaperPool

logger = logging.getLogger(__name__)


class HotPaperCLI:
    def __init__(self):
        self.pool = HotPaperPool()

    # ------------------------------
    # list all papers
    # ------------------------------
    def list_all(self):
        papers = self.pool.fetch_all()
        for p in papers:
            flag = "USED" if p["used"] else "unused"
            print(f"[{flag}] {p['id']} — {p['title']} ({p.get('year')})")

    # ------------------------------
    # list only unused
    # ------------------------------
    def list_unused(self):
        papers = self.pool.fetch_unused()
        for p in papers:
            print(f"[unused] {p['id']} — {p['title']} ({p.get('year')})")

    # ------------------------------
    # list only used
    # ------------------------------
    def list_used(self):
        papers = self.pool.fetch_used()
        for p in papers:
            print(f"[USED] {p['id']} — {p['title']} ({p.get('year')})")

    # ------------------------------
    # show one paper by ID
    # ------------------------------
    def show(self, pid: str):
        p = self.pool.get_by_id(pid)
        if not p:
            print(f"No paper with id={pid}")
            return

        print("---------------------------------------------------")
        print(f"Title : {p['title']}")
        print(f"Year  : {p.get('year')}")
        print(f"arXiv : {p.get('arxiv')}")
        print(f"Used  : {p.get('used')}")
        print("---------------------------------------------------")
        print("Summary:")
        print(p["summary"])
        print("---------------------------------------------------")

    # ------------------------------
    # search by keyword in title
    # ------------------------------
    def search(self, keyword: str):
        papers = self.pool.fetch_all()
        kw = keyword.lower()
        found = [
            p for p in papers
            if kw in p["title"].lower()
        ]

        if not found:
            print(f"No papers found containing '{keyword}'.")
            return

        for p in found:
            flag = "USED" if p["used"] else "unused"
            print(f"[{flag}] {p['id']} — {p['title']} ({p.get('year')})")

    # ------------------------------
    # stats
    # ------------------------------
    def stats(self):
        total = self.pool.count_all()
        unused = self.pool.count_unused()
        used = self.pool.count_used()

        print("------ Hot Paper Pool Stats ------")
        print(f"Total papers : {total}")
        print(f"Unused       : {unused}")
        print(f"Used         : {used}")
        print("----------------------------------")
