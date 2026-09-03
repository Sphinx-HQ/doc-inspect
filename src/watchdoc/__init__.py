from watchdoc._version import __version__
from watchdoc.client import Client
from watchdoc.errors import UnsupportedFileError, WatchDocError
from watchdoc.facts import Facts
from watchdoc.inspect import inspect

__all__ = [
    "Client",
    "Facts",
    "UnsupportedFileError",
    "WatchDocError",
    "__version__",
    "inspect",
]
