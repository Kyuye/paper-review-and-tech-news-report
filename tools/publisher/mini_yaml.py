from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import Any


_INT_RE = re.compile(r"^-?\d+$")


def load_yaml(text: str) -> Any:
    lines = _preprocess(text)
    if not lines:
        return {}
    val, idx = _parse_block(lines, 0, indent=0)
    if idx < len(lines):
        # Best-effort: ignore trailing.
        return val
    return val


def load_yaml_file(path) -> Any:
    return load_yaml(path.read_text(encoding="utf-8"))


def dump_yaml_mapping(mapping: dict[str, Any]) -> str:
    # Minimal YAML emitter for simple frontmatter/config generation.
    lines: list[str] = []
    for k, v in mapping.items():
        lines.extend(_dump_kv(str(k), v, indent=0))
    return "\n".join(lines).rstrip() + "\n"


def _dump_kv(key: str, value: Any, indent: int) -> list[str]:
    pad = " " * indent
    if isinstance(value, dict):
        out = [f"{pad}{key}:"]
        for k2, v2 in value.items():
            out.extend(_dump_kv(str(k2), v2, indent=indent + 2))
        return out
    if isinstance(value, (list, tuple)):
        # Use inline JSON-style list to keep it simple and parseable by our loader.
        return [f"{pad}{key}: {json.dumps(list(value), ensure_ascii=False)}"]
    if isinstance(value, bool):
        return [f"{pad}{key}: {'true' if value else 'false'}"]
    if isinstance(value, int):
        return [f"{pad}{key}: {value}"]
    s = str(value)
    if any(ch in s for ch in [":", "#", "\n"]):
        s = json.dumps(s, ensure_ascii=False)
    return [f"{pad}{key}: {s}"]


def _preprocess(text: str) -> list[str]:
    out: list[str] = []
    for raw in (text or "").splitlines():
        line = raw.rstrip("\n").rstrip("\r")
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        # Remove inline comments (best-effort; assumes no # inside strings).
        if " #" in line:
            line = line.split(" #", 1)[0].rstrip()
        out.append(line.rstrip())
    return out


@dataclass
class _Cursor:
    lines: list[str]
    idx: int = 0

    def peek(self) -> str | None:
        return self.lines[self.idx] if self.idx < len(self.lines) else None

    def pop(self) -> str | None:
        if self.idx >= len(self.lines):
            return None
        v = self.lines[self.idx]
        self.idx += 1
        return v


def _parse_block(lines: list[str], idx: int, indent: int) -> tuple[Any, int]:
    cur = _Cursor(lines, idx)
    line = cur.peek()
    if line is None:
        return {}, cur.idx
    if _indent_of(line) < indent:
        return {}, cur.idx

    if line.startswith(" " * indent + "- "):
        val = _parse_list(cur, indent)
        return val, cur.idx
    val = _parse_map(cur, indent)
    return val, cur.idx


def _parse_map(cur: _Cursor, indent: int) -> dict[str, Any]:
    out: dict[str, Any] = {}
    while True:
        line = cur.peek()
        if line is None:
            break
        ind = _indent_of(line)
        if ind < indent:
            break
        if ind != indent:
            # Unexpected indent; stop to avoid mis-parsing.
            break
        if line.lstrip().startswith("- "):
            break

        raw = line[ind:]
        if ":" not in raw:
            cur.pop()
            continue
        key, rest = raw.split(":", 1)
        key = key.strip()
        rest = rest.strip()
        cur.pop()

        if rest == "":
            # Nested structure expected.
            nxt = cur.peek()
            if nxt is None or _indent_of(nxt) <= indent:
                out[key] = {}
            else:
                val, new_idx = _parse_block(cur.lines, cur.idx, indent=indent + 2)
                cur.idx = new_idx
                out[key] = val
        else:
            out[key] = _parse_scalar(rest)
    return out


def _parse_list(cur: _Cursor, indent: int) -> list[Any]:
    out: list[Any] = []
    while True:
        line = cur.peek()
        if line is None:
            break
        ind = _indent_of(line)
        if ind < indent:
            break
        if not line.startswith(" " * indent + "- "):
            break
        raw = line[ind + 2 :].strip()
        cur.pop()

        if raw == "":
            val, new_idx = _parse_block(cur.lines, cur.idx, indent=indent + 2)
            cur.idx = new_idx
            out.append(val)
            continue

        # Inline dict starter: "- key: value"
        if ":" in raw and not raw.startswith("[") and not raw.startswith("{"):
            key, rest = raw.split(":", 1)
            key = key.strip()
            rest = rest.strip()
            item: dict[str, Any] = {}
            if rest == "":
                val, new_idx = _parse_block(cur.lines, cur.idx, indent=indent + 2)
                cur.idx = new_idx
                item[key] = val
            else:
                item[key] = _parse_scalar(rest)

            # Continue consuming mapping lines at indent+2.
            while True:
                nxt = cur.peek()
                if nxt is None:
                    break
                nind = _indent_of(nxt)
                if nind < indent + 2:
                    break
                if nind != indent + 2 or nxt.lstrip().startswith("- "):
                    break
                raw2 = nxt[nind:]
                if ":" not in raw2:
                    cur.pop()
                    continue
                k2, r2 = raw2.split(":", 1)
                k2 = k2.strip()
                r2 = r2.strip()
                cur.pop()
                if r2 == "":
                    nxt = cur.peek()
                    if nxt is None or _indent_of(nxt) <= indent + 2:
                        item[k2] = {}
                    else:
                        val, new_idx = _parse_block(cur.lines, cur.idx, indent=indent + 4)
                        cur.idx = new_idx
                        item[k2] = val
                else:
                    item[k2] = _parse_scalar(r2)
            out.append(item)
            continue

        out.append(_parse_scalar(raw))
    return out


def _parse_scalar(raw: str) -> Any:
    s = raw.strip()
    if not s:
        return ""
    if s.lower() in {"true", "false"}:
        return s.lower() == "true"
    if _INT_RE.match(s):
        try:
            return int(s)
        except Exception:
            return s
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    if s.startswith("[") and s.endswith("]"):
        try:
            return json.loads(s)
        except Exception:
            inner = s[1:-1].strip()
            if not inner:
                return []
            return [x.strip().strip('"').strip("'") for x in inner.split(",")]
    return s


def _indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))
