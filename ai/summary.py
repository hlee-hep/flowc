from .openai_client import AI
from .prompt_manager import PromptManager


# -------------------------------------------------------------------------
# Commit Summaries
# -------------------------------------------------------------------------
def summarize_commits(raw: str, mode="notion") -> str:
    prompt_name = f"commit_summary_{mode}"
    prompt = PromptManager.format(prompt_name, commits=raw)
    return AI.model("gpt-4o").ask(prompt, ttl=7200)  # 2 hours


# -------------------------------------------------------------------------
# Arxiv Summaries
# -------------------------------------------------------------------------
def summarize_arxiv(papers: list[dict], mode="email") -> list[str]:
    """
    Return a list of summaries, one per paper.
    - email : multi-sentence summaries (2-4 sentences)
    - telegram : ultra-compact 1-line summaries
    """

    # build per-paper blocks
    blocks = []
    for i, p in enumerate(papers, start=1):
        blocks.append(f"[{i}] {p['title']}\n{p['summary']}")

    prompt_name = f"arxiv_summary_{mode}"
    prompt = PromptManager.format(
        prompt_name,
        papers="\n\n".join(blocks),
        count=len(papers)
    )

    model = "gpt-5.1"
    out = AI.model(model).ask(prompt).strip()

    # Split into lines or blocks
    lines = [x.strip() for x in out.split("\n") if x.strip()]

    # Telegram: exactly count lines
    if mode == "telegram" and len(lines) == len(papers):
        return lines

    # Email: paragraphs separated by blank lines
    para_blocks = [x.strip() for x in out.split("\n\n") if x.strip()]
    if mode == "email" and len(para_blocks) == len(papers):
        return para_blocks

    # Fallback: duplicate entire output for all papers (never breaks flow)
    return [out] * len(papers)


# -------------------------------------------------------------------------
# Daily Log Rewrite
# -------------------------------------------------------------------------
def rewrite_daily_log(text: str, mode="email") -> str:
    prompt_name = f"daily_rewrite_{mode}"
    prompt = PromptManager.format(prompt_name, text=text)
    return AI.model("gpt-4o").ask(prompt, ttl=80000)  # about 22.5 hours


# -------------------------------------------------------------------------
# Daily TODO
# -------------------------------------------------------------------------
def rewrite_daily_todo(text: str, mode="telegram") -> str:
    prompt_name = f"daily_todo_{mode}"
    prompt = PromptManager.format(prompt_name, text=text)
    return AI.model("gpt-4o").ask(prompt, ttl=3600)  # 1 hour
