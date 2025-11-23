import hashlib
import json
import time
from flowc.config import Config 
from pathlib import Path

CACHE_DIR = Config.FLOWC_ROOT / ".flowc_cache"
CACHE_DIR.mkdir(exist_ok=True)


def _key(model: str, prompt: str) -> str:
    raw = f"{model}\n{prompt}"
    return hashlib.sha256(raw.encode()).hexdigest()


def cache_get(model: str, prompt: str, ttl: int | None):
    key = _key(model, prompt)
    f = CACHE_DIR / f"{key}.json"
    if not f.exists():
        return None

    try:
        data = json.loads(f.read_text())
    except Exception:
        return None

    if ttl is None:
        return data["out"]

    # ttl
    if time.time() - data["time"] < ttl:
        return data["out"]

    return None


def cache_set(model: str, prompt: str, out: str):
    key = _key(model, prompt)
    f = CACHE_DIR / f"{key}.json"
    f.write_text(json.dumps({"time": time.time(), "out": out}, ensure_ascii=False))
