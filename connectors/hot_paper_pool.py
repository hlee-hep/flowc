import logging
import sqlite3
from pathlib import Path
from datetime import datetime
from flowc.config import Config

logger = logging.getLogger(__name__)


class HotPaperPool:
    """
    Pre-filled pool of historically important HEP papers.
    We only POP ONE per day in DawnFlow.
    """

    def __init__(self, path: str | None = None):
        self.path = Path(path or Config.SQLITE_PATH)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self._init_table()

    def _init_table(self):
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS hot_paper_pool (
                id TEXT PRIMARY KEY,        -- internal key (usually arxiv or synthetic)
                title TEXT NOT NULL,
                summary TEXT,
                year INTEGER,
                arxiv TEXT,                 -- raw arxiv ID as string (may be None)
                created_at TEXT,
                used INTEGER DEFAULT 0      -- 0: not used, 1: already consumed
            )
            """
        )
        cur.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_hot_paper_title_year
            ON hot_paper_pool(title, year)
            """
        )
        self.conn.commit()

    def add_paper(self, pid: str, title: str, summary: str, year: int | None, arxiv: str | None):
        """
        Insert one paper into the pool.
        """
        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                INSERT OR IGNORE INTO hot_paper_pool
                (id, title, summary, year, arxiv, created_at, used)
                VALUES (?, ?, ?, ?, ?, ?, 0)
                """,
                (pid, title, summary, year, arxiv, datetime.utcnow().isoformat()),
            )
            self.conn.commit()
        except Exception as exc:
            logger.error("HotPaperPool: failed to insert %s: %s", pid, exc)

    def get_one_unused(self) -> dict | None:
        """
        Get ONE unused paper (oldest first).
        """
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT id, title, summary, year, arxiv
            FROM hot_paper_pool
            WHERE used = 0
            ORDER BY created_at ASC
            LIMIT 1
            """
        )
        row = cur.fetchone()
        return dict(row) if row else None

    def mark_used(self, pid: str):
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE hot_paper_pool SET used = 1 WHERE id = ?",
            (pid,),
        )
        self.conn.commit()

    def remaining_count(self) -> int:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) AS c FROM hot_paper_pool WHERE used = 0")
        row = cur.fetchone()
        return int(row["c"]) if row else 0

    def close(self):
        self.conn.close()
        logger.info("Closed SQLite connection to HotPaperPool %s", self.path)

    def fetch_all(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM hot_paper_pool ORDER BY id")
        rows = cur.fetchall()
        return [dict(r) for r in rows]

    def fetch_unused(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM hot_paper_pool WHERE used=0 ORDER BY id")
        return [dict(r) for r in cur.fetchall()]

    def fetch_used(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM hot_paper_pool WHERE used=1 ORDER BY id")
        return [dict(r) for r in cur.fetchall()]

    def get_by_id(self, pid: str):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM hot_paper_pool WHERE id=?", (pid,))
        row = cur.fetchone()
        return dict(row) if row else None

    def count_all(self):
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM hot_paper_pool")
        return cur.fetchone()[0]

    def count_unused(self):
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM hot_paper_pool WHERE used=0")
        return cur.fetchone()[0]

    def count_used(self):
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM hot_paper_pool WHERE used=1")
        return cur.fetchone()[0]
