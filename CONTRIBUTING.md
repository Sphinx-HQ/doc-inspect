# Contributing

Thank you for considering a contribution.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[demo,dev]"
make test
make lint
```

`uv` works the same way (`uv venv` then `uv pip install -e ".[demo,dev]"`).

## Facts only

This toolkit reports what a file contains. Pull requests should not add:

- Heuristics, thresholds, scores, severity, or confidence.
- Software or editor name lists.
- Verdicts, decisions, or risk language in `inspect()` output or notes.
- Copy or identifiers taken from proprietary sources.

If you are proposing a new fact, it should be something you can point to in a
public specification (PDF, XMP, EXIF, C2PA, and so on).

## Schema changes

Changes to the facts JSON require an update to [docs/facts-schema.md](docs/facts-schema.md).
Removing or renaming a field needs a discussion about bumping `schema_version`.

## License

By contributing you agree that your contribution is licensed under the Apache
License 2.0 in [LICENSE](LICENSE). A `Signed-off-by` line in the commit
(Developer Certificate of Origin) is welcome but not required.
