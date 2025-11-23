from flowc.services.notion_service import NotionService
from flowc.services.telegram_digest_service import TelegramDigestService
from flowc.services.commit_service import CommitService
from flowc.services.email_report_service import EmailReportService
from flowc.services.arxiv_service import ArxivService
from flowc.ai.summary import rewrite_daily_log, summarize_commits, summarize_arxiv


class EveningFlow:
    def __init__(self):
        self.notion = NotionService()
        self.telegram = TelegramDigestService()
        self.commit = CommitService()
        self.email = EmailReportService()
        self.arxiv = ArxivService()

    def run(self):
        telegram_msg = ""

        # 1) Commit
        commit_results = self._process_commits()
        telegram_msg += commit_results["telegram"] + "\n"

        # 2) Notion Daily AI Summary
        summary_msg = self._process_notion(commit_results)
        telegram_msg += summary_msg + "\n"

        # 3) Arxiv digest
        arxiv_msg = self._process_arxiv()

        # 4) Email report
        self._process_email(summary_msg, commit_results, arxiv_msg)

        # 5) Telegram digest
        if telegram_msg.strip():
            formatted = self.telegram.format_evening(telegram_msg.strip())
            self.telegram.send(formatted)

    # --------------------------------------------------------
    # Commit Section
    # --------------------------------------------------------
    def _process_commits(self):
        raw_commit = self.commit.get_raw()

        result = {
            "notion": None,
            "email": None,
            "telegram": "",
        }

        if not raw_commit:
            result["telegram"] = "No commits today."
            return result

        commit_summary = summarize_commits(raw_commit)

        result["notion"] = self.commit.for_notion(commit_summary)
        result["email"] = self.commit.for_email(commit_summary)
        result["telegram"] = self.commit.for_telegram(commit_summary)

        return result

    # --------------------------------------------------------
    # Notion Section
    # --------------------------------------------------------
    def _process_notion(self, commit_results):
        page = self.notion.get_today_page(self.notion.db_id)
        if not page:
            return "No notion page today."

        raw_time = self.notion.read_time_summary(page)
        raw_sum = self.notion.read_summary(page)

        daily_log = f"Summary:\n{raw_sum}\n\n{raw_time}"
        daily_log_ai = rewrite_daily_log(daily_log)

        if commit_results["notion"]:
            self.notion.write_git_summary(page["id"], commit_results["notion"])

        self.notion.write_ai_summary(page["id"], daily_log_ai)

        return daily_log_ai

    # --------------------------------------------------------
    # Arxiv Section
    # --------------------------------------------------------
    def _process_arxiv(self):
        papers = self.arxiv.run()

        if papers:
            summaries = summarize_arxiv(papers)
            html_blocks = []
            for p, s in zip(papers, summaries):
                self.arxiv.save(p["id"], p["title"], s)
                html_blocks.append(self.arxiv.format_html(p, s))

            arxiv_html = "\n".join(html_blocks)
        else:
            arxiv_html = "<p>No interesting new papers today.</p>"
        
        return arxiv_html
    # --------------------------------------------------------
    # Email Section
    # --------------------------------------------------------
    def _process_email(self, summary_msg, commit_results, arxiv_msg):
        commits_html = commit_results["email"] or ""
        
        email_html = self.email.build_html(
            summary=summary_msg,
            commits_html=commit_results["email"],
            arxiv_text=arxiv_msg,
        )
        self.email.send(email_html)
