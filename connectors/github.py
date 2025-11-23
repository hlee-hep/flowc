import subprocess
from pathlib import Path
from flowc.config import Config

class GitConnector:
    def __init__(self, repo_path: str | None = None):
        self.repo_path = Path(repo_path or Config.GIT_REPO_PATH)

    def get_commit_log(self, days: int = 1) -> str:
        cmd = [
            "git", "-C", str(self.repo_path),
            "log", f"--since={days}.days",
            "--pretty=format:%h %ad %s",
            "--date=short"
        ]
        try:
            out = subprocess.check_output(cmd, text=True)
        except subprocess.CalledProcessError:
            return ""
        return out.strip()

    def pull(self) -> bool:
        """Run git pull in the repo. Return True if success."""
        cmd = ["git", "-C", str(self.repo_path), "pull", "--ff-only"]
        try:
            subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
            return True
        except subprocess.CalledProcessError as e:
            print("Git pull failed:", e.output)
            return False