from .openai_client import AI
from .prompt_manager import PromptManager


# -------------------------------------------------------------------------
# Commit Summaries
# -------------------------------------------------------------------------
def summarize_commits(raw: str, mode="notion") -> str:
    prompt_name = f"commit_summary_{mode}"
    prompt = PromptManager.format(prompt_name, commits=raw)
    return AI.model("gpt-4o-mini").ask(prompt, ttl=7200)  # 2 hours


# -------------------------------------------------------------------------
# Arxiv Summaries
# -------------------------------------------------------------------------
def summarize_arxiv(raw: str, mode="email") -> str:
    prompt_name = f"arxiv_summary_{mode}"
    prompt = PromptManager.format(prompt_name, papers=raw)

    model = "gpt-5.1" if mode == "email" else "gpt-4o-mini"
    return AI.model(model).ask(prompt, ttl=80000)  # about 22.5 hours


# -------------------------------------------------------------------------
# Daily Log Rewrite
# -------------------------------------------------------------------------
def rewrite_daily_log(text: str, mode="email") -> str:
    prompt_name = f"daily_rewrite_{mode}"
    prompt = PromptManager.format(prompt_name, text=text)
    return AI.model("gpt-4o-mini").ask(prompt, ttl=80000)  # about 22.5 hours


# -------------------------------------------------------------------------
# Daily TODO
# -------------------------------------------------------------------------
def rewrite_daily_todo(text: str, mode="telegram") -> str:
    prompt_name = f"daily_todo_{mode}"
    prompt = PromptManager.format(prompt_name, text=text)
    return AI.model("gpt-4o-mini").ask(prompt, ttl=3600)  # 1 hour
