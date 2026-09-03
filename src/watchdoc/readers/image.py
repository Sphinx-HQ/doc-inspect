from __future__ import annotations

import io
from typing import Any

from PIL import ExifTags, Image
from PIL.ExifTags import IFD, Base

from watchdoc._text import clean_text
from watchdoc.facts import ExifFacts, ImageFacts

_GPS_IFD = int(IFD.GPSInfo)
_EXIF_IFD = int(IFD.Exif)
_SKIP_TAGS = {_GPS_IFD, _EXIF_IFD, int(Base.MakerNote), int(Base.UserComment)}
_TAG_NAMES = {int(k): v for k, v in ExifTags.TAGS.items()}


def read_image(data: bytes) -> ImageFacts:
    with Image.open(io.BytesIO(data)) as img:
        img.load()
        exif = _read_exif(img)
        png_software = img.info.get("Software")
        if png_software and not exif.software:
            exif.software = clean_text(str(png_software))
            exif.present = True
        return ImageFacts(
            format=img.format,
            width=img.size[0],
            height=img.size[1],
            mode=img.mode,
            exif=exif,
        )


def _read_exif(img: Image.Image) -> ExifFacts:
    exif = img.getexif()
    if not exif:
        return ExifFacts(present=False)

    ifd0 = dict(exif.items())
    exif_ifd = dict(exif.get_ifd(_EXIF_IFD))
    gps_ifd = dict(exif.get_ifd(_GPS_IFD))
    gps_present = bool(gps_ifd) or _GPS_IFD in ifd0

    merged: dict[int, Any] = {**ifd0, **exif_ifd}
    raw: dict[str, str] = {}
    for tag, value in merged.items():
        if tag in _SKIP_TAGS:
            continue
        rendered = _as_str(value)
        if rendered:
            raw[_TAG_NAMES.get(int(tag), str(tag))] = rendered

    orientation = merged.get(int(Base.Orientation))
    if orientation is not None:
        orientation = int(orientation)

    if not raw and not gps_present:
        return ExifFacts(present=False, gps_present=gps_present)

    return ExifFacts(
        present=True,
        make=_as_str(merged.get(int(Base.Make))),
        model=_as_str(merged.get(int(Base.Model))),
        software=_as_str(merged.get(int(Base.Software))),
        datetime=_as_str(merged.get(int(Base.DateTime))),
        datetime_original=_as_str(merged.get(int(Base.DateTimeOriginal))),
        datetime_digitized=_as_str(merged.get(int(Base.DateTimeDigitized))),
        orientation=orientation,
        gps_present=gps_present,
        raw=raw,
    )


def _as_str(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, bytes):
        value = value.decode("latin-1")
    elif isinstance(value, (list, tuple)):
        parts = [_as_str(v) for v in value]
        value = ", ".join(p for p in parts if p)
    elif isinstance(value, dict):
        return None
    return clean_text(str(value))
