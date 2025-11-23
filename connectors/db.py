import sqlite3
from pathlib import Path
from datetime import datetime
from flowc.config import Config

class PaperDatabase:
    def __init__(self, path: str | None = None):
        self.path = Path(path or Config.SQLITE_PATH)
        self.conn = sqlite3.connect(self.path)
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

    def close(self):
        self.conn.close()
