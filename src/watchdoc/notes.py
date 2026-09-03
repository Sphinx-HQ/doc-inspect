from __future__ import annotations

from datetime import datetime

from watchdoc.facts import Facts, ImageFacts, Note, PdfDate, PdfFacts, PdfInfo, XmpFacts


def notes_for(facts: Facts) -> list[Note]:
    if facts.pdf is not None:
        return _pdf_notes(facts.pdf)
    if facts.image is not None:
        return _image_notes(facts.image)
    return []


def _pdf_notes(pdf: PdfFacts) -> list[Note]:
    info = pdf.info
    xmp = pdf.xmp
    notes: list[Note] = []
    if not info.present and not xmp.present:
        notes.append(
            Note(
                code="no_metadata",
                text="No PDF Info dictionary and no XMP metadata packet were found.",
            )
        )
        return notes
    if not info.present:
        notes.append(Note(code="info_absent", text="No PDF Info dictionary was found."))
    if not xmp.present:
        notes.append(Note(code="xmp_absent", text="No XMP metadata packet was found."))
    if info.present and xmp.present:
        notes.extend(_info_xmp_differs(info, xmp))
    notes.extend(_dates_differ(info, xmp))
    return notes


def _image_notes(image: ImageFacts) -> list[Note]:
    if image.exif.present:
        return []
    return [Note(code="exif_absent", text="No EXIF metadata was found.")]


def _info_xmp_differs(info: PdfInfo, xmp: XmpFacts) -> list[Note]:
    pairs = (
        (_text(info.producer), _text(xmp.producer), "producer"),
        (_text(info.creator), _text(xmp.creator_tool), "creator"),
        (_text(info.title), _text(xmp.title), "title"),
        (_date_text(info.creation_date), _text(xmp.create_date), "creation_date"),
        (_date_text(info.modification_date), _text(xmp.modify_date), "modification_date"),
    )
    notes: list[Note] = []
    for left, right, field in pairs:
        if left is None or right is None or _values_equal(left, right):
            continue
        notes.append(
            Note(
                code="info_xmp_differ",
                field=field,
                text=f"Info dict and XMP report different {field.replace('_', ' ')} values.",
            )
        )
    return notes


def _dates_differ(info: PdfInfo, xmp: XmpFacts) -> list[Note]:
    created = _date_text(info.creation_date)
    modified = _date_text(info.modification_date)
    if created is None or modified is None:
        created = _text(xmp.create_date)
        modified = _text(xmp.modify_date)
    if created is None or modified is None or _values_equal(created, modified):
        return []
    return [Note(code="dates_differ", text="Creation and modification dates are not the same.")]


def _text(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _date_text(value: PdfDate | None) -> str | None:
    if value is None:
        return None
    return value.iso or value.raw


def _values_equal(left: str, right: str) -> bool:
    if left == right:
        return True
    parsed_left = _parse_any_date(left)
    parsed_right = _parse_any_date(right)
    if parsed_left is not None and parsed_right is not None:
        return parsed_left == parsed_right
    return " ".join(left.split()).casefold() == " ".join(right.split()).casefold()


def _parse_any_date(value: str) -> datetime | None:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    for candidate in (text, text.replace(" ", "T")):
        try:
            return datetime.fromisoformat(candidate)
        except ValueError:
            continue
    return None
