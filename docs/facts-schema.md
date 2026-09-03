# Facts schema

`inspect()` returns a `Facts` object. `Facts.to_dict()` / `Facts.to_json()` emit this
JSON. `schema_version` is `"1"`. Additive fields may appear in later toolkit
versions; removing or renaming a field requires a `schema_version` bump and a
discussion in the pull request (see [CONTRIBUTING.md](../CONTRIBUTING.md)).

Unknown or missing values are JSON `null`. The toolkit reports what the file
contains. It does not decide whether a document is genuine.

## Top level

| Field | Type | Meaning |
| --- | --- | --- |
| `schema_version` | string | Facts contract version. Currently `"1"`. |
| `toolkit.name` | string | Always `"watchdoc"`. |
| `toolkit.version` | string | Package version. |
| `file` | object | The bytes that were read. |
| `pdf` | object or null | Present for PDFs; `null` for images. |
| `image` | object or null | Present for raster images; `null` for PDFs. |
| `notes` | array | Observational notes derived from the fields above. |

## `file`

| Field | Type | Meaning |
| --- | --- | --- |
| `name` | string or null | Filename if one was provided. |
| `size_bytes` | integer | Length of the file. |
| `sha256` | string | Hex SHA-256 of the bytes. |
| `media_type` | string | Sniffed media type, e.g. `application/pdf`. |
| `kind` | string | `"pdf"` or `"image"`. |

## `pdf`

| Field | Type | Meaning |
| --- | --- | --- |
| `version` | string or null | Header version, e.g. `"1.7"`. |
| `page_count` | integer | Number of pages. |
| `encrypted` | boolean | Whether the trailer names an Encrypt dictionary. |
| `info` | object | Document Information Dictionary (ISO 32000-1 §14.3.3). |
| `xmp` | object | XMP packet, if any (ISO 32000-1 §14.3.2). |

### `pdf.info`

| Field | Type | Meaning |
| --- | --- | --- |
| `present` | boolean | True when the Info dict exists and has at least one value. |
| `title`, `author`, `subject`, `keywords`, `creator`, `producer`, `trapped` | string or null | Standard Info keys. |
| `creation_date`, `modification_date` | object or null | `{ "raw": "D:…", "iso": "…" }`. `iso` is null when the raw string does not parse as a PDF date (ISO 32000-1 §7.9.4). |
| `custom` | object | Any other Info keys, string to string. |

### `pdf.xmp`

| Field | Type | Meaning |
| --- | --- | --- |
| `present` | boolean | True when an XMP packet was found. |
| `creator_tool` | string or null | `xmp:CreatorTool`. |
| `create_date` | string or null | `xmp:CreateDate`. |
| `modify_date` | string or null | `xmp:ModifyDate`. |
| `metadata_date` | string or null | `xmp:MetadataDate`. |
| `producer` | string or null | `pdf:Producer`. |
| `title` | string or null | `dc:title` (first `rdf:Alt` entry when present). |
| `creators` | array of string | `dc:creator` sequence. |
| `document_id` | string or null | `xmpMM:DocumentID`. |
| `instance_id` | string or null | `xmpMM:InstanceID`. |
| `raw_xml_length` | integer | Byte length of the XML as stored. The XML itself is not included. |

Malformed XMP still sets `present` to true and leaves fields null.

## `image`

| Field | Type | Meaning |
| --- | --- | --- |
| `format` | string or null | Pillow format name, e.g. `JPEG`. |
| `width`, `height` | integer | Pixel size. |
| `mode` | string or null | Pixel mode, e.g. `RGB`. |
| `exif` | object | EXIF IFD0 + Exif IFD. |

### `image.exif`

| Field | Type | Meaning |
| --- | --- | --- |
| `present` | boolean | True when EXIF tags were found. |
| `make`, `model`, `software` | string or null | IFD0 camera / software tags. `software` also includes a PNG `Software` text chunk when EXIF has none. |
| `datetime` | string or null | IFD0 DateTime. |
| `datetime_original`, `datetime_digitized` | string or null | Exif IFD date tags. |
| `orientation` | integer or null | IFD0 Orientation. |
| `gps_present` | boolean | True when a GPS IFD is present. Coordinates are not decoded. |
| `raw` | object | Other IFD0 / Exif IFD tags as name → string. GPS tags and large binary blobs are omitted. |

## `notes`

Each note is `{ "code": "…", "text": "…", "field": "…" }`. `field` is null except
for `info_xmp_differ`.

| Code | When |
| --- | --- |
| `no_metadata` | PDF with no Info dict and no XMP. |
| `info_absent` | PDF with XMP but no Info dict. |
| `xmp_absent` | PDF with Info but no XMP. |
| `info_xmp_differ` | Both present, and the named field disagrees. |
| `dates_differ` | Creation and modification dates are not the same. |
| `exif_absent` | Image with no EXIF. |

Notes describe presence and consistency. They do not name software, assign
severity, or decide authenticity.
