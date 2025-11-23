import logging
import time

from openai import OpenAI
from flowc.config import Config
from flowc.ai.cache import cache_get, cache_set  #

logger = logging.getLogger(__name__)

class AI:
    client = OpenAI(api_key=Config.OPENAI_API_KEY)
    model_name = "gpt-4o-mini"

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
        ttl: int | None = None,  # 
        **kwargs,
    ):
        # 
        cached = cache_get(cls.model_name, prompt, ttl)
        if cached is not None:
            return cached
        # 

        last_error = None
        for attempt in range(1, retries + 1):
            try:
                r = cls.client.chat.completions.create(
                    model=cls.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=700,
                    **kwargs
                )
                out = r.choices[0].message.content
                cache_set(cls.model_name, prompt, out)  # 
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

