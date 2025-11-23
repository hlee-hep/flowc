import logging

from flowc.connectors.github import GitConnector

logger = logging.getLogger(__name__)


class CommitService:
    def __init__(self):
        self.git = GitConnector()

    def get_raw(self, days=1):
        logger.info("Pulling latest commits for last %s day(s)", days)
        try:
            self.git.pull()
        except Exception as e:  # noqa: BLE001
            logger.warning("git pull failed: %s", e)

        commits = self.git.get_commit_log(days=days)
        logger.info("Retrieved %d characters of commit log", len(commits))
        return commits

    def run(self, days=1) -> str:
        raw = self.get_raw(days)
        return self.summarize(raw)
