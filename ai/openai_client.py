from openai import OpenAI
from flowc.config import Config

class AI:
    client = OpenAI(api_key=Config.OPENAI_API_KEY)
    model_name = "gpt-4o-mini"

    @classmethod
    def model(cls, name: str):
        cls.model_name = name
        return cls

    @classmethod
    def ask(cls, prompt: str, **kwargs):
        r = cls.client.chat.completions.create(
            model=cls.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=700,
            **kwargs
        )
        return r.choices[0].message.content
