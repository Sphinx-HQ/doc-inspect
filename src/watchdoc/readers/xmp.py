from __future__ import annotations

import xml.etree.ElementTree as ET

from watchdoc.facts import XmpFacts

RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
XMP = "http://ns.adobe.com/xap/1.0/"
PDF = "http://ns.adobe.com/pdf/1.3/"
DC = "http://purl.org/dc/elements/1.1/"
XMPMM = "http://ns.adobe.com/xap/1.0/mm/"
_CONTAINERS = {f"{{{RDF}}}Alt", f"{{{RDF}}}Seq", f"{{{RDF}}}Bag"}
_LI = f"{{{RDF}}}li"
_DESCRIPTION = f"{{{RDF}}}Description"

_TAGS = {
    f"{{{XMP}}}CreatorTool": "creator_tool",
    f"{{{XMP}}}CreateDate": "create_date",
    f"{{{XMP}}}ModifyDate": "modify_date",
    f"{{{XMP}}}MetadataDate": "metadata_date",
    f"{{{PDF}}}Producer": "producer",
    f"{{{DC}}}title": "title",
    f"{{{DC}}}creator": "creators",
    f"{{{XMPMM}}}DocumentID": "document_id",
    f"{{{XMPMM}}}InstanceID": "instance_id",
}


def parse_xmp(xml_text: str | None) -> XmpFacts:
    if not xml_text or not xml_text.strip():
        return XmpFacts(present=False)
    xml_text = xml_text.strip()
    facts = XmpFacts(present=True, raw_xml_length=len(xml_text))
    try:
        root = ET.fromstring(_unwrap_xpacket(xml_text))
    except ET.ParseError:
        return facts

    found: dict[str, str | list[str]] = {}
    for el in root.iter():
        name = _TAGS.get(el.tag)
        if name and name not in found:
            found[name] = _list_values(el) if name == "creators" else (_scalar(el) or "")
        if el.tag != _DESCRIPTION:
            continue
        for qname, raw in el.attrib.items():
            name = _TAGS.get(qname)
            if name and name not in found and raw:
                found[name] = [raw] if name == "creators" else raw

    facts.creator_tool = _as_optional(found.get("creator_tool"))
    facts.create_date = _as_optional(found.get("create_date"))
    facts.modify_date = _as_optional(found.get("modify_date"))
    facts.metadata_date = _as_optional(found.get("metadata_date"))
    facts.producer = _as_optional(found.get("producer"))
    facts.title = _as_optional(found.get("title"))
    creators = found.get("creators") or []
    facts.creators = [c for c in creators if c] if isinstance(creators, list) else [creators]
    facts.document_id = _as_optional(found.get("document_id"))
    facts.instance_id = _as_optional(found.get("instance_id"))
    return facts


def _unwrap_xpacket(text: str) -> str:
    start = text.find("<")
    end = text.rfind(">")
    if start == -1 or end <= start:
        return text
    return text[start : end + 1]


def _text(el: ET.Element) -> str | None:
    if el.text and el.text.strip():
        return el.text.strip()
    return None


def _list_values(el: ET.Element) -> list[str]:
    items: list[str] = []
    for child in el:
        if child.tag in _CONTAINERS:
            items.extend(_list_values(child))
        elif child.tag == _LI:
            text = _text(child)
            if text:
                items.append(text)
            else:
                items.extend(_list_values(child))
    if not items:
        text = _text(el)
        if text:
            items.append(text)
    return items


def _scalar(el: ET.Element) -> str | None:
    items = _list_values(el)
    return items[0] if items else _text(el)


def _as_optional(value: str | list[str] | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, list):
        return value[0].strip() or None if value else None
    return value.strip() or None
