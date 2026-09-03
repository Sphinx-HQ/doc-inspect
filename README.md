# WatchDoc open-source toolkit

Reads what a document says about itself. Facts, not verdicts.

Local inspection is free and runs on your machine. Production detection lives on
[WatchDoc](https://watchdoc.sphinxhq.com/?utm_source=oss&utm_medium=readme&utm_campaign=watchdoc-python).

## What it is

- A Python package that reports PDF Info, XMP, and image EXIF as structured facts.
- A thin client for WatchDoc's existing document-checks API, in the same import.
- A small local demo UI: upload a file, see a key/value table.

## What it is not

- A fraud decision, score, or risk rating.
- A replacement for WatchDoc.
- A catalogue of flags, rules, or editor-specific judgements.

## Install

```bash
pip install watchdoc
```

For the demo UI:

```bash
pip install "watchdoc[demo]"
```

With uv:

```bash
uv add watchdoc
```

Until this package is published to PyPI, install from a clone:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[demo,dev]"
```

## Quickstart

```python
from watchdoc import inspect

facts = inspect("samples/edited_statement.pdf")
print(facts.to_json())
```

Trimmed output:

```json
{
  "schema_version": "1",
  "file": {"name": "edited_statement.pdf", "kind": "pdf"},
  "pdf": {
    "info": {
      "creator": "Example Statement Writer 1.0",
      "creation_date": {"raw": "D:20240101120000Z", "iso": "2024-01-01T12:00:00Z"},
      "modification_date": {"raw": "D:20240615120000Z", "iso": "2024-06-15T12:00:00Z"}
    }
  },
  "notes": [
    {"code": "dates_differ", "text": "Creation and modification dates are not the same."}
  ]
}
```

### Same file, real decision

```python
from watchdoc import Client

client = Client()  # reads WATCHDOC_API_KEY
result = client.check("samples/edited_statement.pdf")
print(result["status"], result["decision"], result["summary"])
```

`Client.check` is one HTTP call: `POST /api/v1/document-checks/?wait=true`. If
WatchDoc is still processing, the dict comes back with `status: "processing"`.
Open that check on WatchDoc rather than waiting here.

See the [WatchDoc API docs](https://watchdoc.sphinxhq.com/api/docs/?utm_source=oss&utm_medium=readme&utm_campaign=watchdoc-python)
for authentication, polling, webhooks, and everything else the hosted API can do.

## Open source vs WatchDoc

| Capability | Open source | WatchDoc |
| --- | --- | --- |
| PDF Info + XMP facts | Yes | Yes |
| Image EXIF facts | Yes | Yes |
| Structural facts (save count, trailer ID, fonts) | Roadmap | Yes |
| Provenance markers (C2PA, generator tags) | Roadmap | Yes |
| Template match (hosted, free with API key) | Roadmap | Yes |
| Visual tampering | No | Yes |
| Font inconsistency | No | Yes |
| Issuer deviation | No | Yes |
| Risk decision and summary | No | Yes |
| Webhooks | No | Yes |
| Org rules | No | Yes |
| Dashboard | No | Yes |

## Demo UI

From a clone, with the package installed (`make install` or `pip install -e ".[demo,dev]"`):

```bash
make demo
# or: flask --app demo.app run
```

Open http://127.0.0.1:5000, upload a PDF or image, and read the facts table.
The demo is functional, not designed. Copy `.env.example` to `.env` and set
`WATCHDOC_API_KEY` if you want a live WatchDoc column next to the local facts.
Without a key, the demo shows locked cards for capabilities that run on WatchDoc
and a primary **Analyze on WatchDoc** button. It never fabricates hosted results.

## Facts schema

The JSON contract is documented in [docs/facts-schema.md](docs/facts-schema.md).
`schema_version` is `"1"`. Additive fields may appear later; removals need a
version bump.

## Samples

Four synthetic files live in [samples/](samples/). See [samples/README.md](samples/README.md)
for what `inspect()` reports locally, and run `Client.check` on
`samples/edited_statement.pdf` to see WatchDoc's result on the same file.

## Development

**venv + pip**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[demo,dev]"
make test
make lint
```

**uv**

```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[demo,dev]"
make test
make lint
```

Copy `.env.example` to `.env` for local demo configuration (`WATCHDOC_API_KEY`,
`WATCHDOC_BASE_URL`, `DEMO_MAX_UPLOAD_MB`).

Regenerate sample files with `make samples`.

## Roadmap

See [ROADMAP.md](ROADMAP.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Security

See [SECURITY.md](SECURITY.md).

## License

Apache License 2.0. See [LICENSE](LICENSE).

## Links

- Product: [watchdoc.sphinxhq.com](https://watchdoc.sphinxhq.com/?utm_source=oss&utm_medium=readme&utm_campaign=watchdoc-python)
- Company: [sphinxhq.com](https://sphinxhq.com/?utm_source=oss&utm_medium=readme&utm_campaign=watchdoc-python)
- API docs: [watchdoc.sphinxhq.com/api/docs/](https://watchdoc.sphinxhq.com/api/docs/?utm_source=oss&utm_medium=readme&utm_campaign=watchdoc-python)
