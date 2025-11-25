import logging

from flowc.services.notion_service import NotionService
from flowc.services.telegram_digest_service import TelegramDigestService
from flowc.services.commit_service import CommitService
from flowc.services.email_report_service import EmailReportService
from flowc.services.arxiv_service import ArxivService
from flowc.services.archive_service import ArchiveService

from flowc.ai.summary import rewrite_daily_log, summarize_commits, summarize_arxiv

logger = logging.getLogger(__name__)


class EveningFlow:
    def __init__(self):
        self.notion = NotionService()
        self.telegram = TelegramDigestService()
        self.commit = CommitService()
        self.email = EmailReportService()
        self.arxiv = ArxivService()
        self.archive = ArchiveService()

    def run(self):
        logger.info("Starting evening flow")

        # ------------------------------------------------
        # 1) Commit
        # ------------------------------------------------
        commit_results = self._process_commits()

        # ------------------------------------------------
        # 2) Notion Summary (AI)
        # ------------------------------------------------
        notion_results = self._process_notion(commit_results)

        # ------------------------------------------------
        # 3) Arxiv (AI)
        # ------------------------------------------------
        arxiv_results = self._process_arxiv()

        # ------------------------------------------------
        # 4) Email
        # ------------------------------------------------
        email_html = self._process_email(
            notion_results["email"],
            commit_results["email"],
            arxiv_results["email"],
        )

        # ------------------------------------------------
        # 5) Telegram digest
        # ------------------------------------------------
        telegram_msg = self._process_telegram(
            commit_results["telegram"],
            notion_results["telegram"],
            arxiv_results["telegram"],
        )

        #
        # 6) Archieving
        #
        self.archive.save_html("email.html", email_html)
        self.archive.save_text("telegram.txt", telegram_msg.strip())

        # Notion summaries
        self.archive.save_text("notion_email.txt", notion_results["email"])
        self.archive.save_text("notion_telegram.txt", notion_results["telegram"])

        # Commit summaries
        self.archive.save_text("commit_email.txt", commit_results["email"])
        self.archive.save_text("commit_telegram.txt", commit_results["telegram"])

        # Arxiv summaries
        self.archive.save_html("arxiv_email.html", arxiv_results["email"])
        self.archive.save_text("arxiv_telegram.txt", arxiv_results["telegram"])
        logger.info("Evening flow completed")
    # ========================================================================
    # Commit Section
    # ========================================================================
    def _process_commits(self):
        logger.info("Fetching and summarizing commits")
        raw_commit = self.commit.get_raw()

        result = {
            "notion": None,
            "email": "",
            "telegram": "",
        }

        if not raw_commit:
            logger.info("No commits found for the selected window")
            result["telegram"] = "No commits today."
            return result

        # AI summarization (separate prompts)
        summary_for_notion = summarize_commits(raw_commit)
        summary_for_telegram = summarize_commits(raw_commit, mode = "telegram")
        summary_for_email = summarize_commits(raw_commit, mode = "email")

        logger.info("Commit summaries generated (notion/telegram/email)")

        # prepare outputs
        result["notion"] = summary_for_notion
        result["telegram"] = summary_for_telegram
        result["email"] = summary_for_email

        return result

    # ========================================================================
    # Notion Section
    # ========================================================================
    def _process_notion(self, commit_results):
        logger.info("Fetching today's Notion page for evening flow")
        page = self.notion.get_today_page(self.notion.db_id)
        if not page:
            logger.warning("No Notion page found for today; skipping Notion summaries")
            return {
                "telegram": "No notion page today.",
                "email": "No notion page today.",
            }
        raw_todo = self.notion.read_todo(page)
        raw_time = self.notion.read_time_summary(page)
        raw_sum = self.notion.read_summary(page)

        daily_log = f"TODO for Today:\n{raw_todo}\n\nSummary:\n{raw_sum}\n\n{raw_time}"

        # Three versions
        ai_telegram = rewrite_daily_log(daily_log, mode="telegram")
        ai_email = rewrite_daily_log(daily_log, mode="email")
        ai_notion = rewrite_daily_log(daily_log, mode="notion")
        logger.info("AI daily log rewrites generated for all channels")

        # Write to Notion
        if commit_results["notion"]:
            self.notion.write_git_summary(page["id"], commit_results["notion"])
            logger.info("Wrote commit summary to Notion")

        self.notion.write_ai_summary(page["id"], ai_notion)
        logger.info("Wrote AI daily summary to Notion")

        return {
            "telegram": ai_telegram,
            "email": ai_email,
        }

    # ========================================================================
    # Arxiv Section
    # ========================================================================
    def _process_arxiv(self):
        logger.info("Fetching and filtering arXiv papers")
        papers = self.arxiv.run()

        if not papers:
            logger.info("No interesting arXiv papers found today")
            return {
                "telegram": "No interesting new papers today.",
                "email": "<p>No interesting new papers today.</p>",
            }

        summaries_default = summarize_arxiv(papers, mode = "email")
        summaries_telegram = summarize_arxiv(papers, mode = "telegram")
        logger.info("Generated arXiv summaries for email and Telegram")

        # HTML (email)
        html_blocks = []
        for p, s in zip(papers, summaries_default):
            self.arxiv.save(p["id"], p["title"], s)
            logger.info("Saved arXiv paper %s to archive", p["id"])
            html_blocks.append(self.arxiv.format_html(p, s))

        return {
            "telegram": "\n".join(
                f"{p['title']}\n{s}" for p, s in zip(papers, summaries_telegram)
            ),
            "email": "\n".join(html_blocks),
        }

    # ========================================================================
    # Email Section
    # ========================================================================
    def _process_email(self, notion_email, commit_email, arxiv_email):
        logger.info("Composing and sending evening email report")
        email_html = self.email.build_html(
            summary=notion_email,
            commits_html=commit_email,
            arxiv_text=arxiv_email,
        )
        self.email.send(email_html)
        logger.info("Evening email report sent")
        return email_html

    def _process_telegram(self, commit_telegram, notion_telegram, arxiv_telegram):
        logger.info("Sending evening Telegram digest")
        telegram_msg = self.telegram.build_message_for_evening(commit_telegram, notion_telegram, arxiv_telegram)
        self.telegram.send(telegram_msg)
        logger.info("Evening Telegram digest sent")
        return telegram_msg