from __future__ import annotations

import re
from datetime import datetime

from watchdoc.facts import PdfDate

_PREFIX = re.compile(r"^D:", re.IGNORECASE)


def parse_pdf_date(raw: str | None) -> PdfDate | None:
    if raw is None:
        return None
    stripped = raw.strip()
    if stripped == "":
        return None
    inner = stripped
    if inner.startswith("(") and inner.endswith(")") and len(inner) >= 2:
        inner = inner[1:-1].strip()
    body = _PREFIX.sub("", inner, count=1)
    iso = _to_iso(body) or _iso_from_calendar_string(inner)
    return PdfDate(raw=stripped, iso=iso)


def _to_iso(body: str) -> str | None:
    if len(body) < 4 or not body[:4].isdigit():
        return None
    year = body[:4]
    rest = body[4:]
    month, day, hour, minute, second = "01", "01", "00", "00", "00"

    def take_digits(src: str, n: int) -> tuple[str | None, str]:
        if len(src) < n or not src[:n].isdigit():
            return None, src
        return src[:n], src[n:]

    if rest:
        value, rest = take_digits(rest, 2)
        if value is None:
            return None
        month = value
    if rest and rest[0].isdigit():
        value, rest = take_digits(rest, 2)
        if value is None:
            return None
        day = value
    if rest and rest[0].isdigit():
        value, rest = take_digits(rest, 2)
        if value is None:
            return None
        hour = value
    if rest and rest[0].isdigit():
        value, rest = take_digits(rest, 2)
        if value is None:
            return None
        minute = value
    if rest and rest[0].isdigit():
        value, rest = take_digits(rest, 2)
        if value is None:
            return None
        second = value

    mo, d, h, mi, se = int(month), int(day), int(hour), int(minute), int(second)
    if not (1 <= mo <= 12 and 1 <= d <= 31 and 0 <= h <= 23 and 0 <= mi <= 59 and 0 <= se <= 59):
        return None

    tz = _parse_offset(rest)
    if tz is None:
        return None
    return f"{year}-{month}-{day}T{hour}:{minute}:{second}{tz}"


def _parse_offset(rest: str) -> str | None:
    token = rest.strip()
    if token == "":
        return ""
    if token[0] in "Zz":
        leftover = token[1:].strip().strip("'")
        if leftover not in ("", "'"):
            return None
        return "Z"
    if token[0] not in "+-":
        return None
    sign = token[0]
    digits = token[1:].replace("'", "")
    if len(digits) < 2 or not digits[:2].isdigit():
        return None
    hh = digits[:2]
    mm = "00"
    if len(digits) >= 4:
        if not digits[2:4].isdigit():
            return None
        mm = digits[2:4]
        if digits[4:].strip():
            return None
    elif len(digits) != 2:
        return None
    if int(hh) > 14 or int(mm) > 59:
        return None
    return f"{sign}{hh}:{mm}"


def _iso_from_calendar_string(text: str) -> str | None:
    candidate = text.strip()
    if candidate.upper().startswith("D:"):
        candidate = candidate[2:].strip()
    if "T" not in candidate and candidate.count("-") < 2:
        return None
    if candidate.endswith("Z") or candidate.endswith("z"):
        candidate = candidate[:-1] + "+00:00"
    candidate = candidate.replace(" ", "T", 1)
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.strftime("%Y-%m-%dT%H:%M:%S")
    offset = parsed.strftime("%z")
    if offset == "+0000":
        return parsed.replace(tzinfo=None).strftime("%Y-%m-%dT%H:%M:%S") + "Z"
    return parsed.strftime("%Y-%m-%dT%H:%M:%S") + f"{offset[:3]}:{offset[3:]}"
