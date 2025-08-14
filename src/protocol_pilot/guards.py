from __future__ import annotations
import re

BANNED_PATTERNS = [
    r"diagnos(e|is|tic)",
    r"treat(ment|ing)?",
    r"patient\-specific",
    r"clinical decision",
]

def contains_banned_language(text: str) -> bool:
    text_low = text.lower()
    return any(re.search(p, text_low) for p in BANNED_PATTERNS)
