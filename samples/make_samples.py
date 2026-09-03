"""Generate the synthetic sample files committed under samples/.

Content is fictional Example Corp / Example Bank data. Re-run from the repo root:

    python samples/make_samples.py
"""

from __future__ import annotations

from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw, ImageFont
from PIL.ExifTags import Base

ROOT = Path(__file__).resolve().parent

EDITOR_CREATOR = "Example Layout Studio 4.2"
EDITOR_PRODUCER = "Example Layout Studio PDF 4.2"


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    write_edited_statement(ROOT / "edited_statement.pdf")
    write_invoice_editor_producer(ROOT / "invoice-editor-producer.pdf")
    write_statement_scrubbed(ROOT / "statement-scrubbed.pdf")
    write_receipt_photo(ROOT / "receipt-photo.jpg")
    print("Wrote sample files in", ROOT)


def write_edited_statement(path: Path) -> None:
    if path.exists():
        path.unlink()
    doc = pymupdf.open()
    page = doc.new_page(width=612, height=792)
    page.insert_text((72, 72), "Example Bank", fontsize=18)
    page.insert_text((72, 100), "Account statement - Example Corp", fontsize=12)
    page.insert_text((72, 140), "Opening balance     1,000.00", fontsize=11)
    page.insert_text((72, 158), "Closing balance     1,000.00", fontsize=11)
    page.insert_text((72, 200), "This document is synthetic sample content.", fontsize=9)
    doc.set_metadata(
        {
            "title": "Example Bank statement",
            "author": "Example Bank",
            "creator": "Example Statement Writer 1.0",
            "producer": "Example Statement Writer 1.0",
            "creationDate": "D:20240101120000Z",
            "modDate": "D:20240101120000Z",
        }
    )
    doc.save(path)
    doc.close()

    doc = pymupdf.open(path)
    page = doc[0]
    page.insert_text((72, 176), "Adjustment posted    8,999.00", fontsize=11)
    page.insert_text((72, 220), "Closing balance     9,999.00", fontsize=11)
    doc.set_metadata(
        {
            "title": "Example Bank statement",
            "author": "Example Bank",
            "creator": "Example Statement Writer 1.0",
            "producer": "Example Statement Writer 1.0",
            "creationDate": "D:20240101120000Z",
            "modDate": "D:20240615120000Z",
        }
    )
    doc.saveIncr()
    doc.close()


def write_invoice_editor_producer(path: Path) -> None:
    doc = pymupdf.open()
    page = doc.new_page(width=612, height=792)
    page.insert_text((72, 72), "INVOICE", fontsize=18)
    page.insert_text((72, 110), "From: Example Corp", fontsize=12)
    page.insert_text((72, 128), "Bill to: Example Customer", fontsize=12)
    page.insert_text((72, 160), "Consulting services          250.00", fontsize=11)
    page.insert_text((72, 200), "This document is synthetic sample content.", fontsize=9)
    doc.set_metadata(
        {
            "title": "Invoice 1001",
            "author": "Example Corp",
            "creator": EDITOR_CREATOR,
            "producer": EDITOR_PRODUCER,
            "creationDate": "D:20240115100000Z",
            "modDate": "D:20240420153000Z",
        }
    )
    xmp = f"""<?xpacket begin="" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/">
  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description rdf:about=""
        xmlns:xmp="http://ns.adobe.com/xap/1.0/"
        xmlns:pdf="http://ns.adobe.com/pdf/1.3/"
        xmlns:dc="http://purl.org/dc/elements/1.1/">
      <xmp:CreatorTool>{EDITOR_CREATOR}</xmp:CreatorTool>
      <xmp:CreateDate>2024-01-15T10:00:00Z</xmp:CreateDate>
      <xmp:ModifyDate>2024-02-01T09:00:00Z</xmp:ModifyDate>
      <pdf:Producer>{EDITOR_PRODUCER}</pdf:Producer>
      <dc:title>
        <rdf:Alt>
          <rdf:li xml:lang="x-default">Invoice 1001</rdf:li>
        </rdf:Alt>
      </dc:title>
    </rdf:Description>
  </rdf:RDF>
</x:xmpmeta>
<?xpacket end="w"?>"""
    doc.set_xml_metadata(xmp)
    doc.save(path, garbage=4, deflate=True)
    doc.close()


def write_statement_scrubbed(path: Path) -> None:
    doc = pymupdf.open()
    page = doc.new_page(width=612, height=792)
    page.insert_text((72, 72), "Example Bank", fontsize=18)
    page.insert_text((72, 110), "Account summary - Example Corp", fontsize=12)
    page.insert_text((72, 150), "Available funds     500.00", fontsize=11)
    page.insert_text((72, 200), "This document is synthetic sample content.", fontsize=9)
    doc.set_metadata({})
    doc.del_xml_metadata()
    first = doc.tobytes()
    doc.close()
    doc = pymupdf.open(stream=first, filetype="pdf")
    doc.del_xml_metadata()
    doc.xref_set_key(-1, "Info", "null")
    path.write_bytes(doc.tobytes())
    doc.close()


def write_receipt_photo(path: Path) -> None:
    image = Image.new("RGB", (640, 800), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    lines = [
        "EXAMPLE MART",
        "Store #12",
        "",
        "Paper clips              3.50",
        "Notebook                 6.00",
        "",
        "Total                    9.50",
        "",
        "Synthetic sample image.",
    ]
    y = 40
    for line in lines:
        draw.text((40, y), line, fill=(20, 20, 20), font=font)
        y += 28
    exif = image.getexif()
    exif[Base.Make] = "ExampleCam"
    exif[Base.Model] = "DeskScan 2"
    exif[Base.Software] = "Example Photo App 1.0"
    exif[Base.DateTime] = "2024:03:01 12:00:00"
    exif[Base.DateTimeOriginal] = "2024:03:01 12:00:00"
    image.save(path, format="JPEG", exif=exif, quality=90)


if __name__ == "__main__":
    main()
