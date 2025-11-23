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

    def for_email(self, summary: str) -> str:
        return f"<h2>Git Commits</h2><pre>{summary}</pre>"

    def for_telegram(self, summary: str) -> str:
        return f"*Commits*\n{summary}"

    def for_notion(self, summary: str) -> str:
        return summary

    def run(self, days=1) -> str:
        raw = self.get_raw(days)
        return self.summarize(raw)
