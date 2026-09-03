from __future__ import annotations

from typing import Any

import httpx


class WatchDocError(Exception):
    """Error from the WatchDoc HTTP API, or a missing API key."""

    def __init__(
        self,
        status: int | None,
        type: str,
        code: str,
        message: str,
    ) -> None:
        self.status = status
        self.type = type
        self.code = code
        self.message = message
        super().__init__(message)

    @classmethod
    def from_response(cls, response: httpx.Response) -> WatchDocError:
        error_type = "api_error"
        code = "http_error"
        message = response.text or response.reason_phrase or "WatchDoc API request failed."
        if "json" in response.headers.get("content-type", ""):
            payload: Any = response.json()
            detail = payload.get("error") if isinstance(payload, dict) else None
            if isinstance(detail, dict):
                error_type = str(detail.get("type") or error_type)
                code = str(detail.get("code") or code)
                message = str(detail.get("message") or message)
            elif isinstance(detail, str) and detail:
                message = detail
        return cls(response.status_code, error_type, code, message)


class UnsupportedFileError(Exception):
    """Raised when inspect() is given a file that is not a PDF or a supported image."""

    def __init__(self, message: str = "Unsupported file type.") -> None:
        self.message = message
        super().__init__(message)
