import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    NOTION_TOKEN = os.getenv("NOTION_TOKEN")
    NOTION_DAILY_DB = os.getenv("NOTION_DAILY_DB")

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    SMTP_HOST = os.getenv("SMTP_HOST")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    SMTP_FROM = os.getenv("SMTP_FROM")
    SMTP_TO = os.getenv("SMTP_TO")

    GIT_REPO_PATH = os.getenv("GIT_REPO_PATH", ".")
    SQLITE_PATH = os.getenv("SQLITE_PATH", "flowc.db")