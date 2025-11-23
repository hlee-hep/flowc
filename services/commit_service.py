# flowc/services/commit_service.py

from flowc.connectors.github import GitConnector

class CommitService:
    def __init__(self):
        self.git = GitConnector()

    def get_raw(self, days=1):
        try:
            self.git.pull() 
        except Exception as e:
            print(f"[WARN] git pull failed: {e}")

        return self.git.get_commit_log(days=days)

    def run(self, days=1) -> str:
        raw = self.get_raw(days)
        return self.summarize(raw)
