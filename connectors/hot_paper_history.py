import os
import yaml
from datetime import date

class HotPaperHistory:
    def __init__(self, base_dir="logs/hotpapers"):
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.base_dir = os.path.join(root, base_dir)

        os.makedirs(self.base_dir, exist_ok=True)

    def save(self, paper: dict):
        """Save today's hot paper with date key."""
        today = date.today().isoformat()
        path = os.path.join(self.base_dir, f"{today}.yaml")

        data = {
            "date": today,
            **paper,
        }

        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True)

        return path

    def list_history(self):
        files = sorted(os.listdir(self.base_dir))
        out = []
        for fn in files:
            if fn.endswith(".yaml"):
                out.append(fn.replace(".yaml", ""))
        return out

    def load(self, day: str) -> dict | None:
        path = os.path.join(self.base_dir, f"{day}.yaml")
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
