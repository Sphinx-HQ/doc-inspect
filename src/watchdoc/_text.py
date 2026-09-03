from __future__ import annotations


def clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    chars: list[str] = []
    for ch in value:
        if ch == "\x00":
            continue
        code = ord(ch)
        if 0xD800 <= code <= 0xDFFF:
            continue
        chars.append(ch)
    stripped = "".join(chars).strip()
    return stripped or None
