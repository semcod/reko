"""Przykład: nieużywane stałe modułowe."""

from __future__ import annotations

API_VERSION = "v2"
UNUSED_ENDPOINT = "https://legacy.example.com/v1"
LEGACY_TIMEOUT = 120
ACTIVE_BASE = "https://api.example.com"


def build_url(path: str) -> str:
    return f"{ACTIVE_BASE}/{API_VERSION}/{path.lstrip('/')}"
