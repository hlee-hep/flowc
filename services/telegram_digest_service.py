import logging

from flowc.connectors.telegram import TelegramClient

logger = logging.getLogger(__name__)


class TelegramDigestService:
    def __init__(self):
        self.client = TelegramClient()

    def format_morning(self) -> str:
        return "*Morning Plan*\n\n"

    def format_evening(self) -> str:
        return "*Evening Summary*\n\n"

    def send(self, text: str):
        logger.info("Sending Telegram message (%d chars)", len(text))
        self.client.send(text)

    def build_message_for_evening(self, commit, summary, arxiv):
        msg = self.format_evening()
        msg += "*Commit*\n"
        if commit:
            msg += commit + "\n\n"
        else:
            msg += "No commit Today.\n\n"
        msg += "*Summary*\n"
        if summary:
            msg += summary + "\n\n"
        else:
            msg += "No summary Today.\n\n"
        msg += "*ArXiv*\n"

        if arxiv:
            msg += arxiv + "\n"
        else:
            msg += "No arxiv article Today.\n"
        
        return msg

    def build_message_for_morning(self, page, todo):
        msg = self.format_morning()
        if not page:
            msg += "No Notion daily page found for today."
            return msg
        
        if todo:
            msg += "*Todo*\n"
            msg += todo
        else:
            msg += "No Todo items for today."
        
        return msg