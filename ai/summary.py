from .openai_client import AI
from .prompt_manager import PromptManager

def summarize_commits(raw: str) -> str:
    prompt = PromptManager.format("commit_summary", commits=raw)
    return AI.model("gpt-4o-mini").ask(prompt)

def summarize_arxiv(raw: str) -> str:
    prompt = PromptManager.format("arxiv_summary", papers=raw)
    return AI.model("gpt-5.1").ask(prompt)

def rewrite_daily_log(text: str) -> str:
    prompt = PromptManager.format("daily_rewrite", text=text)
    return AI.model("gpt-4o-mini").ask(prompt)

def rewrite_daily_todo(text: str) -> str:
    prompt = PromptManager.format("daily_todo", text=text)
    return AI.model("gpt-4o-mini").ask(prompt)
