import logging
from flowc.ai.openai_client import AI

logger = logging.getLogger(__name__)


DEFAULT_BASE_KEYWORDS = [
    "tau",
    "lfv",
    "belle ii",
    "trigger",
    "form factor",
    "tdcpv",
]


class KeywordEngine:

    def __init__(self, base_keywords=None):
        self.base_keywords = base_keywords or DEFAULT_BASE_KEYWORDS

    def generate(self, recent_papers: list[dict], ttl: int = 3600) -> list[str]:

        if not recent_papers:
            logger.info("KeywordEngine: No recent papers; using base keywords only.")
            return self.base_keywords

        # recent_papers
        sample_text = "\n".join(
            f"- {p['title']}: {p['summary'][:200]}"
            for p in recent_papers[:8]
        )

        prompt = f"""
You are assisting an experimental high-energy physicist working on:
- Belle II
- tau LFV searches
- trigger & flavor physics
- form factors
- TDCPV

Given the following recent arXiv papers (titles and partial summaries),
suggest 5-10 keywords that would best filter future relevant papers.

Return ONLY a comma-separated list of lowercase keywords.

Papers:
{sample_text}
"""

        logger.info("KeywordEngine: Generating recommended arXiv filter keywords via AI.")

        out = AI.ask(prompt, ttl=ttl)
        if not out:
            logger.warning("KeywordEngine: GPT returned empty result; using base keywords.")
            return self.base_keywords

        # comma-separated 
        kws = [kw.strip().lower() for kw in out.split(",") if kw.strip()]

        # fallback safety
        if not kws:
            logger.warning("KeywordEngine: Parsed keyword list empty; using base keywords.")
            return self.base_keywords

        logger.info("KeywordEngine: Generated %d recommended keywords: %s", len(kws), kws)
        return kws
