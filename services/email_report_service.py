from pathlib import Path
from flowc.connectors.email_sender import EmailSender
from datetime import datetime

class EmailReportService:
    def __init__(self):
        self.sender = EmailSender()
        self.template_path = (
            Path(__file__).resolve().parents[1] / "templates" / "email_report.html"
        )

    def build_html(self, summary: str, commits_html: str, arxiv_text: str) -> str:
        template = self.template_path.read_text(encoding="utf-8")
        # .format
        return template.format(
            summary=summary,
            commits=commits_html,
            arxiv=arxiv_text.replace("\n", "<br/>"),
        )

    def send(self, html: str, subject: str = "[FlowC] Evening Report"):
        self.sender.send(html, subject=subject)
