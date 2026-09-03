from __future__ import annotations

import pymupdf

from watchdoc._text import clean_text
from watchdoc.facts import PdfFacts, PdfInfo
from watchdoc.readers.pdf_dates import parse_pdf_date
from watchdoc.readers.xmp import parse_xmp

_STANDARD_KEYS = {
    "Title",
    "Author",
    "Subject",
    "Keywords",
    "Creator",
    "Producer",
    "CreationDate",
    "ModDate",
    "Trapped",
    "Type",
}


def read_pdf(data: bytes) -> PdfFacts:
    doc = pymupdf.open(stream=data, filetype="pdf")
    try:
        if doc.needs_pass:
            doc.authenticate("")
        xml = (doc.get_xml_metadata() or "").strip()
        return PdfFacts(
            version=_version(doc),
            page_count=doc.page_count,
            encrypted=_is_encrypted(doc),
            info=_read_info(doc),
            xmp=parse_xmp(xml or None),
        )
    finally:
        doc.close()


def _version(doc: pymupdf.Document) -> str | None:
    fmt = str((doc.metadata or {}).get("format") or "")
    parts = fmt.split()
    if len(parts) >= 2 and parts[0].upper() == "PDF":
        return parts[1]
    return None


def _is_encrypted(doc: pymupdf.Document) -> bool:
    kind, value = doc.xref_get_key(-1, "Encrypt")
    return kind not in ("null", "") and value not in ("", "null", None)


def _read_info(doc: pymupdf.Document) -> PdfInfo:
    meta = doc.metadata or {}
    info = PdfInfo(
        present=False,
        title=clean_text(meta.get("title")),
        author=clean_text(meta.get("author")),
        subject=clean_text(meta.get("subject")),
        keywords=clean_text(meta.get("keywords")),
        creator=clean_text(meta.get("creator")),
        producer=clean_text(meta.get("producer")),
        trapped=clean_text(meta.get("trapped")),
        creation_date=parse_pdf_date(clean_text(meta.get("creationDate"))),
        modification_date=parse_pdf_date(clean_text(meta.get("modDate"))),
        custom=_custom_keys(doc),
    )
    info.present = bool(
        info.title
        or info.author
        or info.subject
        or info.keywords
        or info.creator
        or info.producer
        or info.trapped
        or info.creation_date
        or info.modification_date
        or info.custom
    )
    return info


def _custom_keys(doc: pymupdf.Document) -> dict[str, str]:
    kind, value = doc.xref_get_key(-1, "Info")
    if kind != "xref" or not value:
        return {}
    xref = int(str(value).split()[0])
    custom: dict[str, str] = {}
    for key in doc.xref_get_keys(xref):
        if key in _STANDARD_KEYS:
            continue
        entry_kind, raw = doc.xref_get_key(xref, key)
        if entry_kind in ("null", "") or raw in ("", "null", None):
            continue
        text = clean_text(str(raw))
        if text:
            custom[key] = text
    return custom
