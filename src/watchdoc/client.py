from __future__ import annotations

import os
from pathlib import Path
from typing import Any, BinaryIO

import httpx

from watchdoc._source import load_source
from watchdoc._version import __version__
from watchdoc.errors import WatchDocError

DEFAULT_BASE_URL = "https://watchdoc.sphinxhq.com"
_DEFAULT_TIMEOUT = 60.0
_CHECK_PATH = "/api/v1/document-checks/"


class Client:
    """POST a file to WatchDoc ``/api/v1/document-checks/?wait=true`` and return the JSON."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = _DEFAULT_TIMEOUT,
        *,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else os.environ.get("WATCHDOC_API_KEY")
        raw_base = base_url if base_url is not None else os.environ.get("WATCHDOC_BASE_URL")
        self.base_url = (raw_base or DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self._transport = transport

    def check(
        self,
        source: str | Path | bytes | BinaryIO,
        *,
        filename: str | None = None,
    ) -> dict[str, Any]:
        if not self.api_key:
            raise WatchDocError(
                status=None,
                type="authentication_error",
                code="missing_api_key",
                message="Set WATCHDOC_API_KEY or pass api_key= to Client().",
            )
        data, name = load_source(source, filename=filename)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": f"watchdoc-python/{__version__}",
        }
        with httpx.Client(timeout=self.timeout, transport=self._transport) as http:
            response = http.post(
                f"{self.base_url}{_CHECK_PATH}",
                params={"wait": "true"},
                files={"file": (name or "document", data)},
                headers=headers,
            )
        if not response.is_success:
            raise WatchDocError.from_response(response)
        payload = response.json()
        if not isinstance(payload, dict):
            raise WatchDocError(
                status=response.status_code,
                type="api_error",
                code="invalid_json",
                message="WatchDoc API returned JSON that was not an object.",
            )
        return payload
