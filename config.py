import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent
load_dotenv(ROOT_DIR / ".env")


def _resolve_path(value: str | None, default: Path) -> Path:
    """Return an absolute path, defaulting to the repo root when relative."""
    if value:
        candidate = Path(value)
        if not candidate.is_absolute():
            candidate = ROOT_DIR / candidate
        return candidate
    return default


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

    FLOWC_ROOT = ROOT_DIR
    GIT_REPO_PATH = _resolve_path(os.getenv("GIT_REPO_PATH"), ROOT_DIR)
    SQLITE_PATH = _resolve_path(os.getenv("SQLITE_PATH"), ROOT_DIR / "flowc.db")
