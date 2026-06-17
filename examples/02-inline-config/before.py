"""Przykład: osadzona konfiguracja aplikacji."""

from __future__ import annotations


def get_settings() -> dict:
    return {
        "app_name": "RekoDemo",
        "debug": False,
        "database": {
            "host": "db.internal.local",
            "port": 5432,
            "name": "reko_demo",
            "pool_size": 10,
        },
        "cache": {
            "backend": "redis",
            "ttl_seconds": 900,
            "prefix": "reko:",
        },
        "features": ["scan", "extract", "split", "move"],
    }


DEFAULT_HEADERS = ["Content-Type", "Authorization", "X-Request-Id", "Accept", "User-Agent"]
