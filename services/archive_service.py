import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

FLOWC_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


class ArchiveService:
    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = os.path.join(FLOWC_ROOT, "archive")

        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def get_today_dir(self):
        today = datetime.now().strftime("%Y-%m-%d")
        path = os.path.join(self.base_dir, today)
        os.makedirs(path, exist_ok=True)
        return path

    def save_text(self, filename: str, text: str):
        path = self.get_today_dir()
        full = os.path.join(path, filename)
        with open(full, "w", encoding="utf-8") as f:
            f.write(text or "")
        logger.info("Saved text archive to %s", full)
        return full

    def save_html(self, filename: str, html: str):
        path = self.get_today_dir()
        full = os.path.join(path, filename)
        with open(full, "w", encoding="utf-8") as f:
            f.write(html or "")
        logger.info("Saved HTML archive to %s", full)
        return full
