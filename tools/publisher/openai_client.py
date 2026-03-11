from __future__ import annotations

from dataclasses import dataclass
import json
import os
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class OpenAISettings:
    api_key: str
    base_url: str
    model: str


def settings_from_env() -> OpenAISettings:
    api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY")
    base_url = (os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
    model = (os.getenv("OPENAI_MODEL") or "").strip()
    if not model:
        raise RuntimeError("Missing OPENAI_MODEL (e.g. gpt-4.1-mini)")
    return OpenAISettings(api_key=api_key, base_url=base_url, model=model)


def chat_complete(*, system: str, user: str, temperature: float = 0.2) -> str:
    s = settings_from_env()
    url = f"{s.base_url}/chat/completions"
    payload = {
        "model": s.model,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    body = json.dumps(payload).encode("utf-8")
    req = Request(
        url,
        method="POST",
        data=body,
        headers={
            "Authorization": f"Bearer {s.api_key}",
            "Content-Type": "application/json",
        },
    )
    with urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8", errors="replace"))
    try:
        return str(data["choices"][0]["message"]["content"])
    except Exception:
        raise RuntimeError(f"Unexpected OpenAI response shape: keys={list(data.keys())}")

