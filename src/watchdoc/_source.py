from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

from watchdoc.errors import UnsupportedFileError

PathLike = str | Path
Source = PathLike | bytes | BinaryIO


def load_source(source: Source, filename: str | None = None) -> tuple[bytes, str | None]:
    if isinstance(source, bytes):
        return source, filename
    if isinstance(source, (str, Path)):
        path = Path(source)
        return path.read_bytes(), filename if filename is not None else path.name
    data = source.read()
    if not isinstance(data, bytes):
        raise TypeError("file object must be opened in binary mode")
    name = filename
    if name is None:
        raw_name = getattr(source, "name", None)
        if isinstance(raw_name, str) and raw_name not in ("", "<stdin>"):
            name = Path(raw_name).name
    return data, name


def sniff(data: bytes) -> tuple[str, str]:
    if data.startswith(b"%PDF"):
        return "pdf", "application/pdf"
    if data.startswith(b"\xff\xd8\xff"):
        return "image", "image/jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image", "image/png"
    if data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
        return "image", "image/gif"
    if data.startswith(b"II*\x00") or data.startswith(b"MM\x00*"):
        return "image", "image/tiff"
    if len(data) >= 12 and data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return "image", "image/webp"
    raise UnsupportedFileError(
        "Unsupported file type. inspect() reads PDF and raster images (JPEG, PNG, GIF, TIFF, WebP)."
    )
