import logging
import subprocess
from pathlib import Path
from flowc.config import Config

logger = logging.getLogger(__name__)

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
            logger.info("Running git log for last %s day(s)", days)
            out = subprocess.check_output(cmd, text=True)
        except subprocess.CalledProcessError:
            logger.warning("git log failed for repo %s", self.repo_path)
            return ""
        return out.strip()

    def pull(self) -> bool:
        """Run git pull in the repo. Return True if success."""
        cmd = ["git", "-C", str(self.repo_path), "pull", "--ff-only"]
        try:
            logger.info("Running git pull in %s", self.repo_path)
            subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
            logger.info("git pull successful")
            return True
        except subprocess.CalledProcessError as e:
            logger.warning("Git pull failed: %s", e.output)
            return False