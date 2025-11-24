import logging
import time

from openai import OpenAI
from flowc.config import Config
from flowc.ai.cache import cache_get, cache_set  #

logger = logging.getLogger(__name__)


class AI:
    client = OpenAI(api_key=Config.OPENAI_API_KEY)
    model_name = "gpt-4o"

    @classmethod
    def model(cls, name: str):
        cls.model_name = name
        return cls

    @classmethod
    def ask(
        cls,
        prompt: str,
        *,
        retries: int = 3,
        retry_delay: float = 1.0,
        fallback: str = "(AI call failed)",
        ttl: int | None = None,
        use_cache: bool = True,
        max_completion_tokens: int = 1500,
        **kwargs,
    ):
        cached = None
        if use_cache and ttl and ttl > 0:
            cached = cache_get(cls.model_name, prompt, ttl)
        if cached is not None:
            logger.info("Cached prompt exists. using cached one.")
            return cached

        last_error = None
        for attempt in range(1, retries + 1):
            try:
                r = cls.client.chat.completions.create(
                    model=cls.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_completion_tokens=max_completion_tokens,
                    **kwargs,
                )

                msg = r.choices[0].message
                out = msg.content

                if not out:
                    logger.error(
                        "AI.ask: empty message.content. raw response: %r",
                        r,
                    )
                    continue

                if use_cache and ttl and ttl > 0:
                    cache_set(cls.model_name, prompt, out)
                    logger.info(
                        "The prompt is cached (vaild for %d seconds).", ttl
                    )
                else:
                    logger.info("The prompt is not cached (ttl=%r).", ttl)

                return out

            except Exception as exc:
                last_error = exc
                logger.warning(
                    "AI call failed (attempt %s/%s): %s", attempt, retries, exc
                )
                if attempt < retries:
                    time.sleep(retry_delay * attempt)

        logger.error("AI call failed after %s attempts: %s", retries, last_error)
        return fallback
