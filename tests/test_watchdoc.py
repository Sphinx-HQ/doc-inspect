from __future__ import annotations

import io

import httpx
import pymupdf
import pytest
from PIL import Image

from watchdoc import Client, inspect
from watchdoc.errors import UnsupportedFileError, WatchDocError


def test_inspect_pdf_and_image() -> None:
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Hello")
    doc.set_metadata({"producer": "Example Writer", "creator": "Example Writer"})
    pdf = doc.tobytes()
    doc.close()

    facts = inspect(pdf, filename="a.pdf")
    assert facts.schema_version == "1"
    assert facts.file.kind == "pdf"
    assert facts.pdf is not None
    assert facts.pdf.info.producer == "Example Writer"

    buf = io.BytesIO()
    Image.new("RGB", (8, 8), color=(255, 0, 0)).save(buf, format="JPEG")
    image = inspect(buf.getvalue(), filename="a.jpg")
    assert image.file.kind == "image"
    assert image.image is not None


def test_inspect_rejects_unknown_type() -> None:
    with pytest.raises(UnsupportedFileError):
        inspect(b"hello", filename="a.txt")


def test_client_check() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer sk_test"
        assert "wait=true" in str(request.url)
        return httpx.Response(201, json={"id": "dc_1", "status": "completed"})

    result = Client(api_key="sk_test", transport=httpx.MockTransport(handler)).check(
        b"%PDF-1.4 x", filename="a.pdf"
    )
    assert result["id"] == "dc_1"


def test_client_missing_key() -> None:
    with pytest.raises(WatchDocError) as excinfo:
        Client(api_key="").check(b"%PDF-1.4 x", filename="a.pdf")
    assert excinfo.value.code == "missing_api_key"
