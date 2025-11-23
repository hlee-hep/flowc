import logging
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from flowc.config import Config

logger = logging.getLogger(__name__)


class PaperDatabase:
    def __init__(self, path: str | None = None):
        self.path = Path(path or Config.SQLITE_PATH)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row  # dict-like rows
        self._init_table()

    def _init_table(self):
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS papers (
                id TEXT PRIMARY KEY,
                title TEXT,
                summary TEXT,
                created_at TEXT
            )
            """
        )
        self.conn.commit()

    def paper_exists(self, paper_id: str) -> bool:
        cur = self.conn.cursor()
        cur.execute("SELECT 1 FROM papers WHERE id = ?", (paper_id,))
        return cur.fetchone() is not None

    def save_paper(self, paper_id: str, title: str, summary: str):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO papers (id, title, summary, created_at) VALUES (?, ?, ?, ?)",
            (paper_id, title, summary, datetime.utcnow().isoformat()),
        )
        self.conn.commit()
        logger.info("Saved paper %s to SQLite archive", paper_id)

    # ----------------------------------------------------------------------
    #  fetch last N papers
    # ----------------------------------------------------------------------
    def fetch_last_n(self, n: int = 20) -> list[dict]:
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT id, title, summary, created_at
            FROM papers
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (n,),
        )
        rows = cur.fetchall()
        return [dict(row) for row in rows]

    # ----------------------------------------------------------------------
    #  fetch papers within recent X days
    # ----------------------------------------------------------------------
    def fetch_recent_papers(self, days: int = 7) -> list[dict]:
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT id, title, summary, created_at
            FROM papers
            WHERE created_at >= ?
            ORDER BY created_at DESC
            """,
            (cutoff,),
        )
        rows = cur.fetchall()
        return [dict(row) for row in rows]

    def close(self):
        self.conn.close()
        logger.info("Closed SQLite connection to %s", self.path)
