import os
from datetime import datetime

class ArchiveService:
    def __init__(self, base_dir="archive"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

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
        return full

    def save_html(self, filename: str, html: str):
        path = self.get_today_dir()
        full = os.path.join(path, filename)
        with open(full, "w", encoding="utf-8") as f:
            f.write(html or "")
        return full
