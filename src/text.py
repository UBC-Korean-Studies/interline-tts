import re

from .config import MAX_SENTENCE

_SENTENCE_END = re.compile(r"(?<=[.!?。！？…])\s+|\n+")


def split_text(text: str, max_len: int = MAX_SENTENCE) -> list[str]:
    parts = [p.strip() for p in _SENTENCE_END.split(text) if p and p.strip()]
    out: list[str] = []
    for p in parts:
        while len(p) > max_len:
            cut = max(p.rfind(c, 0, max_len) for c in ",;，、 ")
            cut = max_len if cut < max_len // 2 else cut + 1
            out.append(p[:cut].strip())
            p = p[cut:].strip()
        if p:
            out.append(p)
    return out
