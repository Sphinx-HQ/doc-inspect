from __future__ import annotations

import base64
import json
import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from watchdoc import Client, UnsupportedFileError, WatchDocError, inspect

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MAX_UPLOAD_MB = 25
WATCHDOC_PRODUCT_URL = (
    "https://watchdoc.sphinxhq.com/?utm_source=oss&utm_medium=demo&utm_campaign=watchdoc-python"
)
LOCKED_TITLES = (
    "Visual tampering",
    "Font inconsistency",
    "Issuer deviation",
    "Risk decision",
    "Webhooks",
    "Org rules",
)
LOCKED_COPY = "Not in the open-source toolkit. Included on WatchDoc."


def _load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key and key not in os.environ:
            os.environ[key] = value


def _max_upload_bytes() -> int:
    megabytes = int(os.environ.get("DEMO_MAX_UPLOAD_MB", str(DEFAULT_MAX_UPLOAD_MB)))
    return max(megabytes, 1) * 1024 * 1024


def _api_key() -> str | None:
    key = os.environ.get("WATCHDOC_API_KEY", "").strip()
    return key or None


def create_app() -> Flask:
    _load_dotenv(ROOT / ".env")
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )
    app.config["MAX_CONTENT_LENGTH"] = _max_upload_bytes()

    @app.errorhandler(413)
    def too_large(_error: object) -> tuple[str, int]:
        return (
            render_template(
                "index.html",
                api_configured=bool(_api_key()),
                error="File is larger than the demo upload limit.",
                product_url=WATCHDOC_PRODUCT_URL,
            ),
            413,
        )

    @app.route("/", methods=["GET"])
    def index() -> str:
        return render_template(
            "index.html",
            api_configured=bool(_api_key()),
            error=None,
            product_url=WATCHDOC_PRODUCT_URL,
        )

    @app.route("/inspect", methods=["POST"])
    def inspect_form() -> str:
        payload = _run_inspect()
        if payload.get("error"):
            return (
                render_template(
                    "index.html",
                    api_configured=bool(_api_key()),
                    error=payload["error"],
                    product_url=WATCHDOC_PRODUCT_URL,
                ),
                payload["error_status"],
            )
        return render_template(
            "result.html",
            api_configured=bool(_api_key()),
            product_url=WATCHDOC_PRODUCT_URL,
            locked_titles=LOCKED_TITLES,
            locked_copy=LOCKED_COPY,
            **payload,
        )

    @app.route("/inspect.json", methods=["POST"])
    def inspect_json() -> tuple[object, int]:
        payload = _run_inspect(json_only=True)
        if payload.get("error"):
            return jsonify({"error": payload["error"]}), payload["error_status"]
        return jsonify(payload["facts"]), 200

    return app


def _run_inspect(*, json_only: bool = False) -> dict:
    uploaded = request.files.get("file")
    if uploaded is None or not uploaded.filename:
        return {"error": "Choose a PDF or image to inspect.", "error_status": 400}
    data = uploaded.read()
    if not data:
        return {"error": "Choose a PDF or image to inspect.", "error_status": 400}
    filename = Path(uploaded.filename).name
    try:
        facts = inspect(data, filename=filename)
    except UnsupportedFileError as exc:
        return {"error": str(exc), "error_status": 400}

    facts_dict = facts.to_dict()
    if json_only:
        return {"facts": facts_dict, "error": None, "error_status": 200}

    watchdoc = None
    watchdoc_error = None
    key = _api_key()
    if key and request.form.get("also_check") == "on":
        try:
            watchdoc = Client(api_key=key).check(data, filename=filename)
        except WatchDocError as exc:
            watchdoc_error = exc.message

    return {
        "error": None,
        "error_status": 200,
        "facts": facts_dict,
        "facts_json": json.dumps(facts_dict, indent=2, ensure_ascii=False),
        "preview_b64": base64.b64encode(data).decode("ascii"),
        "watchdoc": watchdoc,
        "watchdoc_error": watchdoc_error,
        "groups": _groups(facts_dict),
    }


def _groups(facts: dict) -> list[dict]:
    groups: list[dict] = [
        {
            "heading": "File",
            "slot": "Metadata",
            "rows": _flatten_prefix("file", facts.get("file") or {}),
        }
    ]
    pdf = facts.get("pdf")
    if pdf:
        info = pdf.get("info") or {}
        xmp = pdf.get("xmp") or {}
        groups.append(
            {
                "heading": "PDF",
                "slot": "Metadata",
                "rows": [
                    ("pdf.version", pdf.get("version")),
                    ("pdf.page_count", pdf.get("page_count")),
                    ("pdf.encrypted", pdf.get("encrypted")),
                ],
            }
        )
        groups.append(
            {
                "heading": "Info dictionary",
                "slot": "Metadata",
                "rows": _flatten_prefix("pdf.info", info),
            }
        )
        groups.append(
            {
                "heading": "XMP",
                "slot": "Provenance",
                "rows": _flatten_prefix("pdf.xmp", xmp),
            }
        )
    image = facts.get("image")
    if image:
        exif = image.get("exif") or {}
        groups.append(
            {
                "heading": "Image",
                "slot": "Metadata",
                "rows": [
                    ("image.format", image.get("format")),
                    ("image.width", image.get("width")),
                    ("image.height", image.get("height")),
                    ("image.mode", image.get("mode")),
                ],
            }
        )
        groups.append(
            {
                "heading": "EXIF",
                "slot": "Metadata",
                "rows": _flatten_prefix("image.exif", exif),
            }
        )
    notes = facts.get("notes") or []
    groups.append(
        {
            "heading": "Notes",
            "slot": "Metadata",
            "rows": [
                (
                    note.get("code") + (f" ({note.get('field')})" if note.get("field") else ""),
                    note.get("text"),
                )
                for note in notes
            ]
            or [("notes", "None")],
        }
    )
    return groups


def _flatten_prefix(prefix: str, value: object) -> list[tuple[str, object]]:
    rows: list[tuple[str, object]] = []
    if isinstance(value, dict):
        for key, inner in value.items():
            if key in ("raw", "custom") and isinstance(inner, dict):
                for nested_key, nested_val in inner.items():
                    rows.append((f"{prefix}.{key}.{nested_key}", nested_val))
                continue
            rows.extend(_flatten_prefix(f"{prefix}.{key}", inner))
        return rows
    if isinstance(value, list):
        rows.append((prefix, ", ".join(str(v) for v in value) if value else None))
        return rows
    rows.append((prefix, value))
    return rows
