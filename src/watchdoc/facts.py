from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class PdfDate:
    raw: str | None
    iso: str | None


@dataclass
class PdfInfo:
    present: bool
    title: str | None = None
    author: str | None = None
    subject: str | None = None
    keywords: str | None = None
    creator: str | None = None
    producer: str | None = None
    trapped: str | None = None
    creation_date: PdfDate | None = None
    modification_date: PdfDate | None = None
    custom: dict[str, str] = field(default_factory=dict)


@dataclass
class XmpFacts:
    present: bool
    creator_tool: str | None = None
    create_date: str | None = None
    modify_date: str | None = None
    metadata_date: str | None = None
    producer: str | None = None
    title: str | None = None
    creators: list[str] = field(default_factory=list)
    document_id: str | None = None
    instance_id: str | None = None
    raw_xml_length: int = 0


@dataclass
class PdfFacts:
    version: str | None
    page_count: int
    encrypted: bool
    info: PdfInfo
    xmp: XmpFacts


@dataclass
class ExifFacts:
    present: bool
    make: str | None = None
    model: str | None = None
    software: str | None = None
    datetime: str | None = None
    datetime_original: str | None = None
    datetime_digitized: str | None = None
    orientation: int | None = None
    gps_present: bool = False
    raw: dict[str, str] = field(default_factory=dict)


@dataclass
class ImageFacts:
    format: str | None
    width: int
    height: int
    mode: str | None
    exif: ExifFacts


@dataclass
class FileFacts:
    name: str | None
    size_bytes: int
    sha256: str
    media_type: str
    kind: str


@dataclass
class Note:
    code: str
    text: str
    field: str | None = None


@dataclass
class Facts:
    schema_version: str
    toolkit: dict[str, str]
    file: FileFacts
    pdf: PdfFacts | None
    image: ImageFacts | None
    notes: list[Note] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int | None = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
