import logging
from pathlib import Path
from datetime import datetime
from flowc.config import Config

logger = logging.getLogger(__name__)


class ArchiveService:
    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = Config.FLOWC_ROOT / "archive"

        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def get_today_dir(self):
        today = datetime.now().strftime("%Y-%m-%d")
        path = self.base_dir / today
        path.mkdir(parents=True, exist_ok=True)
        return path

    def save_text(self, filename: str, text: str):
        path = self.get_today_dir()
        full = path / filename
        full.write_text(text or "", encoding="utf-8")
        logger.info("Saved text archive to %s", full)
        return full

    def save_html(self, filename: str, html: str):
        path = self.get_today_dir()
        full = path / filename
        full.write_text(html or "", encoding="utf-8")
        logger.info("Saved HTML archive to %s", full)
        return full
