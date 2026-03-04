from __future__ import annotations

import json
import re
from typing import Any


_JSON_OBJ_RE = re.compile(r"\{.*\}", re.DOTALL)


def loads_first_object(text: str) -> dict[str, Any]:
    raw = (text or "").strip()
    if not raw:
        raise ValueError("Empty JSON text")
    try:
        val = json.loads(raw)
        if isinstance(val, dict):
            return val
    except Exception:
        pass

    m = _JSON_OBJ_RE.search(raw)
    if not m:
        raise ValueError("No JSON object found in text")
    snippet = m.group(0)
    val = json.loads(snippet)
    if not isinstance(val, dict):
        raise ValueError("JSON is not an object")
    return val

