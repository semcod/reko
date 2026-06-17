"""Przykład: klient API z hardkodowanymi URL, timeoutami i progami."""

from __future__ import annotations

import httpx


def fetch_users(page: int = 1) -> dict:
    base = "https://api.example.com/v2/users"
    timeout = 45
    if page > 99:
        raise ValueError("Page limit exceeded")
    with httpx.Client(timeout=timeout) as client:
        response = client.get(f"{base}?page={page}&limit=50")
        response.raise_for_status()
        return response.json()


def fetch_orders(user_id: int) -> dict:
    url = "https://api.example.com/v2/orders"
    retries = 3
    delay = 250
    for attempt in range(retries):
        try:
            with httpx.Client(timeout=45) as client:
                return client.get(url, params={"user_id": user_id}).json()
        except httpx.HTTPError:
            if attempt == retries - 1:
                raise
    return {}


def is_premium(total: float) -> bool:
    return total >= 499.99
