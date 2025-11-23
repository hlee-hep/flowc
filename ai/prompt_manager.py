import os

class PromptManager:
    BASE = os.path.join(os.path.dirname(__file__), "prompts")

    @staticmethod
    def load(name: str):
        path = os.path.join(PromptManager.BASE, f"{name}.txt")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def format(name: str, **kwargs):
        template = PromptManager.load(name)
        return template.format(**kwargs)
