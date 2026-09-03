from __future__ import annotations

import hashlib

from watchdoc._source import Source, load_source, sniff
from watchdoc._version import __version__
from watchdoc.facts import Facts, FileFacts
from watchdoc.notes import notes_for
from watchdoc.readers.image import read_image
from watchdoc.readers.pdf import read_pdf


def inspect(source: Source, *, filename: str | None = None) -> Facts:
    """Read what a PDF or image says about itself. Local; never uploads."""
    data, name = load_source(source, filename=filename)
    kind, media_type = sniff(data)
    file_facts = FileFacts(
        name=name,
        size_bytes=len(data),
        sha256=hashlib.sha256(data).hexdigest(),
        media_type=media_type,
        kind=kind,
    )
    pdf = read_pdf(data) if kind == "pdf" else None
    image = read_image(data) if kind == "image" else None
    facts = Facts(
        schema_version="1",
        toolkit={"name": "watchdoc", "version": __version__},
        file=file_facts,
        pdf=pdf,
        image=image,
    )
    facts.notes = notes_for(facts)
    return facts
